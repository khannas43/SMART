"""
Data preprocessing utilities for NLP model training
"""

import json
import torch
from typing import List, Dict, Any
from transformers import AutoTokenizer
from torch.utils.data import Dataset


class EligibilityCriteriaDataset(Dataset):
    """Dataset class for eligibility criteria extraction"""
    
    def __init__(self, examples: List[Dict], tokenizer, max_length=512):
        self.examples = examples
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        # Build rule type and operator mappings
        self.rule_type_to_id = self._build_rule_type_mapping()
        self.operator_to_id = self._build_operator_mapping()
        self.id_to_rule_type = {v: k for k, v in self.rule_type_to_id.items()}
        self.id_to_operator = {v: k for k, v in self.operator_to_id.items()}
    
    def _build_rule_type_mapping(self):
        """Build mapping from rule type to ID"""
        rule_types = [
            "AGE", "GENDER", "INCOME_GROUP", "ANNUAL_INCOME",
            "DISTRICT", "BLOCK", "VILLAGE", "STATE",
            "DISABILITY", "DISABILITY_TYPE", "DISABILITY_PERCENTAGE",
            "FAMILY_SIZE", "CATEGORY", "RATION_CARD",
            "LAND_OWNERSHIP", "PROPERTY_OWNERSHIP",
            "PRIOR_PARTICIPATION", "EDUCATION_LEVEL",
            "EMPLOYMENT_STATUS", "MARITAL_STATUS"
        ]
        return {rt: i for i, rt in enumerate(rule_types)}
    
    def _build_operator_mapping(self):
        """Build mapping from operator to ID"""
        operators = [">=", "<=", "==", "!=", "IN", "NOT_IN", "BETWEEN"]
        return {op: i for i, op in enumerate(operators)}
    
    def __len__(self):
        return len(self.examples)
    
    def __getitem__(self, idx):
        example = self.examples[idx]
        
        # Tokenize text
        text = example["natural_language_criteria"]
        encoded = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt"
        )
        
        # Extract first rule as target (for simplicity, we'll predict the first rule)
        # In a more complex setup, we'd predict all rules
        rules = example.get("extracted_rules", [])
        if rules:
            first_rule = rules[0]
            rule_type = first_rule.get("rule_type", "AGE")
            operator = first_rule.get("operator", ">=")
            value = first_rule.get("value", 0)
            
            # Convert to IDs
            rule_type_id = self.rule_type_to_id.get(rule_type, 0)
            operator_id = self.operator_to_id.get(operator, 0)
            
            # Normalize value (convert to float)
            if isinstance(value, (int, float)):
                value_float = float(value)
            elif isinstance(value, bool):
                value_float = 1.0 if value else 0.0
            else:
                value_float = 0.0
        else:
            rule_type_id = 0
            operator_id = 0
            value_float = 0.0
        
        return {
            "input_ids": encoded["input_ids"].squeeze(),
            "attention_mask": encoded["attention_mask"].squeeze(),
            "rule_type_id": torch.tensor(rule_type_id, dtype=torch.long),
            "operator_id": torch.tensor(operator_id, dtype=torch.long),
            "value": torch.tensor(value_float, dtype=torch.float),
            "text": text,
            "scheme_code": example.get("scheme_code", "")
        }


def load_training_data(filepath: str) -> List[Dict]:
    """Load training data from JSON file"""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def prepare_datasets(train_file: str, val_file: str, test_file: str, 
                    tokenizer, max_length=512):
    """Prepare train/val/test datasets"""
    
    # Load data
    train_data = load_training_data(train_file)
    val_data = load_training_data(val_file)
    test_data = load_training_data(test_file)
    
    # Create datasets
    train_dataset = EligibilityCriteriaDataset(train_data, tokenizer, max_length)
    val_dataset = EligibilityCriteriaDataset(val_data, tokenizer, max_length)
    test_dataset = EligibilityCriteriaDataset(test_data, tokenizer, max_length)
    
    return train_dataset, val_dataset, test_dataset

