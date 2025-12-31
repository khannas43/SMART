"""
Data Loader for Golden Record Use Case
Loads data from PostgreSQL for deduplication and conflict resolution
"""

import sys
from pathlib import Path
import pandas as pd
import yaml

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class GoldenRecordDataLoader:
    """Load data from various sources for Golden Record creation"""
    
    def __init__(self, config_path: str = None):
        """
        Initialize data loader
        
        Args:
            config_path: Path to db_config.yaml. If None, uses default.
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize database connector
        db_config = self.config['database']
        self.db = DBConnector(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['dbname'],
            user=db_config['user'],
            password=db_config['password']
        )
        self.db.connect()
    
    def load_all_citizens(self) -> pd.DataFrame:
        """
        Load all active citizens for deduplication
        Tries smart_warehouse first, falls back to smart_citizen portal DB
        """
        query = self.config['queries']['all_citizens']
        try:
            return self.db.execute_query(query)
        except Exception as e:
            # Fallback: Try loading from smart_citizen portal database
            if 'does not exist' in str(e).lower() or 'relation' in str(e).lower():
                print(f"⚠️  Citizens table not found in {self.db.database}, trying smart_citizen portal DB...")
                # Temporarily switch to smart_citizen database
                original_db = self.db.database
                self.db.database = 'smart_citizen'
                self.db.disconnect()
                self.db.connect()
                result = self.db.execute_query(query)
                # Restore original database
                self.db.database = original_db
                self.db.disconnect()
                self.db.connect()
                return result
            else:
                raise
    
    def load_citizen_by_aadhaar(self, jan_aadhaar: str) -> pd.DataFrame:
        """Load citizen by Jan Aadhaar number"""
        query = self.config['queries']['citizen_by_aadhaar']
        return self.db.execute_query(query, (jan_aadhaar,))
    
    def load_schemes_data(self) -> pd.DataFrame:
        """Load schemes data"""
        query = self.config['queries']['schemes']
        return self.db.execute_query(query)
    
    def load_for_deduplication(self, batch_size: int = 10000) -> pd.DataFrame:
        """
        Load data in batches for deduplication processing
        
        Args:
            batch_size: Number of records per batch
            
        Yields:
            DataFrame batches
        """
        query = self.config['queries']['all_citizens']
        offset = 0
        
        while True:
            batch_query = f"{query} LIMIT {batch_size} OFFSET {offset}"
            batch = self.db.execute_query(batch_query)
            
            if batch.empty:
                break
            
            yield batch
            offset += batch_size
    
    def close(self):
        """Close database connection"""
        if self.db:
            self.db.disconnect()


if __name__ == "__main__":
    # Example usage
    loader = GoldenRecordDataLoader()
    
    # Load all citizens
    print("Loading citizens...")
    citizens = loader.load_all_citizens()
    print(f"Loaded {len(citizens)} citizens")
    
    # Load schemes
    print("Loading schemes...")
    schemes = loader.load_schemes_data()
    print(f"Loaded {len(schemes)} schemes")
    
    loader.close()

