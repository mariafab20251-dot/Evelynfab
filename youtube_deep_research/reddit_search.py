"""
Reddit API integration for searching viral posts.
"""

import praw
from datetime import datetime, timedelta
from typing import Optional

from config import (
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_SECRET,
    REDDIT_USER_AGENT
)


class RedditSearcher:
    """Handles Reddit API interactions for finding viral posts."""

    def __init__(self, client_id: Optional[str] = None,
                 client_secret: Optional[str] = None,
                 user_agent: Optional[str] = None):
        """Initialize Reddit API client."""
        self.client_id = client_id or REDDIT_CLIENT_ID
        self.client_secret = client_secret or REDDIT_CLIENT_SECRET
        self.user_agent = user_agent or REDDIT_USER_AGENT

        if not self.client_id or not self.client_secret:
            raise ValueError("Reddit API credentials required. Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET.")

        self.reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent
        )

    def search_posts(self, query: str, subreddit: str = "all",
                     sort: str = "hot", time_filter: str = "week",
                     limit: int = 50) -> list:
        """
        Search Reddit for posts matching the query.

        Args:
            query: Search term (e.g., "Taylor Swift")
            subreddit: Subreddit to search ("all" for all Reddit)
            sort: Sort method (hot, new, top, rising)
            time_filter: Time filter for top posts (hour, day, week, month, year, all)
            limit: Maximum number of results

        Returns:
            List of post data dictionaries
        """
        posts = []

        try:
            subreddit_obj = self.reddit.subreddit(subreddit)

            if sort == "top":
                submissions = subreddit_obj.search(query, sort=sort, time_filter=time_filter, limit=limit)
            else:
                submissions = subreddit_obj.search(query, sort=sort, limit=limit)

            for submission in submissions:
                post_data = {
                    "id": submission.id,
                    "title": submission.title,
                    "subreddit": submission.subreddit.display_name,
                    "author": str(submission.author) if submission.author else "[deleted]",
                    "score": submission.score,
                    "upvote_ratio": submission.upvote_ratio,
                    "num_comments": submission.num_comments,
                    "url": f"https://reddit.com{submission.permalink}",
                    "created_utc": datetime.utcfromtimestamp(submission.created_utc).isoformat(),
                    "is_video": submission.is_video,
                    "thumbnail": submission.thumbnail if submission.thumbnail.startswith("http") else "",
                    "selftext": submission.selftext[:500] if submission.selftext else "",
                    "link_url": submission.url if not submission.is_self else ""
                }

                # Calculate engagement score
                post_data["engagement_score"] = (
                    post_data["score"] + (post_data["num_comments"] * 2)
                ) * post_data["upvote_ratio"]

                posts.append(post_data)

        except Exception as e:
            print(f"Reddit API error: {e}")

        return posts

    def get_trending_subreddits(self, limit: int = 10) -> list:
        """Get trending subreddits."""
        try:
            trending = []
            for subreddit in self.reddit.subreddits.popular(limit=limit):
                trending.append({
                    "name": subreddit.display_name,
                    "title": subreddit.title,
                    "subscribers": subreddit.subscribers,
                    "description": subreddit.public_description[:200]
                })
            return trending
        except Exception as e:
            print(f"Error getting trending subreddits: {e}")
            return []

    def get_hot_posts(self, subreddit: str = "all", limit: int = 25) -> list:
        """Get hot posts from a subreddit."""
        posts = []

        try:
            for submission in self.reddit.subreddit(subreddit).hot(limit=limit):
                post_data = {
                    "id": submission.id,
                    "title": submission.title,
                    "subreddit": submission.subreddit.display_name,
                    "author": str(submission.author) if submission.author else "[deleted]",
                    "score": submission.score,
                    "upvote_ratio": submission.upvote_ratio,
                    "num_comments": submission.num_comments,
                    "url": f"https://reddit.com{submission.permalink}",
                    "created_utc": datetime.utcfromtimestamp(submission.created_utc).isoformat(),
                    "engagement_score": (submission.score + submission.num_comments * 2) * submission.upvote_ratio
                }
                posts.append(post_data)

        except Exception as e:
            print(f"Reddit API error: {e}")

        return posts


def search_reddit(query: str, subreddit: str = "all",
                  sort: str = "hot", time_filter: str = "week",
                  limit: int = 50) -> list:
    """
    Convenience function to search Reddit.

    Args:
        query: Search term
        subreddit: Subreddit to search
        sort: Sort method
        time_filter: Time filter
        limit: Max results

    Returns:
        List of viral posts
    """
    searcher = RedditSearcher()
    posts = searcher.search_posts(query, subreddit, sort, time_filter, limit)

    # Sort by engagement score
    posts.sort(key=lambda x: x.get("engagement_score", 0), reverse=True)

    return posts


def filter_reddit_posts(posts: list, min_score: int = 100,
                        min_comments: int = 10,
                        min_upvote_ratio: float = 0.7) -> list:
    """
    Filter Reddit posts by engagement thresholds.

    Args:
        posts: List of post dictionaries
        min_score: Minimum score (upvotes)
        min_comments: Minimum number of comments
        min_upvote_ratio: Minimum upvote ratio (0-1)

    Returns:
        Filtered list of posts
    """
    return [
        post for post in posts
        if post.get("score", 0) >= min_score
        and post.get("num_comments", 0) >= min_comments
        and post.get("upvote_ratio", 0) >= min_upvote_ratio
    ]
