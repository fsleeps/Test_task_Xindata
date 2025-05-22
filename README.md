# Freelancer Earnings Analysis System

This system analyzes statistical data about freelancer earnings and provides answers to natural language queries. It uses a combination of data processing and language models to understand and respond to questions about freelancer earnings patterns.

## Features

- Natural language query processing
- Analysis of freelancer earnings data
- Command-line interface
- Integration with OpenAI's language model

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

3. Download the dataset from Kaggle and place it in the `data` directory as `freelancer_earnings_bd.csv`

## Usage

Run the main script:
```bash
python main.py
```

Then you can ask questions about the freelancer earnings data in natural language, for example:
- "How much higher is the income for freelancers who accept cryptocurrency payments compared to other payment methods?"
- "How is freelancer income distributed by region?"
- "What percentage of freelancers who consider themselves experts have completed less than 100 projects?" 