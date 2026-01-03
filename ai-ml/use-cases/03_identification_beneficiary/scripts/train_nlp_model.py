#!/usr/bin/env python3
"""
Train fine-tuned BERT/RoBERTa model for eligibility criteria extraction
"""

import sys
import os
import yaml
import torch
import mlflow
import mlflow.pytorch
from pathlib import Path
from transformers import AutoTokenizer, TrainingArguments, Trainer
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.nlp_criteria_model import EligibilityCriteriaExtractor
from utils.nlp_preprocessing import prepare_datasets

# Load configuration
config_path = Path(__file__).parent.parent / "config" / "nlp_model_config.yaml"
with open(config_path, "r") as f:
    config = yaml.safe_load(f)


class EligibilityTrainer(Trainer):
    """Custom trainer with combined loss"""
    
    def compute_loss(self, model, inputs, return_outputs=False):
        """Compute combined loss for rule type, operator, and value"""
        
        # Get predictions
        outputs = model(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"]
        )
        
        # Loss for rule type classification
        rule_type_loss = torch.nn.CrossEntropyLoss()(
            outputs["rule_type_logits"],
            inputs["rule_type_id"]
        )
        
        # Loss for operator classification
        operator_loss = torch.nn.CrossEntropyLoss()(
            outputs["operator_logits"],
            inputs["operator_id"]
        )
        
        # Loss for value (MSE for numeric)
        value_pred = outputs["value_pred"].squeeze()
        if len(value_pred.shape) == 0:
            value_pred = value_pred.unsqueeze(0)
        value_loss = torch.nn.MSELoss()(
            value_pred,
            inputs["value"]
        )
        
        # Combined loss (weighted)
        total_loss = rule_type_loss + operator_loss + 0.5 * value_loss
        
        return (total_loss, outputs) if return_outputs else total_loss
    
    def prediction_step(self, model, inputs, prediction_loss_only, ignore_keys=None):
        """Custom prediction step to return all outputs"""
        has_labels = "rule_type_id" in inputs
        
        with torch.no_grad():
            outputs = model(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"]
            )
            
            loss = None
            if has_labels:
                loss = self.compute_loss(model, inputs)
            
            # Prepare predictions for metrics
            predictions = (
                outputs["rule_type_logits"].cpu().numpy(),
                outputs["operator_logits"].cpu().numpy(),
                outputs["value_pred"].cpu().numpy()
            )
            
            labels = None
            if has_labels:
                labels = (
                    inputs["rule_type_id"].cpu().numpy(),
                    inputs["operator_id"].cpu().numpy(),
                    inputs["value"].cpu().numpy()
                )
        
        return (loss, predictions, labels)


def compute_metrics(eval_pred):
    """Compute evaluation metrics"""
    # eval_pred is a tuple: (predictions, labels)
    # predictions is a tuple: (rule_type_logits, operator_logits, value_pred)
    # labels is a tuple: (rule_type_ids, operator_ids, values)
    
    predictions, labels = eval_pred
    
    # Extract predictions
    if isinstance(predictions, tuple) and len(predictions) >= 2:
        rule_type_logits = predictions[0]
        operator_logits = predictions[1]
    else:
        # Fallback if structure is different
        rule_type_logits = predictions
        operator_logits = predictions
    
    # Extract labels
    if isinstance(labels, tuple) and len(labels) >= 2:
        rule_type_labels = labels[0]
        operator_labels = labels[1]
    else:
        rule_type_labels = labels
        operator_labels = labels
    
    # Rule type accuracy
    rule_type_preds = np.argmax(rule_type_logits, axis=-1)
    rule_type_acc = accuracy_score(rule_type_labels, rule_type_preds)
    
    # Operator accuracy
    operator_preds = np.argmax(operator_logits, axis=-1)
    operator_acc = accuracy_score(operator_labels, operator_preds)
    
    # Precision, recall, F1 for rule type
    rule_type_prec, rule_type_rec, rule_type_f1, _ = precision_recall_fscore_support(
        rule_type_labels, rule_type_preds, average="weighted", zero_division=0
    )
    
    return {
        "rule_type_accuracy": float(rule_type_acc),
        "rule_type_precision": float(rule_type_prec),
        "rule_type_recall": float(rule_type_rec),
        "rule_type_f1": float(rule_type_f1),
        "operator_accuracy": float(operator_acc),
    }


def train_model():
    """Main training function"""
    
    # Initialize MLflow
    mlflow.set_experiment(config["output"]["mlflow_experiment"])
    
    print("=" * 60)
    print("NLP Criteria Extraction Model Training")
    print("=" * 60)
    print(f"Base Model: {config['model']['base_model']}")
    print(f"Training Epochs: {config['training']['num_epochs']}")
    print(f"Batch Size: {config['training']['batch_size']}")
    print(f"Learning Rate: {config['training']['learning_rate']}")
    print("=" * 60)
    
    # Load tokenizer
    print("\n[1/5] Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(config["model"]["base_model"])
    print(f"✓ Tokenizer loaded: {config['model']['base_model']}")
    
    # Prepare datasets
    print("\n[2/5] Preparing datasets...")
    train_dataset, val_dataset, test_dataset = prepare_datasets(
        config["data"]["train_file"],
        config["data"]["val_file"],
        config["data"]["test_file"],
        tokenizer,
        config["data"]["max_length"]
    )
    print(f"✓ Train: {len(train_dataset)} examples")
    print(f"✓ Val: {len(val_dataset)} examples")
    print(f"✓ Test: {len(test_dataset)} examples")
    
    # Initialize model
    print("\n[3/5] Initializing model...")
    model = EligibilityCriteriaExtractor(
        model_name=config["model"]["base_model"],
        num_rule_types=len(config["rule_types"]),
        num_operators=len(config["operators"]),
        dropout=config["model"]["dropout"]
    )
    print(f"✓ Model initialized")
    
    # Training arguments
    print("\n[4/5] Setting up training arguments...")
    training_args = TrainingArguments(
        output_dir=config["output"]["output_dir"],
        num_train_epochs=config["training"]["num_epochs"],
        per_device_train_batch_size=config["training"]["batch_size"],
        per_device_eval_batch_size=config["training"]["batch_size"],
        learning_rate=config["training"]["learning_rate"],
        warmup_steps=config["training"]["warmup_steps"],
        weight_decay=config["training"]["weight_decay"],
        logging_dir=config["output"]["logging_dir"],
        logging_steps=50,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="rule_type_f1",
        greater_is_better=True,
        save_total_limit=3,
        gradient_accumulation_steps=config["training"]["gradient_accumulation_steps"],
        fp16=torch.cuda.is_available(),  # Use mixed precision if GPU available
        dataloader_num_workers=2,
        report_to="mlflow",
    )
    print(f"✓ Training arguments configured")
    
    # Trainer
    print("\n[5/5] Creating trainer...")
    trainer = EligibilityTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
    )
    print(f"✓ Trainer created")
    
    # Train
    print("\n" + "=" * 60)
    print("Starting Training...")
    print("=" * 60)
    
    with mlflow.start_run():
        # Log parameters
        mlflow.log_params({
            "base_model": config["model"]["base_model"],
            "num_epochs": config["training"]["num_epochs"],
            "batch_size": config["training"]["batch_size"],
            "learning_rate": config["training"]["learning_rate"],
            "train_size": len(train_dataset),
            "val_size": len(val_dataset),
            "test_size": len(test_dataset),
        })
        
        # Train
        trainer.train()
        
        # Evaluate
        print("\nEvaluating on validation set...")
        eval_results = trainer.evaluate()
        
        # Log metrics
        mlflow.log_metrics(eval_results)
        
        # Save model
        model_path = Path(config["output"]["output_dir"]) / "best_model"
        trainer.save_model(str(model_path))
        
        # Log model to MLflow
        mlflow.pytorch.log_model(model, "model", registered_model_name="eligibility_criteria_extractor")
        
        print("\n" + "=" * 60)
        print("Training Complete!")
        print("=" * 60)
        print(f"Model saved to: {model_path}")
        print(f"\nValidation Metrics:")
        for key, value in eval_results.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.4f}")
        
        # Test set evaluation
        print("\nEvaluating on test set...")
        test_results = trainer.evaluate(eval_dataset=test_dataset)
        print(f"\nTest Set Metrics:")
        for key, value in test_results.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.4f}")
        
        mlflow.log_metrics({f"test_{k}": v for k, v in test_results.items() if isinstance(v, float)})


if __name__ == "__main__":
    # Check if MLflow is running
    try:
        import requests
        response = requests.get("http://127.0.0.1:5000", timeout=2)
        print("✓ MLflow UI is running")
    except:
        print("⚠ Warning: MLflow UI may not be running")
        print("  Start it with: mlflow ui --host 0.0.0.0 --port 5000")
        print("  Continuing anyway...")
    
    train_model()

