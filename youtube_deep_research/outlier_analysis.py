"""
Outlier analysis and advanced filtering for viral video detection.
"""

from typing import Optional
import re


def filter_by_outlier_score(videos: list, min_score: float = 2.0, max_score: float = None) -> list:
    """
    Filter videos by outlier score (views / channel average views).

    Args:
        videos: List of video dictionaries
        min_score: Minimum outlier score (e.g., 2.0 = 2x average)
        max_score: Maximum outlier score (optional)

    Returns:
        Filtered list of videos
    """
    filtered = []
    for video in videos:
        score = video.get("outlier_score", 0)
        if score >= min_score:
            if max_score is None or score <= max_score:
                filtered.append(video)
    return filtered


def filter_by_channel_size(videos: list, sizes: list = None) -> list:
    """
    Filter videos by channel size category.

    Args:
        videos: List of video dictionaries
        sizes: List of sizes to include ["Micro", "Small", "Medium", "Large"]

    Returns:
        Filtered list of videos
    """
    if not sizes:
        return videos

    return [v for v in videos if v.get("channel_size", "") in sizes]


def filter_by_subscribers(videos: list, min_subs: int = 0, max_subs: int = None) -> list:
    """
    Filter videos by channel subscriber count.
    """
    filtered = []
    for video in videos:
        subs = video.get("channel_subscribers", 0)
        if subs >= min_subs:
            if max_subs is None or subs <= max_subs:
                filtered.append(video)
    return filtered


def filter_by_velocity(videos: list, min_views_per_day: int = 100) -> list:
    """
    Filter videos by view velocity (views per day since posted).
    """
    return [v for v in videos if v.get("views_per_day", 0) >= min_views_per_day]


def filter_by_duration(videos: list, min_seconds: int = 0, max_seconds: int = None,
                       duration_type: str = None) -> list:
    """
    Filter videos by duration.

    Args:
        duration_type: "short" (<60s), "medium" (1-20min), "long" (>20min)
    """
    if duration_type:
        if duration_type == "short":
            min_seconds, max_seconds = 0, 60
        elif duration_type == "medium":
            min_seconds, max_seconds = 60, 1200
        elif duration_type == "long":
            min_seconds, max_seconds = 1200, None

    filtered = []
    for video in videos:
        duration = video.get("duration_seconds", 0)
        if duration >= min_seconds:
            if max_seconds is None or duration <= max_seconds:
                filtered.append(video)
    return filtered


def analyze_title_patterns(videos: list) -> list:
    """
    Analyze titles for viral patterns and add pattern scores.
    """
    patterns = {
        "numbers": r'\b\d+\b',
        "question": r'\?',
        "how_to": r'\bhow\s+to\b',
        "list": r'\b(top|best|\d+\s+(ways|tips|tricks|things))\b',
        "emotional": r'\b(shocking|amazing|incredible|unbelievable|secret|revealed)\b',
        "year": r'\b20\d{2}\b',
        "brackets": r'[\[\(].+[\]\)]',
        "capitalized": r'\b[A-Z]{3,}\b',
    }

    for video in videos:
        title = video.get("title", "").lower()
        pattern_matches = []
        pattern_score = 0

        for pattern_name, regex in patterns.items():
            if re.search(regex, title, re.IGNORECASE):
                pattern_matches.append(pattern_name)
                pattern_score += 1

        video["title_patterns"] = pattern_matches
        video["title_pattern_score"] = pattern_score

    return videos


def calculate_viral_score(videos: list) -> list:
    """
    Calculate overall viral potential score combining multiple factors.
    """
    for video in videos:
        # Weights for different factors
        outlier_weight = 3
        velocity_weight = 2
        engagement_weight = 2
        pattern_weight = 1

        # Normalize scores (0-10 scale)
        outlier = min(video.get("outlier_score", 0) / 10, 10)
        velocity = min(video.get("views_per_day", 0) / 10000, 10)

        # Engagement score
        views = video.get("views", 1)
        likes = video.get("likes", 0)
        comments = video.get("comments", 0)
        engagement = min(((likes + comments * 2) / views) * 100, 10) if views > 0 else 0

        # Pattern score
        patterns = min(video.get("title_pattern_score", 0) * 2, 10)

        # Calculate weighted viral score
        viral_score = (
            (outlier * outlier_weight) +
            (velocity * velocity_weight) +
            (engagement * engagement_weight) +
            (patterns * pattern_weight)
        ) / (outlier_weight + velocity_weight + engagement_weight + pattern_weight)

        video["viral_score"] = round(viral_score, 2)

        # Categorize viral potential
        if viral_score >= 7:
            video["viral_potential"] = "🔥 Hot"
        elif viral_score >= 5:
            video["viral_potential"] = "⭐ Good"
        elif viral_score >= 3:
            video["viral_potential"] = "👍 Okay"
        else:
            video["viral_potential"] = "📊 Low"

    return videos


def sort_by_viral_score(videos: list, reverse: bool = True) -> list:
    """Sort videos by viral score."""
    return sorted(videos, key=lambda v: v.get("viral_score", 0), reverse=reverse)


def sort_by_outlier_score(videos: list, reverse: bool = True) -> list:
    """Sort videos by outlier score."""
    return sorted(videos, key=lambda v: v.get("outlier_score", 0), reverse=reverse)


def sort_by_velocity(videos: list, reverse: bool = True) -> list:
    """Sort videos by view velocity."""
    return sorted(videos, key=lambda v: v.get("views_per_day", 0), reverse=reverse)


def get_content_opportunities(videos: list) -> list:
    """
    Find content opportunities: high outlier score + small channel.
    These represent topics where content is performing well even without
    a large existing audience.
    """
    opportunities = []

    for video in videos:
        outlier = video.get("outlier_score", 0)
        subs = video.get("channel_subscribers", 0)

        # High performance from small channel = opportunity
        if outlier >= 3 and subs < 100000:
            opportunity_score = outlier * (1 + (100000 - subs) / 100000)
            video["opportunity_score"] = round(opportunity_score, 2)
            opportunities.append(video)

    return sorted(opportunities, key=lambda v: v.get("opportunity_score", 0), reverse=True)


def format_number(num: int) -> str:
    """Format large numbers for display."""
    if num >= 1000000:
        return f"{num / 1000000:.1f}M"
    elif num >= 1000:
        return f"{num / 1000:.1f}K"
    else:
        return str(num)
