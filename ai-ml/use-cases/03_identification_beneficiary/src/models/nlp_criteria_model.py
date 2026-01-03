"""
NLP Criteria Extraction Model Architecture
Fine-tuned BERT/RoBERTa for eligibility criteria extraction
"""

import torch
import torch.nn as nn
from transformers import AutoModel, AutoConfig


class EligibilityCriteriaExtractor(nn.Module):
    """
    Fine-tuned BERT/RoBERTa model for extracting structured eligibility rules
    from natural language criteria text.
    """
    
    def __init__(self, model_name="roberta-base", num_rule_types=20, num_operators=7, dropout=0.1):
        super().__init__()
        
        # Base encoder
        self.encoder = AutoModel.from_pretrained(model_name)
        config = AutoConfig.from_pretrained(model_name)
        hidden_size = config.hidden_size
        
        # Task-specific heads
        # Rule type classification (NER-like task)
        self.rule_type_head = nn.Linear(hidden_size, num_rule_types)
        
        # Operator classification
        self.operator_head = nn.Linear(hidden_size, num_operators)
        
        # Value extraction (regression for numeric, classification for categorical)
        self.value_head = nn.Linear(hidden_size, 1)  # For numeric values
        
        # Dropout
        self.dropout = nn.Dropout(dropout)
        
        # Initialize heads
        self._init_weights()
    
    def _init_weights(self):
        """Initialize task-specific heads"""
        nn.init.xavier_uniform_(self.rule_type_head.weight)
        nn.init.zeros_(self.rule_type_head.bias)
        
        nn.init.xavier_uniform_(self.operator_head.weight)
        nn.init.zeros_(self.operator_head.bias)
        
        nn.init.xavier_uniform_(self.value_head.weight)
        nn.init.zeros_(self.value_head.bias)
    
    def forward(self, input_ids, attention_mask):
        """
        Forward pass
        
        Args:
            input_ids: Tokenized input text
            attention_mask: Attention mask
            
        Returns:
            Dictionary with rule_type_logits, operator_logits, value_pred
        """
        # Encode input
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
            "value_pred": value_pred,
            "hidden_states": outputs.last_hidden_state
        }

