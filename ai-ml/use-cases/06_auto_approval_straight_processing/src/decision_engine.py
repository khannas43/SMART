"""
Decision Engine
Main orchestrator for evaluating applications and making approval decisions
Use Case ID: AI-PLATFORM-06
"""

from typing import Dict, Any, Optional
from datetime import datetime
import sys
from pathlib import Path
import yaml
import json

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class DecisionEngine:
    """Main orchestrator for decision evaluation workflow"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Decision Engine"""
        if config_path is None:
            base_dir = Path(__file__).parent.parent
            config_path = base_dir / "config" / "db_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize database connections
        db_config = self.config['database']
        self.db = DBConnector(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['name'],
            user=db_config['user'],
            password=db_config['password']
        )
        
        # External database connections
        self.external_dbs = {}
        for name, ext_config in self.config.get('external_databases', {}).items():
            self.external_dbs[name] = DBConnector(
                host=ext_config['host'],
                port=ext_config['port'],
                database=ext_config['name'],
                user=ext_config['user'],
                password=ext_config['password']
            )
        
        # Load use case config
        use_case_config_path = Path(config_path).parent / "use_case_config.yaml"
        if use_case_config_path.exists():
            with open(use_case_config_path, 'r') as f:
                self.use_case_config = yaml.safe_load(f)
        else:
            self.use_case_config = {}
        
        # Initialize sub-engines (will be imported when needed to avoid circular imports)
        self.rule_engine = None
        self.risk_scorer = None
        self.decision_router = None
        self._engines_initialized = False
    
    def connect(self):
        """Connect to all databases"""
        self.db.connect()
        for ext_db in self.external_dbs.values():
            ext_db.connect()
        
        # Initialize and connect sub-engines
        if not self._engines_initialized:
            self._initialize_engines()
        
        self.rule_engine.connect()
        self.risk_scorer.connect()
        self.decision_router.connect()
    
    def _initialize_engines(self):
        """Initialize sub-engines (lazy loading to avoid import issues)"""
        if self._engines_initialized:
            return
        
        base_dir = Path(__file__).parent.parent
        config_path = base_dir / "config" / "db_config.yaml"
        
        # Import sub-engines
        sys.path.insert(0, str(Path(__file__).parent))
        from engines.rule_engine import RuleEngine
        from models.risk_scorer import RiskScorer
        from engines.decision_router import DecisionRouter
        
        self.rule_engine = RuleEngine(str(config_path))
        self.risk_scorer = RiskScorer(str(config_path))
        self.decision_router = DecisionRouter(str(config_path))
        self._engines_initialized = True
    
    def disconnect(self):
        """Disconnect from all databases"""
        self.db.disconnect()
        for ext_db in self.external_dbs.values():
            ext_db.disconnect()
        
        # Disconnect sub-engines
        if self._engines_initialized:
            self.rule_engine.disconnect()
            self.risk_scorer.disconnect()
            self.decision_router.disconnect()
    
    def evaluate_application(
        self,
        application_id: int,
        family_id: Optional[str] = None,
        scheme_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate an application and make a decision
        
        Args:
            application_id: Application ID from AI-PLATFORM-05
            family_id: Family ID (optional, fetched if not provided)
            scheme_code: Scheme code (optional, fetched if not provided)
        
        Returns:
            Decision result with decision_type, risk_score, reasons, etc.
        """
        print(f"\n🔄 Evaluating application ID: {application_id}")
        
        # Ensure engines are initialized
        if not self._engines_initialized:
            self._initialize_engines()
        
        try:
            # Step 1: Fetch application details
            application_data = self._fetch_application(application_id)
            if not application_data:
                return {
                    'success': False,
                    'error': 'Application not found',
                    'application_id': application_id
                }
            
            family_id = family_id or application_data['family_id']
            scheme_code = scheme_code or application_data['scheme_code']
            
            # Step 2: Load decision configuration
            decision_config = self._load_decision_config(scheme_code)
            
            # Step 3: Rule-based evaluation
            rule_results = self._evaluate_rules(application_id, family_id, scheme_code)
            
            # Step 4: Risk scoring
            risk_results = self._calculate_risk_score(application_id, family_id, scheme_code)
            
            # Step 5: Make decision
            decision = self._make_decision(
                application_id,
                family_id,
                scheme_code,
                rule_results,
                risk_results,
                decision_config
            )
            
            # Step 6: Save decision
            decision_id = self._save_decision(application_id, family_id, scheme_code, decision, rule_results, risk_results)
            
            # Step 7: Save rule evaluations
            self.rule_engine.save_rule_evaluations(decision_id, rule_results['evaluations'])
            
            # Step 8: Route decision (trigger payment, route to officer, etc.)
            routing_result = self.decision_router.route_decision(decision_id, decision, application_id)
            
            return {
                'success': True,
                'decision_id': decision_id,
                'decision': decision,
                'rule_results': rule_results,
                'risk_results': risk_results,
                'routing': routing_result
            }
            
        except Exception as e:
            print(f"❌ Decision evaluation failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'application_id': application_id
            }
    
    def _fetch_application(self, application_id: int) -> Optional[Dict[str, Any]]:
        """Fetch application details from application schema"""
        conn = self.external_dbs['application'].connection
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                application_id, family_id, member_id, scheme_code,
                status, submission_mode, eligibility_score, eligibility_status
            FROM application.applications
            WHERE application_id = %s
        """, (application_id,))
        
        row = cursor.fetchone()
        cursor.close()
        
        if not row:
            return None
        
        return {
            'application_id': row[0],
            'family_id': row[1],
            'member_id': row[2],
            'scheme_code': row[3],
            'status': row[4],
            'submission_mode': row[5],
            'eligibility_score': row[6],
            'eligibility_status': row[7]
        }
    
    def _load_decision_config(self, scheme_code: str) -> Dict[str, Any]:
        """Load decision configuration for scheme"""
        conn = self.db.connection
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                low_risk_max, medium_risk_min, medium_risk_max, high_risk_min,
                enable_auto_approval, require_document_verification,
                route_medium_risk_to_officer, route_high_risk_to_fraud,
                require_human_review_medium, require_human_review_high,
                auto_reject_rules, mandatory_checks
            FROM decision.decision_config
            WHERE scheme_code = %s AND is_active = true
            ORDER BY effective_from DESC
            LIMIT 1
        """, (scheme_code,))
        
        row = cursor.fetchone()
        cursor.close()
        
        if row:
            return {
                'low_risk_max': float(row[0]),
                'medium_risk_min': float(row[1]),
                'medium_risk_max': float(row[2]),
                'high_risk_min': float(row[3]),
                'enable_auto_approval': row[4],
                'require_document_verification': row[5],
                'route_medium_risk_to_officer': row[6],
                'route_high_risk_to_fraud': row[7],
                'require_human_review_medium': row[8],
                'require_human_review_high': row[9],
                'auto_reject_rules': row[10] or [],
                'mandatory_checks': row[11] or []
            }
        
        # Return defaults if no config found
        default_thresholds = self.use_case_config.get('decision', {}).get('default_risk_thresholds', {})
        return {
            'low_risk_max': default_thresholds.get('low_risk_max', 0.3),
            'medium_risk_min': default_thresholds.get('medium_risk_min', 0.3),
            'medium_risk_max': default_thresholds.get('medium_risk_max', 0.7),
            'high_risk_min': default_thresholds.get('high_risk_min', 0.7),
            'enable_auto_approval': True,
            'require_document_verification': True,
            'route_medium_risk_to_officer': True,
            'route_high_risk_to_fraud': True,
            'require_human_review_medium': True,
            'require_human_review_high': True,
            'auto_reject_rules': [],
            'mandatory_checks': []
        }
    
    def _evaluate_rules(self, application_id: int, family_id: str, scheme_code: str) -> Dict[str, Any]:
        """Evaluate rule-based checks using RuleEngine"""
        return self.rule_engine.evaluate_rules(application_id, family_id, scheme_code)
    
    def _calculate_risk_score(self, application_id: int, family_id: str, scheme_code: str) -> Dict[str, Any]:
        """Calculate risk score using RiskScorer"""
        return self.risk_scorer.calculate_risk_score(application_id, family_id, scheme_code)
    
    def _make_decision(
        self,
        application_id: int,
        family_id: str,
        scheme_code: str,
        rule_results: Dict[str, Any],
        risk_results: Dict[str, Any],
        decision_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make decision based on rules and risk score"""
        
        risk_score = risk_results['risk_score']
        rules_passed = rule_results.get('all_passed', False)
        critical_failures = rule_results.get('critical_failures', [])
        
        # Auto reject on critical failures
        if critical_failures:
            return {
                'decision_type': 'AUTO_REJECT',
                'decision_status': 'rejected',
                'reason': f"Critical rule failures: {', '.join(critical_failures)}",
                'risk_score': risk_score,
                'risk_band': risk_results['risk_band']
            }
        
        # Rules didn't pass - route to officer
        if not rules_passed:
            return {
                'decision_type': 'ROUTE_TO_OFFICER',
                'decision_status': 'under_review',
                'reason': 'Some eligibility checks failed',
                'risk_score': risk_score,
                'risk_band': risk_results['risk_band']
            }
        
        # Determine risk band
        if risk_score <= decision_config['low_risk_max']:
            risk_band = 'LOW'
        elif risk_score <= decision_config['medium_risk_max']:
            risk_band = 'MEDIUM'
        else:
            risk_band = 'HIGH'
        
        # Make decision based on risk band and configuration
        if risk_band == 'LOW' and decision_config['enable_auto_approval']:
            return {
                'decision_type': 'AUTO_APPROVE',
                'decision_status': 'approved',
                'reason': 'Low risk, rules passed, auto-approved',
                'risk_score': risk_score,
                'risk_band': risk_band
            }
        elif risk_band == 'MEDIUM':
            if decision_config['require_human_review_medium']:
                return {
                    'decision_type': 'ROUTE_TO_OFFICER',
                    'decision_status': 'under_review',
                    'reason': 'Medium risk, requires officer review',
                    'risk_score': risk_score,
                    'risk_band': risk_band
                }
            else:
                return {
                    'decision_type': 'AUTO_APPROVE',
                    'decision_status': 'approved',
                    'reason': 'Medium risk but auto-approval allowed',
                    'risk_score': risk_score,
                    'risk_band': risk_band
                }
        else:  # HIGH risk
            if decision_config['route_high_risk_to_fraud']:
                return {
                    'decision_type': 'ROUTE_TO_FRAUD',
                    'decision_status': 'under_review',
                    'reason': 'High risk, routed to fraud queue',
                    'risk_score': risk_score,
                    'risk_band': risk_band
                }
            else:
                return {
                    'decision_type': 'ROUTE_TO_OFFICER',
                    'decision_status': 'under_review',
                    'reason': 'High risk, requires officer review',
                    'risk_score': risk_score,
                    'risk_band': risk_band
                }
    
    def _save_decision(
        self,
        application_id: int,
        family_id: str,
        scheme_code: str,
        decision: Dict[str, Any],
        rule_results: Dict[str, Any],
        risk_results: Dict[str, Any]
    ) -> int:
        """Save decision to database"""
        conn = self.db.connection
        cursor = conn.cursor()
        
        # Insert decision
        cursor.execute("""
            INSERT INTO decision.decisions (
                application_id, family_id, scheme_code,
                decision_type, decision_status,
                risk_score, risk_band, risk_factors,
                rules_passed, rules_failed_count, critical_rules_failed,
                routing_reason, decision_by,
                model_version, model_type, thresholds_used
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING decision_id
        """, (
            application_id,
            family_id,
            scheme_code,
            decision['decision_type'],
            decision['decision_status'],
            decision['risk_score'],
            decision['risk_band'],
            json.dumps(risk_results.get('top_factors', [])),
            rule_results.get('all_passed', False),
            rule_results.get('failed_count', 0),
            rule_results.get('critical_failures', []),
            decision.get('reason', ''),
            'decision_engine',
            risk_results.get('model_version', 'N/A'),
            risk_results.get('model_type', 'N/A'),
            json.dumps({})  # thresholds_used
        ))
        
        decision_id = cursor.fetchone()[0]
        
        # Save risk score
        cursor.execute("""
            INSERT INTO decision.risk_scores (
                decision_id, overall_score, score_band,
                feature_contributions, top_risk_factors,
                model_version, model_type,
                input_features
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            decision_id,
            decision['risk_score'],
            decision['risk_band'],
            json.dumps({}),
            risk_results.get('top_factors', []),
            risk_results.get('model_version', 'N/A'),
            risk_results.get('model_type', 'N/A'),
            json.dumps({})
        ))
        
        conn.commit()
        cursor.close()
        
        return decision_id
    


