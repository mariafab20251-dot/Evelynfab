"""
Transcript extraction and AI summarization for YouTube videos.
"""

import requests
from typing import Optional

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
    TRANSCRIPT_API_AVAILABLE = True
except ImportError:
    TRANSCRIPT_API_AVAILABLE = False

from config import OPENROUTER_API_KEY, OPENROUTER_MODEL


def get_video_transcript(video_id: str, languages: list = None) -> dict:
    """
    Extract transcript from a YouTube video.

    Returns dict with:
    - transcript: full text
    - segments: list of {text, start, duration}
    - language: detected language
    """
    if not TRANSCRIPT_API_AVAILABLE:
        return {"error": "youtube-transcript-api not installed. Run: pip install youtube-transcript-api"}

    if languages is None:
        languages = ['en', 'en-US', 'en-GB']

    try:
        # Try to get transcript
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Try manual transcripts first, then auto-generated
        transcript = None
        try:
            transcript = transcript_list.find_manually_created_transcript(languages)
        except:
            try:
                transcript = transcript_list.find_generated_transcript(languages)
            except:
                # Try any available transcript
                for t in transcript_list:
                    transcript = t
                    break

        if not transcript:
            return {"error": "No transcript available for this video"}

        # Fetch the transcript
        segments = transcript.fetch()

        # Combine into full text
        full_text = " ".join([seg['text'] for seg in segments])

        return {
            "transcript": full_text,
            "segments": segments,
            "language": transcript.language,
            "language_code": transcript.language_code,
            "is_generated": transcript.is_generated
        }

    except TranscriptsDisabled:
        return {"error": "Transcripts are disabled for this video"}
    except NoTranscriptFound:
        return {"error": "No transcript found for this video"}
    except Exception as e:
        return {"error": f"Error fetching transcript: {str(e)}"}


def summarize_transcript(transcript: str, video_title: str = "",
                         summary_type: str = "detailed") -> dict:
    """
    Use AI to summarize the transcript.

    summary_type: "brief", "detailed", "bullet_points", "key_topics"
    """
    if not OPENROUTER_API_KEY:
        return {"error": "OpenRouter API key not configured"}

    if not transcript:
        return {"error": "No transcript provided"}

    # Truncate if too long (most models have context limits)
    max_chars = 15000
    if len(transcript) > max_chars:
        transcript = transcript[:max_chars] + "... [truncated]"

    # Create prompt based on summary type
    if summary_type == "brief":
        prompt = f"""Summarize this YouTube video transcript in 2-3 sentences:

Title: {video_title}

Transcript:
{transcript}

Brief Summary:"""

    elif summary_type == "bullet_points":
        prompt = f"""Extract the key points from this YouTube video as bullet points:

Title: {video_title}

Transcript:
{transcript}

Key Points:
-"""

    elif summary_type == "key_topics":
        prompt = f"""List the main topics and themes discussed in this video:

Title: {video_title}

Transcript:
{transcript}

Main Topics:
1."""

    else:  # detailed
        prompt = f"""Provide a detailed summary of this YouTube video transcript. Include:
- Main topic and purpose
- Key points discussed
- Important details and examples
- Conclusion or takeaway

Title: {video_title}

Transcript:
{transcript}

Detailed Summary:"""

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": OPENROUTER_MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1000
            },
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            summary = result["choices"][0]["message"]["content"]
            return {
                "summary": summary,
                "summary_type": summary_type,
                "model": OPENROUTER_MODEL
            }
        else:
            return {"error": f"API error: {response.status_code} - {response.text}"}

    except Exception as e:
        return {"error": f"Error generating summary: {str(e)}"}


def extract_video_content(video_id: str, title: str = "", tags: list = None,
                          include_summary: bool = True) -> dict:
    """
    Extract complete content from a video including transcript and summary.
    """
    result = {
        "video_id": video_id,
        "title": title,
        "tags": tags or [],
        "transcript": None,
        "summary": None,
        "error": None
    }

    # Get transcript
    transcript_result = get_video_transcript(video_id)

    if "error" in transcript_result:
        result["error"] = transcript_result["error"]
        return result

    result["transcript"] = transcript_result["transcript"]
    result["language"] = transcript_result.get("language", "")
    result["is_auto_generated"] = transcript_result.get("is_generated", False)

    # Generate summary if requested
    if include_summary and OPENROUTER_API_KEY:
        summary_result = summarize_transcript(
            transcript_result["transcript"],
            title,
            "detailed"
        )

        if "error" not in summary_result:
            result["summary"] = summary_result["summary"]

    return result


def batch_extract_content(videos: list, include_summary: bool = True,
                          progress_callback=None) -> list:
    """
    Extract content from multiple videos.

    videos: list of dicts with video_id, title, tags
    progress_callback: function(current, total, video_title)
    """
    results = []
    total = len(videos)

    for i, video in enumerate(videos):
        if progress_callback:
            progress_callback(i + 1, total, video.get("title", ""))

        result = extract_video_content(
            video.get("video_id", ""),
            video.get("title", ""),
            video.get("tags", []),
            include_summary
        )

        # Add original video data
        result["url"] = video.get("url", "")
        result["views"] = video.get("views", 0)
        result["channel_title"] = video.get("channel_title", "")

        results.append(result)

    return results


def export_content_report(videos_content: list, filename: str):
    """
    Export extracted content to a formatted text file.
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("VIRAL VIDEO CONTENT REPORT\n")
        f.write("=" * 80 + "\n\n")

        for i, video in enumerate(videos_content, 1):
            f.write(f"\n{'=' * 80}\n")
            f.write(f"VIDEO {i}: {video.get('title', 'Unknown')}\n")
            f.write(f"{'=' * 80}\n\n")

            f.write(f"URL: {video.get('url', '')}\n")
            f.write(f"Channel: {video.get('channel_title', '')}\n")
            f.write(f"Views: {video.get('views', 0):,}\n")

            if video.get('tags'):
                f.write(f"\nTAGS:\n")
                f.write(", ".join(video['tags'][:20]) + "\n")

            if video.get('error'):
                f.write(f"\nERROR: {video['error']}\n")
            else:
                if video.get('summary'):
                    f.write(f"\nSUMMARY:\n")
                    f.write("-" * 40 + "\n")
                    f.write(video['summary'] + "\n")

                if video.get('transcript'):
                    f.write(f"\nTRANSCRIPT:\n")
                    f.write("-" * 40 + "\n")
                    # Truncate long transcripts in report
                    transcript = video['transcript']
                    if len(transcript) > 3000:
                        transcript = transcript[:3000] + "\n... [truncated - see full export]"
                    f.write(transcript + "\n")

            f.write("\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write(f"Total videos processed: {len(videos_content)}\n")
        f.write("=" * 80 + "\n")
