"""
Utility script to manage MLflow runs
- View runs
- Delete failed runs
- Compare runs
- Export run data
"""

import mlflow
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd


def list_runs(experiment_name: str = "smart/golden_record/baseline_v1", 
               status_filter: str = None):
    """
    List all runs in an experiment
    
    Args:
        experiment_name: Name of the experiment
        status_filter: Filter by status ('FINISHED', 'FAILED', 'RUNNING')
    """
    mlflow.set_tracking_uri('http://127.0.0.1:5000')
    
    try:
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            print(f"❌ Experiment '{experiment_name}' not found")
            return
        
        print(f"\n📊 Experiment: {experiment_name}")
        print(f"   ID: {experiment.experiment_id}")
        print("="*60)
        
        # Get all runs
        runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id], 
                                   order_by=["start_time DESC"])
        
        if runs.empty:
            print("No runs found")
            return
        
        # Filter by status if specified
        if status_filter:
            runs = runs[runs['status'] == status_filter.upper()]
        
        print(f"\nTotal runs: {len(runs)}")
        print(f"Status breakdown:")
        print(runs['status'].value_counts().to_string())
        
        print("\n" + "="*60)
        print("Recent Runs:")
        print("="*60)
        
        # Display summary
        for idx, run in runs.head(10).iterrows():
            status = run['status']
            status_emoji = "✅" if status == "FINISHED" else "❌" if status == "FAILED" else "🏃"
            
            print(f"\n{status_emoji} {run['tags.mlflow.runName']}")
            print(f"   Run ID: {run['run_id']}")
            print(f"   Status: {status}")
            print(f"   Start Time: {run['start_time']}")
            
            if status == "FINISHED":
                if 'metrics.precision' in run:
                    print(f"   Precision: {run['metrics.precision']:.4f}")
                if 'metrics.recall' in run:
                    print(f"   Recall: {run['metrics.recall']:.4f}")
                if 'metrics.f1_score' in run:
                    print(f"   F1 Score: {run['metrics.f1_score']:.4f}")
            
            print(f"   View: http://127.0.0.1:5000/#/experiments/{experiment.experiment_id}/runs/{run['run_id']}")
        
        return runs
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def delete_failed_runs(experiment_name: str = "smart/golden_record/baseline_v1",
                       confirm: bool = False):
    """
    Delete all failed runs from an experiment
    
    Args:
        experiment_name: Name of the experiment
        confirm: If False, just shows what would be deleted. If True, actually deletes.
    """
    mlflow.set_tracking_uri('http://127.0.0.1:5000')
    
    try:
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            print(f"❌ Experiment '{experiment_name}' not found")
            return
        
        runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
        failed_runs = runs[runs['status'] == 'FAILED']
        
        if failed_runs.empty:
            print("✅ No failed runs found")
            return
        
        print(f"\n📋 Found {len(failed_runs)} failed runs:")
        for idx, run in failed_runs.iterrows():
            print(f"   - {run['tags.mlflow.runName']} ({run['run_id']})")
        
        if not confirm:
            print("\n⚠️  This is a preview. To actually delete, run with --confirm flag")
            print("   python manage_mlflow_runs.py --delete-failed --confirm")
            return
        
        # Delete runs
        deleted = 0
        for idx, run in failed_runs.iterrows():
            try:
                mlflow.delete_run(run['run_id'])
                deleted += 1
                print(f"✅ Deleted: {run['tags.mlflow.runName']}")
            except Exception as e:
                print(f"❌ Failed to delete {run['tags.mlflow.runName']}: {e}")
        
        print(f"\n✅ Deleted {deleted} failed runs")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def compare_runs(experiment_name: str = "smart/golden_record/baseline_v1", 
                 num_runs: int = 5):
    """
    Compare recent successful runs
    
    Args:
        experiment_name: Name of the experiment
        num_runs: Number of recent runs to compare
    """
    mlflow.set_tracking_uri('http://127.0.0.1:5000')
    
    try:
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            print(f"❌ Experiment '{experiment_name}' not found")
            return
        
        runs = mlflow.search_runs(
            experiment_ids=[experiment.experiment_id],
            filter_string="status = 'FINISHED'",
            order_by=["start_time DESC"],
            max_results=num_runs
        )
        
        if runs.empty:
            print("No successful runs found")
            return
        
        print("\n" + "="*60)
        print(f"Comparison of {len(runs)} Recent Successful Runs")
        print("="*60)
        
        # Select key columns for comparison
        compare_cols = ['tags.mlflow.runName', 'params.model_type', 
                       'params.auto_merge_threshold', 'params.manual_review_threshold',
                       'metrics.precision', 'metrics.recall', 'metrics.f1_score',
                       'metrics.training_pairs']
        
        # Filter to columns that exist
        available_cols = [col for col in compare_cols if col in runs.columns]
        comparison = runs[available_cols].copy()
        
        print(comparison.to_string(index=False))
        
        # Summary statistics
        if 'metrics.precision' in comparison.columns:
            print(f"\n📊 Summary:")
            print(f"   Best Precision: {comparison['metrics.precision'].max():.4f}")
            print(f"   Average Precision: {comparison['metrics.precision'].mean():.4f}")
        if 'metrics.recall' in comparison.columns:
            print(f"   Best Recall: {comparison['metrics.recall'].max():.4f}")
            print(f"   Average Recall: {comparison['metrics.recall'].mean():.4f}")
        if 'metrics.f1_score' in comparison.columns:
            print(f"   Best F1 Score: {comparison['metrics.f1_score'].max():.4f}")
            print(f"   Average F1 Score: {comparison['metrics.f1_score'].mean():.4f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def export_runs_to_csv(experiment_name: str = "smart/golden_record/baseline_v1",
                       output_file: str = None):
    """
    Export all runs to CSV
    
    Args:
        experiment_name: Name of the experiment
        output_file: Output CSV file path
    """
    mlflow.set_tracking_uri('http://127.0.0.1:5000')
    
    try:
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            print(f"❌ Experiment '{experiment_name}' not found")
            return
        
        runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
        
        if output_file is None:
            output_file = f"mlflow_runs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        runs.to_csv(output_file, index=False)
        print(f"✅ Exported {len(runs)} runs to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage MLflow runs')
    parser.add_argument('--list', action='store_true', help='List all runs')
    parser.add_argument('--status', type=str, help='Filter by status (FINISHED, FAILED, RUNNING)')
    parser.add_argument('--delete-failed', action='store_true', help='Delete failed runs')
    parser.add_argument('--confirm', action='store_true', help='Confirm deletion')
    parser.add_argument('--compare', action='store_true', help='Compare recent successful runs')
    parser.add_argument('--export', type=str, help='Export runs to CSV file')
    parser.add_argument('--experiment', type=str, default='smart/golden_record/baseline_v1',
                       help='Experiment name')
    
    args = parser.parse_args()
    
    if args.list:
        list_runs(args.experiment, args.status)
    elif args.delete_failed:
        delete_failed_runs(args.experiment, args.confirm)
    elif args.compare:
        compare_runs(args.experiment)
    elif args.export:
        export_runs_to_csv(args.experiment, args.export)
    else:
        # Default: list runs
        print("📊 MLflow Run Manager")
        print("="*60)
        list_runs(args.experiment)

