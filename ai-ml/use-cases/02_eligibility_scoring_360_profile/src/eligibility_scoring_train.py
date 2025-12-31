"""
Train Eligibility Scoring Model (XGBoost)
Use Case: AI-PLATFORM-02 - Eligibility Scoring & 360° Profiles
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import yaml
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
    classification_report, confusion_matrix
)

import mlflow
import mlflow.xgboost
import mlflow.sklearn

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class EligibilityScoringTrainer:
    """Train XGBoost model for eligibility scoring"""
    
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "model_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Database connection
        db_config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
        with open(db_config_path, 'r') as f:
            db_config = yaml.safe_load(f)['database']
        
        self.db = DBConnector(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['dbname'],
            user=db_config['user'],
            password=db_config['password']
        )
        self.db.connect()
        
        # Model config
        self.model_config = self.config['eligibility_scoring']
        self.training_config = self.config['training']
        
        # MLflow setup
        mlflow_config = self.config['mlflow']
        mlflow.set_tracking_uri(mlflow_config['tracking_uri'])
        mlflow.set_experiment(f"{mlflow_config['experiment_name']}/eligibility_scoring")
        
        # Feature encoders
        self.label_encoders = {}
        self.scaler = StandardScaler()
        
    def load_training_data(self):
        """Load training data from database"""
        print("📊 Loading training data...")
        
        # Load citizen-scheme pairs with eligibility scores
        # Note: This assumes we have historical applications with eligibility scores
        # For initial training, we can use rule-based scores or synthetic labels
        
        query = """
        WITH citizen_scheme_features AS (
            SELECT 
                gr.gr_id,
                gr.age,
                gr.gender,
                gr.caste_id,
                gr.district_id,
                gr.is_urban,
                sm.scheme_id,
                sm.category as scheme_category,
                
                -- Family context
                COALESCE(sef.family_size, 1) as family_size,
                COALESCE(sef.family_income, 0) as family_income,
                
                -- Education
                sef.education_level,
                sef.employment_type,
                sef.house_type,
                
                -- Benefit history
                COALESCE(SUM(CASE WHEN be.txn_date >= CURRENT_DATE - INTERVAL '1 year' THEN be.amount ELSE 0 END), 0) as benefit_total_1y,
                COUNT(DISTINCT CASE WHEN be.txn_date >= CURRENT_DATE - INTERVAL '1 year' THEN be.scheme_id END) as schemes_count_1y,
                
                -- Scheme criteria
                CASE WHEN gr.age BETWEEN COALESCE(sec.min_age, 0) AND COALESCE(sec.max_age, 999) THEN 1 ELSE 0 END as age_match,
                CASE WHEN COALESCE(sef.family_income, 0) <= COALESCE(sec.max_income, 999999999) THEN 1 ELSE 0 END as income_match,
                CASE WHEN sec.target_caste IS NULL OR sec.target_caste = gr.caste_id THEN 1 ELSE 0 END as caste_match,
                
                -- Application history (if exists)
                CASE WHEN ae.application_id IS NOT NULL THEN 1 ELSE 0 END as has_previous_application,
                CASE WHEN ae.status = 'APPROVED' THEN 1 ELSE 0 END as was_approved
                
            FROM golden_records gr
            CROSS JOIN scheme_master sm
            LEFT JOIN socio_economic_facts sef ON gr.gr_id = sef.gr_id
            LEFT JOIN benefit_events be ON gr.gr_id = be.gr_id
            LEFT JOIN scheme_eligibility_criteria sec ON sm.scheme_id = sec.scheme_id
            LEFT JOIN application_events ae ON gr.gr_id = ae.gr_id AND sm.scheme_id = ae.scheme_id
            WHERE gr.status = 'active'
            AND sm.status = 'active'
            GROUP BY 
                gr.gr_id, gr.age, gr.gender, gr.caste_id, gr.district_id, gr.is_urban,
                sm.scheme_id, sm.category,
                sef.family_size, sef.family_income, sef.education_level, 
                sef.employment_type, sef.house_type,
                sec.min_age, sec.max_age, sec.max_income, sec.target_caste,
                ae.application_id, ae.status
        )
        SELECT * FROM citizen_scheme_features
        LIMIT 50000
        """
        
        df = self.db.execute_query(query)
        print(f"   Loaded {len(df)} citizen-scheme pairs")
        
        return df
    
    def engineer_features(self, df):
        """Engineer features for eligibility scoring"""
        print("🔧 Engineering features...")
        
        # Create eligibility match score (rule-based baseline)
        match_features = ['age_match', 'income_match', 'caste_match']
        df['eligibility_match_score'] = df[match_features].sum(axis=1) / len(match_features) * 100
        
        # Create target variable (for training)
        # Use rule-based score as initial target, or use historical approval status
        if 'was_approved' in df.columns:
            # Binary classification target
            df['target'] = df['was_approved'].fillna(0)
            # For regression, use eligibility_match_score as proxy
            df['target_score'] = df['eligibility_match_score']
        else:
            # Use match score as target (regression)
            df['target_score'] = df['eligibility_match_score']
            df['target'] = (df['target_score'] >= 60).astype(int)
        
        # Derive features
        df['income_per_person'] = df['family_income'] / df['family_size'].replace(0, 1)
        df['age_category'] = pd.cut(
            df['age'],
            bins=[0, 18, 35, 60, 100],
            labels=['child', 'adult', 'senior', 'elderly']
        )
        
        # Encode categorical features
        categorical_cols = ['gender', 'education_level', 'employment_type', 'house_type', 
                           'scheme_category', 'age_category']
        
        for col in categorical_cols:
            if col in df.columns:
                le = LabelEncoder()
                df[f'{col}_encoded'] = le.fit_transform(df[col].fillna('UNKNOWN').astype(str))
                self.label_encoders[col] = le
        
        print(f"   Created {len(df.columns)} features")
        return df
    
    def prepare_features(self, df):
        """Prepare feature matrix and target"""
        print("📋 Preparing feature matrix...")
        
        # Select feature columns
        feature_cols = [
            'age', 'caste_id', 'district_id', 'is_urban',
            'family_size', 'family_income', 'income_per_person',
            'benefit_total_1y', 'schemes_count_1y',
            'age_match', 'income_match', 'caste_match',
            'has_previous_application',
            'gender_encoded', 'education_level_encoded', 
            'employment_type_encoded', 'house_type_encoded',
            'scheme_category_encoded', 'age_category_encoded'
        ]
        
        # Filter to available columns
        feature_cols = [col for col in feature_cols if col in df.columns]
        
        X = df[feature_cols].fillna(0)
        y_score = df['target_score'] if 'target_score' in df.columns else df['eligibility_match_score']
        y_binary = df['target'] if 'target' in df.columns else None
        
        # Scale features
        X_scaled = pd.DataFrame(
            self.scaler.fit_transform(X),
            columns=X.columns,
            index=X.index
        )
        
        print(f"   Features: {len(feature_cols)}")
        print(f"   Samples: {len(X_scaled)}")
        
        return X_scaled, y_score, y_binary, feature_cols
    
    def train(self, X, y_score, y_binary=None):
        """Train XGBoost model"""
        print("🚀 Training XGBoost model...")
        
        # Use regression (score prediction)
        target = y_score
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, target,
            test_size=self.training_config['test_size'],
            random_state=self.training_config['random_state'],
            shuffle=True
        )
        
        # Model parameters
        params = self.model_config['params'].copy()
        
        # Train model
        model = xgb.XGBRegressor(**params)
        model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            early_stopping_rounds=self.training_config.get('early_stopping_rounds', 20),
            verbose=False
        )
        
        # Predictions
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)
        
        # Metrics
        train_mse = mean_squared_error(y_train, y_train_pred)
        test_mse = mean_squared_error(y_test, y_test_pred)
        train_mae = mean_absolute_error(y_train, y_train_pred)
        test_mae = mean_absolute_error(y_test, y_test_pred)
        train_r2 = r2_score(y_train, y_train_pred)
        test_r2 = r2_score(y_test, y_test_pred)
        
        print(f"\n📊 Training Metrics:")
        print(f"   Train MSE: {train_mse:.2f}, MAE: {train_mae:.2f}, R²: {train_r2:.4f}")
        print(f"   Test MSE: {test_mse:.2f}, MAE: {test_mae:.2f}, R²: {test_r2:.4f}")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n🔝 Top 10 Features:")
        print(feature_importance.head(10).to_string(index=False))
        
        # Cross-validation
        print("\n🔄 Cross-validation...")
        cv_scores = cross_val_score(
            model, X_train, y_train,
            cv=StratifiedKFold(n_splits=self.training_config['cross_validation_folds'], shuffle=True),
            scoring='neg_mean_squared_error'
        )
        cv_mse = -cv_scores.mean()
        cv_std = cv_scores.std()
        print(f"   CV MSE: {cv_mse:.2f} (±{cv_std:.2f})")
        
        return model, {
            'train_mse': train_mse,
            'test_mse': test_mse,
            'train_mae': train_mae,
            'test_mae': test_mae,
            'train_r2': train_r2,
            'test_r2': test_r2,
            'cv_mse': cv_mse,
            'cv_std': cv_std
        }, feature_importance, X_test, y_test, y_test_pred
    
    def log_to_mlflow(self, model, metrics, feature_importance, X_test, y_test, y_pred):
        """Log model to MLflow"""
        print("\n📝 Logging to MLflow...")
        
        with mlflow.start_run(run_name=f"eligibility_scoring_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
            # Log parameters
            mlflow.log_params(self.model_config['params'])
            mlflow.log_params({
                'model_type': 'xgb_regressor',
                'output_type': 'regression',
                'n_features': len(X_test.columns),
                'n_samples': len(X_test)
            })
            
            # Log metrics
            mlflow.log_metrics(metrics)
            
            # Log model
            mlflow.xgboost.log_model(model, "model")
            mlflow.sklearn.log_model(self.scaler, "scaler")
            
            # Log feature importance
            feature_importance.to_csv('feature_importance.csv', index=False)
            mlflow.log_artifact('feature_importance.csv')
            
            # Log threshold configuration
            mlflow.log_dict(
                self.model_config['score_thresholds'],
                'score_thresholds.yaml'
            )
            
            # Log sample predictions
            sample_preds = pd.DataFrame({
                'actual': y_test[:100],
                'predicted': y_pred[:100]
            })
            sample_preds.to_csv('sample_predictions.csv', index=False)
            mlflow.log_artifact('sample_predictions.csv')
            
            print(f"   ✅ Logged to MLflow run: {mlflow.active_run().info.run_id}")
    
    def save_model(self, model, feature_importance):
        """Save model artifacts"""
        print("\n💾 Saving model artifacts...")
        
        model_dir = Path(__file__).parent.parent / "models" / "checkpoints"
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Save model
        model_path = model_dir / "eligibility_scoring_model.pkl"
        joblib.dump(model, model_path)
        print(f"   Model: {model_path}")
        
        # Save scaler
        scaler_path = model_dir / "eligibility_scoring_scaler.pkl"
        joblib.dump(self.scaler, scaler_path)
        print(f"   Scaler: {scaler_path}")
        
        # Save encoders
        encoders_path = model_dir / "eligibility_scoring_encoders.pkl"
        with open(encoders_path, 'wb') as f:
            pickle.dump(self.label_encoders, f)
        print(f"   Encoders: {encoders_path}")
        
        # Save feature importance
        importance_path = model_dir / "eligibility_scoring_feature_importance.csv"
        feature_importance.to_csv(importance_path, index=False)
        print(f"   Feature importance: {importance_path}")
    
    def train_pipeline(self):
        """Complete training pipeline"""
        try:
            # Load data
            df = self.load_training_data()
            
            # Engineer features
            df = self.engineer_features(df)
            
            # Prepare features
            X, y_score, y_binary, feature_cols = self.prepare_features(df)
            
            # Train model
            model, metrics, feature_importance, X_test, y_test, y_pred = self.train(X, y_score, y_binary)
            
            # Log to MLflow
            self.log_to_mlflow(model, metrics, feature_importance, X_test, y_test, y_pred)
            
            # Save model
            self.save_model(model, feature_importance)
            
            print("\n✅ Training complete!")
            return model, metrics
            
        except Exception as e:
            print(f"\n❌ Training failed: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            self.db.disconnect()


def main():
    """Main training function"""
    trainer = EligibilityScoringTrainer()
    trainer.train_pipeline()


if __name__ == "__main__":
    main()

