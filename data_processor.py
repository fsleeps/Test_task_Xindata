import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple

class DataProcessor:
    def __init__(self, csv_path: str):
        """Initialize the data processor with the path to the CSV file."""
        self.df = pd.read_csv(csv_path)
        self._preprocess_data()

    def _preprocess_data(self):
        """Preprocess the data to ensure it's in the correct format."""
        # Convert numeric columns to appropriate types
        numeric_columns = ['earnings', 'projects_completed', 'years_of_experience']
        for col in numeric_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')

    def get_crypto_vs_other_earnings(self) -> Dict[str, float]:
        """Compare earnings between freelancers who accept crypto and those who don't."""
        crypto_earnings = self.df[self.df['payment_methods'].str.contains('cryptocurrency', case=False, na=False)]['earnings'].mean()
        other_earnings = self.df[~self.df['payment_methods'].str.contains('cryptocurrency', case=False, na=False)]['earnings'].mean()
        
        return {
            'crypto_earnings': crypto_earnings,
            'other_earnings': other_earnings,
            'difference_percentage': ((crypto_earnings - other_earnings) / other_earnings) * 100
        }

    def get_earnings_by_region(self) -> Dict[str, float]:
        """Get average earnings by region."""
        return self.df.groupby('region')['earnings'].mean().to_dict()

    def get_expert_projects_stats(self) -> Dict[str, float]:
        """Get statistics about experts with less than 100 projects."""
        experts = self.df[self.df['expertise_level'].str.contains('expert', case=False, na=False)]
        experts_less_than_100 = experts[experts['projects_completed'] < 100]
        
        total_experts = len(experts)
        experts_less_than_100_count = len(experts_less_than_100)
        
        return {
            'total_experts': total_experts,
            'experts_less_than_100': experts_less_than_100_count,
            'percentage': (experts_less_than_100_count / total_experts) * 100 if total_experts > 0 else 0
        }

    def get_earnings_by_experience(self) -> Dict[str, float]:
        """Get average earnings by years of experience."""
        return self.df.groupby('years_of_experience')['earnings'].mean().to_dict()

    def get_top_skills_earnings(self, top_n: int = 5) -> Dict[str, float]:
        """Get average earnings for top N skills."""
        # Assuming skills are stored in a column named 'skills'
        if 'skills' not in self.df.columns:
            return {}
            
        # Split skills and calculate average earnings for each
        skills_earnings = {}
        for skills_str in self.df['skills'].dropna():
            skills = [s.strip() for s in skills_str.split(',')]
            for skill in skills:
                if skill not in skills_earnings:
                    skills_earnings[skill] = []
                skills_earnings[skill].append(self.df[self.df['skills'] == skills_str]['earnings'].mean())
        
        # Calculate average earnings for each skill
        avg_earnings = {skill: np.mean(earnings) for skill, earnings in skills_earnings.items()}
        
        # Get top N skills by earnings
        return dict(sorted(avg_earnings.items(), key=lambda x: x[1], reverse=True)[:top_n])

    def get_earnings_by_education(self) -> Dict[str, float]:
        """Get average earnings by education level."""
        return self.df.groupby('education_level')['earnings'].mean().to_dict() 