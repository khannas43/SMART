#!/usr/bin/env python3
"""
Train Risk Scoring Model
Use Case ID: AI-PLATFORM-06

This script trains ML models for risk scoring using historical decision data.
Supports XGBoost, Logistic Regression, and Random Forest models.
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import yaml
import json

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared', 'utils'))

from db_connector import DBConnector

# ML Libraries
try:
    import xgboost as xgb
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
    import joblib
    import mlflow
    import mlflow.sklearn
    import mlflow.xgboost
except ImportError as e:
    print(f"❌ Error: Missing ML library. Install with: pip install xgboost scikit-learn mlflow joblib")
    sys.exit(1)


class RiskModelTrainer:
    """Train risk scoring models for decision evaluation"""
    
    def __init__(self, config_path=None):
        """Initialize trainer"""
        if config_path is None:
            base_dir = Path(__file__).parent.parent.parent
            config_path = base_dir / "config" / "db_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Load use case config
        use_case_config_path = Path(config_path).parent / "use_case_config.yaml"
        if use_case_config_path.exists():
            with open(use_case_config_path, 'r') as f:
                self.use_case_config = yaml.safe_load(f)
        else:
            self.use_case_config = {}
        
        # Initialize database
        db_config = self.config['database']
        self.db = DBConnector(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['name'],
            user=db_config['user'],
            password=db_config['password']
        )
        
        # MLflow setup
        mlflow.set_tracking_uri("http://127.0.0.1:5000")
        mlflow.set_experiment("AI-PLATFORM-06-Risk-Models")
    
    def prepare_training_data(self, scheme_code=None, min_samples=100):
        """
        Prepare training data from historical decisions
        
        Args:
            scheme_code: Optional scheme code to filter
            min_samples: Minimum samples required
        
        Returns:
            X (features), y (target), feature_names
        """
        print("📊 Preparing training data...")
        
        self.db.connect()
        conn = self.db.connection
        
        # Query historical decisions with features
        query = """
            SELECT 
                d.decision_id,
                d.scheme_code,
                d.risk_score,
                d.risk_band,
                d.decision_type,
                d.decision_status,
                rs.feature_contributions,
                rs.input_features
            FROM decision.decisions d
            LEFT JOIN decision.risk_scores rs ON d.decision_id = rs.decision_id
            WHERE d.risk_score IS NOT NULL
        """
        
        params = []
        if scheme_code:
            query += " AND d.scheme_code = %s"
            params.append(scheme_code)
        
        query += " ORDER BY d.decision_timestamp DESC LIMIT 10000"
        
        df = pd.read_sql(query, conn, params=params)
        
        if len(df) < min_samples:
            print(f"⚠️  Warning: Only {len(df)} samples found, minimum {min_samples} required")
            print("   Using rule-based scoring for now. Train model when more data is available.")
            self.db.disconnect()
            return None, None, None
        
        print(f"   ✅ Found {len(df)} decision records")
        
        # Extract features
        features_list = []
        targets = []
        
        for _, row in df.iterrows():
            # Get features from input_features JSON
            input_features = row.get('input_features')
            if input_features and isinstance(input_features, str):
                try:
                    features = json.loads(input_features)
                except:
                    features = {}
            elif isinstance(input_features, dict):
                features = input_features
            else:
                features = {}
            
            # Use risk score as target (binary: low risk = 0, medium/high = 1)
            # Or use decision outcome: approved = 0, rejected/routed = 1
            risk_score = float(row['risk_score']) if pd.notna(row['risk_score']) else 0.5
            decision_type = row['decision_type']
            
            # Target: 0 = low risk (auto-approved), 1 = medium/high risk (needs review)
            target = 1 if risk_score > 0.3 or decision_type != 'AUTO_APPROVE' else 0
            
            # Standard features
            feature_vector = {
                'family_size': features.get('family_size', 0),
                'avg_age': features.get('avg_age', 0),
                'total_benefits': features.get('total_benefits', 0),
                'unique_schemes': features.get('unique_schemes', 0),
                'is_auto_submission': features.get('is_auto_submission', 0),
                'eligibility_score': features.get('eligibility_score', 0.0),
                'past_rejections': features.get('past_rejections', 0),
                'eligibility_status_rule': features.get('eligibility_status_rule', 0),
                'eligibility_status_possible': features.get('eligibility_status_possible', 0)
            }
            
            features_list.append(feature_vector)
            targets.append(target)
        
        # Convert to DataFrame
        X = pd.DataFrame(features_list)
        y = np.array(targets)
        
        print(f"   ✅ Prepared {len(X)} samples with {len(X.columns)} features")
        print(f"   ✅ Target distribution: {np.bincount(y)}")
        
        self.db.disconnect()
        
        return X, y, list(X.columns)
    
    def train_model(self, X, y, model_type='xgboost', scheme_code=None):
        """
        Train risk scoring model
        
        Args:
            X: Feature matrix
            y: Target vector
            model_type: 'xgboost', 'logistic_regression', 'random_forest'
            scheme_code: Scheme code for model naming
        
        Returns:
            Trained model, metrics
        """
        print(f"\n🎯 Training {model_type} model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"   Training samples: {len(X_train)}")
        print(f"   Test samples: {len(X_test)}")
        
        # Train model
        with mlflow.start_run(run_name=f"{model_type}_{scheme_code or 'general'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
            if model_type == 'xgboost':
                model = xgb.XGBClassifier(
                    n_estimators=100,
                    max_depth=5,
                    learning_rate=0.1,
                    random_state=42
                )
                model.fit(X_train, y_train)
                mlflow.xgboost.log_model(model, "model")
            
            elif model_type == 'logistic_regression':
                model = LogisticRegression(random_state=42, max_iter=1000)
                model.fit(X_train, y_train)
                mlflow.sklearn.log_model(model, "model")
            
            elif model_type == 'random_forest':
                model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )
                model.fit(X_train, y_train)
                mlflow.sklearn.log_model(model, "model")
            
            else:
                raise ValueError(f"Unknown model type: {model_type}")
            
            # Evaluate
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, zero_division=0)
            recall = recall_score(y_test, y_pred, zero_division=0)
            f1 = f1_score(y_test, y_pred, zero_division=0)
            auc = roc_auc_score(y_test, y_pred_proba)
            
            metrics = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'auc_score': auc
            }
            
            # Log metrics
            mlflow.log_params({
                'model_type': model_type,
                'scheme_code': scheme_code or 'general',
                'n_estimators': model.n_estimators if hasattr(model, 'n_estimators') else 'N/A',
                'max_depth': model.max_depth if hasattr(model, 'max_depth') else 'N/A'
            })
            
            mlflow.log_metrics(metrics)
            
            print(f"   ✅ Model trained successfully")
            print(f"      Accuracy: {accuracy:.4f}")
            print(f"      Precision: {precision:.4f}")
            print(f"      Recall: {recall:.4f}")
            print(f"      F1 Score: {f1:.4f}")
            print(f"      AUC: {auc:.4f}")
            
            # Log feature importance (if available)
            if hasattr(model, 'feature_importances_'):
                feature_importance = dict(zip(X.columns, model.feature_importances_))
                mlflow.log_dict(feature_importance, "feature_importance.json")
            
            return model, metrics
    
    def save_model(self, model, model_type, scheme_code, metrics, feature_names):
        """Save model to database and filesystem"""
        print(f"\n💾 Saving model...")
        
        self.db.connect()
        conn = self.db.connection
        cursor = conn.cursor()
        
        # Generate model version
        model_version = f"1.0.{datetime.now().strftime('%Y%m%d')}"
        model_name = f"risk_model_{scheme_code or 'general'}_{model_type}"
        
        # Save model to file
        model_dir = Path(__file__).parent.parent.parent / "models" / "trained"
        model_dir.mkdir(parents=True, exist_ok=True)
        model_path = model_dir / f"{model_name}_{model_version}.pkl"
        joblib.dump(model, model_path)
        
        print(f"   ✅ Model saved to: {model_path}")
        
        # Save to database
        cursor.execute("""
            INSERT INTO decision.risk_models (
                model_name, model_type, model_version, scheme_code,
                model_path, training_samples_count, feature_list,
                training_accuracy, validation_accuracy, test_accuracy,
                auc_score, precision_score, recall_score, f1_score,
                is_active, is_production, created_by, trained_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING model_id
        """, (
            model_name,
            model_type,
            model_version,
            scheme_code,
            str(model_path),
            1000,  # training_samples_count (placeholder)
            feature_names,
            metrics.get('accuracy'),
            metrics.get('accuracy'),  # validation = test for now
            metrics.get('accuracy'),
            metrics.get('auc_score'),
            metrics.get('precision'),
            metrics.get('recall'),
            metrics.get('f1_score'),
            True,  # is_active
            False,  # is_production (set manually after validation)
            'system',
            datetime.now()
        ))
        
        model_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        self.db.disconnect()
        
        print(f"   ✅ Model saved to database (ID: {model_id})")
        print(f"   ⚠️  Note: Set is_production = true after validation")
        
        return model_id


def main():
    """Main training function"""
    parser = argparse.ArgumentParser(description='Train risk scoring model')
    parser.add_argument('--scheme', type=str, help='Scheme code (optional)')
    parser.add_argument('--model-type', type=str, default='xgboost',
                       choices=['xgboost', 'logistic_regression', 'random_forest'],
                       help='Model type to train')
    parser.add_argument('--min-samples', type=int, default=100,
                       help='Minimum samples required for training')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("Risk Model Training - AI-PLATFORM-06")
    print("=" * 80)
    
    trainer = RiskModelTrainer()
    
    # Prepare data
    X, y, feature_names = trainer.prepare_training_data(
        scheme_code=args.scheme,
        min_samples=args.min_samples
    )
    
    if X is None:
        print("\n⚠️  Insufficient training data. Cannot train model.")
        print("   The system will use rule-based scoring until enough data is available.")
        return
    
    # Train model
    model, metrics = trainer.train_model(
        X, y,
        model_type=args.model_type,
        scheme_code=args.scheme
    )
    
    # Save model
    model_id = trainer.save_model(
        model, args.model_type, args.scheme, metrics, feature_names
    )
    
    print("\n" + "=" * 80)
    print("✅ Model training complete!")
    print(f"   Model ID: {model_id}")
    print(f"   Model Type: {args.model_type}")
    print(f"   Scheme: {args.scheme or 'General'}")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Validate model on test data")
    print("2. Set is_production = true in decision.risk_models")
    print("3. Update RiskScorer to use the new model")


if __name__ == '__main__':
    main()

