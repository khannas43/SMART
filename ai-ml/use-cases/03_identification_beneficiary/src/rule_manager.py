"""
Rule Management Service
Provides programmatic access to rule CRUD operations and versioning
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, date
import yaml
import json
import warnings
warnings.filterwarnings('ignore')

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class RuleManager:
    """
    Rule Management Service
    
    Provides CRUD operations for eligibility rules with version control
    """
    
    def __init__(self, config_path=None):
        """Initialize rule manager"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "use_case_config.yaml"
        
        # Database connection
        db_config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
        with open(db_config_path, 'r') as f:
            db_config = yaml.safe_load(f)['database']
        
        self.db = DBConnector(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['name'],
            user=db_config['user'],
            password=db_config['password']
        )
        self.db.connect()
    
    def create_rule(
        self,
        scheme_code: str,
        rule_name: str,
        rule_type: str,
        rule_expression: str,
        rule_operator: str,
        rule_value: str,
        is_mandatory: bool = True,
        priority: int = 0,
        effective_from: Optional[date] = None,
        effective_to: Optional[date] = None,
        created_by: str = "system"
    ) -> Dict[str, Any]:
        """
        Create a new eligibility rule
        
        Args:
            scheme_code: Scheme code (e.g., 'CHIRANJEEVI')
            rule_name: Name of the rule
            rule_type: Type (AGE, INCOME, GENDER, etc.)
            rule_expression: Rule expression
            rule_operator: Operator (>=, <=, =, IN, etc.)
            rule_value: Rule value
            is_mandatory: Whether rule is mandatory
            priority: Priority (higher = evaluated first)
            effective_from: Effective from date (default: today)
            effective_to: Effective to date (optional)
            created_by: User who created the rule
        
        Returns:
            Created rule dictionary
        """
        if effective_from is None:
            effective_from = date.today()
        
        cursor = self.db.connection.cursor()
        
        try:
            insert_query = """
                INSERT INTO eligibility.scheme_eligibility_rules (
                    scheme_code, rule_name, rule_type, rule_expression,
                    rule_operator, rule_value, is_mandatory, priority,
                    version, effective_from, effective_to
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1, %s, %s)
                RETURNING rule_id, scheme_code, rule_name, rule_type, rule_expression,
                          rule_operator, rule_value, is_mandatory, priority,
                          version, effective_from, effective_to, created_at
            """
            
            cursor.execute(insert_query, (
                scheme_code, rule_name, rule_type, rule_expression,
                rule_operator, rule_value, is_mandatory, priority,
                effective_from, effective_to
            ))
            
            result = cursor.fetchone()
            self.db.connection.commit()
            
            # Log change
            self._log_rule_change(
                result[0], scheme_code, 'CREATED', None, 
                {'rule_name': rule_name, 'rule_type': rule_type},
                created_by
            )
            
            return {
                'rule_id': result[0],
                'scheme_code': result[1],
                'rule_name': result[2],
                'rule_type': result[3],
                'rule_expression': result[4],
                'rule_operator': result[5],
                'rule_value': result[6],
                'is_mandatory': result[7],
                'priority': result[8],
                'version': result[9],
                'effective_from': result[10].isoformat() if result[10] else None,
                'effective_to': result[11].isoformat() if result[11] else None,
                'created_at': result[12].isoformat() if result[12] else None
            }
        
        except Exception as e:
            # Rollback on error to allow subsequent operations
            self.db.connection.rollback()
            raise
        finally:
            cursor.close()
    
    def update_rule(
        self,
        rule_id: int,
        rule_name: Optional[str] = None,
        rule_type: Optional[str] = None,
        rule_expression: Optional[str] = None,
        rule_operator: Optional[str] = None,
        rule_value: Optional[str] = None,
        is_mandatory: Optional[bool] = None,
        priority: Optional[int] = None,
        effective_from: Optional[date] = None,
        effective_to: Optional[date] = None,
        updated_by: str = "system"
    ) -> Dict[str, Any]:
        """
        Update an existing rule (creates new version)
        
        Args:
            rule_id: Rule ID
            updated_by: User who updated the rule
            Other args: Fields to update (None = no change)
        
        Returns:
            Updated rule dictionary
        """
        cursor = self.db.connection.cursor()
        
        try:
            # Get current rule
            cursor.execute("""
                SELECT scheme_code, version FROM eligibility.scheme_eligibility_rules
                WHERE rule_id = %s
            """, (rule_id,))
            
            current = cursor.fetchone()
            if not current:
                raise ValueError(f"Rule {rule_id} not found")
            
            scheme_code, current_version = current
            new_version = current_version + 1
            
            # Build update query
            updates = []
            params = []
            
            if rule_name is not None:
                updates.append("rule_name = %s")
                params.append(rule_name)
            if rule_type is not None:
                updates.append("rule_type = %s")
                params.append(rule_type)
            if rule_expression is not None:
                updates.append("rule_expression = %s")
                params.append(rule_expression)
            if rule_operator is not None:
                updates.append("rule_operator = %s")
                params.append(rule_operator)
            if rule_value is not None:
                updates.append("rule_value = %s")
                params.append(rule_value)
            if is_mandatory is not None:
                updates.append("is_mandatory = %s")
                params.append(is_mandatory)
            if priority is not None:
                updates.append("priority = %s")
                params.append(priority)
            if effective_from is not None:
                updates.append("effective_from = %s")
                params.append(effective_from)
            if effective_to is not None:
                updates.append("effective_to = %s")
                params.append(effective_to)
            
            if not updates:
                raise ValueError("No fields to update")
            
            # Add version and updated_at
            updates.append("version = %s")
            params.append(new_version)
            updates.append("updated_at = CURRENT_TIMESTAMP")
            
            params.append(rule_id)
            
            update_query = f"""
                UPDATE eligibility.scheme_eligibility_rules
                SET {', '.join(updates)}
                WHERE rule_id = %s
                RETURNING rule_id, scheme_code, rule_name, rule_type, rule_expression,
                          rule_operator, rule_value, is_mandatory, priority,
                          version, effective_from, effective_to, updated_at
            """
            
            cursor.execute(update_query, params)
            result = cursor.fetchone()
            self.db.connection.commit()
            
            # Log change
            self._log_rule_change(
                rule_id, scheme_code, 'UPDATED', current_version,
                {'new_version': new_version}, updated_by
            )
            
            return {
                'rule_id': result[0],
                'scheme_code': result[1],
                'rule_name': result[2],
                'rule_type': result[3],
                'rule_expression': result[4],
                'rule_operator': result[5],
                'rule_value': result[6],
                'is_mandatory': result[7],
                'priority': result[8],
                'version': result[9],
                'effective_from': result[10].isoformat() if result[10] else None,
                'effective_to': result[11].isoformat() if result[11] else None,
                'updated_at': result[12].isoformat() if result[12] else None
            }
        
        except Exception as e:
            # Rollback on error to allow subsequent operations
            self.db.connection.rollback()
            raise
        finally:
            cursor.close()
    
    def delete_rule(self, rule_id: int, deleted_by: str = "system"):
        """
        Delete a rule (soft delete by setting effective_to)
        
        Args:
            rule_id: Rule ID
            deleted_by: User who deleted the rule
        """
        cursor = self.db.connection.cursor()
        
        try:
            # Get current rule
            cursor.execute("""
                SELECT scheme_code FROM eligibility.scheme_eligibility_rules
                WHERE rule_id = %s
            """, (rule_id,))
            
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Rule {rule_id} not found")
            
            scheme_code = result[0]
            
            # Soft delete: set effective_to to today
            cursor.execute("""
                UPDATE eligibility.scheme_eligibility_rules
                SET effective_to = CURRENT_DATE,
                    updated_at = CURRENT_TIMESTAMP
                WHERE rule_id = %s
            """, (rule_id,))
            
            self.db.connection.commit()
            
            # Log change
            self._log_rule_change(
                rule_id, scheme_code, 'DELETED', None,
                {'effective_to': date.today().isoformat()}, deleted_by
            )
        
        except Exception as e:
            # Rollback on error to allow subsequent operations
            self.db.connection.rollback()
            raise
        finally:
            cursor.close()
    
    def create_rule_set_snapshot(
        self,
        scheme_code: str,
        snapshot_version: str,
        snapshot_name: Optional[str] = None,
        description: Optional[str] = None,
        created_by: str = "system"
    ) -> int:
        """
        Create a snapshot of current rule set for a scheme
        
        Args:
            scheme_code: Scheme code (e.g., 'CHIRANJEEVI')
            snapshot_version: Version identifier (e.g., "v2.0")
            snapshot_name: Optional name for snapshot
            description: Optional description
            created_by: User who created snapshot
        
        Returns:
            Snapshot ID
        """
        cursor = self.db.connection.cursor()
        
        try:
            # Use database function to create snapshot
            cursor.execute("""
                SELECT eligibility.create_rule_set_snapshot(
                    %s, %s, %s, %s, %s
                )
            """, (scheme_code, snapshot_version, snapshot_name, description, created_by))
            
            snapshot_id = cursor.fetchone()[0]
            self.db.connection.commit()
            
            return snapshot_id
        
        finally:
            cursor.close()
    
    def get_rule_set_snapshots(self, scheme_code: str) -> List[Dict[str, Any]]:
        """
        Get all rule set snapshots for a scheme
        
        Args:
            scheme_code: Scheme code (e.g., 'CHIRANJEEVI')
        
        Returns:
            List of snapshot dictionaries
        """
        import pandas as pd
        
        query = """
            SELECT 
                snapshot_id, snapshot_name, snapshot_version, snapshot_date,
                description, created_by, created_at
            FROM eligibility.rule_set_snapshots
            WHERE scheme_code = %s
            ORDER BY snapshot_date DESC
        """
        
        df = pd.read_sql(query, self.db.connection, params=(scheme_code,))
        return df.to_dict('records')
    
    def compare_evaluations(
        self,
        scheme_code: str,
        rule_set_version_old: str,
        rule_set_version_new: str,
        family_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compare evaluation results across rule set versions
        
        Args:
            scheme_code: Scheme code (e.g., 'CHIRANJEEVI')
            rule_set_version_old: Old rule set version
            rule_set_version_new: New rule set version
            family_id: Optional family ID filter
        
        Returns:
            Comparison results
        """
        import pandas as pd
        
        query = """
            SELECT 
                family_id, scheme_code,
                COUNT(*) FILTER (WHERE rule_set_version = %s) as old_count,
                COUNT(*) FILTER (WHERE rule_set_version = %s) as new_count,
                COUNT(*) FILTER (
                    WHERE rule_set_version = %s AND evaluation_status = 'RULE_ELIGIBLE'
                ) as old_eligible,
                COUNT(*) FILTER (
                    WHERE rule_set_version = %s AND evaluation_status = 'RULE_ELIGIBLE'
                ) as new_eligible
            FROM eligibility.eligibility_snapshots
            WHERE scheme_code = %s
                AND rule_set_version IN (%s, %s)
        """
        
        if family_id:
            query += " AND family_id = %s"
            params = (
                rule_set_version_old, rule_set_version_new,
                rule_set_version_old, rule_set_version_new,
                scheme_code, rule_set_version_old, rule_set_version_new,
                family_id
            )
        else:
            params = (
                rule_set_version_old, rule_set_version_new,
                rule_set_version_old, rule_set_version_new,
                scheme_code, rule_set_version_old, rule_set_version_new
            )
        
        query += " GROUP BY family_id, scheme_code"
        
        df = pd.read_sql(query, self.db.connection, params=params)
        
        return {
            'scheme_code': scheme_code,
            'rule_set_version_old': rule_set_version_old,
            'rule_set_version_new': rule_set_version_new,
            'comparison': df.to_dict('records')
        }
    
    def _log_rule_change(
        self,
        rule_id: int,
        scheme_code: str,
        change_type: str,
        old_version: Optional[int],
        change_data: Dict,
        changed_by: str
    ):
        """Log rule change to audit log"""
        cursor = self.db.connection.cursor()
        
        try:
            insert_query = """
                INSERT INTO eligibility.rule_change_history (
                    rule_id, scheme_code, change_type, new_value, changed_by
                ) VALUES (%s, %s, %s, %s, %s)
            """
            
            cursor.execute(insert_query, (
                rule_id, scheme_code, change_type, json.dumps(change_data), changed_by
            ))
            
            self.db.connection.commit()
        
        except Exception as e:
            # Don't abort main operation if logging fails
            # Just rollback the log insert and continue
            self.db.connection.rollback()
            # Optionally log to console, but don't raise
            import warnings
            warnings.warn(f"Failed to log rule change: {e}")
        
        finally:
            cursor.close()
    
    def close(self):
        """Close database connection"""
        if self.db:
            self.db.disconnect()


def main():
    """Test rule manager"""
    manager = RuleManager()
    
    # Example: Create a rule
    rule = manager.create_rule(
        scheme_code='CHIRANJEEVI',
        rule_name='Age Requirement',
        rule_type='AGE',
        rule_expression='age >= 0',
        rule_operator='>=',
        rule_value='0',
        is_mandatory=True,
        priority=10,
        created_by='admin'
    )
    
    print("Created rule:", rule)
    
    manager.close()


if __name__ == "__main__":
    main()

