"""
YouTube API integration for searching and fetching video details.
"""

from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import Optional

from config import YOUTUBE_API_KEY, SEARCH_DAYS_AGO, MAX_RESULTS


class YouTubeSearcher:
    """Handles YouTube API interactions for video search and details."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize YouTube API client."""
        self.api_key = api_key or YOUTUBE_API_KEY
        if not self.api_key:
            raise ValueError("YouTube API key is required. Set YOUTUBE_API_KEY environment variable.")
        self.youtube = build("youtube", "v3", developerKey=self.api_key)

    def search_videos(self, query: str, days_ago: int = SEARCH_DAYS_AGO,
                      max_results: int = MAX_RESULTS) -> list:
        """
        Search YouTube for videos matching the query from the past N days.

        Args:
            query: Search term (e.g., "Best SaaS Business")
            days_ago: Number of days to look back
            max_results: Maximum number of results to return

        Returns:
            List of video IDs
        """
        # Calculate date range
        published_after = (datetime.utcnow() - timedelta(days=days_ago)).isoformat() + "Z"

        try:
            search_response = self.youtube.search().list(
                q=query,
                part="id",
                type="video",
                order="relevance",
                publishedAfter=published_after,
                maxResults=max_results
            ).execute()

            video_ids = [
                item["id"]["videoId"]
                for item in search_response.get("items", [])
            ]

            return video_ids

        except HttpError as e:
            print(f"YouTube API error during search: {e}")
            return []

    def get_video_details(self, video_ids: list) -> list:
        """
        Fetch detailed statistics for a list of video IDs.

        Args:
            video_ids: List of YouTube video IDs

        Returns:
            List of video details with statistics
        """
        if not video_ids:
            return []

        videos = []

        # YouTube API allows max 50 IDs per request
        for i in range(0, len(video_ids), 50):
            batch_ids = video_ids[i:i + 50]

            try:
                videos_response = self.youtube.videos().list(
                    part="snippet,statistics",
                    id=",".join(batch_ids)
                ).execute()

                for item in videos_response.get("items", []):
                    video_data = {
                        "video_id": item["id"],
                        "title": item["snippet"]["title"],
                        "description": item["snippet"].get("description", ""),
                        "channel_title": item["snippet"]["channelTitle"],
                        "published_at": item["snippet"]["publishedAt"],
                        "url": f"https://www.youtube.com/watch?v={item['id']}",
                        "views": int(item["statistics"].get("viewCount", 0)),
                        "likes": int(item["statistics"].get("likeCount", 0)),
                        "comments": int(item["statistics"].get("commentCount", 0))
                    }
                    videos.append(video_data)

            except HttpError as e:
                print(f"YouTube API error fetching details: {e}")
                continue

        return videos


def search_youtube_videos(query: str, api_key: Optional[str] = None) -> list:
    """
    Convenience function to search YouTube and get video details.

    Args:
        query: Search term
        api_key: Optional YouTube API key

    Returns:
        List of video details with statistics
    """
    searcher = YouTubeSearcher(api_key)
    video_ids = searcher.search_videos(query)
    videos = searcher.get_video_details(video_ids)
    return videos
