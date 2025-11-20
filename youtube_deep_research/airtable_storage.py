"""
Airtable integration for storing research results.
"""

import requests
from typing import Optional

from config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME


class AirtableStorage:
    """Stores video research results in Airtable."""

    def __init__(self, api_key: Optional[str] = None,
                 base_id: Optional[str] = None,
                 table_name: Optional[str] = None):
        """Initialize Airtable client."""
        self.api_key = api_key or AIRTABLE_API_KEY
        self.base_id = base_id or AIRTABLE_BASE_ID
        self.table_name = table_name or AIRTABLE_TABLE_NAME

        if not self.api_key:
            print("Warning: Airtable API key not set. Storage will be skipped.")

        self.api_url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_name}"

    def store_video(self, video: dict) -> Optional[dict]:
        """
        Store a single video record in Airtable.

        Args:
            video: Video data dictionary

        Returns:
            Created record or None on error
        """
        if not self.api_key or not self.base_id:
            return None

        # Map video data to Airtable fields
        fields = {
            "Video Name": video.get("title", ""),
            "URL": video.get("url", ""),
            "Channel": video.get("channel_title", ""),
            "Views": video.get("views", 0),
            "Likes": video.get("likes", 0),
            "Comments": video.get("comments", 0),
            "Like Ratio": video.get("like_ratio_percent", ""),
            "Comment Ratio": video.get("comment_ratio_percent", ""),
            "Published": video.get("published_at", "")
        }

        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={"fields": fields},
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Airtable error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"Airtable storage error: {e}")
            return None

    def store_videos(self, videos: list) -> list:
        """
        Store multiple videos in Airtable.

        Args:
            videos: List of video dictionaries

        Returns:
            List of created records
        """
        if not self.api_key or not self.base_id:
            print("Skipping Airtable storage (missing credentials)")
            return []

        created_records = []

        for video in videos:
            record = self.store_video(video)
            if record:
                created_records.append(record)
                print(f"Stored: {video.get('title', 'Unknown')}")

        return created_records

    def batch_store_videos(self, videos: list) -> list:
        """
        Store videos in batches (Airtable allows up to 10 records per request).

        Args:
            videos: List of video dictionaries

        Returns:
            List of created records
        """
        if not self.api_key or not self.base_id:
            print("Skipping Airtable storage (missing credentials)")
            return []

        created_records = []

        # Airtable allows max 10 records per batch
        for i in range(0, len(videos), 10):
            batch = videos[i:i + 10]

            records = []
            for video in batch:
                fields = {
                    "Video Name": video.get("title", ""),
                    "URL": video.get("url", ""),
                    "Channel": video.get("channel_title", ""),
                    "Views": video.get("views", 0),
                    "Likes": video.get("likes", 0),
                    "Comments": video.get("comments", 0),
                    "Like Ratio": video.get("like_ratio_percent", ""),
                    "Comment Ratio": video.get("comment_ratio_percent", ""),
                    "Published": video.get("published_at", "")
                }
                records.append({"fields": fields})

            try:
                response = requests.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={"records": records},
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    created_records.extend(result.get("records", []))
                    print(f"Stored batch of {len(batch)} videos")
                else:
                    print(f"Airtable batch error: {response.status_code} - {response.text}")

            except Exception as e:
                print(f"Airtable batch storage error: {e}")

        return created_records


def store_to_airtable(videos: list, api_key: Optional[str] = None,
                      base_id: Optional[str] = None,
                      table_name: Optional[str] = None) -> list:
    """
    Convenience function to store videos in Airtable.

    Args:
        videos: List of video dictionaries
        api_key: Optional Airtable API key
        base_id: Optional Airtable base ID
        table_name: Optional table name

    Returns:
        List of created records
    """
    storage = AirtableStorage(api_key, base_id, table_name)
    return storage.batch_store_videos(videos)
