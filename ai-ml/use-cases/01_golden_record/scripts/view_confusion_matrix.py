"""
View Confusion Matrix Metrics from MLflow Runs
Shows True Positives, True Negatives, False Positives, False Negatives
"""

import mlflow
import pandas as pd
import sys
from pathlib import Path
import argparse


def get_confusion_matrix_metrics(run_id: str = None, 
                                 experiment_name: str = "smart/golden_record/baseline_v1",
                                 latest_only: bool = False):
    """
    Get confusion matrix metrics from MLflow run(s)
    
    Args:
        run_id: Specific run ID. If None, gets from latest successful run
        experiment_name: Experiment name
        latest_only: If True and run_id is None, get only latest run
    """
    mlflow.set_tracking_uri('http://127.0.0.1:5000')
    
    try:
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            print(f"❌ Experiment '{experiment_name}' not found")
            return None
        
        if run_id:
            # Get specific run
            run = mlflow.get_run(run_id)
            runs_data = [run]
        else:
            # Get runs from experiment
            runs_df = mlflow.search_runs(
                experiment_ids=[experiment.experiment_id],
                filter_string="status = 'FINISHED'",
                order_by=["start_time DESC"]
            )
            
            if runs_df.empty:
                print("❌ No successful runs found")
                return None
            
            if latest_only:
                runs_df = runs_df.head(1)
            
            # Get run objects
            runs_data = []
            for idx, row in runs_df.iterrows():
                runs_data.append(mlflow.get_run(row['run_id']))
        
        results = []
        
        for run in runs_data:
            metrics = run.data.metrics
            
            # Extract confusion matrix metrics
            tp = metrics.get('true_positives', None)
            fp = metrics.get('false_positives', None)
            tn = metrics.get('true_negatives', None)
            fn = metrics.get('false_negatives', None)
            
            # Calculate additional metrics
            precision = metrics.get('precision', None)
            recall = metrics.get('recall', None)
            f1 = metrics.get('f1_score', None)
            
            # Calculate totals
            total_predictions = None
            if all(v is not None for v in [tp, fp, tn, fn]):
                total_predictions = tp + fp + tn + fn
            
            result = {
                'run_id': run.info.run_id,
                'run_name': run.data.tags.get('mlflow.runName', 'N/A'),
                'status': run.info.status,
                'start_time': run.info.start_time,
                'true_positives': tp,
                'false_positives': fp,
                'true_negatives': tn,
                'false_negatives': fn,
                'total_predictions': total_predictions,
                'precision': precision,
                'recall': recall,
                'f1_score': f1
            }
            results.append(result)
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def display_confusion_matrix_table(results):
    """
    Display confusion matrix in a formatted table
    """
    if not results:
        print("No results to display")
        return
    
    print("\n" + "="*80)
    print("CONFUSION MATRIX METRICS")
    print("="*80)
    
    for result in results:
        print(f"\n📊 Run: {result['run_name']}")
        print(f"   Run ID: {result['run_id']}")
        print(f"   Status: {result['status']}")
        print(f"   Start Time: {pd.to_datetime(result['start_time'], unit='ms')}")
        print()
        
        # Confusion Matrix Table
        print("   Confusion Matrix:")
        print("   " + "-"*76)
        
        tp = result['true_positives']
        fp = result['false_positives']
        tn = result['true_negatives']
        fn = result['false_negatives']
        
        if all(v is not None for v in [tp, fp, tn, fn]):
            # Format as 2x2 confusion matrix
            print(f"   {'':20s} | {'Predicted: Match':20s} | {'Predicted: Non-Match':20s}")
            print("   " + "-"*76)
            print(f"   {'Actual: Match':20s} | {f'TP = {tp:6d}':20s} | {f'FN = {fn:6d}':20s}")
            print(f"   {'Actual: Non-Match':20s} | {f'FP = {fp:6d}':20s} | {f'TN = {tn:6d}':20s}")
            print("   " + "-"*76)
            
            # Totals
            actual_positives = tp + fn if (tp is not None and fn is not None) else None
            actual_negatives = tn + fp if (tn is not None and fp is not None) else None
            predicted_positives = tp + fp if (tp is not None and fp is not None) else None
            predicted_negatives = tn + fn if (tn is not None and fn is not None) else None
            
            print(f"\n   Totals:")
            print(f"   - Actual Positives (matches):     {actual_positives:,}" if actual_positives else "   - Actual Positives: N/A")
            print(f"   - Actual Negatives (non-matches): {actual_negatives:,}" if actual_negatives else "   - Actual Negatives: N/A")
            print(f"   - Predicted Positives (merged):   {predicted_positives:,}" if predicted_positives else "   - Predicted Positives: N/A")
            print(f"   - Predicted Negatives (rejected): {predicted_negatives:,}" if predicted_negatives else "   - Predicted Negatives: N/A")
            print(f"   - Total Predictions:              {result['total_predictions']:,}" if result['total_predictions'] else "   - Total Predictions: N/A")
        else:
            print("   ⚠️  Confusion matrix metrics not available")
            print(f"   TP: {tp}, FP: {fp}, TN: {tn}, FN: {fn}")
        
        # Performance Metrics
        print(f"\n   Performance Metrics:")
        if result['precision'] is not None:
            print(f"   - Precision: {result['precision']:.4f} ({result['precision']*100:.2f}%)")
        if result['recall'] is not None:
            print(f"   - Recall:    {result['recall']:.4f} ({result['recall']*100:.2f}%)")
        if result['f1_score'] is not None:
            print(f"   - F1 Score:  {result['f1_score']:.4f}")
        
        # Interpretation
        if all(v is not None for v in [tp, fp, tn, fn]):
            print(f"\n   Interpretation:")
            print(f"   ✅ True Positives ({tp:,}): Correctly identified duplicate pairs")
            print(f"   ❌ False Positives ({fp:,}): Incorrectly merged different people (Type I error)")
            print(f"   ✅ True Negatives ({tn:,}): Correctly identified non-duplicate pairs")
            print(f"   ❌ False Negatives ({fn:,}): Missed duplicate pairs (Type II error)")
            
            # Error rates
            if (tp + fp) > 0:
                false_positive_rate = fp / (fp + tn) * 100
                print(f"\n   Error Rates:")
                print(f"   - False Positive Rate: {false_positive_rate:.2f}% (lower is better)")
            
            if (tp + fn) > 0:
                false_negative_rate = fn / (tp + fn) * 100
                print(f"   - False Negative Rate: {false_negative_rate:.2f}% (lower is better)")
        
        # MLflow Link
        exp_id = mlflow.get_experiment_by_name("smart/golden_record/baseline_v1").experiment_id
        print(f"\n   🔗 View in MLflow: http://127.0.0.1:5000/#/experiments/{exp_id}/runs/{result['run_id']}")
        print("   " + "-"*76)


def export_to_csv(results, output_file: str = None):
    """
    Export confusion matrix metrics to CSV
    """
    if not results:
        print("No results to export")
        return
    
    if output_file is None:
        from datetime import datetime
        output_file = f"confusion_matrix_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    df = pd.DataFrame(results)
    
    # Reorder columns
    cols = ['run_name', 'run_id', 'status', 'start_time',
            'true_positives', 'false_positives', 'true_negatives', 'false_negatives',
            'total_predictions', 'precision', 'recall', 'f1_score']
    
    df = df[[col for col in cols if col in df.columns]]
    
    df.to_csv(output_file, index=False)
    print(f"\n✅ Exported to: {output_file}")
    return output_file


def compare_runs(results):
    """
    Compare confusion matrix metrics across multiple runs
    """
    if not results or len(results) < 2:
        print("Need at least 2 runs to compare")
        return
    
    print("\n" + "="*80)
    print("COMPARISON OF RUNS")
    print("="*80)
    
    # Create comparison DataFrame
    compare_data = []
    for result in results:
        compare_data.append({
            'Run Name': result['run_name'],
            'TP': result['true_positives'],
            'FP': result['false_positives'],
            'TN': result['true_negatives'],
            'FN': result['false_negatives'],
            'Precision': result['precision'],
            'Recall': result['recall'],
            'F1': result['f1_score']
        })
    
    df = pd.DataFrame(compare_data)
    
    # Display formatted comparison
    print("\n" + df.to_string(index=False))
    
    # Best run analysis
    print("\n📈 Best Performers:")
    if 'Precision' in df.columns and df['Precision'].notna().any():
        best_precision = df.loc[df['Precision'].idxmax()]
        print(f"   Highest Precision: {best_precision['Run Name']} ({best_precision['Precision']:.4f})")
    
    if 'Recall' in df.columns and df['Recall'].notna().any():
        best_recall = df.loc[df['Recall'].idxmax()]
        print(f"   Highest Recall: {best_recall['Run Name']} ({best_recall['Recall']:.4f})")
    
    if 'F1' in df.columns and df['F1'].notna().any():
        best_f1 = df.loc[df['F1'].idxmax()]
        print(f"   Best F1 Score: {best_f1['Run Name']} ({best_f1['F1']:.4f})")
    
    # Error analysis
    if all(col in df.columns for col in ['FP', 'FN']):
        print("\n⚠️  Error Analysis:")
        lowest_fp = df.loc[df['FP'].idxmin()]
        print(f"   Lowest False Positives (best at avoiding incorrect merges): {lowest_fp['Run Name']} ({lowest_fp['FP']})")
        lowest_fn = df.loc[df['FN'].idxmin()]
        print(f"   Lowest False Negatives (best at finding duplicates): {lowest_fn['Run Name']} ({lowest_fn['FN']})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='View Confusion Matrix Metrics from MLflow')
    parser.add_argument('--run-id', type=str, help='Specific run ID to view')
    parser.add_argument('--experiment', type=str, default='smart/golden_record/baseline_v1',
                       help='Experiment name')
    parser.add_argument('--latest', action='store_true', help='Show only latest successful run')
    parser.add_argument('--all', action='store_true', help='Show all successful runs')
    parser.add_argument('--compare', action='store_true', help='Compare multiple runs')
    parser.add_argument('--export', type=str, help='Export to CSV file')
    
    args = parser.parse_args()
    
    print("📊 MLflow Confusion Matrix Viewer")
    print("="*80)
    
    # Get metrics
    if args.latest:
        results = get_confusion_matrix_metrics(run_id=args.run_id, 
                                               experiment_name=args.experiment,
                                               latest_only=True)
    elif args.all:
        results = get_confusion_matrix_metrics(run_id=args.run_id,
                                               experiment_name=args.experiment,
                                               latest_only=False)
    else:
        # Default: latest only
        results = get_confusion_matrix_metrics(run_id=args.run_id,
                                               experiment_name=args.experiment,
                                               latest_only=True)
    
    if results:
        # Display results
        display_confusion_matrix_table(results)
        
        # Compare if requested
        if args.compare and len(results) > 1:
            compare_runs(results)
        
        # Export if requested
        if args.export:
            export_to_csv(results, args.export)
    else:
        print("\n❌ No results found")
        print("\nTroubleshooting:")
        print("1. Make sure MLflow UI is running: http://127.0.0.1:5000")
        print("2. Check if you have any successful training runs")
        print("3. Verify experiment name is correct")
        print("\nTo view all runs:")
        print("  python view_confusion_matrix.py --all")

