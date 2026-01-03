# NLP Model Training Guide - BERT/RoBERTa Fine-tuning

**Purpose:** Step-by-step guide for training fine-tuned BERT/RoBERTa model for eligibility criteria extraction  
**Model:** RoBERTa-base (or BERT-base-uncased)  
**Training Data:** 500+ schemes  
**Created:** 2024-12-30  
**Status:** 📚 Training Guide

---

## Overview

This guide provides detailed instructions for training a fine-tuned BERT/RoBERTa model to extract structured eligibility rules from natural language scheme criteria.

---

## Prerequisites

### Software Requirements

```bash
# Python 3.12+
python --version

# Required packages
pip install torch torchvision torchaudio
pip install transformers
pip install datasets
pip install scikit-learn
pip install mlflow
pip install pandas numpy
pip install tqdm
```

### Hardware Requirements

- **Minimum:** CPU-only training (slower, ~2-4 hours for 500 schemes)
- **Recommended:** GPU (NVIDIA T4 or better, ~30-60 minutes)
- **RAM:** 8GB+ recommended
- **Storage:** 5GB+ for model and data

---

## Model Architecture

### Task: Named Entity Recognition (NER) + Sequence Classification

**Input:** Natural language eligibility criteria text  
**Output:** Structured rules (rule_type, operator, value, expression)

### Architecture Choice

**Option 1: RoBERTa-base (Recommended)**
- Better performance on most NLP tasks
- 125M parameters
- ~500MB model size

**Option 2: BERT-base-uncased**
- Well-established, widely used
- 110M parameters
- ~440MB model size

### Model Structure

```
Input Text: "Citizen must be 60+ years old, BPL, resident of Rajasthan"
    ↓
Tokenization (RoBERTa Tokenizer)
    ↓
RoBERTa Encoder (12 layers, 768 hidden size)
    ↓
Task-Specific Heads:
    ├── NER Head (Rule Type Detection)
    ├── Value Extraction Head
    └── Operator Classification Head
    ↓
Rule Expression Generator
    ↓
Output: [
    {"rule_type": "AGE", "operator": ">=", "value": 60, ...},
    {"rule_type": "INCOME_GROUP", "operator": "==", "value": "BPL", ...},
    ...
]
```

---

## Data Preparation

### Step 1: Load Training Data

```python
import json
from typing import List, Dict

def load_training_data(filepath: str) -> List[Dict]:
    """Load training data from JSON file"""
    with open(filepath, "r") as f:
        return json.load(f)

# Load splits
train_data = load_training_data("data/training/train.json")
val_data = load_training_data("data/training/val.json")
test_data = load_training_data("data/training/test.json")

print(f"Train: {len(train_data)}, Val: {len(val_data)}, Test: {len(test_data)}")
```

### Step 2: Convert to Model Format

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("roberta-base")

def prepare_example(scheme: Dict) -> Dict:
    """Convert scheme to model input format"""
    text = scheme["natural_language_criteria"]
    
    # Tokenize
    encoded = tokenizer(
        text,
        truncation=True,
        padding="max_length",
        max_length=512,
        return_tensors="pt"
    )
    
    # Extract rules as labels
    rules = scheme["extracted_rules"]
    
    # Convert rules to label format
    labels = []
    for rule in rules:
        labels.append({
            "rule_type": rule["rule_type"],
            "operator": rule.get("operator", "=="),
            "value": rule.get("value"),
            "rule_expression": rule.get("rule_expression", "")
        })
    
    return {
        "input_ids": encoded["input_ids"].squeeze(),
        "attention_mask": encoded["attention_mask"].squeeze(),
        "labels": labels,
        "text": text
    }

# Prepare datasets
train_examples = [prepare_example(s) for s in train_data]
val_examples = [prepare_example(s) for s in val_data]
test_examples = [prepare_example(s) for s in test_data]
```

### Step 3: Create Dataset Class

```python
from torch.utils.data import Dataset

class EligibilityCriteriaDataset(Dataset):
    def __init__(self, examples: List[Dict], tokenizer, max_length=512):
        self.examples = examples
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.examples)
    
    def __getitem__(self, idx):
        example = self.examples[idx]
        
        # Tokenize
        encoded = self.tokenizer(
            example["text"],
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt"
        )
        
        return {
            "input_ids": encoded["input_ids"].squeeze(),
            "attention_mask": encoded["attention_mask"].squeeze(),
            "labels": example["labels"]
        }

# Create datasets
train_dataset = EligibilityCriteriaDataset(train_examples, tokenizer)
val_dataset = EligibilityCriteriaDataset(val_examples, tokenizer)
test_dataset = EligibilityCriteriaDataset(test_examples, tokenizer)
```

---

## Model Implementation

### Step 1: Define Model Architecture

```python
from transformers import AutoModel, AutoTokenizer
import torch
import torch.nn as nn

class EligibilityCriteriaExtractor(nn.Module):
    def __init__(self, model_name="roberta-base", num_rule_types=20):
        super().__init__()
        
        # Base model
        self.encoder = AutoModel.from_pretrained(model_name)
        hidden_size = self.encoder.config.hidden_size
        
        # Task-specific heads
        # Rule type classification (NER)
        self.rule_type_head = nn.Linear(hidden_size, num_rule_types)
        
        # Operator classification
        self.operator_head = nn.Linear(hidden_size, 7)  # >=, <=, ==, !=, IN, NOT_IN, BETWEEN
        
        # Value extraction (regression/classification)
        self.value_head = nn.Linear(hidden_size, 1)  # For numeric values
        
        # Dropout
        self.dropout = nn.Dropout(0.1)
    
    def forward(self, input_ids, attention_mask):
        # Encode
        outputs = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        
        # Use [CLS] token representation
        cls_output = outputs.last_hidden_state[:, 0, :]
        cls_output = self.dropout(cls_output)
        
        # Predictions
        rule_type_logits = self.rule_type_head(cls_output)
        operator_logits = self.operator_head(cls_output)
        value_pred = self.value_head(cls_output)
        
        return {
            "rule_type_logits": rule_type_logits,
            "operator_logits": operator_logits,
            "value_pred": value_pred
        }
```

### Step 2: Training Configuration

```python
from transformers import TrainingArguments, Trainer

# Training arguments
training_args = TrainingArguments(
    output_dir="./models/nlp_criteria_extractor",
    num_train_epochs=10,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    warmup_steps=100,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=50,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    greater_is_better=True,
    save_total_limit=3,
    learning_rate=2e-5,
    gradient_accumulation_steps=2,
    fp16=True,  # Use mixed precision if GPU available
    dataloader_num_workers=4,
)
```

### Step 3: Custom Trainer

```python
from transformers import Trainer
import torch

class EligibilityTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False):
        # Get predictions
        outputs = model(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"]
        )
        
        # Compute loss for each head
        # Rule type loss
        rule_type_loss = nn.CrossEntropyLoss()(
            outputs["rule_type_logits"],
            inputs["rule_type_labels"]
        )
        
        # Operator loss
        operator_loss = nn.CrossEntropyLoss()(
            outputs["operator_logits"],
            inputs["operator_labels"]
        )
        
        # Value loss (MSE for numeric)
        value_loss = nn.MSELoss()(
            outputs["value_pred"],
            inputs["value_labels"]
        )
        
        # Combined loss
        total_loss = rule_type_loss + operator_loss + 0.5 * value_loss
        
        return (total_loss, outputs) if return_outputs else total_loss
```

---

## Training Script

### Complete Training Script

```python
import json
import torch
from transformers import AutoTokenizer, TrainingArguments, Trainer
from torch.utils.data import Dataset
import mlflow
import mlflow.pytorch

# Load configuration
from config.nlp_model_config import config

class EligibilityCriteriaDataset(Dataset):
    # ... (as defined above)

class EligibilityCriteriaExtractor(nn.Module):
    # ... (as defined above)

def train_model():
    # Initialize MLflow
    mlflow.set_experiment("nlp_criteria_extraction")
    
    # Load data
    train_data = load_training_data("data/training/train.json")
    val_data = load_training_data("data/training/val.json")
    
    # Prepare datasets
    tokenizer = AutoTokenizer.from_pretrained(config["model"]["base_model"])
    train_dataset = EligibilityCriteriaDataset(train_data, tokenizer)
    val_dataset = EligibilityCriteriaDataset(val_data, tokenizer)
    
    # Initialize model
    model = EligibilityCriteriaExtractor(
        model_name=config["model"]["base_model"],
        num_rule_types=len(config["rule_types"])
    )
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=config["output_dir"],
        num_train_epochs=config["training"]["num_epochs"],
        per_device_train_batch_size=config["training"]["batch_size"],
        per_device_eval_batch_size=config["training"]["batch_size"],
        learning_rate=config["training"]["learning_rate"],
        warmup_steps=config["training"]["warmup_steps"],
        weight_decay=config["training"]["weight_decay"],
        logging_dir=config["logging_dir"],
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
    )
    
    # Trainer
    trainer = EligibilityTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
    )
    
    # Train
    with mlflow.start_run():
        trainer.train()
        
        # Log metrics
        metrics = trainer.evaluate()
        mlflow.log_metrics(metrics)
        
        # Save model
        model_path = f"{config['output_dir']}/best_model"
        trainer.save_model(model_path)
        
        # Log to MLflow
        mlflow.pytorch.log_model(model, "model")
        
        print(f"Model saved to {model_path}")
        print(f"Metrics: {metrics}")

if __name__ == "__main__":
    train_model()
```

---

## Evaluation

### Evaluation Metrics

```python
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import numpy as np

def evaluate_model(model, test_dataset):
    """Evaluate model on test set"""
    model.eval()
    
    all_rule_type_preds = []
    all_rule_type_labels = []
    all_operator_preds = []
    all_operator_labels = []
    
    with torch.no_grad():
        for batch in test_dataset:
            outputs = model(
                input_ids=batch["input_ids"],
                attention_mask=batch["attention_mask"]
            )
            
            # Get predictions
            rule_type_preds = torch.argmax(outputs["rule_type_logits"], dim=-1)
            operator_preds = torch.argmax(outputs["operator_logits"], dim=-1)
            
            all_rule_type_preds.extend(rule_type_preds.cpu().numpy())
            all_operator_preds.extend(operator_preds.cpu().numpy())
            # ... collect labels
    
    # Calculate metrics
    rule_type_acc = accuracy_score(all_rule_type_labels, all_rule_type_preds)
    rule_type_prec, rule_type_rec, rule_type_f1, _ = precision_recall_fscore_support(
        all_rule_type_labels, all_rule_type_preds, average="weighted"
    )
    
    operator_acc = accuracy_score(all_operator_labels, all_operator_preds)
    
    return {
        "rule_type_accuracy": rule_type_acc,
        "rule_type_precision": rule_type_prec,
        "rule_type_recall": rule_type_rec,
        "rule_type_f1": rule_type_f1,
        "operator_accuracy": operator_acc,
    }
```

---

## Hyperparameter Tuning

### Grid Search

```python
from itertools import product

# Hyperparameter grid
learning_rates = [1e-5, 2e-5, 3e-5]
batch_sizes = [8, 16, 32]
num_epochs = [5, 10, 15]

best_score = 0
best_params = None

for lr, bs, epochs in product(learning_rates, batch_sizes, num_epochs):
    # Update config
    config["training"]["learning_rate"] = lr
    config["training"]["batch_size"] = bs
    config["training"]["num_epochs"] = epochs
    
    # Train
    trainer = train_model()
    
    # Evaluate
    metrics = evaluate_model(trainer.model, test_dataset)
    score = metrics["rule_type_f1"]
    
    if score > best_score:
        best_score = score
        best_params = {"lr": lr, "batch_size": bs, "epochs": epochs}

print(f"Best params: {best_params}, Best F1: {best_score}")
```

---

## Model Configuration

### Configuration File: `config/nlp_model_config.yaml`

```yaml
model:
  base_model: "roberta-base"  # or "bert-base-uncased"
  max_length: 512
  hidden_size: 768
  num_rule_types: 20
  num_operators: 7

training:
  num_epochs: 10
  batch_size: 16
  learning_rate: 2e-5
  warmup_steps: 100
  weight_decay: 0.01
  gradient_accumulation_steps: 2
  early_stopping_patience: 3

data:
  train_split: 0.7
  val_split: 0.15
  test_split: 0.15
  max_length: 512

rule_types:
  - AGE
  - GENDER
  - INCOME_GROUP
  - ANNUAL_INCOME
  - DISTRICT
  - BLOCK
  - VILLAGE
  - STATE
  - DISABILITY
  - DISABILITY_TYPE
  - DISABILITY_PERCENTAGE
  - FAMILY_SIZE
  - CATEGORY
  - RATION_CARD
  - LAND_OWNERSHIP
  - PROPERTY_OWNERSHIP
  - PRIOR_PARTICIPATION
  - EDUCATION_LEVEL
  - EMPLOYMENT_STATUS
  - MARITAL_STATUS

operators:
  - ">="
  - "<="
  - "=="
  - "!="
  - "IN"
  - "NOT_IN"
  - "BETWEEN"

output:
  output_dir: "./models/nlp_criteria_extractor"
  logging_dir: "./logs"
  mlflow_experiment: "nlp_criteria_extraction"
```

---

## Training Steps

### Step 1: Prepare Environment

```bash
# Activate virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
pip install transformers datasets torch mlflow
```

### Step 2: Prepare Data

```bash
# Ensure training data is ready
python scripts/validate_training_data.py data/training/train.json
```

### Step 3: Train Model

```bash
# Run training
python scripts/train_nlp_model.py \
    --config config/nlp_model_config.yaml \
    --train_data data/training/train.json \
    --val_data data/training/val.json \
    --output_dir models/nlp_criteria_extractor
```

### Step 4: Evaluate

```bash
# Evaluate on test set
python scripts/evaluate_nlp_model.py \
    --model_path models/nlp_criteria_extractor/best_model \
    --test_data data/training/test.json
```

### Step 5: Register Model

```bash
# Register in MLflow
python scripts/register_model.py \
    --model_path models/nlp_criteria_extractor/best_model \
    --model_name "eligibility_criteria_extractor" \
    --version "1.0.0"
```

---

## Expected Results

### Performance Targets

- **Rule Type Accuracy:** >90%
- **Rule Type F1-Score:** >85%
- **Operator Accuracy:** >95%
- **Overall Extraction Accuracy:** >85%
- **Inference Time:** <100ms per extraction

### Training Time

- **CPU:** 2-4 hours (500 schemes, 10 epochs)
- **GPU (T4):** 30-60 minutes
- **GPU (V100/A100):** 15-30 minutes

---

## Troubleshooting

### Issue: Out of Memory

**Solution:**
- Reduce batch size
- Use gradient accumulation
- Use mixed precision (fp16)

### Issue: Low Accuracy

**Solution:**
- Increase training data
- Tune hyperparameters
- Try different base model
- Add data augmentation

### Issue: Overfitting

**Solution:**
- Add dropout
- Use early stopping
- Increase weight decay
- Add more training data

---

## Next Steps

1. **Train Model:** Follow steps above
2. **Evaluate:** Run evaluation script
3. **Register:** Save to MLflow
4. **Integrate:** Move to API development (see `NLP_CRITERIA_EXTRACTION_IMPLEMENTATION_PLAN.md`)

---

**Document Version:** 1.0  
**Last Updated:** 2024-12-30  
**Status:** 📚 Ready for Training

