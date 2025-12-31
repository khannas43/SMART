"""
Anomaly Detection for Benefit Analytics
Detects over-concentration and under-coverage
Use Case: AI-PLATFORM-02
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yaml
import json

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class AnomalyDetector:
    """Detect anomalies in benefit distribution"""
    
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "model_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Database connection
        db_config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
        with open(db_config_path, 'r') as f:
            db_config = yaml.safe_load(f)['database']
        
        self.db = DBConnector(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['dbname'],
            user=db_config['user'],
            password=db_config['password']
        )
        self.db.connect()
        
        # Anomaly config
        self.anomaly_config = self.config['anomaly_detection']
    
    def detect_over_concentration(self):
        """Detect over-concentration of benefits"""
        print("Detecting over-concentration...")
        
        # Load benefit summaries
        query = """
        SELECT 
            p.gr_id,
            p.inferred_income_band,
            COALESCE(ABS.benefit_total_3y, 0) as benefit_total_3y,
            COALESCE(ABS.scheme_count, 0) as scheme_count,
            gr.district_id,
            p.cluster_id
        FROM profile_360 p
        JOIN golden_records gr ON p.gr_id = gr.gr_id
        LEFT JOIN analytics_benefit_summary ABS ON p.gr_id = ABS.gr_id 
            AND ABS.time_window = 'LAST_3Y'
        WHERE p.inferred_income_band IS NOT NULL
        """
        
        df = self.db.execute_query(query)
        
        if len(df) == 0:
            print("⚠️  No data found for over-concentration detection")
            return []
        
        flags = []
        rules_config = self.anomaly_config['over_concentration']['rules']
        
        # Calculate local averages by district and income band
        district_avg = df.groupby(['district_id', 'inferred_income_band'])['benefit_total_3y'].mean()
        
        for _, row in df.iterrows():
            gr_id = row['gr_id']
            benefit_total = row['benefit_total_3y']
            scheme_count = row['scheme_count']
            district_id = row['district_id']
            income_band = row['inferred_income_band']
            
            # Get local average
            local_avg = district_avg.get((district_id, income_band), df['benefit_total_3y'].mean())
            
            # Rule 1: Benefit vs local average
            if local_avg > 0 and benefit_total > local_avg * rules_config['benefit_vs_local_avg_multiplier']:
                flags.append({
                    'gr_id': gr_id,
                    'flag_type': 'OVER_CONCENTRATION',
                    'flag_severity': 'HIGH' if benefit_total > local_avg * 5 else 'MEDIUM',
                    'flag_score': min(1.0, (benefit_total / local_avg) / 10.0),
                    'flag_explanation': f"Benefit amount ({benefit_total:,.0f}) is {benefit_total/local_avg:.1f}x the local average ({local_avg:,.0f}) for {income_band} income band in district {district_id}",
                    'district_id': district_id,
                    'trigger_metrics': {
                        'benefit_amount': float(benefit_total),
                        'local_average': float(local_avg),
                        'multiplier': float(benefit_total / local_avg)
                    }
                })
            
            # Rule 2: Too many schemes
            if scheme_count > rules_config['schemes_count_threshold']:
                flags.append({
                    'gr_id': gr_id,
                    'flag_type': 'POSSIBLE_LEAKAGE',
                    'flag_severity': 'MEDIUM',
                    'flag_score': min(1.0, scheme_count / 15.0),
                    'flag_explanation': f"Enrolled in {scheme_count} schemes, which exceeds threshold of {rules_config['schemes_count_threshold']}",
                    'district_id': district_id,
                    'trigger_metrics': {
                        'schemes_count': int(scheme_count),
                        'threshold': rules_config['schemes_count_threshold']
                    }
                })
        
        # ML-based detection using Isolation Forest
        if len(df) > 100:  # Need sufficient data
            features = df[['benefit_total_3y', 'scheme_count']].fillna(0)
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            iso_config = self.anomaly_config['over_concentration']
            iso_forest = IsolationForest(
                contamination=iso_config['contamination'],
                n_estimators=iso_config['n_estimators'],
                max_samples=iso_config['max_samples'],
                random_state=42
            )
            
            outliers = iso_forest.fit_predict(features_scaled)
            
            for idx, (_, row) in enumerate(df.iterrows()):
                if outliers[idx] == -1:  # Anomaly detected
                    # Check if already flagged
                    if not any(f['gr_id'] == row['gr_id'] and f['flag_type'] == 'OVER_CONCENTRATION' for f in flags):
                        flags.append({
                            'gr_id': row['gr_id'],
                            'flag_type': 'OVER_CONCENTRATION',
                            'flag_severity': 'MEDIUM',
                            'flag_score': 0.75,  # ML-detected anomaly
                            'flag_explanation': f"ML model detected unusual benefit pattern: {row['benefit_total_3y']:,.0f} benefits, {row['scheme_count']} schemes",
                            'district_id': row['district_id'],
                            'trigger_metrics': {
                                'benefit_amount': float(row['benefit_total_3y']),
                                'schemes_count': int(row['scheme_count']),
                                'detection_method': 'isolation_forest'
                            }
                        })
        
        print(f"✅ Detected {len(flags)} over-concentration flags")
        return flags
    
    def detect_under_coverage(self):
        """Detect under-coverage (eligible but not receiving benefits)"""
        print("Detecting under-coverage...")
        
        under_coverage_config = self.anomaly_config['under_coverage']
        
        # Load eligibility data
        query = """
        SELECT 
            p.gr_id,
            p.inferred_income_band,
            p.cluster_id,
            gr.district_id,
            COALESCE(ABS.benefit_total_1y, 0) as benefit_total_1y,
            COALESCE(ABS.scheme_count, 0) as scheme_count,
            ae.eligibility_probability,
            ae.eligibility_score
        FROM profile_360 p
        JOIN golden_records gr ON p.gr_id = gr.gr_id
        LEFT JOIN analytics_benefit_summary ABS ON p.gr_id = ABS.gr_id 
            AND ABS.time_window = 'LAST_1Y'
        LEFT JOIN LATERAL (
            SELECT eligibility_probability, eligibility_score
            FROM application_events ae
            WHERE ae.gr_id = p.gr_id
            ORDER BY ae.application_date DESC
            LIMIT 1
        ) ae ON true
        WHERE p.inferred_income_band IN ('VERY_LOW', 'LOW')
        """
        
        df = self.db.execute_query(query)
        
        if len(df) == 0:
            print("⚠️  No data found for under-coverage detection")
            return []
        
        flags = []
        
        # Get cluster averages
        cluster_avg = df.groupby('cluster_id')['benefit_total_1y'].mean()
        
        for _, row in df.iterrows():
            gr_id = row['gr_id']
            benefit_total = row['benefit_total_1y']
            scheme_count = row['scheme_count']
            eligibility_prob = row['eligibility_probability']
            cluster_id = row['cluster_id']
            
            # Check eligibility threshold
            if pd.notna(eligibility_prob) and eligibility_prob >= under_coverage_config['eligibility_threshold']:
                # Check if receiving benefits
                if benefit_total <= under_coverage_config['benefit_threshold']:
                    cluster_avg_benefit = cluster_avg.get(cluster_id, 0) if cluster_id else 0
                    
                    flags.append({
                        'gr_id': gr_id,
                        'flag_type': 'UNDER_COVERAGE',
                        'flag_severity': 'HIGH' if eligibility_prob > 0.9 else 'MEDIUM',
                        'flag_score': float(eligibility_prob),
                        'flag_explanation': f"High eligibility probability ({eligibility_prob:.2f}) but receiving no/low benefits. Cluster average: {cluster_avg_benefit:,.0f}",
                        'district_id': row['district_id'],
                        'trigger_metrics': {
                            'eligibility_probability': float(eligibility_prob),
                            'benefit_amount': float(benefit_total),
                            'cluster_average': float(cluster_avg_benefit),
                            'schemes_count': int(scheme_count)
                        }
                    })
        
        # Priority vulnerable: Very low income + no benefits
        very_low_income = df[df['inferred_income_band'] == 'VERY_LOW']
        for _, row in very_low_income.iterrows():
            if row['benefit_total_1y'] == 0 and row['scheme_count'] == 0:
                flags.append({
                    'gr_id': row['gr_id'],
                    'flag_type': 'PRIORITY_VULNERABLE',
                    'flag_severity': 'HIGH',
                    'flag_score': 0.95,
                    'flag_explanation': "Very low income band with no benefits or schemes. Priority for outreach.",
                    'district_id': row['district_id'],
                    'trigger_metrics': {
                        'income_band': row['inferred_income_band'],
                        'benefit_amount': 0,
                        'schemes_count': 0
                    }
                })
        
        print(f"✅ Detected {len(flags)} under-coverage flags")
        return flags
    
    def save_flags(self, flags):
        """Save flags to database"""
        if len(flags) == 0:
            return
        
        print(f"Saving {len(flags)} flags to database...")
        
        cursor = self.db.connection.cursor()
        
        for flag in flags:
            insert_query = """
            INSERT INTO analytics_flags (
                gr_id, flag_type, flag_severity, flag_score, 
                flag_explanation, district_id, trigger_metrics,
                flagged_at, flag_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s, 'ACTIVE')
            ON CONFLICT DO NOTHING
            """
            
            cursor.execute(
                insert_query,
                (
                    flag['gr_id'],
                    flag['flag_type'],
                    flag['flag_severity'],
                    flag['flag_score'],
                    flag['flag_explanation'],
                    flag.get('district_id'),
                    json.dumps(flag['trigger_metrics']) if 'trigger_metrics' in flag else None,
                    datetime.now(),
                    'ACTIVE'
                )
            )
        
        self.db.connection.commit()
        cursor.close()
        
        print(f"✅ Saved {len(flags)} flags")
    
    def run(self):
        """Run complete anomaly detection pipeline"""
        print("="*80)
        print("Anomaly Detection Pipeline")
        print("="*80)
        print()
        
        # Detect over-concentration
        over_flags = self.detect_over_concentration()
        
        # Detect under-coverage
        under_flags = self.detect_under_coverage()
        
        # Combine flags
        all_flags = over_flags + under_flags
        
        # Save to database
        if all_flags:
            self.save_flags(all_flags)
        
        # Summary
        flag_summary = {}
        for flag in all_flags:
            flag_type = flag['flag_type']
            flag_summary[flag_type] = flag_summary.get(flag_type, 0) + 1
        
        print("\n" + "="*80)
        print("✅ Anomaly detection completed!")
        print("\nFlag Summary:")
        for flag_type, count in flag_summary.items():
            print(f"  {flag_type}: {count}")
        print("="*80)
        
        return all_flags
    
    def close(self):
        """Close database connection"""
        if self.db:
            self.db.disconnect()


def main():
    """Main function"""
    import json
    detector = AnomalyDetector()
    
    try:
        flags = detector.run()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        detector.close()


if __name__ == "__main__":
    main()

