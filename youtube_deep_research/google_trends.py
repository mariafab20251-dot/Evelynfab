"""
Google Trends integration for finding trending topics.
"""

from pytrends.request import TrendReq
from typing import Optional
import pandas as pd


class GoogleTrendsSearcher:
    """Handles Google Trends API for finding trending topics."""

    def __init__(self, hl: str = "en-US", tz: int = 360):
        """
        Initialize Google Trends client.

        Args:
            hl: Language (e.g., "en-US")
            tz: Timezone offset in minutes
        """
        self.pytrends = TrendReq(hl=hl, tz=tz)

    def get_trending_searches(self, country: str = "united_states") -> list:
        """
        Get daily trending searches for a country.

        Args:
            country: Country name (e.g., "united_states", "united_kingdom", "india")

        Returns:
            List of trending search terms
        """
        try:
            df = self.pytrends.trending_searches(pn=country)
            return df[0].tolist()
        except Exception as e:
            print(f"Google Trends error: {e}")
            return []

    def get_realtime_trends(self, country: str = "US", category: str = "all") -> list:
        """
        Get realtime trending topics.

        Args:
            country: Country code (e.g., "US", "GB", "IN")
            category: Category (all, e, b, t, m, s, h)
                     e=entertainment, b=business, t=technology,
                     m=health, s=sports, h=top stories

        Returns:
            List of trending topics with details
        """
        try:
            df = self.pytrends.realtime_trending_searches(pn=country, cat=category)

            trends = []
            for _, row in df.iterrows():
                trend = {
                    "title": row.get("title", ""),
                    "entityNames": row.get("entityNames", []),
                    "articles": row.get("articles", [])
                }
                trends.append(trend)

            return trends[:20]  # Limit to top 20
        except Exception as e:
            print(f"Realtime trends error: {e}")
            return []

    def get_interest_over_time(self, keywords: list, timeframe: str = "today 3-m",
                                geo: str = "") -> dict:
        """
        Get interest over time for keywords.

        Args:
            keywords: List of search terms (max 5)
            timeframe: Time range (e.g., "today 3-m", "today 12-m", "2023-01-01 2023-12-31")
            geo: Country code (e.g., "US", "GB", empty for worldwide)

        Returns:
            Dictionary with interest data
        """
        try:
            self.pytrends.build_payload(keywords[:5], cat=0, timeframe=timeframe, geo=geo)
            df = self.pytrends.interest_over_time()

            if df.empty:
                return {}

            result = {
                "keywords": keywords[:5],
                "timeframe": timeframe,
                "geo": geo or "Worldwide",
                "data": []
            }

            for date, row in df.iterrows():
                data_point = {"date": date.strftime("%Y-%m-%d")}
                for kw in keywords[:5]:
                    if kw in df.columns:
                        data_point[kw] = int(row[kw])
                result["data"].append(data_point)

            return result

        except Exception as e:
            print(f"Interest over time error: {e}")
            return {}

    def get_related_queries(self, keyword: str, geo: str = "") -> dict:
        """
        Get related queries for a keyword.

        Args:
            keyword: Search term
            geo: Country code

        Returns:
            Dictionary with top and rising queries
        """
        try:
            self.pytrends.build_payload([keyword], geo=geo)
            related = self.pytrends.related_queries()

            result = {
                "keyword": keyword,
                "top": [],
                "rising": []
            }

            if keyword in related:
                # Top queries
                top_df = related[keyword].get("top")
                if top_df is not None and not top_df.empty:
                    result["top"] = top_df.to_dict("records")

                # Rising queries
                rising_df = related[keyword].get("rising")
                if rising_df is not None and not rising_df.empty:
                    result["rising"] = rising_df.to_dict("records")

            return result

        except Exception as e:
            print(f"Related queries error: {e}")
            return {"keyword": keyword, "top": [], "rising": []}

    def get_interest_by_region(self, keyword: str, geo: str = "",
                                resolution: str = "COUNTRY") -> list:
        """
        Get interest by region for a keyword.

        Args:
            keyword: Search term
            geo: Country code (empty for worldwide)
            resolution: COUNTRY, REGION, CITY, DMA

        Returns:
            List of regions with interest scores
        """
        try:
            self.pytrends.build_payload([keyword], geo=geo)
            df = self.pytrends.interest_by_region(resolution=resolution)

            if df.empty:
                return []

            regions = []
            for region, row in df.iterrows():
                if row[keyword] > 0:
                    regions.append({
                        "region": region,
                        "interest": int(row[keyword])
                    })

            # Sort by interest
            regions.sort(key=lambda x: x["interest"], reverse=True)
            return regions[:20]

        except Exception as e:
            print(f"Interest by region error: {e}")
            return []


def get_trending_now(country: str = "united_states") -> list:
    """
    Get currently trending searches.

    Args:
        country: Country name

    Returns:
        List of trending search terms
    """
    searcher = GoogleTrendsSearcher()
    return searcher.get_trending_searches(country)


def compare_trends(keywords: list, country: str = "", timeframe: str = "today 3-m") -> dict:
    """
    Compare interest for multiple keywords.

    Args:
        keywords: List of keywords to compare (max 5)
        country: Country code
        timeframe: Time range

    Returns:
        Comparison data
    """
    searcher = GoogleTrendsSearcher()
    return searcher.get_interest_over_time(keywords, timeframe, country)


def get_related_topics(keyword: str, country: str = "") -> dict:
    """
    Get related queries for a topic.

    Args:
        keyword: Search term
        country: Country code

    Returns:
        Related queries (top and rising)
    """
    searcher = GoogleTrendsSearcher()
    return searcher.get_related_queries(keyword, country)


# Country code mapping
COUNTRY_CODES = {
    "united_states": "US",
    "united_kingdom": "GB",
    "canada": "CA",
    "australia": "AU",
    "india": "IN",
    "germany": "DE",
    "france": "FR",
    "brazil": "BR",
    "japan": "JP",
    "south_korea": "KR",
    "pakistan": "PK",
    "bangladesh": "BD"
}
