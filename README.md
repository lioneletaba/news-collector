# News Automation System

A Python-based news automation system that collects, filters, and presents news articles based on specific topics

## Features

- Hybrid news collection using NewsAPI with Newscatcher fallback
- Topic-based filtering using OpenAI GPT-4
- SQLite database for article storage
- Streamlit web interface for article management
- PDF report generation
- Comprehensive error handling and logging

## Architecture

The system follows clean architecture principles with the following components:

- **ArticleCollector**: Handles article collection using multiple sources
- **ArticleFilter**: Filters articles by topic using OpenAI GPT-4
- **PDFGenerator**: Generates PDF reports from selected articles
- **NewsService**: Orchestrates the entire workflow
- **Streamlit Interface**: Provides user interaction

## Requirements

- Python 3.10 or higher
- NewsAPI key
- OpenAI API key
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key
NEWS_API_KEY=your_newsapi_key                 # https://newsapi.org
NEWS_DATA_API_KEY=your_news_data_io_api_key   # https://newsdata.io
DATABASE_URL=sqlite:///./news_automation.db   # Optional, defaults to this
```

## Usage

1. Start the Streamlit interface:
```bash
streamlit run app.py
```

2. In the web interface:
   - Enter a news source domain (e.g., "bbc.com")
   - Specify the topic to filter by
   - Set the date range (defaults to yesterday)
   - Click "Fetch Articles"
   - Select articles of interest
   - Generate and download PDF report

## Development

### Project Structure
```
src/news_automation/
├── collectors/          # Article collection implementations
├── filters/            # Content filtering using OpenAI
├── generators/         # PDF report generation
├── models/             # Database models and schemas
├── services/           # Business logic and orchestration
├── utils/             # Utilities and helpers
└── app.py             # Streamlit interface
```

### Running Tests
```bash
pytest
```

### Code Style
The project follows PEP 8 guidelines. Format code using:
```bash
black src/
```

## Error Handling

The system includes comprehensive error handling:
- Pool of collectors to get articles data from, in case we reach limits for one source we can still use the others, as long as they have a compatible API or we create an adapter on top to keep the same Collector interface 
- Retry mechanisms for API calls
- Detailed error logging
- User-friendly error messages in UI

## Future Enhancements

- Caching layer for API responses
- Batch processing for large article sets
- Additional news sources
- Enhanced PDF templates
- Article sentiment analysis
- Topic trending analysis

## License

This project is licensed under the MIT License - see the LICENSE file for details.
