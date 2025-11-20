"""
YouTube API integration for searching and fetching video details.
Enhanced with channel statistics for outlier detection.
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
        self._channel_cache = {}  # Cache channel stats to reduce API calls

    def search_videos(self, query: str, days_ago: int = SEARCH_DAYS_AGO,
                      max_results: int = MAX_RESULTS) -> list:
        """
        Search YouTube for videos matching the query from the past N days.
        """
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

    def get_channel_stats(self, channel_ids: list) -> dict:
        """
        Fetch channel statistics for calculating outlier scores.

        Returns dict mapping channel_id to stats.
        """
        # Filter out already cached channels
        uncached = [cid for cid in channel_ids if cid not in self._channel_cache]

        if not uncached:
            return {cid: self._channel_cache[cid] for cid in channel_ids}

        # Fetch uncached channels
        for i in range(0, len(uncached), 50):
            batch_ids = uncached[i:i + 50]

            try:
                response = self.youtube.channels().list(
                    part="statistics,snippet",
                    id=",".join(batch_ids)
                ).execute()

                for item in response.get("items", []):
                    channel_id = item["id"]
                    stats = item.get("statistics", {})

                    self._channel_cache[channel_id] = {
                        "channel_id": channel_id,
                        "channel_name": item["snippet"]["title"],
                        "subscribers": int(stats.get("subscriberCount", 0)),
                        "total_views": int(stats.get("viewCount", 0)),
                        "video_count": int(stats.get("videoCount", 1)),
                    }

                    # Calculate average views per video
                    vc = self._channel_cache[channel_id]["video_count"]
                    tv = self._channel_cache[channel_id]["total_views"]
                    self._channel_cache[channel_id]["avg_views"] = tv // vc if vc > 0 else 0

            except HttpError as e:
                print(f"YouTube API error fetching channel stats: {e}")
                continue

        return {cid: self._channel_cache.get(cid, {}) for cid in channel_ids}

    def get_video_details(self, video_ids: list, include_channel_stats: bool = True) -> list:
        """
        Fetch detailed statistics for a list of video IDs.
        Includes channel stats for outlier calculation.
        """
        if not video_ids:
            return []

        videos = []
        channel_ids = set()

        # YouTube API allows max 50 IDs per request
        for i in range(0, len(video_ids), 50):
            batch_ids = video_ids[i:i + 50]

            try:
                videos_response = self.youtube.videos().list(
                    part="snippet,statistics,contentDetails",
                    id=",".join(batch_ids)
                ).execute()

                for item in videos_response.get("items", []):
                    # Parse duration
                    duration = item.get("contentDetails", {}).get("duration", "PT0S")
                    duration_seconds = self._parse_duration(duration)

                    # Parse publish date
                    published_at = item["snippet"]["publishedAt"]
                    publish_date = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                    days_since_posted = (datetime.now(publish_date.tzinfo) - publish_date).days
                    if days_since_posted < 1:
                        days_since_posted = 1

                    channel_id = item["snippet"]["channelId"]
                    channel_ids.add(channel_id)

                    views = int(item["statistics"].get("viewCount", 0))

                    video_data = {
                        "video_id": item["id"],
                        "title": item["snippet"]["title"],
                        "description": item["snippet"].get("description", ""),
                        "channel_id": channel_id,
                        "channel_title": item["snippet"]["channelTitle"],
                        "published_at": published_at,
                        "days_since_posted": days_since_posted,
                        "url": f"https://www.youtube.com/watch?v={item['id']}",
                        "thumbnail": item["snippet"]["thumbnails"].get("high", {}).get("url", ""),
                        "views": views,
                        "likes": int(item["statistics"].get("likeCount", 0)),
                        "comments": int(item["statistics"].get("commentCount", 0)),
                        "duration_seconds": duration_seconds,
                        "duration_formatted": self._format_duration(duration_seconds),
                        "views_per_day": views // days_since_posted,
                        "category_id": item["snippet"].get("categoryId", ""),
                    }
                    videos.append(video_data)

            except HttpError as e:
                print(f"YouTube API error fetching details: {e}")
                continue

        # Get channel stats and calculate outlier scores
        if include_channel_stats and channel_ids:
            channel_stats = self.get_channel_stats(list(channel_ids))

            for video in videos:
                ch_stats = channel_stats.get(video["channel_id"], {})
                video["channel_subscribers"] = ch_stats.get("subscribers", 0)
                video["channel_avg_views"] = ch_stats.get("avg_views", 0)
                video["channel_video_count"] = ch_stats.get("video_count", 0)

                # Calculate outlier score
                avg_views = ch_stats.get("avg_views", 1)
                if avg_views > 0:
                    video["outlier_score"] = round(video["views"] / avg_views, 2)
                else:
                    video["outlier_score"] = 0

                # Categorize channel size
                subs = video["channel_subscribers"]
                if subs < 10000:
                    video["channel_size"] = "Micro"
                elif subs < 100000:
                    video["channel_size"] = "Small"
                elif subs < 1000000:
                    video["channel_size"] = "Medium"
                else:
                    video["channel_size"] = "Large"

        return videos

    def _parse_duration(self, duration: str) -> int:
        """Parse ISO 8601 duration to seconds."""
        import re
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if not match:
            return 0
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        return hours * 3600 + minutes * 60 + seconds

    def _format_duration(self, seconds: int) -> str:
        """Format seconds to human readable duration."""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m {seconds % 60}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"


def search_youtube_videos(query: str, api_key: Optional[str] = None,
                          include_channel_stats: bool = True) -> list:
    """
    Convenience function to search YouTube and get video details.
    """
    searcher = YouTubeSearcher(api_key)
    video_ids = searcher.search_videos(query)
    videos = searcher.get_video_details(video_ids, include_channel_stats)
    return videos
