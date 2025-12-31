"""
Training Pipeline for Golden Record Deduplication Models
Trains Fellegi-Sunter and evaluates performance
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix
import yaml
from datetime import datetime

# Add paths
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))

from data_loader import GoldenRecordDataLoader
from deduplication import FellegiSunterDeduplication, create_deduplication_model
from features import GoldenRecordFeatureEngineer
from log_model_descriptions import get_model_description, log_model_description_to_mlflow


def create_training_pairs(citizens: pd.DataFrame, 
                         num_match_pairs: int = 1000,
                         num_nonmatch_pairs: int = 5000) -> pd.DataFrame:
    """
    Create training pairs for deduplication model
    
    Args:
        citizens: DataFrame of citizens
        num_match_pairs: Number of matching pairs to create
        num_nonmatch_pairs: Number of non-matching pairs to create
        
    Returns:
        DataFrame with columns [record1, record2, label] where label is 1 for match, 0 for non-match
    """
    pairs = []
    
    # Create matching pairs (same person, different records)
    # Find records with same Jan Aadhaar
    duplicate_aadhaar = citizens[citizens['jan_aadhaar'].duplicated(keep=False)]
    
    if len(duplicate_aadhaar) > 0:
        # Group by Jan Aadhaar
        grouped = duplicate_aadhaar.groupby('jan_aadhaar')
        
        match_count = 0
        for aadhaar, group in grouped:
            if len(group) >= 2 and match_count < num_match_pairs:
                # Take first two records as a match pair
                record1 = group.iloc[0]
                record2 = group.iloc[1]
                pairs.append({
                    'record1': record1,
                    'record2': record2,
                    'label': 1  # Match
                })
                match_count += 1
    
    # If not enough matches, create synthetic matches by adding small variations
    while len([p for p in pairs if p['label'] == 1]) < num_match_pairs:
        # Randomly sample a record and create a slight variation
        idx = np.random.randint(0, len(citizens))
        record1 = citizens.iloc[idx]
        
        # Create variation (small changes to name, address)
        record2 = record1.copy()
        # Add small variation to name
        if pd.notna(record2['full_name']):
            record2['full_name'] = record2['full_name'] + ' '  # Add space
        
        pairs.append({
            'record1': record1,
            'record2': record2,
            'label': 1  # Match
        })
    
    # Create non-matching pairs
    nonmatch_count = 0
    while nonmatch_count < num_nonmatch_pairs:
        idx1, idx2 = np.random.choice(len(citizens), size=2, replace=False)
        record1 = citizens.iloc[idx1]
        record2 = citizens.iloc[idx2]
        
        # Ensure they're actually different (different Jan Aadhaar)
        if record1['jan_aadhaar'] != record2['jan_aadhaar']:
            pairs.append({
                'record1': record1,
                'record2': record2,
                'label': 0  # Non-match
            })
            nonmatch_count += 1
    
    return pd.DataFrame(pairs)


def evaluate_model(model: FellegiSunterDeduplication, 
                   test_pairs: pd.DataFrame) -> dict:
    """
    Evaluate deduplication model
    
    Args:
        model: Trained deduplication model
        test_pairs: Test pairs with labels
        
    Returns:
        Dictionary of evaluation metrics
    """
    y_true = test_pairs['label'].values
    y_pred = []
    y_scores = []
    
    for idx, row in test_pairs.iterrows():
        match_score, decision = model.predict(row['record1'], row['record2'])
        y_scores.append(match_score)
        
        # Convert decision to binary prediction
        if decision == 'auto_merge':
            y_pred.append(1)
        elif decision == 'manual_review':
            # For evaluation, count manual review as positive (conservative)
            y_pred.append(1)
        else:
            y_pred.append(0)
    
    # Calculate metrics
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    
    metrics = {
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'true_positives': int(cm[1, 1]),
        'false_positives': int(cm[0, 1]),
        'true_negatives': int(cm[0, 0]),
        'false_negatives': int(cm[1, 0])
    }
    
    return metrics


def train_deduplication_model():
    """Main training function"""
    
    # Initialize MLflow
    mlflow.set_tracking_uri('http://127.0.0.1:5000')
    mlflow.set_experiment('smart/golden_record/baseline_v1')
    
    run_name = f"deduplication_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        with mlflow.start_run(run_name=run_name):
            
            print("="*60)
            print("GOLDEN RECORD DEDUPLICATION MODEL TRAINING")
            print("="*60)
            
            # Load configuration
            config_path = Path(__file__).parent.parent / "config" / "model_config.yaml"
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            mlflow_config = config['mlflow']
            dedup_config = config['deduplication']
            
            print(f"\nMLflow Experiment: {mlflow_config['experiment_name']}")
            print(f"Model Type: {dedup_config['model_type']}")
            
            # Get model description and log to MLflow (visible in browser UI)
            current_model = dedup_config['model_type']
            model_info = get_model_description('deduplication', current_model)
            
            # Log model description and metadata as tags (visible in MLflow UI Overview tab)
            mlflow.set_tags({
                'model_name': model_info.get('name', current_model),
                'model_algorithm': model_info.get('algorithm', 'N/A'),
                'use_case': model_info.get('use_case', 'Golden Record Deduplication'),
                'model_category': 'deduplication',
                'model_type': current_model
            })
            
            # Log detailed description (visible in MLflow UI Notes/Description section)
            log_model_description_to_mlflow(None, 'deduplication', current_model)
            
            # Log configuration
            mlflow.log_params({
                'model_type': dedup_config['model_type'],
                'auto_merge_threshold': dedup_config['thresholds']['auto_merge'],
                'manual_review_threshold': dedup_config['thresholds']['manual_review']
            })
            
            # Log model description as text artifact (visible in Artifacts tab)
            description_text = f"""
MODEL INFORMATION
==================

Model Name: {model_info.get('name', current_model)}
Algorithm: {model_info.get('algorithm', 'N/A')}

DESCRIPTION
-----------
{model_info.get('description', 'ML model for deduplication')}

USE CASE
--------
{model_info.get('use_case', 'Golden Record Deduplication')}

FEATURES
--------
{model_info.get('features', 'Multiple similarity features')}

OUTPUT
------
{model_info.get('output', 'Match probability score')}

CONFIGURATION
-------------
Model Type: {current_model}
Auto Merge Threshold: {dedup_config['thresholds']['auto_merge']*100:.0f}% confidence
Manual Review Threshold: {dedup_config['thresholds']['manual_review']*100:.0f}% - {dedup_config['thresholds']['auto_merge']*100:.0f}% confidence
Reject Threshold: <{dedup_config['thresholds']['reject']*100:.0f}% confidence

FEATURE WEIGHTS
---------------
"""
            for feature in dedup_config.get('features', []):
                description_text += f"- {feature.get('name', 'N/A')}: {feature.get('weight', 0)*100:.1f}% ({feature.get('algorithm', 'N/A')})\n"
            
            mlflow.log_text(description_text, "model_description.txt")
            
            # Load data
            print("\nLoading data...")
            loader = GoldenRecordDataLoader()
            citizens = loader.load_all_citizens()
            print(f"✅ Loaded {len(citizens)} citizens")
            
            mlflow.log_param('dataset_size', len(citizens))
            
            # Create training pairs
            print("\nCreating training pairs...")
            training_pairs = create_training_pairs(citizens, num_match_pairs=1000, num_nonmatch_pairs=5000)
            print(f"✅ Created {len(training_pairs)} training pairs")
            print(f"   - Matches: {training_pairs['label'].sum()}")
            print(f"   - Non-matches: {(training_pairs['label'] == 0).sum()}")
            
            mlflow.log_param('training_pairs', len(training_pairs))
            mlflow.log_param('match_pairs', training_pairs['label'].sum())
            mlflow.log_param('nonmatch_pairs', (training_pairs['label'] == 0).sum())
            
            # Split into train and test
            train_pairs, test_pairs = train_test_split(
                training_pairs, 
                test_size=0.2, 
                random_state=42, 
                stratify=training_pairs['label']
            )
            
            print(f"\nTrain pairs: {len(train_pairs)}")
            print(f"Test pairs: {len(test_pairs)}")
            
            # Separate match and non-match pairs for training
            match_pairs = train_pairs[train_pairs['label'] == 1].copy()
            nonmatch_pairs = train_pairs[train_pairs['label'] == 0].copy()
            
            print(f"\nTraining model ({dedup_config['model_type']})...")
            
            # Initialize model
            if dedup_config['model_type'] == 'fellegi_sunter':
                model = FellegiSunterDeduplication(config_path)
                
                # Estimate parameters
                print("Estimating Fellegi-Sunter parameters...")
                model.estimate_parameters(match_pairs, nonmatch_pairs)
                print("✅ Parameters estimated")
                
                # Log model info
                mlflow.log_param('num_features', len(model.m_probs))
                
            else:
                raise ValueError(f"Model type {dedup_config['model_type']} not yet implemented")
            
            # Evaluate on test set
            print("\nEvaluating model...")
            metrics = evaluate_model(model, test_pairs)
            
            print("\n" + "="*60)
            print("EVALUATION RESULTS")
            print("="*60)
            for key, value in metrics.items():
                print(f"{key}: {value:.4f}" if isinstance(value, float) else f"{key}: {value}")
                mlflow.log_metric(key, value)
            
            # Check if metrics meet targets
            target_precision = config['evaluation']['target_metrics']['deduplication_precision']
            target_recall = config['evaluation']['target_metrics']['deduplication_recall']
            
            print("\n" + "="*60)
            print("TARGET COMPARISON")
            print("="*60)
            print(f"Target Precision: {target_precision:.2%}")
            print(f"Actual Precision: {metrics['precision']:.2%}")
            print(f"Target Recall: {target_recall:.2%}")
            print(f"Actual Recall: {metrics['recall']:.2%}")
            
            # Save model
            model_dir = Path(__file__).parent.parent / "models" / "checkpoints"
            model_dir.mkdir(parents=True, exist_ok=True)
            model_path = model_dir / f"fellegi_sunter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
            model.save_model(str(model_path))
            
            print(f"\n✅ Model saved to: {model_path}")
            mlflow.log_artifact(str(model_path))
            
            # Log model to MLflow with metadata and description
            try:
                mlflow.sklearn.log_model(
                    model, 
                    "deduplication_model",
                    registered_model_name="GoldenRecord_Deduplication_Model"
                )
            except Exception as e:
                # If model registration fails, just log the model
                print(f"⚠️  Model registration warning: {e}")
                mlflow.sklearn.log_model(model, "deduplication_model")
            
            # Add model metadata tags (visible in MLflow UI Tags section)
            mlflow.set_tags({
                "model_version": "1.0",
                "deployment_status": "development",
                "target_metrics": "precision>95%, recall>95%",
                "model_description": model_info.get('description', '')[:250]  # Truncate for tag display
            })
            
            loader.close()
            
            print("\n" + "="*60)
            print("✅ Training completed successfully")
            print("="*60)
            run_id = mlflow.active_run().info.run_id
            print(f"\n🏃 View run '{run_name}' at: http://127.0.0.1:5000/#/experiments/2/runs/{run_id}")
            print(f"🧪 View experiment at: http://127.0.0.1:5000/#/experiments/2")
            
    except Exception as e:
        # Log error to MLflow if run is active
        error_msg = str(e)
        print(f"\n❌ Training failed: {error_msg}")
        
        if mlflow.active_run():
            mlflow.log_param("error", error_msg)
            mlflow.set_tag("status", "failed")
            mlflow.log_text(f"Error traceback:\n{error_msg}", "error.txt")
            
            run_id = mlflow.active_run().info.run_id
            print(f"\n🏃 View failed run at: http://127.0.0.1:5000/#/experiments/2/runs/{run_id}")
            print(f"🧪 View experiment at: http://127.0.0.1:5000/#/experiments/2")
        
        # Re-raise to see full traceback in terminal
        raise


if __name__ == "__main__":
    train_deduplication_model()

