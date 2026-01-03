#!/usr/bin/env python3
"""
Check if training environment is set up correctly
"""

import sys
from pathlib import Path

def check_imports():
    """Check if required packages are installed"""
    print("Checking required packages...")
    
    required = {
        "torch": "PyTorch",
        "transformers": "Transformers",
        "mlflow": "MLflow",
        "sklearn": "scikit-learn",
        "yaml": "PyYAML"
    }
    
    missing = []
    for module, name in required.items():
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} - MISSING")
            missing.append(name)
    
    return len(missing) == 0

def check_files():
    """Check if required files exist"""
    print("\nChecking required files...")
    
    base_path = Path(__file__).parent.parent
    
    required_files = [
        "config/nlp_model_config.yaml",
        "src/models/nlp_criteria_model.py",
        "src/utils/nlp_preprocessing.py",
        "scripts/train_nlp_model.py",
        "data/training/train.json",
        "data/training/val.json",
        "data/training/test.json",
    ]
    
    missing = []
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} - MISSING")
            missing.append(file_path)
    
    return len(missing) == 0

def check_data():
    """Check training data"""
    print("\nChecking training data...")
    
    base_path = Path(__file__).parent.parent
    
    import json
    
    for split in ["train", "val", "test"]:
        file_path = base_path / "data" / "training" / f"{split}.json"
        if file_path.exists():
            with open(file_path, "r") as f:
                data = json.load(f)
            print(f"  ✓ {split}.json: {len(data)} examples")
        else:
            print(f"  ✗ {split}.json - MISSING")
            return False
    
    return True

def check_mlflow():
    """Check if MLflow is accessible"""
    print("\nChecking MLflow...")
    
    try:
        import requests
        response = requests.get("http://127.0.0.1:5000", timeout=2)
        print("  ✓ MLflow UI is running")
        return True
    except:
        print("  ⚠ MLflow UI is not running")
        print("    Start it with: mlflow ui --host 0.0.0.0 --port 5000")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Training Environment Check")
    print("=" * 60)
    
    all_ok = True
    
    if not check_imports():
        all_ok = False
        print("\n⚠ Install missing packages:")
        print("  pip install transformers scikit-learn pyyaml")
    
    if not check_files():
        all_ok = False
    
    if not check_data():
        all_ok = False
    
    mlflow_ok = check_mlflow()
    
    print("\n" + "=" * 60)
    if all_ok:
        print("✓ All checks passed! Ready for training.")
        if not mlflow_ok:
            print("\n⚠ Note: Start MLflow UI before training for better tracking")
    else:
        print("✗ Some checks failed. Please fix issues above.")
    print("=" * 60)

