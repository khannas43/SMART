#!/usr/bin/env python3
"""
Split training data into train/val/test sets
"""

import json
import random
from pathlib import Path

def split_dataset(input_file: str, 
                 train_ratio: float = 0.7,
                 val_ratio: float = 0.15,
                 test_ratio: float = 0.15):
    """Split dataset into train/val/test"""
    
    if not Path(input_file).exists():
        print(f"Error: {input_file} not found")
        return
    
    with open(input_file, "r", encoding="utf-8") as f:
        schemes = json.load(f)
    
    # Shuffle
    random.seed(42)  # For reproducibility
    random.shuffle(schemes)
    
    # Calculate splits
    n = len(schemes)
    train_end = int(n * train_ratio)
    val_end = train_end + int(n * val_ratio)
    
    train = schemes[:train_end]
    val = schemes[train_end:val_end]
    test = schemes[val_end:]
    
    # Save splits
    output_dir = Path("data/training")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "train.json", "w", encoding="utf-8") as f:
        json.dump(train, f, indent=2, ensure_ascii=False)
    
    with open(output_dir / "val.json", "w", encoding="utf-8") as f:
        json.dump(val, f, indent=2, ensure_ascii=False)
    
    with open(output_dir / "test.json", "w", encoding="utf-8") as f:
        json.dump(test, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Split complete:")
    print(f"  Train: {len(train)} schemes ({len(train)/n*100:.1f}%)")
    print(f"  Val: {len(val)} schemes ({len(val)/n*100:.1f}%)")
    print(f"  Test: {len(test)} schemes ({len(test)/n*100:.1f}%)")

if __name__ == "__main__":
    split_dataset("data/training/schemes_raw.json")

