"""
Profile 360° Recompute Service
Orchestrates profile updates and recomputation
Use Case: AI-PLATFORM-02
"""

import sys
from pathlib import Path
import pandas as pd
import json
from datetime import datetime
import yaml
import time
from uuid import UUID

# Add paths
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector

# Import ML models (from same src directory)
from income_band_predict import IncomeBandPredictor
# Use Neo4j version for graph clustering
try:
    from graph_clustering_neo4j import GraphClusteringNeo4j as GraphClustering
except ImportError:
    # Fallback to NetworkX if Neo4j not available
    from graph_clustering import GraphClustering


class ProfileRecomputeService:
    """Service to recompute 360° profiles"""
    
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
        
        with open(config_path, 'r') as f:
            db_config = yaml.safe_load(f)['database']
        
        self.db = DBConnector(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['dbname'],
            user=db_config['user'],
            password=db_config['password']
        )
        self.db.connect()
        
        # Load ML models
        self.income_predictor = IncomeBandPredictor()
        
    def get_gr_data(self, gr_id):
        """Get all data for a Golden Record"""
        # Get basic GR data
        gr_query = "SELECT * FROM golden_records WHERE gr_id = %s"
        gr_df = self.db.execute_query(gr_query, params=(str(gr_id),))
        if len(gr_df) == 0:
            return None
        gr_data = gr_df.iloc[0]
        
        # Get relationships
        rel_query = """
        SELECT * FROM gr_relationships 
        WHERE from_gr_id = %s OR to_gr_id = %s
        """
        relationships = self.db.execute_query(rel_query, params=(str(gr_id), str(gr_id)))
        
        # Get benefits
        benefit_query = """
        SELECT be.*, sm.scheme_code, sm.scheme_name, sm.category
        FROM benefit_events be
        JOIN scheme_master sm ON be.scheme_id = sm.scheme_id
        WHERE be.gr_id = %s
        ORDER BY be.txn_date DESC
        """
        benefits = self.db.execute_query(benefit_query, params=(str(gr_id),))
        
        # Get applications
        app_query = """
        SELECT ae.*, sm.scheme_code, sm.scheme_name
        FROM application_events ae
        JOIN scheme_master sm ON ae.scheme_id = sm.scheme_id
        WHERE ae.gr_id = %s
        ORDER BY ae.application_date DESC
        """
        applications = self.db.execute_query(app_query, params=(str(gr_id),))
        
        # Get socio-economic
        socio_query = "SELECT * FROM socio_economic_facts WHERE gr_id = %s ORDER BY as_of_date DESC LIMIT 1"
        socio = self.db.execute_query(socio_query, params=(str(gr_id),))
        socio_data = socio.iloc[0] if len(socio) > 0 else None
        
        # Get consent
        consent_query = "SELECT * FROM consent_flags WHERE gr_id = %s"
        consent = self.db.execute_query(consent_query, params=(str(gr_id),))
        consent_data = consent.iloc[0] if len(consent) > 0 else None
        
        return {
            'gr': gr_data.to_dict(),
            'relationships': relationships.to_dict('records'),
            'benefits': benefits.to_dict('records'),
            'applications': applications.to_dict('records'),
            'socio': socio_data.to_dict() if socio_data is not None else None,
            'consent': consent_data.to_dict() if consent_data is not None else None
        }
    
    def compute_benefit_summary(self, gr_id, data):
        """Compute benefit summaries by time window"""
        benefits = pd.DataFrame(data['benefits'])
        if len(benefits) == 0:
            return {
                'lifetime_total': 0,
                'last_1y': 0,
                'last_3y': 0,
                'last_5y': 0,
                'by_category': {}
            }
        
        benefits['txn_date'] = pd.to_datetime(benefits['txn_date'])
        now = datetime.now()
        
        # Calculate totals by time window
        lifetime_total = benefits['amount'].sum()
        last_1y = benefits[benefits['txn_date'] >= now - pd.Timedelta(days=365)]['amount'].sum()
        last_3y = benefits[benefits['txn_date'] >= now - pd.Timedelta(days=1095)]['amount'].sum()
        last_5y = benefits[benefits['txn_date'] >= now - pd.Timedelta(days=1825)]['amount'].sum()
        
        # By category
        by_category = benefits.groupby('category')['amount'].sum().to_dict()
        
        return {
            'lifetime_total': float(lifetime_total),
            'last_1y': float(last_1y),
            'last_3y': float(last_3y),
            'last_5y': float(last_5y),
            'by_category': {k: float(v) for k, v in by_category.items()},
            'scheme_count': len(benefits['scheme_id'].unique()),
            'transaction_count': len(benefits)
        }
    
    def infer_income_band(self, gr_id, data):
        """Infer income band using ML model"""
        # Check consent
        consent = data.get('consent')
        if consent and not consent.get('income_inference_consent', False):
            return None, None, "Consent not provided"
        
        try:
            income_band, confidence, error = self.income_predictor.predict(gr_id)
            return income_band, confidence, error
        except Exception as e:
            return None, None, str(e)
    
    def build_profile_json(self, gr_id, data, income_band, income_confidence):
        """Build complete 360° profile JSON"""
        gr = data['gr']
        
        # Identity section
        identity = {
            'gr_id': str(gr_id),
            'citizen_id': gr.get('citizen_id'),
            'jan_aadhaar': gr.get('jan_aadhaar'),
            'full_name': gr.get('full_name'),
            'date_of_birth': str(gr.get('date_of_birth')) if pd.notna(gr.get('date_of_birth')) else None,
            'age': int(gr.get('age')) if pd.notna(gr.get('age')) else None,
            'gender': gr.get('gender'),
            'district_id': int(gr.get('district_id')) if pd.notna(gr.get('district_id')) else None,
            'is_urban': bool(gr.get('is_urban')) if pd.notna(gr.get('is_urban')) else False
        }
        
        # Relationships section
        relationships = []
        for rel in data['relationships']:
            relationships.append({
                'to_gr_id': str(rel['to_gr_id']),
                'relationship_type': rel['relationship_type'],
                'is_verified': bool(rel.get('is_verified', False)),
                'confidence': float(rel.get('inference_confidence', 1.0)) if pd.notna(rel.get('inference_confidence')) else None
            })
        
        # Socio-economic section
        socio = data.get('socio')
        socio_economic = {
            'inferred_income_band': income_band,
            'income_band_confidence': float(income_confidence) if income_confidence else None,
            'education_level': socio.get('education_level') if socio else None,
            'employment_type': socio.get('employment_type') if socio else None,
            'house_type': socio.get('house_type') if socio else None,
            'family_size': int(socio.get('family_size')) if socio and pd.notna(socio.get('family_size')) else None
        }
        
        # Benefits section
        benefit_summary = self.compute_benefit_summary(gr_id, data)
        
        # Build complete profile
        profile = {
            'identity': identity,
            'relationships': relationships,
            'socio_economic': socio_economic,
            'benefits': benefit_summary,
            'cluster': {
                'cluster_id': None,  # Will be set by graph clustering
                'cluster_type': None
            },
            'risk_flags': [],  # Will be populated by anomaly detection
            'metadata': {
                'last_updated': datetime.now().isoformat(),
                'model_version': '1.0',
                'data_sources': ['golden_records', 'benefit_events', 'gr_relationships']
            }
        }
        
        return profile
    
    def recompute_profile(self, gr_id):
        """Recompute 360° profile for a Golden Record"""
        print(f"Recomputing profile for {gr_id}...")
        
        # Get all data
        data = self.get_gr_data(gr_id)
        if data is None:
            return False, "Golden Record not found"
        
        # Infer income band
        income_band, income_confidence, income_error = self.infer_income_band(gr_id, data)
        if income_error:
            print(f"  ⚠️  Income inference error: {income_error}")
        
        # Build profile JSON
        profile_json = self.build_profile_json(gr_id, data, income_band, income_confidence)
        
        # Get cluster_id from profile_360 if exists
        cluster_query = "SELECT cluster_id FROM profile_360 WHERE gr_id = %s"
        cluster_df = self.db.execute_query(cluster_query, params=(str(gr_id),))
        if len(cluster_df) > 0:
            profile_json['cluster']['cluster_id'] = cluster_df.iloc[0]['cluster_id']
        
        # Get risk flags
        flags_query = """
        SELECT flag_type, flag_score, flag_explanation 
        FROM analytics_flags 
        WHERE gr_id = %s AND flag_status = 'ACTIVE'
        """
        flags_df = self.db.execute_query(flags_query, params=(str(gr_id),))
        profile_json['risk_flags'] = [
            {
                'type': row['flag_type'],
                'score': float(row['flag_score']),
                'explanation': row['flag_explanation']
            }
            for _, row in flags_df.iterrows()
        ]
        
        # Save/update profile_360
        cursor = self.db.connection.cursor()
        
        # Check if profile exists
        check_query = "SELECT profile_id FROM profile_360 WHERE gr_id = %s"
        cursor.execute(check_query, (str(gr_id),))
        exists = cursor.fetchone()
        
        if exists:
            # Update
            update_query = """
            UPDATE profile_360
            SET profile_data = %s::jsonb,
                inferred_income_band = %s,
                income_band_confidence = %s,
                cluster_id = %s,
                risk_flags = %s,
                updated_at = CURRENT_TIMESTAMP,
                last_recomputed_at = CURRENT_TIMESTAMP
            WHERE gr_id = %s
            """
            cursor.execute(
                update_query,
                (
                    json.dumps(profile_json),
                    income_band,
                    income_confidence,
                    profile_json['cluster']['cluster_id'],
                    [f['type'] for f in profile_json['risk_flags']],
                    str(gr_id)
                )
            )
        else:
            # Insert
            insert_query = """
            INSERT INTO profile_360 (
                gr_id, family_id, profile_data, inferred_income_band,
                income_band_confidence, cluster_id, risk_flags,
                created_at, updated_at, last_recomputed_at
            ) VALUES (%s, %s, %s::jsonb, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """
            cursor.execute(
                insert_query,
                (
                    str(gr_id),
                    data['gr'].get('family_id'),
                    json.dumps(profile_json),
                    income_band,
                    income_confidence,
                    profile_json['cluster']['cluster_id'],
                    [f['type'] for f in profile_json['risk_flags']]
                )
            )
        
        self.db.connection.commit()
        cursor.close()
        
        print(f"  ✅ Profile recomputed successfully")
        return True, None
    
    def process_queue(self, batch_size=10):
        """Process recompute queue"""
        print("Processing recompute queue...")
        
        query = """
        SELECT queue_id, gr_id, priority
        FROM profile_recompute_queue
        WHERE status = 'PENDING'
        ORDER BY priority DESC, created_at ASC
        LIMIT %s
        FOR UPDATE SKIP LOCKED
        """
        
        cursor = self.db.connection.cursor()
        cursor.execute(query, (batch_size,))
        rows = cursor.fetchall()
        
        processed = 0
        failed = 0
        
        for row in rows:
            queue_id, gr_id, priority = row
            
            # Mark as processing
            cursor.execute(
                "UPDATE profile_recompute_queue SET status = 'PROCESSING', processing_started_at = CURRENT_TIMESTAMP WHERE queue_id = %s",
                (queue_id,)
            )
            self.db.connection.commit()
            
            try:
                # Recompute profile
                success, error = self.recompute_profile(gr_id)
                
                if success:
                    # Mark as completed
                    cursor.execute(
                        "UPDATE profile_recompute_queue SET status = 'COMPLETED', completed_at = CURRENT_TIMESTAMP WHERE queue_id = %s",
                        (queue_id,)
                    )
                    processed += 1
                else:
                    # Mark as failed
                    cursor.execute(
                        "UPDATE profile_recompute_queue SET status = 'FAILED', error_message = %s WHERE queue_id = %s",
                        (error, queue_id)
                    )
                    failed += 1
                
                self.db.connection.commit()
                
            except Exception as e:
                # Mark as failed
                cursor.execute(
                    "UPDATE profile_recompute_queue SET status = 'FAILED', error_message = %s WHERE queue_id = %s",
                    (str(e), queue_id)
                )
                self.db.connection.commit()
                failed += 1
                print(f"  ❌ Error processing {gr_id}: {e}")
        
        cursor.close()
        
        print(f"✅ Processed {processed} profiles, {failed} failed")
        return processed, failed
    
    def run_scheduler(self, interval_seconds=3600):
        """Run scheduler loop"""
        print("="*80)
        print("Profile Recompute Service - Scheduler Mode")
        print(f"Processing queue every {interval_seconds} seconds")
        print("Press Ctrl+C to stop")
        print("="*80)
        
        try:
            while True:
                self.process_queue(batch_size=50)
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n✅ Scheduler stopped")
    
    def close(self):
        """Close connections"""
        if self.income_predictor:
            self.income_predictor.close()
        if self.db:
            self.db.disconnect()


def main():
    """Main function"""
    import sys
    
    service = ProfileRecomputeService()
    
    try:
        if len(sys.argv) > 1:
            # Recompute specific GR
            gr_id = sys.argv[1]
            success, error = service.recompute_profile(gr_id)
            if not success:
                print(f"❌ Error: {error}")
        else:
            # Process queue once
            service.process_queue(batch_size=50)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        service.close()


if __name__ == "__main__":
    main()


