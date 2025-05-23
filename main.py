import os
from pathlib import Path
from typing import Dict, Any
import json
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
import requests
from data_processor import DataProcessor

# Load environment variables
load_dotenv()

# YandexGPT API endpoint (standard example)
YANDEXGPT_ENDPOINT = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
YANDEX_IAM_TOKEN = os.getenv('YANDEX_IAM_TOKEN')

# Initialize Rich console
console = Console()

class FreelancerAnalysisSystem:
    def __init__(self):
        """Initialize the analysis system."""
        self.data_processor = None
        self.available_analyses = {
            'crypto_vs_other': None,
            'earnings_by_region': None,
            'expert_projects': None,
            'earnings_by_experience': None,
            'top_skills': None,
            'earnings_by_education': None
        }

    def initialize(self):
        """Initialize the data processor and available analyses."""
        try:
            self.data_processor = DataProcessor()
            # Update available analyses with the initialized data processor
            self.available_analyses = {
                'crypto_vs_other': self.data_processor.get_crypto_vs_other_earnings,
                'earnings_by_region': self.data_processor.get_earnings_by_region,
                'expert_projects': self.data_processor.get_expert_projects_stats,
                'earnings_by_experience': self.data_processor.get_earnings_by_experience,
                'top_skills': self.data_processor.get_top_skills_earnings,
                'earnings_by_education': self.data_processor.get_earnings_by_education
            }
            console.print("[green]Data loaded successfully![/green]")
        except Exception as e:
            console.print(f"[red]Error loading data: {str(e)}[/red]")
            raise

    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze the query using YandexGPT API and return relevant data."""
        try:
            # Compose the system prompt
            system_message = (
                "You are an AI assistant that helps analyze freelancer earnings data. "
                "You have access to the following types of analyses:\n"
                "- Comparison of earnings between crypto and non-crypto payment methods\n"
                "- Earnings distribution by region\n"
                "- Statistics about experts with less than 100 projects\n"
                "- Earnings by years of experience\n"
                "- Top skills by earnings\n"
                "- Earnings by education level\n\n"
                "Based on the user's query, determine which analysis would be most appropriate and return a JSON object with: "
                "1. The type of analysis needed (as 'analysis_type')\n"
                "2. Any additional parameters required\n"
            )

            # Prepare YandexGPT request
            headers = {
                f"Authorization: Bearer <{YANDEX_IAM_TOKEN}>",
                "Content-Type: application/json"
            }
            payload = {
                "modelUri": "gpt://aje78mro50ila53rqvm5/yandexgpt",
                "completionOptions": {"stream": False, "temperature": 0.1, "maxTokens": 200},
                "messages": [
                    {"role": "system", "text": system_message},
                    {"role": "user", "text": query}
                ]
            }
            response = requests.post(YANDEXGPT_ENDPOINT, headers=headers, json=payload)
            if response.status_code != 200:
                return {"error": f"YandexGPT API error: {response.status_code} {response.text}"}
            data = response.json()
            # YandexGPT returns completions as a list
            completion = data["result"]["alternatives"][0]["message"]["text"]
            analysis_request = json.loads(completion)
            analysis_type = analysis_request.get('analysis_type')
            if analysis_type not in self.available_analyses:
                return {"error": f"Analysis type '{analysis_type}' not available"}
            # Get the analysis function and execute it
            analysis_func = self.available_analyses[analysis_type]
            result = analysis_func()
            return {
                "analysis_type": analysis_type,
                "result": result
            }
        except Exception as e:
            return {"error": str(e)}

    def format_response(self, analysis_result: Dict[str, Any]) -> str:
        """Format the analysis result into a human-readable response."""
        if "error" in analysis_result:
            return f"Error: {analysis_result['error']}"
        analysis_type = analysis_result["analysis_type"]
        result = analysis_result["result"]
        if analysis_type == "crypto_vs_other":
            return f"""Crypto vs Other Payment Methods Analysis:
            - Average earnings for crypto payments: ${result['crypto_earnings']:.2f}
            - Average earnings for other payment methods: ${result['other_earnings']:.2f}
            - Crypto freelancers earn {result['difference_percentage']:.1f}% more"""
        elif analysis_type == "earnings_by_region":
            regions = "\n".join([f"- {region}: ${earnings:.2f}" for region, earnings in result.items()])
            return f"Earnings by Region:\n{regions}"
        elif analysis_type == "expert_projects":
            return f"""Expert Projects Analysis:
            - Total experts: {result['total_experts']}
            - Experts with <100 projects: {result['experts_less_than_100']}
            - Percentage: {result['percentage']:.1f}%"""
        elif analysis_type == "earnings_by_experience":
            experience = "\n".join([f"- {years} years: ${earnings:.2f}" for years, earnings in result.items()])
            return f"Earnings by Experience:\n{experience}"
        elif analysis_type == "top_skills":
            skills = "\n".join([f"- {skill}: ${earnings:.2f}" for skill, earnings in result.items()])
            return f"Top Skills by Earnings:\n{skills}"
        elif analysis_type == "earnings_by_education":
            education = "\n".join([f"- {level}: ${earnings:.2f}" for level, earnings in result.items()])
            return f"Earnings by Education Level:\n{education}"
        return "Analysis completed, but no specific format available for this type."

def main():
    """Main function to run the CLI interface."""
    console.print(Panel.fit(
        "[bold blue]Freelancer Earnings Analysis System[/bold blue]\n"
        "Ask questions about freelancer earnings data in natural language.",
        title="Welcome"
    ))
    # Initialize the system
    system = FreelancerAnalysisSystem()
    try:
        system.initialize()
    except Exception as e:
        console.print(f"[red]Error initializing the system: {str(e)}[/red]")
        return
    # Main interaction loop
    while True:
        query = Prompt.ask("\n[bold]Enter your question[/bold] (or 'quit' to exit)")
        if query.lower() == 'quit':
            break
        console.print("\n[bold]Analyzing your question...[/bold]")
        result = system.analyze_query(query)
        formatted_response = system.format_response(result)
        console.print(Panel(
            formatted_response,
            title="Analysis Result",
            border_style="green"
        ))

if __name__ == "__main__":
    main() 