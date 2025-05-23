# Freelancer Earnings Analysis System

This system analyzes statistical data about freelancer earnings and provides answers to natural language queries. It uses a combination of data processing and language models to understand and respond to questions about freelancer earnings patterns.

## Features

- Natural language query processing
- Analysis of freelancer earnings data
- Command-line interface
- Integration with YandexGPT language model
- SQL-based data processing
- Direct Kaggle dataset integration

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root and add your Yandex IAM token:
```
YANDEX_IAM_TOKEN=your_yandex_iam_token_here
```

3. Set up Kaggle credentials:
   - Go to your Kaggle account settings (https://www.kaggle.com/settings)
   - Scroll down to the "API" section
   - Click "Create New API Token"
   - This will download a `kaggle.json` file
   - Place the `kaggle.json` file in the project root directory (same directory as main.py)

## Usage

Run the main script:
```bash
python main.py
```

Then you can ask questions about the freelancer earnings data in natural language, for example:
- "How much higher is the income for freelancers who accept cryptocurrency payments compared to other payment methods?"
- "How is freelancer income distributed by region?"
- "What percentage of freelancers who consider themselves experts have completed less than 100 projects?"
- "What are the top 5 highest-paying skills?"
- "How does education level affect freelancer earnings?"
- "What's the relationship between years of experience and earnings?"

## Technical Details

The system uses:
- SQLite for efficient data processing
- SQL queries for data analysis
- YandexGPT for natural language understanding
- Kaggle's API for dataset access
- Rich library for beautiful CLI interface 