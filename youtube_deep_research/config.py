"""
Configuration settings for YouTube Deep Research Agent.
Set your API keys in a .env file or as environment variables.
"""

import os

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use system env vars

# YouTube Data API v3
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

# OpenRouter API (for DeepSeek LLM)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat")

# Google Sheets Configuration
GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE", "credentials.json")
GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID", "")
GOOGLE_SHEETS_SHEET_NAME = os.getenv("GOOGLE_SHEETS_SHEET_NAME", "Sheet1")

# Reddit API Configuration
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "ViralResearchAgent/1.0")

# Search Configuration
SEARCH_DAYS_AGO = 7  # Search videos from past N days
MAX_RESULTS = 50  # Maximum videos to fetch per search

# Engagement Thresholds
MIN_LIKE_RATIO = 0.05  # 5% minimum like ratio
MIN_COMMENT_RATIO = 0.002  # 0.2% minimum comment ratio
MIN_VIEWS = 1000  # Minimum view count
