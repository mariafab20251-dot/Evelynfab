"""
Language validation using LLM (DeepSeek via OpenRouter).
"""

import requests
from typing import Optional

from config import OPENROUTER_API_KEY, OPENROUTER_MODEL


class LanguageValidator:
    """Validates video titles are in English using LLM."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize OpenRouter client."""
        self.api_key = api_key or OPENROUTER_API_KEY
        self.model = model or OPENROUTER_MODEL
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

        if not self.api_key:
            print("Warning: OpenRouter API key not set. Language validation will be skipped.")

    def is_english(self, title: str) -> bool:
        """
        Check if a video title is in English.

        Args:
            title: Video title to check

        Returns:
            True if title is in English, False otherwise
        """
        if not self.api_key:
            # If no API key, assume English (skip validation)
            return True

        prompt = f"""Analyze the following video title and determine if it's in English.
Respond with only "yes" if the title is in English, or "no" if it's in another language.

Title: {title}

Is this title in English?"""

        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 10,
                    "temperature": 0
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                answer = result["choices"][0]["message"]["content"].strip().lower()
                return answer == "yes"
            else:
                print(f"OpenRouter API error: {response.status_code} - {response.text}")
                return True  # Assume English on error

        except Exception as e:
            print(f"Language validation error: {e}")
            return True  # Assume English on error

    def filter_english_videos(self, videos: list) -> list:
        """
        Filter videos to keep only those with English titles.

        Args:
            videos: List of video dictionaries

        Returns:
            Filtered list with only English-titled videos
        """
        if not self.api_key:
            print("Skipping language validation (no API key)")
            return videos

        english_videos = []

        for video in videos:
            title = video.get("title", "")
            if self.is_english(title):
                english_videos.append(video)
            else:
                print(f"Filtered out non-English video: {title}")

        return english_videos


def validate_english_videos(videos: list, api_key: Optional[str] = None) -> list:
    """
    Convenience function to filter English videos.

    Args:
        videos: List of video dictionaries
        api_key: Optional OpenRouter API key

    Returns:
        Filtered list with only English-titled videos
    """
    validator = LanguageValidator(api_key)
    return validator.filter_english_videos(videos)
