"""
Train Eligibility Scoring Model (XGBoost)
Use Case: AI-PLATFORM-03 - Auto Identification of Beneficiaries
"""

import sys
from pathlib import Path
from typing import List
import pandas as pd
import numpy as np
from datetime import datetime
import yaml
import json
import joblib
import pickle
import warnings
warnings.filterwarnings('ignore')

import xgboost as xgb
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, mean_squared_error, mean_absolute_error, r2_score,
    classification_report, confusion_matrix, average_precision_score
)

import mlflow
import mlflow.xgboost
import mlflow.sklearn
import shap

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class EligibilityModelTrainer:
    """Train XGBoost model for eligibility scoring per scheme"""
    
    def __init__(self, config_path=None):
        """Initialize trainer"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "model_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Database connections
        db_config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
        with open(db_config_path, 'r') as f:
            db_config = yaml.safe_load(f)
        
        # 360° Profile database (for training data)
        profile_db_config = db_config['external_databases']['profile_360']
        self.db = DBConnector(
            host=profile_db_config['host'],
            port=profile_db_config['port'],
            database=profile_db_config['name'],
            user=profile_db_config['user'],
            password=profile_db_config['password']
        )
        self.db.connect()
        
        # Eligibility database (for saving model metadata)
        eligibility_db_config = db_config['database']
        self.eligibility_db = DBConnector(
            host=eligibility_db_config['host'],
            port=eligibility_db_config['port'],
            database=eligibility_db_config['name'],
            user=eligibility_db_config['user'],
            password=eligibility_db_config['password']
        )
        self.eligibility_db.connect()
        
        # MLflow setup
        mlflow_config = self.config['mlflow']
        mlflow.set_tracking_uri(mlflow_config['tracking_uri'])
        mlflow.set_experiment(mlflow_config['experiment_name'])
        
        # Model config
        self.model_config = self.config['eligibility_scoring']
    
    def load_training_data(self, scheme_code: str, min_samples: int = 100) -> pd.DataFrame:
        """
        Load training data from historical beneficiaries
        
        Args:
            scheme_code: Scheme code to train for (e.g., 'CHIRANJEEVI')
            min_samples: Minimum samples required
        
        Returns:
            DataFrame with features and target
        """
        print(f"📊 Loading training data for scheme {scheme_code}...")
        
        # Query: Get historical beneficiaries (approved applications) and non-beneficiaries
        # Join with scheme_master to get scheme_id from scheme_code
        query = """
            SELECT DISTINCT ON (gr.gr_id)
                gr.gr_id,
                gr.family_id,
                gr.age,
                gr.gender,
                gr.caste_id,
                gr.district_id,
                gr.is_urban,
                gr.city_village,
                
                -- Family composition
                (SELECT COUNT(*) FROM golden_records 
                 WHERE family_id = gr.family_id OR (family_id IS NULL AND gr_id = gr.gr_id)) as family_size,
                
                -- Benefits history
                COALESCE((
                    SELECT SUM(amount) 
                    FROM benefit_events be
                    INNER JOIN public.scheme_master sm ON be.scheme_id = sm.scheme_id
                    WHERE be.gr_id = gr.gr_id 
                    AND be.txn_date >= CURRENT_DATE - INTERVAL '1 year'
                    AND sm.scheme_code = %s
                ), 0) as benefits_received_1y,
                
                COALESCE((
                    SELECT COUNT(DISTINCT be.scheme_id)
                    FROM benefit_events be
                    WHERE be.gr_id = gr.gr_id
                ), 0) as schemes_enrolled_count,
                
                -- Application status (target variable)
                CASE 
                    WHEN EXISTS (
                        SELECT 1 FROM application_events ae
                        INNER JOIN public.scheme_master sm ON ae.scheme_id = sm.scheme_id
                        WHERE ae.gr_id = gr.gr_id 
                        AND sm.scheme_code = %s
                        AND ae.application_status = 'APPROVED'
                    ) THEN 1
                    ELSE 0
                END as is_eligible,
                
                -- Income band (from 360° Profile)
                p.inferred_income_band,
                
                -- Socio-economic
                se.education_level,
                se.employment_type,
                se.house_type
                
            FROM golden_records gr
            LEFT JOIN profile_360 p ON gr.gr_id = p.gr_id
            LEFT JOIN socio_economic_facts se ON gr.gr_id = se.gr_id
            WHERE gr.status = 'active'
                AND (
                    -- Has application for this scheme (approved or rejected)
                    EXISTS (
                        SELECT 1 FROM application_events ae
                        INNER JOIN public.scheme_master sm ON ae.scheme_id = sm.scheme_id
                        WHERE ae.gr_id = gr.gr_id AND sm.scheme_code = %s
                    )
                    OR
                    -- Currently receiving benefits from this scheme
                    EXISTS (
                        SELECT 1 FROM benefit_events be
                        INNER JOIN public.scheme_master sm ON be.scheme_id = sm.scheme_id
                        WHERE be.gr_id = gr.gr_id AND sm.scheme_code = %s
                    )
                )
            ORDER BY gr.gr_id
        """
        
        df = pd.read_sql(query, self.db.connection, params=(scheme_code, scheme_code, scheme_code, scheme_code))
        
        if len(df) < min_samples:
            raise ValueError(f"Insufficient training data: {len(df)} samples (minimum: {min_samples})")
        
        print(f"✅ Loaded {len(df)} training samples")
        print(f"   Eligible: {df['is_eligible'].sum()}, Not Eligible: {(~df['is_eligible'].astype(bool)).sum()}")
        
        return df
    
    def prepare_features(self, df: pd.DataFrame) -> tuple:
        """
        Prepare features for training
        
        Returns:
            Tuple of (X, y, feature_names)
        """
        print("🔧 Preparing features...")
        
        # Feature config
        feature_config = self.model_config['feature_engineering']
        
        # Select features
        feature_columns = []
        
        # Demographic features
        if 'demographics' in feature_config:
            for feat in feature_config['demographics']:
                if feat in df.columns:
                    feature_columns.append(feat)
        
        # Household features
        if 'household' in feature_config:
            for feat in feature_config['household']:
                if feat in df.columns or 'family_size' in feat:
                    if feat == 'family_size':
                        feature_columns.append('family_size')
        
        # Income features
        if 'income_assets' in feature_config:
            for feat in feature_config['income_assets']:
                if feat in df.columns or 'benefits_received_1y' in feat:
                    feature_columns.append('benefits_received_1y')
                    feature_columns.append('schemes_enrolled_count')
        
        # Education/Employment
        if 'education_employment' in feature_config:
            for feat in feature_config['education_employment']:
                if feat in df.columns:
                    feature_columns.append(feat)
        
        # Handle categorical features
        categorical_features = ['gender', 'caste_id', 'inferred_income_band', 'education_level', 'employment_type', 'house_type', 'is_urban']
        
        # Encode categoricals
        label_encoders = {}
        for col in categorical_features:
            if col in df.columns and col in feature_columns:
                le = LabelEncoder()
                df[f'{col}_encoded'] = df[col].astype(str).fillna('UNKNOWN')
                df[f'{col}_encoded'] = le.fit_transform(df[f'{col}_encoded'])
                feature_columns.remove(col)
                feature_columns.append(f'{col}_encoded')
                label_encoders[col] = le
        
        # Fill missing values
        X = df[feature_columns].copy()
        X = X.fillna(0)
        
        # Target
        y = df['is_eligible'].astype(int)
        
        print(f"✅ Prepared {len(feature_columns)} features")
        print(f"   Features: {feature_columns[:10]}...")
        
        return X, y, feature_columns, label_encoders
    
    def train(self, scheme_code: str, save_model: bool = True):
        """
        Train model for a scheme
        
        Args:
            scheme_code: Scheme code (e.g., 'CHIRANJEEVI')
            save_model: Whether to save model to registry
        """
        print(f"\n{'='*80}")
        print(f"Training Eligibility Model for Scheme: {scheme_code}")
        print(f"{'='*80}\n")
        
        # Load data
        df = self.load_training_data(scheme_code)
        
        # Prepare features
        X, y, feature_names, label_encoders = self.prepare_features(df)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.model_config['training']['train_test_split'],
            random_state=42, stratify=y
        )
        
        print(f"\n📊 Data Split:")
        print(f"   Train: {len(X_train)} samples")
        print(f"   Test: {len(X_test)} samples")
        
        # Get hyperparameters
        params = self.model_config['hyperparameters'].copy()
        # Add eval_metric to params (for newer XGBoost versions)
        eval_metric = self.model_config['training']['eval_metric']
        params['eval_metric'] = eval_metric
        
        # Start MLflow run
        with mlflow.start_run(run_name=f"{scheme_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
                # Log parameters
                mlflow.log_params({
                    'scheme_code': scheme_code,
                    'model_type': 'xgboost',
                    'objective': self.model_config['objective'],
                    **params
                })
                
                mlflow.set_tags({
                    'use_case': 'AI-PLATFORM-03',
                    'model_name': f'EligibilityScorer_{scheme_code}',
                    'scheme_code': scheme_code
                })
                
                # Train model
                print(f"\n🚀 Training XGBoost model...")
                model = xgb.XGBClassifier(**params)
                
                # Early stopping
                eval_set = [(X_train, y_train), (X_test, y_test)]
                early_stopping_rounds = self.model_config['training']['early_stopping_rounds']
                
                # Try XGBoost 2.0+ callback approach first, fallback to older API
                try:
                    # XGBoost 2.0+ uses callbacks
                    try:
                        from xgboost.callback import EarlyStopping
                        callbacks = [EarlyStopping(rounds=early_stopping_rounds)]
                        model.fit(
                            X_train, y_train,
                            eval_set=eval_set,
                            callbacks=callbacks,
                            verbose=False
                        )
                    except ImportError:
                        # Try alternative import path
                        import xgboost.callback as xgb_callback
                        callbacks = [xgb_callback.EarlyStopping(rounds=early_stopping_rounds)]
                        model.fit(
                            X_train, y_train,
                            eval_set=eval_set,
                            callbacks=callbacks,
                            verbose=False
                        )
                except (TypeError, AttributeError) as e:
                    # If callback approach fails, try older API with early_stopping_rounds
                    try:
                        model.fit(
                            X_train, y_train,
                            eval_set=eval_set,
                            early_stopping_rounds=early_stopping_rounds,
                            verbose=False
                        )
                    except TypeError:
                        # If that also fails, fit without early stopping
                        print(f"⚠️  Early stopping not supported, training without it")
                        model.fit(
                            X_train, y_train,
                            eval_set=eval_set,
                            verbose=False
                        )
                
                # Predictions
                y_pred = model.predict(X_test)
                y_pred_proba = model.predict_proba(X_test)[:, 1]
                
                # Metrics
                accuracy = accuracy_score(y_test, y_pred)
                precision = precision_score(y_test, y_pred, zero_division=0)
                recall = recall_score(y_test, y_pred, zero_division=0)
                f1 = f1_score(y_test, y_pred, zero_division=0)
                roc_auc = roc_auc_score(y_test, y_pred_proba)
                pr_auc = average_precision_score(y_test, y_pred_proba)
                
                print(f"\n📈 Model Performance:")
                print(f"   Accuracy:  {accuracy:.4f}")
                print(f"   Precision: {precision:.4f}")
                print(f"   Recall:    {recall:.4f}")
                print(f"   F1 Score:  {f1:.4f}")
                print(f"   ROC-AUC:   {roc_auc:.4f}")
                print(f"   PR-AUC:    {pr_auc:.4f}")
                
                # Log metrics
                mlflow.log_metrics({
                    'accuracy': accuracy,
                    'precision': precision,
                    'recall': recall,
                    'f1_score': f1,
                    'roc_auc': roc_auc,
                    'pr_auc': pr_auc
                })
                
                # Feature importance
                feature_importance = dict(zip(feature_names, model.feature_importances_))
                importance_df = pd.DataFrame([
                    {'feature': k, 'importance': v}
                    for k, v in sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
                ])
                
                # Log feature importance
                mlflow.log_dict(importance_df.to_dict('records'), 'feature_importance.json')
                
                # SHAP explainability
                try:
                    print(f"\n🔍 Computing SHAP values...")
                    explainer = shap.TreeExplainer(model)
                    shap_values = explainer.shap_values(X_test[:100])  # Sample for speed
                    
                    # Log SHAP summary plot (artifact)
                    import matplotlib.pyplot as plt
                    plt.figure(figsize=(10, 8))
                    shap.summary_plot(shap_values, X_test[:100], show=False)
                    plt.tight_layout()
                    shap_path = Path(__file__).parent.parent / "models" / f"shap_summary_{scheme_code}.png"
                    shap_path.parent.mkdir(exist_ok=True)
                    plt.savefig(shap_path)
                    plt.close()
                    mlflow.log_artifact(str(shap_path))
                
                except Exception as e:
                    print(f"⚠️  SHAP computation failed: {e}")
                
                # Log model
                model_name = f"{self.config['mlflow']['registered_model_prefix']}_{scheme_code}"
                
                # Try different methods to log model (handle version compatibility)
                try:
                    # Method 1: Try xgboost.log_model first
                    mlflow.xgboost.log_model(
                        model,
                        "model",
                        registered_model_name=model_name
                    )
                except (TypeError, AttributeError) as e:
                    # Method 2: Use sklearn.log_model (XGBClassifier is sklearn-compatible)
                    # mlflow.sklearn is already imported at the top
                    try:
                        mlflow.sklearn.log_model(
                            model,
                            "model",
                            registered_model_name=model_name
                        )
                    except Exception as e2:
                        # Method 3: Save model file using joblib and log as artifact
                        print(f"⚠️  Direct model logging failed, saving as artifact: {e2}")
                        import tempfile
                        import os
                        
                        with tempfile.NamedTemporaryFile(mode='wb', suffix='.pkl', delete=False) as f:
                            joblib.dump(model, f)
                            temp_path = f.name
                        
                        mlflow.log_artifact(temp_path, "model")
                        # Also save model path for reference
                        mlflow.log_param("model_saved_as", "joblib_artifact")
                        os.unlink(temp_path)  # Clean up temp file
                
                # Save model metadata to database
                if save_model:
                    run_id = mlflow.active_run().info.run_id
                    self._save_model_registry(
                        scheme_code, model_name, run_id, feature_names,
                        len(X_train), accuracy, precision, recall, f1, roc_auc
                    )
                
                # Log model description
                model_desc = f"""
Eligibility Scoring Model for Scheme: {scheme_code}

This XGBoost model predicts eligibility probability (0-1) for scheme {scheme_code}.

Features: {len(feature_names)}
Training Samples: {len(X_train)}
Test Performance:
  - Accuracy: {accuracy:.4f}
  - Precision: {precision:.4f}
  - Recall: {recall:.4f}
  - F1 Score: {f1:.4f}
  - ROC-AUC: {roc_auc:.4f}

Top Features: {', '.join(importance_df.head(10)['feature'].tolist())}
                """
                mlflow.log_text(model_desc, "model_description.txt")
                
                print(f"\n✅ Model training complete!")
                run_id = mlflow.active_run().info.run_id
                print(f"   MLflow Run ID: {run_id}")
                print(f"   Model Name: {model_name}")
                
                # Generate MLflow UI URL
                experiment_id = mlflow.active_run().info.experiment_id
                mlflow_url = f"http://127.0.0.1:5000/#/experiments/{experiment_id}/runs/{run_id}"
                print(f"   View in MLflow UI: {mlflow_url}")
    
    def _save_model_registry(
        self,
        scheme_code: str,
        model_version: str,
        mlflow_run_id: str,
        feature_list: List[str],
        training_samples: int,
        accuracy: float,
        precision: float,
        recall: float,
        f1: float,
        roc_auc: float
    ):
        """Save model metadata to database"""
        cursor = self.eligibility_db.connection.cursor()
        
        try:
            insert_query = """
                INSERT INTO eligibility.ml_model_registry (
                    scheme_code, model_version, model_type, model_path,
                    mlflow_run_id, training_samples_count, training_metrics,
                    feature_list, feature_importance, is_active, is_production,
                    deployed_at
                ) VALUES (
                    %s, %s, 'xgboost', %s, %s, %s, %s, %s, %s, true, false, CURRENT_TIMESTAMP
                )
            """
            
            model_path = f"models:/{self.config['mlflow']['registered_model_prefix']}_{scheme_code}/1"
            
            training_metrics = {
                'accuracy': float(accuracy),
                'precision': float(precision),
                'recall': float(recall),
                'f1_score': float(f1),
                'roc_auc': float(roc_auc)
            }
            
            cursor.execute(insert_query, (
                scheme_code,
                model_version,
                model_path,
                mlflow_run_id,
                training_samples,
                json.dumps(training_metrics),
                feature_list,
                json.dumps({}),  # Feature importance will be populated separately
            ))
            
            self.eligibility_db.connection.commit()
            cursor.close()
            
            print(f"✅ Model metadata saved to registry")
        
        except Exception as e:
            print(f"⚠️  Error saving model metadata: {e}")
            self.eligibility_db.connection.rollback()
            cursor.close()
    
    def close(self):
        """Close database connections"""
        if self.db:
            self.db.disconnect()
        if self.eligibility_db:
            self.eligibility_db.disconnect()


def main():
    """Main training function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Train eligibility scoring model')
    parser.add_argument('--scheme-code', required=True, help='Scheme code to train for (e.g., CHIRANJEEVI)')
    parser.add_argument('--config', help='Path to config file')
    
    args = parser.parse_args()
    
    trainer = EligibilityModelTrainer(args.config)
    
    try:
        trainer.train(args.scheme_code)
    finally:
        trainer.close()


if __name__ == "__main__":
    main()

