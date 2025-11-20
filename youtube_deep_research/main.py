#!/usr/bin/env python3
"""
YouTube Deep Research Agent

A Python implementation of the n8n workflow for finding high-engagement
YouTube videos on specific topics.

Usage:
    python main.py "Best SaaS Business"
    python main.py --topic "AI Tools" --days 14 --min-views 5000
"""

import argparse
import json
import sys
from typing import Optional

from youtube_search import search_youtube_videos
from engagement import (
    calculate_engagement_ratios,
    filter_by_engagement,
    remove_duplicates,
    sort_by_engagement
)
from language_validator import validate_english_videos
from google_sheets_storage import store_to_google_sheets
from config import (
    MIN_LIKE_RATIO,
    MIN_COMMENT_RATIO,
    MIN_VIEWS,
    SEARCH_DAYS_AGO
)


def run_youtube_research(
    topic: str,
    days_ago: int = SEARCH_DAYS_AGO,
    min_views: int = MIN_VIEWS,
    min_like_ratio: float = MIN_LIKE_RATIO,
    min_comment_ratio: float = MIN_COMMENT_RATIO,
    validate_language: bool = True,
    save_to_sheets: bool = True,
    output_json: Optional[str] = None
) -> list:
    """
    Run the complete YouTube research pipeline.

    Args:
        topic: Search topic (e.g., "Best SaaS Business")
        days_ago: Number of days to look back
        min_views: Minimum view count threshold
        min_like_ratio: Minimum like ratio (e.g., 0.05 for 5%)
        min_comment_ratio: Minimum comment ratio (e.g., 0.002 for 0.2%)
        validate_language: Whether to validate English titles
        save_to_sheets: Whether to save results to Google Sheets
        output_json: Optional path to save results as JSON

    Returns:
        List of high-engagement videos
    """
    print(f"\n{'='*60}")
    print(f"YouTube Deep Research Agent")
    print(f"{'='*60}")
    print(f"Topic: {topic}")
    print(f"Looking back: {days_ago} days")
    print(f"Thresholds: {min_views}+ views, {min_like_ratio*100}%+ likes, {min_comment_ratio*100}%+ comments")
    print(f"{'='*60}\n")

    # Step 1: Search YouTube
    print("Step 1: Searching YouTube...")
    videos = search_youtube_videos(topic)
    print(f"  Found {len(videos)} videos")

    if not videos:
        print("No videos found. Check your API key and search term.")
        return []

    # Step 2: Calculate engagement ratios
    print("\nStep 2: Calculating engagement ratios...")
    videos = calculate_engagement_ratios(videos)
    print(f"  Calculated ratios for {len(videos)} videos")

    # Step 3: Filter by engagement
    print("\nStep 3: Filtering by engagement thresholds...")
    videos = filter_by_engagement(
        videos,
        min_like_ratio=min_like_ratio,
        min_comment_ratio=min_comment_ratio,
        min_views=min_views
    )
    print(f"  {len(videos)} videos passed engagement filters")

    if not videos:
        print("No videos met the engagement criteria.")
        return []

    # Step 4: Remove duplicates
    print("\nStep 4: Removing duplicates...")
    videos = remove_duplicates(videos)
    print(f"  {len(videos)} unique videos")

    # Step 5: Validate language (optional)
    if validate_language:
        print("\nStep 5: Validating English titles...")
        videos = validate_english_videos(videos)
        print(f"  {len(videos)} English videos")

    # Step 6: Sort by engagement
    print("\nStep 6: Sorting by engagement...")
    videos = sort_by_engagement(videos, key="like_ratio")

    # Step 7: Store in Google Sheets (optional)
    if save_to_sheets:
        print("\nStep 7: Storing in Google Sheets...")
        rows_added = store_to_google_sheets(videos)
        print(f"  Stored {rows_added} records")

    # Save to JSON (optional)
    if output_json:
        print(f"\nSaving results to {output_json}...")
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(videos, f, indent=2, ensure_ascii=False)
        print(f"  Saved {len(videos)} videos to JSON")

    # Print results summary
    print(f"\n{'='*60}")
    print(f"Results: {len(videos)} high-engagement videos found")
    print(f"{'='*60}\n")

    for i, video in enumerate(videos[:10], 1):  # Show top 10
        print(f"{i}. {video['title'][:60]}...")
        print(f"   Views: {video['views']:,} | Likes: {video['like_ratio_percent']} | Comments: {video['comment_ratio_percent']}")
        print(f"   URL: {video['url']}")
        print()

    if len(videos) > 10:
        print(f"... and {len(videos) - 10} more videos")

    return videos


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="YouTube Deep Research Agent - Find high-engagement videos"
    )

    parser.add_argument(
        "topic",
        nargs="?",
        help="Search topic (e.g., 'Best SaaS Business')"
    )

    parser.add_argument(
        "--topic", "-t",
        dest="topic_flag",
        help="Search topic (alternative to positional argument)"
    )

    parser.add_argument(
        "--days", "-d",
        type=int,
        default=SEARCH_DAYS_AGO,
        help=f"Days to look back (default: {SEARCH_DAYS_AGO})"
    )

    parser.add_argument(
        "--min-views", "-v",
        type=int,
        default=MIN_VIEWS,
        help=f"Minimum views (default: {MIN_VIEWS})"
    )

    parser.add_argument(
        "--min-likes", "-l",
        type=float,
        default=MIN_LIKE_RATIO * 100,
        help=f"Minimum like ratio %% (default: {MIN_LIKE_RATIO * 100})"
    )

    parser.add_argument(
        "--min-comments", "-c",
        type=float,
        default=MIN_COMMENT_RATIO * 100,
        help=f"Minimum comment ratio %% (default: {MIN_COMMENT_RATIO * 100})"
    )

    parser.add_argument(
        "--no-language-check",
        action="store_true",
        help="Skip language validation"
    )

    parser.add_argument(
        "--no-sheets",
        action="store_true",
        help="Skip saving to Google Sheets"
    )

    parser.add_argument(
        "--output", "-o",
        help="Save results to JSON file"
    )

    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode (prompt for topic)"
    )

    args = parser.parse_args()

    # Get topic from arguments or interactive input
    topic = args.topic or args.topic_flag

    if args.interactive or not topic:
        topic = input("Enter search topic: ").strip()
        if not topic:
            print("Error: Topic is required")
            sys.exit(1)

    # Run the research pipeline
    videos = run_youtube_research(
        topic=topic,
        days_ago=args.days,
        min_views=args.min_views,
        min_like_ratio=args.min_likes / 100,
        min_comment_ratio=args.min_comments / 100,
        validate_language=not args.no_language_check,
        save_to_sheets=not args.no_sheets,
        output_json=args.output
    )

    return 0 if videos else 1


if __name__ == "__main__":
    sys.exit(main())
