"""
Train Income Band Inference Model (RandomForest)
Use Case: AI-PLATFORM-02
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import yaml
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

import mlflow
import mlflow.sklearn

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class IncomeBandTrainer:
    """Train RandomForest model for income band inference"""
    
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
        
        # MLflow setup
        mlflow_config = self.config['mlflow']
        mlflow.set_tracking_uri(mlflow_config['tracking_uri'])
        mlflow.set_experiment(f"{mlflow_config['experiment_name']}/income_band")
        
        # Model config
        self.income_config = self.config['income_band']
        self.bands = self.income_config['bands']
        
    def load_data(self):
        """Load training data from database"""
        print("Loading training data...")
        
        # Query to get features for income band prediction
        query = """
        WITH benefit_totals AS (
            SELECT 
                gr.gr_id,
                COALESCE(SUM(CASE WHEN be.txn_date >= CURRENT_DATE - INTERVAL '1 year' THEN be.amount ELSE 0 END), 0) as benefit_total_1y,
                COALESCE(SUM(CASE WHEN be.txn_date >= CURRENT_DATE - INTERVAL '3 years' THEN be.amount ELSE 0 END), 0) as benefit_total_3y,
                COUNT(CASE WHEN be.txn_date >= CURRENT_DATE - INTERVAL '1 year' THEN 1 END) as benefit_count_1y,
                COUNT(CASE WHEN be.txn_date >= CURRENT_DATE - INTERVAL '3 years' THEN 1 END) as benefit_count_3y,
                COUNT(DISTINCT be.scheme_id) as schemes_enrolled_count
            FROM golden_records gr
            LEFT JOIN benefit_events be ON gr.gr_id = be.gr_id
            WHERE gr.status = 'active'
            GROUP BY gr.gr_id
        ),
        socio_context AS (
            SELECT 
                gr.gr_id,
                sef.education_level,
                sef.employment_type,
                sef.house_type,
                sef.family_size,
                gr.is_urban,
                gr.district_id
            FROM golden_records gr
            LEFT JOIN socio_economic_facts sef ON gr.gr_id = sef.gr_id
            WHERE gr.status = 'active'
        )
        SELECT 
            bt.gr_id,
            bt.benefit_total_1y,
            bt.benefit_total_3y,
            bt.benefit_count_1y,
            bt.benefit_count_3y,
            bt.schemes_enrolled_count,
            sc.education_level,
            sc.employment_type,
            sc.house_type,
            sc.family_size,
            sc.is_urban,
            sc.district_id
        FROM benefit_totals bt
        JOIN socio_context sc ON bt.gr_id = sc.gr_id
        LIMIT 10000  -- Use subset for training
        """
        
        df = self.db.execute_query(query)
        print(f"✅ Loaded {len(df)} records")
        return df
    
    def create_income_band_labels(self, df):
        """Create income band labels based on benefit totals and context"""
        print("Creating income band labels...")
        
        # For synthetic data, infer income band from benefit patterns
        # In real scenario, this would come from labeled data
        
        def infer_income_band(row):
            # Simple heuristic: Higher benefits + better education + employment = higher income
            benefit_score = (row['benefit_total_3y'] / 1000)  # Normalize
            education_score = {'ILLITERATE': 1, 'PRIMARY': 2, 'SECONDARY': 3, 
                              'HIGHER_SECONDARY': 4, 'GRADUATE': 5, 'POST_GRADUATE': 6}.get(
                row['education_level'], 1
            )
            employment_score = {'UNEMPLOYED': 1, 'CASUAL': 2, 'SELF_EMPLOYED': 3, 
                               'REGULAR': 4, 'GOVERNMENT': 5}.get(
                row['employment_type'], 1
            )
            house_score = {'KUTCHA': 1, 'SEMI_PUCCA': 2, 'PUCCA': 3}.get(
                row['house_type'], 1
            )
            
            total_score = benefit_score * 0.3 + education_score * 2 + employment_score * 2 + house_score * 1
            
            if total_score < 8:
                return 'VERY_LOW'
            elif total_score < 15:
                return 'LOW'
            elif total_score < 25:
                return 'MEDIUM'
            else:
                return 'HIGH'
        
        df['income_band'] = df.apply(infer_income_band, axis=1)
        
        # Distribution
        print("\nIncome Band Distribution:")
        print(df['income_band'].value_counts())
        
        return df
    
    def prepare_features(self, df):
        """Prepare features for training"""
        print("Preparing features...")
        
        # Select features
        feature_cols = [
            'benefit_total_1y', 'benefit_total_3y', 'benefit_count_1y', 
            'benefit_count_3y', 'schemes_enrolled_count', 'family_size', 'is_urban'
        ]
        
        # Encode categorical features
        le_education = LabelEncoder()
        le_employment = LabelEncoder()
        le_house = LabelEncoder()
        
        df['education_encoded'] = le_education.fit_transform(df['education_level'].fillna('ILLITERATE'))
        df['employment_encoded'] = le_employment.fit_transform(df['employment_type'].fillna('UNEMPLOYED'))
        df['house_encoded'] = le_house.fit_transform(df['house_type'].fillna('KUTCHA'))
        
        feature_cols.extend(['education_encoded', 'employment_encoded', 'house_encoded', 'district_id'])
        
        X = df[feature_cols].fillna(0)
        y = df['income_band']
        
        # Encode target
        le_target = LabelEncoder()
        y_encoded = le_target.fit_transform(y)
        
        # Store encoders
        self.label_encoders = {
            'education': le_education,
            'employment': le_employment,
            'house': le_house,
            'target': le_target
        }
        self.feature_cols = feature_cols
        
        print(f"✅ Prepared {len(feature_cols)} features")
        return X, y_encoded, le_target
    
    def train_model(self, X, y):
        """Train RandomForest model"""
        print("\nTraining RandomForest model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Get model params
        params = self.income_config['params']
        
        # Train model
        model = RandomForestClassifier(**params)
        model.fit(X_train, y_train)
        
        # Predictions
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"✅ Model trained. Test Accuracy: {accuracy:.4f}")
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
        print(f"✅ Cross-validation Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        # Classification report
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=self.label_encoders['target'].classes_))
        
        return model, X_test, y_test, y_pred, accuracy, cv_scores.mean()
    
    def log_to_mlflow(self, model, X_test, y_test, y_pred, accuracy, cv_accuracy):
        """Log model to MLflow"""
        print("\nLogging to MLflow...")
        
        run_name = f"income_band_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        with mlflow.start_run(run_name=run_name):
            # Log parameters
            mlflow.log_params(self.income_config['params'])
            mlflow.log_param("model_type", "random_forest")
            mlflow.log_param("n_features", len(self.feature_cols))
            mlflow.log_param("target_classes", len(self.bands))
            
            # Log metrics
            mlflow.log_metric("test_accuracy", accuracy)
            mlflow.log_metric("cv_accuracy", cv_accuracy)
            
            # Log model
            mlflow.sklearn.log_model(
                model, 
                "income_band_model",
                registered_model_name="income_band_inference"
            )
            
            # Log encoders (as artifacts)
            import pickle
            encoders_path = Path(__file__).parent.parent / "models" / "checkpoints" / "encoders.pkl"
            with open(encoders_path, 'wb') as f:
                pickle.dump(self.label_encoders, f)
            mlflow.log_artifact(str(encoders_path))
            
            # Log feature importance
            feature_importance = pd.DataFrame({
                'feature': self.feature_cols,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            feature_importance_path = Path(__file__).parent.parent / "models" / "checkpoints" / "feature_importance.csv"
            feature_importance.to_csv(feature_importance_path, index=False)
            mlflow.log_artifact(str(feature_importance_path))
            
            run_id = mlflow.active_run().info.run_id
            experiment_id = mlflow.active_run().info.experiment_id
            print(f"✅ Logged to MLflow. Run ID: {run_id}")
            print(f"   View at: http://127.0.0.1:5000/#/experiments/{experiment_id}/runs/{run_id}")
        
        return run_id
    
    def save_model(self, model, model_path=None):
        """Save model locally"""
        if model_path is None:
            model_path = Path(__file__).parent.parent / "models" / "checkpoints" / "income_band_model.pkl"
        
        joblib.dump(model, model_path)
        print(f"✅ Model saved to {model_path}")
        
        # Save encoders
        encoders_path = Path(__file__).parent / "encoders.pkl"
        import pickle
        with open(encoders_path, 'wb') as f:
            pickle.dump(self.label_encoders, f)
        print(f"✅ Encoders saved to {encoders_path}")
    
    def close(self):
        """Close database connection"""
        if self.db:
            self.db.disconnect()


def main():
    """Main training function"""
    print("="*80)
    print("AI-PLATFORM-02: Income Band Inference Model Training")
    print("="*80)
    print()
    
    trainer = IncomeBandTrainer()
    
    try:
        # Load data
        df = trainer.load_data()
        
        # Create labels
        df = trainer.create_income_band_labels(df)
        
        # Prepare features
        X, y, le_target = trainer.prepare_features(df)
        
        # Train model
        model, X_test, y_test, y_pred, accuracy, cv_accuracy = trainer.train_model(X, y)
        
        # Log to MLflow
        run_id = trainer.log_to_mlflow(model, X_test, y_test, y_pred, accuracy, cv_accuracy)
        
        # Save model locally
        trainer.save_model(model)
        
        print("\n" + "="*80)
        print("✅ Training completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        trainer.close()


if __name__ == "__main__":
    main()

