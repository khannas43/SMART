"""
Database Connector for SMART Platform
Connects to PostgreSQL database using psycopg2 and pandas
"""

import psycopg2
import pandas as pd
from typing import Optional, Dict, Any
import os


class DBConnector:
    """PostgreSQL database connector with pandas integration"""
    
    def __init__(
        self,
        host: str = "172.17.16.1",
        port: int = 5432,
        database: str = "smart",
        user: str = "sameer",
        password: str = "anjali143"
    ):
        """
        Initialize database connector
        
        Args:
            host: Database host
            port: Database port
            database: Database name
            user: Database user
            password: Database password
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                connect_timeout=10
            )
            print(f"✅ Connected to PostgreSQL: {self.host}:{self.port}/{self.database}")
            return self.connection
        except psycopg2.Error as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            print("Database connection closed")
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> pd.DataFrame:
        """
        Execute SQL query and return results as pandas DataFrame
        
        Args:
            query: SQL query string (use %(param_name)s for named parameters)
            params: Optional query parameters as dict for named parameters
            
        Returns:
            pandas DataFrame with query results
        """
        if not self.connection:
            self.connect()
        
        try:
            # For psycopg2 with pandas, we need to handle parameters properly
            if params:
                # Use cursor.execute for parameterized queries, then read with pandas
                cursor = self.connection.cursor()
                cursor.execute(query, params)
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                data = cursor.fetchall()
                cursor.close()
                df = pd.DataFrame(data, columns=columns)
            else:
                # No parameters, use pandas directly
                df = pd.read_sql(query, self.connection)
            return df
        except Exception as e:
            print(f"❌ Query execution failed: {e}")
            print(f"Query: {query[:100]}...")
            raise
    
    def get_table_info(self, table_name: str) -> pd.DataFrame:
        """
        Get table schema information
        
        Args:
            table_name: Name of the table
            
        Returns:
            DataFrame with column information
        """
        query = """
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_name = %(table_name)s
        ORDER BY ordinal_position;
        """
        return self.execute_query(query, {'table_name': table_name})
    
    def get_table_count(self, table_name: str) -> int:
        """
        Get row count for a table
        
        Args:
            table_name: Name of the table
            
        Returns:
            Number of rows
        """
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        result = self.execute_query(query)
        return result['count'].iloc[0]
    
    def list_tables(self) -> list:
        """
        List all tables in the database
        
        Returns:
            List of table names
        """
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
        """
        result = self.execute_query(query)
        return result['table_name'].tolist()
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


# Convenience function for quick queries
def query_db(query: str, host: str = "172.17.16.1", **kwargs) -> pd.DataFrame:
    """
    Quick function to execute a query and return DataFrame
    
    Args:
        query: SQL query string
        host: Database host (default: 172.17.16.1)
        **kwargs: Additional connection parameters
        
    Returns:
        pandas DataFrame
    """
    with DBConnector(host=host, **kwargs) as db:
        return db.execute_query(query)

