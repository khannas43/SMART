#!/usr/bin/env python3
"""
Check MLflow Models for Auto Identification of Beneficiaries
Use Case: AI-PLATFORM-03
"""

import sys
from pathlib import Path
import mlflow
from mlflow.tracking import MlflowClient

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

def check_mlflow_models():
    """Check MLflow for eligibility models"""
    
    # Set MLflow tracking URI
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    client = MlflowClient()
    
    print("=" * 70)
    print("MLflow Models Check: Auto Identification of Beneficiaries")
    print("=" * 70)
    
    # Check experiments
    experiment_names = [
        "smart/identification_beneficiary",
        "smart/identification_beneficiary/eligibility_scoring",
        "identification_beneficiary",
        "eligibility_scoring"
    ]
    
    found_experiments = []
    for exp_name in experiment_names:
        try:
            experiment = mlflow.get_experiment_by_name(exp_name)
            if experiment:
                found_experiments.append(experiment)
                print(f"\n✅ Found Experiment: {exp_name}")
                print(f"   Experiment ID: {experiment.experiment_id}")
                print(f"   Artifact Location: {experiment.artifact_location}")
        except Exception as e:
            pass
    
    # List all experiments with 'identification' or 'eligibility' in name
    print("\n" + "=" * 70)
    print("Searching for related experiments...")
    print("=" * 70)
    
    try:
        all_experiments = mlflow.search_experiments()
        related_experiments = [
            exp for exp in all_experiments 
            if any(keyword in exp.name.lower() for keyword in ['identification', 'eligibility', 'beneficiary', 'smart'])
        ]
        
        if related_experiments:
            print(f"\nFound {len(related_experiments)} related experiments:")
            for exp in related_experiments:
                print(f"\n  📊 {exp.name}")
                print(f"     ID: {exp.experiment_id}")
                
                # Get runs for this experiment
                runs = mlflow.search_runs(experiment_ids=[exp.experiment_id], max_results=5)
                if not runs.empty:
                    print(f"     Runs: {len(runs)}")
                    print(f"     Latest Run: {runs.iloc[0]['tags.mlflow.runName'] if 'tags.mlflow.runName' in runs.columns else 'N/A'}")
                else:
                    print(f"     Runs: 0 (no training runs yet)")
        else:
            print("\n❌ No related experiments found")
    
    except Exception as e:
        print(f"\n⚠️  Error searching experiments: {e}")
    
    # Check registered models
    print("\n" + "=" * 70)
    print("Checking Registered Models...")
    print("=" * 70)
    
    try:
        registered_models = client.search_registered_models()
        eligibility_models = [
            model for model in registered_models
            if any(keyword in model.name.lower() for keyword in ['eligibility', 'identification', 'beneficiary'])
        ]
        
        if eligibility_models:
            print(f"\n✅ Found {len(eligibility_models)} registered models:")
            for model in eligibility_models:
                print(f"\n  🤖 {model.name}")
                print(f"     Latest Version: {model.latest_versions[0].version if model.latest_versions else 'N/A'}")
                print(f"     Description: {model.description[:100] if model.description else 'N/A'}")
                
                # Get model versions
                versions = model.latest_versions
                if versions:
                    print(f"     Versions: {len(versions)}")
                    for v in versions[:3]:  # Show latest 3
                        print(f"       - Version {v.version}: {v.current_stage} ({v.last_updated_timestamp})")
        else:
            print("\n❌ No registered models found for eligibility/identification")
            print("   Models need to be trained first using: python src/train_eligibility_model.py")
    
    except Exception as e:
        print(f"\n⚠️  Error checking registered models: {e}")
    
    # Check if MLflow UI is running
    print("\n" + "=" * 70)
    print("MLflow UI Status")
    print("=" * 70)
    
    try:
        import requests
        response = requests.get("http://127.0.0.1:5000", timeout=2)
        if response.status_code == 200:
            print("\n✅ MLflow UI is running")
            print("   View models at: http://127.0.0.1:5000")
        else:
            print("\n⚠️  MLflow UI returned status code:", response.status_code)
    except requests.exceptions.RequestException:
        print("\n❌ MLflow UI is not accessible at http://127.0.0.1:5000")
        print("   Start MLflow UI with: mlflow ui --port 5000")
    
    print("\n" + "=" * 70)
    print("Next Steps")
    print("=" * 70)
    print("""
1. To train a model:
   cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
   python src/train_eligibility_model.py --scheme_id SCHEME_001

2. View in MLflow UI:
   http://127.0.0.1:5000

3. Check specific experiment:
   - Experiment name: smart/identification_beneficiary/*
   - Models are registered as: Eligibility_Model_SCHEME_001
    """)
    
    print("=" * 70)


if __name__ == "__main__":
    check_mlflow_models()

