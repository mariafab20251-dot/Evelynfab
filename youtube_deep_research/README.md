# YouTube Deep Research Agent

A Python implementation of the n8n YouTube Deep Research workflow. This tool searches YouTube for videos on specific topics, calculates engagement metrics, filters high-performing content, and stores results in Google Sheets.

## Features

- **YouTube Search**: Find recent videos (configurable time range)
- **Engagement Analysis**: Calculate like/comment ratios
- **Smart Filtering**: Filter by views, like ratio, and comment ratio
- **Language Validation**: Verify English titles using LLM (DeepSeek via OpenRouter)
- **Google Sheets Storage**: Store results in Google Sheets
- **CLI Interface**: Easy command-line usage with flexible options

## Installation

```bash
cd youtube_deep_research
pip install -r requirements.txt
```

## Configuration

### API Keys Required

1. **YouTube Data API v3**
   - Get your key at: https://console.cloud.google.com/apis/credentials
   - Enable "YouTube Data API v3"

2. **OpenRouter API** (optional, for language validation)
   - Get your key at: https://openrouter.ai/keys

3. **Google Sheets API** (optional, for storage)
   - Create a service account at: https://console.cloud.google.com/iam-admin/serviceaccounts
   - Enable Google Sheets API
   - Download the JSON credentials file
   - Share your spreadsheet with the service account email

### Set Environment Variables

```bash
export YOUTUBE_API_KEY="your_youtube_api_key"
export OPENROUTER_API_KEY="your_openrouter_api_key"
export GOOGLE_SHEETS_CREDENTIALS_FILE="credentials.json"
export GOOGLE_SHEETS_SPREADSHEET_ID="your_spreadsheet_id"
export GOOGLE_SHEETS_SHEET_NAME="Sheet1"
```

Or copy `.env.example` to `.env` and fill in your keys.

## Usage

### Basic Usage

```bash
python main.py "Best SaaS Business"
```

### With Options

```bash
python main.py --topic "AI Tools" \
    --days 14 \
    --min-views 5000 \
    --min-likes 3 \
    --min-comments 0.1 \
    --output results.json
```

### Interactive Mode

```bash
python main.py --interactive
```

### Skip Optional Features

```bash
# Skip language validation
python main.py "Topic" --no-language-check

# Skip Google Sheets storage
python main.py "Topic" --no-sheets
```

### All Options

```
usage: main.py [-h] [--topic TOPIC] [--days DAYS] [--min-views MIN_VIEWS]
               [--min-likes MIN_LIKES] [--min-comments MIN_COMMENTS]
               [--no-language-check] [--no-sheets] [--output OUTPUT]
               [--interactive]
               [topic]

Options:
  topic               Search topic (e.g., 'Best SaaS Business')
  --topic, -t         Search topic (alternative)
  --days, -d          Days to look back (default: 7)
  --min-views, -v     Minimum views (default: 1000)
  --min-likes, -l     Minimum like ratio % (default: 5)
  --min-comments, -c  Minimum comment ratio % (default: 0.2)
  --no-language-check Skip language validation
  --no-sheets         Skip saving to Google Sheets
  --output, -o        Save results to JSON file
  --interactive, -i   Run in interactive mode
```

## Python API

```python
from youtube_deep_research import run_youtube_research

# Run the full pipeline
videos = run_youtube_research(
    topic="Best SaaS Business",
    days_ago=7,
    min_views=1000,
    min_like_ratio=0.05,
    min_comment_ratio=0.002,
    validate_language=True,
    save_to_sheets=True
)

# Or use individual components
from youtube_deep_research import (
    search_youtube_videos,
    calculate_engagement_ratios,
    filter_by_engagement
)

videos = search_youtube_videos("AI Tools")
videos = calculate_engagement_ratios(videos)
videos = filter_by_engagement(videos, min_views=5000)
```

## Project Structure

```
youtube_deep_research/
├── __init__.py              # Package exports
├── main.py                  # CLI entry point & orchestration
├── config.py                # Configuration settings
├── youtube_search.py        # YouTube API integration
├── engagement.py            # Engagement calculations
├── language_validator.py    # LLM language validation
├── google_sheets_storage.py # Google Sheets integration
├── requirements.txt         # Dependencies
├── .env.example             # Environment template
└── README.md                # This file
```

## Workflow Pipeline

1. **Search** - Query YouTube API for recent videos
2. **Fetch Details** - Get views, likes, comments for each video
3. **Calculate Ratios** - Compute like_ratio and comment_ratio
4. **Filter** - Apply engagement thresholds
5. **Deduplicate** - Remove duplicate videos
6. **Validate Language** - Confirm English titles with LLM
7. **Store** - Save results to Google Sheets

## Google Sheets Setup

1. Create a new Google Sheet
2. Copy the spreadsheet ID from the URL: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
3. Share the sheet with your service account email (found in credentials.json)
4. The script will automatically add headers: Video Name, URL, Channel, Views, Likes, Comments, Like Ratio, Comment Ratio, Published

## Default Thresholds

- **Minimum views**: 1,000
- **Minimum like ratio**: 5%
- **Minimum comment ratio**: 0.2%
- **Search period**: 7 days

## License

MIT
