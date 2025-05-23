import os
from pathlib import Path

# Set up Kaggle credentials before any other imports
kaggle_json_path = Path("kaggle.json")
if kaggle_json_path.exists():
    os.environ['KAGGLE_CONFIG_DIR'] = str(Path.cwd())
    os.environ['KAGGLE_USERNAME'] = ''  # Clear any existing credentials
    os.environ['KAGGLE_KEY'] = ''      # Clear any existing credentials
else:
    raise FileNotFoundError(
        "kaggle.json not found in project directory. "
        "Please download it from Kaggle and place it in the project root."
    )

import sqlite3
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
import kaggle
import tempfile

class DataProcessor:
    def __init__(self):
        """Initialize the data processor with Kaggle dataset."""
        self.conn = None
        self._load_data()

    def _load_data(self):
        """Load data from Kaggle and create SQLite database."""
        # Create a temporary SQLite database
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, 'freelancer_data.db')
        self.conn = sqlite3.connect(db_path)

        # Download dataset from Kaggle
        kaggle.api.dataset_download_file(
            'shohinurpervezshohan/freelancer-earnings-and-job-trends',
            'freelancer_earnings_bd.csv',
            path=temp_dir
        )

        # Load the CSV file
        csv_path = os.path.join(temp_dir, 'freelancer_earnings_bd.csv')
        df = pd.read_csv(csv_path)

        # Convert numeric columns
        numeric_columns = ['earnings', 'projects_completed', 'years_of_experience']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Save to SQLite database
        df.to_sql('freelancers', self.conn, if_exists='replace', index=False)

    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a SQL query and return results as DataFrame."""
        return pd.read_sql_query(query, self.conn)

    def get_crypto_vs_other_earnings(self) -> Dict[str, float]:
        """Compare earnings between freelancers who accept crypto and those who don't."""
        query = """
        SELECT 
            AVG(CASE WHEN payment_methods LIKE '%cryptocurrency%' THEN earnings END) as crypto_earnings,
            AVG(CASE WHEN payment_methods NOT LIKE '%cryptocurrency%' THEN earnings END) as other_earnings
        FROM freelancers
        """
        result = self.execute_query(query).iloc[0]
        
        crypto_earnings = result['crypto_earnings']
        other_earnings = result['other_earnings']
        
        return {
            'crypto_earnings': crypto_earnings,
            'other_earnings': other_earnings,
            'difference_percentage': ((crypto_earnings - other_earnings) / other_earnings) * 100
        }

    def get_earnings_by_region(self) -> Dict[str, float]:
        """Get average earnings by region."""
        query = """
        SELECT region, AVG(earnings) as avg_earnings
        FROM freelancers
        GROUP BY region
        """
        result = self.execute_query(query)
        return dict(zip(result['region'], result['avg_earnings']))

    def get_expert_projects_stats(self) -> Dict[str, float]:
        """Get statistics about experts with less than 100 projects."""
        query = """
        WITH expert_stats AS (
            SELECT 
                COUNT(*) as total_experts,
                SUM(CASE WHEN projects_completed < 100 THEN 1 ELSE 0 END) as experts_less_than_100
            FROM freelancers
            WHERE expertise_level LIKE '%expert%'
        )
        SELECT 
            total_experts,
            experts_less_than_100,
            (experts_less_than_100 * 100.0 / total_experts) as percentage
        FROM expert_stats
        """
        result = self.execute_query(query).iloc[0]
        
        return {
            'total_experts': result['total_experts'],
            'experts_less_than_100': result['experts_less_than_100'],
            'percentage': result['percentage']
        }

    def get_earnings_by_experience(self) -> Dict[str, float]:
        """Get average earnings by years of experience."""
        query = """
        SELECT years_of_experience, AVG(earnings) as avg_earnings
        FROM freelancers
        GROUP BY years_of_experience
        ORDER BY years_of_experience
        """
        result = self.execute_query(query)
        return dict(zip(result['years_of_experience'], result['avg_earnings']))

    def get_top_skills_earnings(self, top_n: int = 5) -> Dict[str, float]:
        """Get average earnings for top N skills."""
        query = f"""
        WITH RECURSIVE split(skills, rest) AS (
            SELECT 
                substr(skills, 1, instr(skills || ',', ',') - 1),
                substr(skills || ',', instr(skills || ',', ',') + 1)
            FROM freelancers
            WHERE skills IS NOT NULL
            UNION ALL
            SELECT 
                substr(rest, 1, instr(rest || ',', ',') - 1),
                substr(rest || ',', instr(rest || ',', ',') + 1)
            FROM split
            WHERE rest != ''
        )
        SELECT 
            TRIM(skills) as skill,
            AVG(earnings) as avg_earnings
        FROM split
        WHERE skills != ''
        GROUP BY TRIM(skills)
        ORDER BY avg_earnings DESC
        LIMIT {top_n}
        """
        result = self.execute_query(query)
        return dict(zip(result['skill'], result['avg_earnings']))

    def get_earnings_by_education(self) -> Dict[str, float]:
        """Get average earnings by education level."""
        query = """
        SELECT education_level, AVG(earnings) as avg_earnings
        FROM freelancers
        GROUP BY education_level
        """
        result = self.execute_query(query)
        return dict(zip(result['education_level'], result['avg_earnings'])) 