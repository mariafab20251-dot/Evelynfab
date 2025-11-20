"""
Configuration settings for YouTube Deep Research Agent.
Set your API keys as environment variables or update the defaults here.
"""

import os

# YouTube Data API v3
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

# OpenRouter API (for DeepSeek LLM)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat")

# Airtable Configuration
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY", "")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID", "")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME", "YouTube Research")

# Search Configuration
SEARCH_DAYS_AGO = 7  # Search videos from past N days
MAX_RESULTS = 50  # Maximum videos to fetch per search

# Engagement Thresholds
MIN_LIKE_RATIO = 0.05  # 5% minimum like ratio
MIN_COMMENT_RATIO = 0.002  # 0.2% minimum comment ratio
MIN_VIEWS = 1000  # Minimum view count
