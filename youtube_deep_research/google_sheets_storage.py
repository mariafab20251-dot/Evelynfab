"""
Google Sheets integration for storing research results.
"""

import os
from typing import Optional
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import (
    GOOGLE_SHEETS_CREDENTIALS_FILE,
    GOOGLE_SHEETS_SPREADSHEET_ID,
    GOOGLE_SHEETS_SHEET_NAME
)


class GoogleSheetsStorage:
    """Stores video research results in Google Sheets."""

    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    def __init__(self, credentials_file: Optional[str] = None,
                 spreadsheet_id: Optional[str] = None,
                 sheet_name: Optional[str] = None):
        """Initialize Google Sheets client."""
        self.credentials_file = credentials_file or GOOGLE_SHEETS_CREDENTIALS_FILE
        self.spreadsheet_id = spreadsheet_id or GOOGLE_SHEETS_SPREADSHEET_ID
        self.sheet_name = sheet_name or GOOGLE_SHEETS_SHEET_NAME

        self.service = None

        if not self.credentials_file or not os.path.exists(self.credentials_file):
            print("Warning: Google Sheets credentials file not found. Storage will be skipped.")
        elif not self.spreadsheet_id:
            print("Warning: Google Sheets spreadsheet ID not set. Storage will be skipped.")
        else:
            self._init_service()

    def _init_service(self):
        """Initialize the Google Sheets API service."""
        try:
            credentials = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=self.SCOPES
            )
            self.service = build("sheets", "v4", credentials=credentials)
        except Exception as e:
            print(f"Error initializing Google Sheets service: {e}")
            self.service = None

    def _ensure_headers(self):
        """Ensure the sheet has headers in the first row."""
        if not self.service:
            return

        headers = [
            "Video Name", "URL", "Channel", "Views", "Likes",
            "Comments", "Like Ratio", "Comment Ratio", "Published"
        ]

        try:
            # Check if headers exist
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!A1:I1"
            ).execute()

            existing = result.get("values", [])

            if not existing or existing[0] != headers:
                # Add headers
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"{self.sheet_name}!A1:I1",
                    valueInputOption="RAW",
                    body={"values": [headers]}
                ).execute()
                print("Added headers to Google Sheet")

        except HttpError as e:
            if e.resp.status == 404:
                # Sheet might not exist, try to add headers anyway
                try:
                    self.service.spreadsheets().values().update(
                        spreadsheetId=self.spreadsheet_id,
                        range=f"{self.sheet_name}!A1:I1",
                        valueInputOption="RAW",
                        body={"values": [headers]}
                    ).execute()
                except Exception:
                    pass
            else:
                print(f"Error checking headers: {e}")

    def store_videos(self, videos: list) -> int:
        """
        Store multiple videos in Google Sheets.

        Args:
            videos: List of video dictionaries

        Returns:
            Number of rows added
        """
        if not self.service or not self.spreadsheet_id:
            print("Skipping Google Sheets storage (missing credentials)")
            return 0

        if not videos:
            return 0

        # Ensure headers exist
        self._ensure_headers()

        # Prepare rows
        rows = []
        for video in videos:
            row = [
                video.get("title", ""),
                video.get("url", ""),
                video.get("channel_title", ""),
                video.get("views", 0),
                video.get("likes", 0),
                video.get("comments", 0),
                video.get("like_ratio_percent", ""),
                video.get("comment_ratio_percent", ""),
                video.get("published_at", "")
            ]
            rows.append(row)

        try:
            # Append rows to sheet
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!A:I",
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body={"values": rows}
            ).execute()

            updates = result.get("updates", {})
            updated_rows = updates.get("updatedRows", 0)
            print(f"Stored {updated_rows} videos to Google Sheets")
            return updated_rows

        except HttpError as e:
            print(f"Google Sheets API error: {e}")
            return 0
        except Exception as e:
            print(f"Google Sheets storage error: {e}")
            return 0

    def get_spreadsheet_url(self) -> str:
        """Get the URL to the Google Spreadsheet."""
        return f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}"


def store_to_google_sheets(videos: list,
                           credentials_file: Optional[str] = None,
                           spreadsheet_id: Optional[str] = None,
                           sheet_name: Optional[str] = None) -> int:
    """
    Convenience function to store videos in Google Sheets.

    Args:
        videos: List of video dictionaries
        credentials_file: Path to service account JSON file
        spreadsheet_id: Google Sheets spreadsheet ID
        sheet_name: Sheet name within spreadsheet

    Returns:
        Number of rows added
    """
    storage = GoogleSheetsStorage(credentials_file, spreadsheet_id, sheet_name)
    return storage.store_videos(videos)
