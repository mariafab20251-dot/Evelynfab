"""
YouTube Deep Research Agent

A Python tool to find high-engagement YouTube videos on specific topics.
Converted from n8n workflow to modular Python project.
"""

__version__ = "1.0.0"

from .youtube_search import YouTubeSearcher, search_youtube_videos
from .engagement import (
    calculate_engagement_ratios,
    filter_by_engagement,
    remove_duplicates,
    sort_by_engagement
)
from .language_validator import LanguageValidator, validate_english_videos
from .google_sheets_storage import GoogleSheetsStorage, store_to_google_sheets
from .main import run_youtube_research

__all__ = [
    "YouTubeSearcher",
    "search_youtube_videos",
    "calculate_engagement_ratios",
    "filter_by_engagement",
    "remove_duplicates",
    "sort_by_engagement",
    "LanguageValidator",
    "validate_english_videos",
    "GoogleSheetsStorage",
    "store_to_google_sheets",
    "run_youtube_research"
]
