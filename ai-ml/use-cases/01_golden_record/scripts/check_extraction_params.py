"""
Quick script to check all extraction parameters and data sources
"""

import yaml
from pathlib import Path
import sys

def load_config_file(config_path):
    """Load YAML configuration file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def check_data_sources():
    """Check data sources configuration"""
    config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    config = load_config_file(config_path)
    
    print_section("DATA SOURCES")
    
    print("\n📊 Primary Data Sources:")
    sources = config.get('data_sources', {})
    
    for source_name, source_config in sources.items():
        enabled = "✅ Enabled" if source_config.get('enabled', False) else "❌ Disabled"
        priority = source_config.get('priority', 'N/A')
        table = source_config.get('table', 'N/A')
        
        print(f"\n  • {source_name.upper()}")
        print(f"    Status: {enabled}")
        print(f"    Priority: {priority}")
        if table != 'N/A':
            print(f"    Table: {table}")
    
    print("\n📋 Database Configuration:")
    db = config.get('database', {})
    print(f"  Host: {db.get('host', 'N/A')}")
    print(f"  Port: {db.get('port', 'N/A')}")
    print(f"  Database: {db.get('dbname', 'N/A')}")
    print(f"  Schema: {db.get('schema', 'N/A')}")

def check_extraction_parameters():
    """Check extraction parameters"""
    config_path = Path(__file__).parent.parent / "config" / "model_config.yaml"
    config = load_config_file(config_path)
    
    print_section("EXTRACTION PARAMETERS")
    
    # Deduplication parameters
    dedup = config.get('deduplication', {})
    print("\n🔍 Deduplication Parameters:")
    print(f"  Model Type: {dedup.get('model_type', 'N/A')}")
    
    thresholds = dedup.get('thresholds', {})
    print(f"\n  Thresholds:")
    print(f"    Auto Merge:      ≥ {thresholds.get('auto_merge', 0.95)*100:.0f}% confidence")
    print(f"    Manual Review:   {thresholds.get('manual_review', 0.80)*100:.0f}% - {thresholds.get('auto_merge', 0.95)*100:.0f}% confidence")
    print(f"    Reject:          < {thresholds.get('reject', 0.80)*100:.0f}% confidence")
    
    # Features
    features = dedup.get('features', [])
    print(f"\n  Feature Weights:")
    total_weight = 0
    for feature in features:
        name = feature.get('name', 'N/A')
        weight = feature.get('weight', 0)
        algorithm = feature.get('algorithm', 'N/A')
        total_weight += weight
        print(f"    • {name:25s} | Weight: {weight*100:5.1f}% | Algorithm: {algorithm}")
    print(f"    {'Total Weight':25s} | Weight: {total_weight*100:5.1f}%")

def check_feature_engineering():
    """Check feature engineering configuration"""
    config_path = Path(__file__).parent.parent / "config" / "feature_config.yaml"
    config = load_config_file(config_path)
    
    print_section("FEATURE ENGINEERING")
    
    attributes = config.get('attributes', {})
    
    for category, attrs in attributes.items():
        print(f"\n📌 {category.upper()} Attributes:")
        total_weight = 0
        for attr in attrs:
            name = attr.get('name', 'N/A')
            method = attr.get('matching_method', 'N/A')
            weight = attr.get('weight', 0)
            total_weight += weight
            tolerance = attr.get('threshold_percent', attr.get('tolerance_years', 'N/A'))
            print(f"    • {name:20s} | Method: {method:20s} | Weight: {weight*100:5.1f}% | Tolerance: {tolerance}")
        print(f"    {'Category Total':20s} | Weight: {total_weight*100:5.1f}%")

def check_conflict_reconciliation():
    """Check conflict reconciliation parameters"""
    config_path = Path(__file__).parent.parent / "config" / "model_config.yaml"
    config = load_config_file(config_path)
    
    print_section("CONFLICT RECONCILIATION")
    
    conflict = config.get('conflict_reconciliation', {})
    print(f"\n🤝 Model Type: {conflict.get('model_type', 'N/A')}")
    
    params = conflict.get('params', {})
    print(f"\n  Model Parameters:")
    print(f"    N Estimators: {params.get('n_estimators', 'N/A')}")
    print(f"    Max Depth:    {params.get('max_depth', 'N/A')}")
    print(f"    Learning Rate: {params.get('learning_rate', 'N/A')}")
    
    ranking = conflict.get('ranking_factors', {})
    print(f"\n  Ranking Factors:")
    
    recency = ranking.get('recency', {})
    print(f"    • Recency Weight:        {recency.get('weight', 0)*100:.1f}%")
    print(f"      Max Age:               {recency.get('max_age_days', 'N/A')} days")
    
    source_auth = ranking.get('source_authority', {})
    weights = source_auth.get('weights', {})
    print(f"\n    • Source Authority Weights:")
    for source, weight in sorted(weights.items(), key=lambda x: x[1], reverse=True):
        print(f"      - {source:25s}: {weight}")
    
    completeness = ranking.get('completeness', {})
    print(f"\n    • Completeness Weight:   {completeness.get('weight', 0)*100:.1f}%")
    print(f"      Min Completeness:      {completeness.get('min_completeness', 0)*100:.0f}%")

def check_source_authority():
    """Check source authority hierarchy"""
    config_path = Path(__file__).parent.parent / "config" / "feature_config.yaml"
    config = load_config_file(config_path)
    
    print_section("SOURCE AUTHORITY HIERARCHY")
    
    source_auth = config.get('source_authority', {})
    
    print("\n📊 Authority Scores (Higher = More Trusted):")
    sorted_sources = sorted(source_auth.items(), key=lambda x: x[1], reverse=True)
    for source, score in sorted_sources:
        bar = "█" * int(score)
        print(f"  {source:30s} | {score:4.1f} | {bar}")

def check_best_truth_selection():
    """Check best truth selection parameters"""
    config_path = Path(__file__).parent.parent / "config" / "model_config.yaml"
    config = load_config_file(config_path)
    
    print_section("BEST TRUTH SELECTION")
    
    best_truth = config.get('best_truth_selection', {})
    print(f"\n🎯 Model Type: {best_truth.get('model_type', 'N/A')}")
    print(f"   Retrain Frequency: {best_truth.get('retrain_frequency', 'N/A')}")
    print(f"   Staleness Threshold: {best_truth.get('staleness_threshold_days', 'N/A')} days")
    
    rules = best_truth.get('rule_based', {})
    priority = rules.get('source_priority', [])
    print(f"\n   Source Priority (Rule-Based):")
    for i, source in enumerate(priority, 1):
        print(f"     {i}. {source}")

def main():
    """Main function to check all parameters"""
    print("\n" + "="*80)
    print("  GOLDEN RECORD EXTRACTION - PARAMETER CHECK")
    print("="*80)
    print("\nThis script displays all parameters and data sources used for")
    print("Golden Record extraction.\n")
    
    try:
        check_data_sources()
        check_extraction_parameters()
        check_feature_engineering()
        check_conflict_reconciliation()
        check_source_authority()
        check_best_truth_selection()
        
        print("\n" + "="*80)
        print("  ✅ Parameter Check Complete")
        print("="*80)
        print("\nFor detailed design documentation, see:")
        print("  docs/GOLDEN_RECORD_EXTRACTION_DESIGN.md\n")
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: Configuration file not found: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

