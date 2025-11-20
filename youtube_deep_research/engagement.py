"""
Engagement ratio calculations and filtering.
"""

from typing import Optional
from config import MIN_LIKE_RATIO, MIN_COMMENT_RATIO, MIN_VIEWS


def calculate_engagement_ratios(videos: list) -> list:
    """
    Calculate engagement ratios for each video.

    Args:
        videos: List of video dictionaries with views, likes, comments

    Returns:
        Videos with added engagement ratio fields
    """
    for video in videos:
        views = video.get("views", 0)
        likes = video.get("likes", 0)
        comments = video.get("comments", 0)

        # Calculate ratios (avoid division by zero)
        if views > 0:
            video["like_ratio"] = likes / views
            video["comment_ratio"] = comments / views
        else:
            video["like_ratio"] = 0
            video["comment_ratio"] = 0

        # Format as percentages for display
        video["like_ratio_percent"] = f"{video['like_ratio'] * 100:.2f}%"
        video["comment_ratio_percent"] = f"{video['comment_ratio'] * 100:.2f}%"

    return videos


def filter_by_engagement(videos: list,
                         min_like_ratio: Optional[float] = None,
                         min_comment_ratio: Optional[float] = None,
                         min_views: Optional[int] = None) -> list:
    """
    Filter videos based on engagement thresholds.

    Args:
        videos: List of videos with engagement ratios
        min_like_ratio: Minimum like ratio (e.g., 0.05 for 5%)
        min_comment_ratio: Minimum comment ratio (e.g., 0.002 for 0.2%)
        min_views: Minimum view count

    Returns:
        Filtered list of high-engagement videos
    """
    # Use defaults from config if not specified
    if min_like_ratio is None:
        min_like_ratio = MIN_LIKE_RATIO
    if min_comment_ratio is None:
        min_comment_ratio = MIN_COMMENT_RATIO
    if min_views is None:
        min_views = MIN_VIEWS

    filtered = []

    for video in videos:
        # Check all engagement criteria
        if (video.get("like_ratio", 0) >= min_like_ratio and
            video.get("comment_ratio", 0) >= min_comment_ratio and
            video.get("views", 0) >= min_views):
            filtered.append(video)

    return filtered


def remove_duplicates(videos: list) -> list:
    """
    Remove duplicate videos based on video_id.

    Args:
        videos: List of video dictionaries

    Returns:
        Deduplicated list of videos
    """
    seen_ids = set()
    unique_videos = []

    for video in videos:
        video_id = video.get("video_id")
        if video_id and video_id not in seen_ids:
            seen_ids.add(video_id)
            unique_videos.append(video)

    return unique_videos


def sort_by_engagement(videos: list, key: str = "like_ratio", reverse: bool = True) -> list:
    """
    Sort videos by engagement metric.

    Args:
        videos: List of videos with engagement ratios
        key: Metric to sort by (like_ratio, comment_ratio, views)
        reverse: Sort descending if True

    Returns:
        Sorted list of videos
    """
    return sorted(videos, key=lambda v: v.get(key, 0), reverse=reverse)
