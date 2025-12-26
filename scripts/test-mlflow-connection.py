#!/usr/bin/env python3
"""
SMART Platform - MLflow Connection Test Script

Tests MLflow tracking server connection and functionality.
Requires WSL Python venv with mlflow installed.
"""

import sys
import os

def test_mlflow_connection():
    """Test MLflow tracking server connection"""
    print("=" * 60)
    print("SMART Platform - MLflow Connection Test")
    print("=" * 60)
    
    mlflow_uri = "http://127.0.0.1:5000"
    
    print(f"\nMLflow Tracking URI: {mlflow_uri}")
    
    try:
        # Try to import mlflow
        try:
            import mlflow
        except ImportError:
            print("\n❌ ERROR: mlflow not installed")
            print("   Install with: pip install mlflow[extras]")
            print("   Or from WSL venv: /mnt/c/Projects/SMART/ai-ml/.venv/bin/pip install mlflow[extras]")
            return False
        
        print("\n✅ MLflow imported successfully")
        print(f"   MLflow version: {mlflow.__version__}")
        
        # Set tracking URI
        mlflow.set_tracking_uri(mlflow_uri)
        print(f"\n📡 Tracking URI set to: {mlflow.get_tracking_uri()}")
        
        # Test connection to tracking server
        print("\nAttempting to connect to MLflow tracking server...")
        try:
            # Try to get tracking URI (this will fail if server is not accessible)
            experiments = mlflow.search_experiments()
            print(f"✅ Connected to MLflow tracking server successfully!")
            print(f"\n📊 Found {len(experiments)} experiment(s)")
            
            # List experiments
            if experiments:
                print(f"\n📋 Available Experiments:")
                for exp in experiments[:10]:  # Show first 10
                    print(f"   - {exp.name} (ID: {exp.experiment_id})")
                    if hasattr(exp, 'description') and exp.description:
                        print(f"     Description: {exp.description[:50]}...")
            
            # Get or create a test experiment
            experiment_name = "smart-connection-test"
            try:
                experiment = mlflow.get_experiment_by_name(experiment_name)
                if experiment is None:
                    experiment_id = mlflow.create_experiment(experiment_name)
                    print(f"\n✅ Created test experiment: {experiment_name} (ID: {experiment_id})")
                else:
                    print(f"\n✅ Found existing experiment: {experiment_name} (ID: {experiment.experiment_id})")
            except Exception as e:
                print(f"\n⚠️  Could not create/find experiment: {e}")
            
            # Test logging (create a simple run)
            print("\n🧪 Testing MLflow run creation...")
            try:
                mlflow.set_experiment(experiment_name)
                with mlflow.start_run(run_name="connection-test") as run:
                    mlflow.log_param("test_param", "connection_test")
                    mlflow.log_metric("test_metric", 1.0)
                    print(f"✅ Successfully created test run: {run.info.run_id}")
                    print(f"   Run name: {run.info.run_name}")
                    print(f"   Status: {run.info.status}")
            except Exception as e:
                print(f"⚠️  Could not create test run: {e}")
            
            print("\n" + "=" * 60)
            print("✅ MLflow connection test PASSED")
            print("=" * 60)
            return True
            
        except Exception as e:
            print(f"\n❌ Connection failed: {e}")
            print("\nTroubleshooting:")
            print("  1. Ensure MLflow UI is running:")
            print("     cd /mnt/c/Projects/SMART/ai-ml")
            print("     source .venv/bin/activate")
            print("     mlflow ui --host 0.0.0.0 --port 5000")
            print("  2. Check if the server is accessible at http://127.0.0.1:5000")
            print("  3. Verify firewall settings")
            print("  4. Check MLflow server logs")
            return False
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_mlflow_connection()
    sys.exit(0 if success else 1)

