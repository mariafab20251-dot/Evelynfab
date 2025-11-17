"""
YouTube Auto Uploader - Multi-Channel Automation
Uploads videos from FinalVideos folder to multiple YouTube channels
Rotates through 5 channels every 5 minutes
"""

import os
import time
import json
from pathlib import Path
from datetime import datetime
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# Configuration
from config import config

# YouTube API scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

class YouTubeUploader:
    """Automated YouTube uploader for multiple channels"""
    
    def __init__(self):
        # Use centralized configuration
        self.videos_folder = config.VIDEOS_UPLOAD_FOLDER
        self.uploaded_folder = config.UPLOADED_FOLDER
        self.failed_folder = config.FAILED_FOLDER
        self.credentials_folder = config.CREDENTIALS_FOLDER

        # Folders are created in config, but safe to call again
        self.uploaded_folder.mkdir(exist_ok=True)
        self.failed_folder.mkdir(exist_ok=True)
        self.credentials_folder.mkdir(exist_ok=True)

        # Upload log
        self.upload_log_file = config.UPLOAD_LOG
        self.upload_log = self.load_upload_log()

        # Retry configuration
        self.max_retries = config.MAX_RETRIES
        self.retry_delay = config.RETRY_DELAY
        
        # Channel configuration
        self.channels = {
            'channel1': {
                'name': 'Channel 1',
                'credentials_file': 'client_secret_channel1.json',
                'token_file': 'token_channel1.pickle',
                'default_category': '22',  # People & Blogs
                'default_privacy': 'public'  # public, unlisted, or private
            },
            'channel2': {
                'name': 'Channel 2',
                'credentials_file': 'client_secret_channel2.json',
                'token_file': 'token_channel2.pickle',
                'default_category': '22',
                'default_privacy': 'public'
            },
            'channel3': {
                'name': 'Channel 3',
                'credentials_file': 'client_secret_channel3.json',
                'token_file': 'token_channel3.pickle',
                'default_category': '22',
                'default_privacy': 'public'
            },
            'channel4': {
                'name': 'Channel 4',
                'credentials_file': 'client_secret_channel4.json',
                'token_file': 'token_channel4.pickle',
                'default_category': '22',
                'default_privacy': 'public'
            },
            'channel5': {
                'name': 'Channel 5',
                'credentials_file': 'client_secret_channel5.json',
                'token_file': 'token_channel5.pickle',
                'default_category': '22',
                'default_privacy': 'public'
            }
        }
        
        # Current channel index for rotation
        self.current_channel_index = 0

        # Upload interval (configurable via environment variable)
        self.upload_interval = config.UPLOAD_INTERVAL  # seconds
        
        print("="*70)
        print("YouTube Auto Uploader Initialized")
        print("="*70)
        print(f"Videos folder: {self.videos_folder}")
        print(f"Upload interval: 5 minutes")
        print(f"Channels configured: {len(self.channels)}")
        print("="*70)
    
    def load_upload_log(self):
        """Load upload history"""
        if self.upload_log_file.exists():
            with open(self.upload_log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'total_uploaded': 0,
            'uploads': [],
            'last_upload_time': None
        }
    
    def save_upload_log(self):
        """Save upload history"""
        with open(self.upload_log_file, 'w', encoding='utf-8') as f:
            json.dump(self.upload_log, f, indent=2, ensure_ascii=False)
    
    def get_credentials(self, channel_id):
        """Get or create credentials for a channel"""
        channel = self.channels[channel_id]
        credentials_path = self.credentials_folder / channel['credentials_file']
        token_path = self.credentials_folder / channel['token_file']
        
        creds = None
        
        # Load saved credentials
        if token_path.exists():
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    print(f"  Refreshing expired token for {channel['name']}...")
                    creds.refresh(Request())
                    print(f"  ✓ Token refreshed successfully")

                    # Save refreshed credentials
                    with open(token_path, 'wb') as token:
                        pickle.dump(creds, token)

                except Exception as e:
                    print(f"  ❌ Error refreshing token: {e}")
                    print(f"  → Need to re-authenticate {channel['name']}")
                    creds = None

            if not creds:
                if not credentials_path.exists():
                    print(f"❌ Missing credentials file: {credentials_path}")
                    print(f"Please add OAuth 2.0 credentials for {channel['name']}")
                    print(f"→ Get credentials from: https://console.cloud.google.com/")
                    return None

                try:
                    print(f"  Authenticating {channel['name']}...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(credentials_path), SCOPES)
                    creds = flow.run_local_server(port=0)
                    print(f"  ✓ Authentication successful")
                except Exception as e:
                    print(f"  ❌ Authentication failed: {e}")
                    return None

            # Save credentials
            try:
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
            except Exception as e:
                print(f"  ⚠ Warning: Could not save token: {e}")

        return creds
    
    def get_youtube_service(self, channel_id):
        """Get YouTube API service for a channel"""
        creds = self.get_credentials(channel_id)
        if not creds:
            return None

        try:
            return build('youtube', 'v3', credentials=creds)
        except Exception as e:
            print(f"Error building YouTube service: {e}")
            return None

    def _retry_with_backoff(self, func, *args, **kwargs):
        """Retry a function with exponential backoff"""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except HttpError as e:
                error_reason = e.reason if hasattr(e, 'reason') else str(e)

                # Check if error is retryable
                if e.resp.status in [500, 502, 503, 504]:
                    # Server error - retry
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (2 ** attempt)
                        print(f"  ⚠ Server error (HTTP {e.resp.status}): {error_reason}")
                        print(f"  → Retrying in {wait_time} seconds... (attempt {attempt + 1}/{self.max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"  ❌ Max retries reached")
                        raise
                elif e.resp.status == 403:
                    # Quota exceeded or forbidden - don't retry
                    print(f"  ❌ Quota exceeded or forbidden: {error_reason}")
                    raise
                elif e.resp.status == 400:
                    # Bad request - don't retry
                    print(f"  ❌ Bad request: {error_reason}")
                    raise
                else:
                    # Other error - retry once
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay
                        print(f"  ⚠ Error: {error_reason}")
                        print(f"  → Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise
            except Exception as e:
                # Non-HTTP error
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    print(f"  ⚠ Unexpected error: {str(e)}")
                    print(f"  → Retrying in {wait_time} seconds... (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    raise

        # Should not reach here, but just in case
        raise Exception("Max retries exceeded")
    
    def extract_title_and_tags(self, filename):
        """Extract title and tags from filename"""
        # Remove .mp4 extension
        name = Path(filename).stem
        
        # Extract hashtags
        import re
        hashtags = re.findall(r'#\w+', name)
        
        # Remove hashtags from title
        title = re.sub(r'#\w+', '', name).strip()
        
        # Clean up title
        title = re.sub(r'\s+', ' ', title)
        
        # Limit title to 100 characters (YouTube limit is 100)
        if len(title) > 97:
            title = title[:97] + "..."
        
        # Convert hashtags to tags
        tags = [tag.replace('#', '') for tag in hashtags]
        
        # Add default tags
        default_tags = ['motivation', 'quotes', 'inspiration', 'mindset']
        tags.extend(default_tags)
        
        # Remove duplicates
        tags = list(set(tags))
        
        return title, tags
    
    def create_description(self, title, tags):
        """Create video description"""
        description = f"{title}\n\n"
        description += "💭 Daily motivation and inspiration\n"
        description += "🔔 Subscribe for more quotes\n\n"
        description += "Tags: " + ", ".join(tags[:5]) + "\n\n"
        description += "#motivation #quotes #inspiration #mindset #success"
        
        return description
    
    def upload_video(self, video_path, channel_id):
        """Upload a video to YouTube"""
        channel = self.channels[channel_id]
        
        print(f"\n{'='*70}")
        print(f"Uploading to: {channel['name']}")
        print(f"Video: {video_path.name}")
        
        # Get YouTube service
        youtube = self.get_youtube_service(channel_id)
        if not youtube:
            print(f"❌ Could not authenticate {channel['name']}")
            return False
        
        # Extract title and tags from filename
        title, tags = self.extract_title_and_tags(video_path.name)
        description = self.create_description(title, tags)
        
        print(f"Title: {title}")
        print(f"Tags: {', '.join(tags[:5])}")
        
        # Prepare video metadata
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': channel['default_category']
            },
            'status': {
                'privacyStatus': channel['default_privacy'],
                'selfDeclaredMadeForKids': False
            }
        }
        
        # Upload video with retry logic
        try:
            def do_upload():
                """Inner function for retry logic"""
                media = MediaFileUpload(
                    str(video_path),
                    mimetype='video/mp4',
                    resumable=True,
                    chunksize=1024*1024  # 1MB chunks
                )

                request = youtube.videos().insert(
                    part=','.join(body.keys()),
                    body=body,
                    media_body=media
                )

                print("Uploading... (this may take several minutes)")

                response = None
                error = None
                while response is None:
                    try:
                        status, response = request.next_chunk()
                        if status:
                            progress = int(status.progress() * 100)
                            print(f"Upload progress: {progress}%", end='\r')
                    except HttpError as e:
                        # If resumable upload fails, re-raise for retry logic
                        if e.resp.status in [500, 502, 503, 504]:
                            raise
                        else:
                            error = e
                            break

                if error:
                    raise error

                return response

            # Use retry logic for upload
            response = self._retry_with_backoff(do_upload)

            print(f"\n✓ Upload complete!")
            print(f"Video ID: {response['id']}")
            print(f"Video URL: https://www.youtube.com/watch?v={response['id']}")
            
            # Log upload
            upload_record = {
                'filename': video_path.name,
                'channel': channel['name'],
                'channel_id': channel_id,
                'video_id': response['id'],
                'title': title,
                'upload_time': datetime.now().isoformat(),
                'status': 'success'
            }
            
            self.upload_log['total_uploaded'] += 1
            self.upload_log['uploads'].append(upload_record)
            self.upload_log['last_upload_time'] = datetime.now().isoformat()
            self.save_upload_log()
            
            # Move to uploaded folder
            uploaded_path = self.uploaded_folder / video_path.name
            video_path.rename(uploaded_path)
            print(f"✓ Moved to: {self.uploaded_folder.name}")
            
            print("="*70)
            return True
            
        except HttpError as e:
            print(f"\n❌ Upload failed: {e}")
            
            # Log failed upload
            upload_record = {
                'filename': video_path.name,
                'channel': channel['name'],
                'channel_id': channel_id,
                'upload_time': datetime.now().isoformat(),
                'status': 'failed',
                'error': str(e)
            }
            
            self.upload_log['uploads'].append(upload_record)
            self.save_upload_log()
            
            # Move to failed folder
            failed_path = self.failed_folder / video_path.name
            video_path.rename(failed_path)
            print(f"✓ Moved to: {self.failed_folder.name}")
            
            print("="*70)
            return False
        
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            print("="*70)
            return False
    
    def get_next_video(self):
        """Get the oldest unuploaded video from FinalVideos folder"""
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv'}
        
        videos = [
            f for f in self.videos_folder.iterdir()
            if f.is_file() and f.suffix.lower() in video_extensions
        ]
        
        if not videos:
            return None
        
        # Sort by creation time (oldest first)
        videos.sort(key=lambda x: x.stat().st_ctime)
        
        return videos[0]
    
    def get_next_channel(self):
        """Get next channel ID in rotation"""
        channel_ids = list(self.channels.keys())
        channel_id = channel_ids[self.current_channel_index]
        
        # Move to next channel
        self.current_channel_index = (self.current_channel_index + 1) % len(channel_ids)
        
        return channel_id
    
    def run_once(self):
        """Upload one video to next channel"""
        video = self.get_next_video()
        
        if not video:
            print("\n⏸️  No videos to upload")
            print(f"Waiting for videos in: {self.videos_folder}")
            return False
        
        channel_id = self.get_next_channel()
        success = self.upload_video(video, channel_id)
        
        return success
    
    def run_continuous(self):
        """Run uploader continuously every 5 minutes"""
        print("\n🚀 Starting continuous upload mode")
        print(f"Upload interval: {self.upload_interval // 60} minutes")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                # Upload one video
                self.run_once()
                
                # Wait for next upload
                next_upload = datetime.now().timestamp() + self.upload_interval
                next_upload_time = datetime.fromtimestamp(next_upload).strftime('%H:%M:%S')
                
                print(f"\n⏰ Next upload at: {next_upload_time}")
                print(f"Waiting {self.upload_interval // 60} minutes...\n")
                
                time.sleep(self.upload_interval)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Upload automation stopped")
            print(f"Total videos uploaded: {self.upload_log['total_uploaded']}")
    
    def show_status(self):
        """Show upload statistics"""
        print("\n" + "="*70)
        print("UPLOAD STATISTICS")
        print("="*70)
        print(f"Total uploads: {self.upload_log['total_uploaded']}")
        
        if self.upload_log['last_upload_time']:
            last_time = datetime.fromisoformat(self.upload_log['last_upload_time'])
            print(f"Last upload: {last_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Count uploads per channel
        channel_counts = {}
        for upload in self.upload_log['uploads']:
            if upload['status'] == 'success':
                channel = upload.get('channel', 'Unknown')
                channel_counts[channel] = channel_counts.get(channel, 0) + 1
        
        print("\nUploads per channel:")
        for channel, count in channel_counts.items():
            print(f"  {channel}: {count}")
        
        # Count pending videos
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv'}
        pending = len([
            f for f in self.videos_folder.iterdir()
            if f.is_file() and f.suffix.lower() in video_extensions
        ])
        
        print(f"\nPending videos: {pending}")
        print("="*70)


def main():
    """Main function"""
    uploader = YouTubeUploader()
    
    print("\n" + "="*70)
    print("YOUTUBE AUTO UPLOADER")
    print("="*70)
    print("\nOptions:")
    print("1. Upload one video now")
    print("2. Start continuous upload (every 5 minutes)")
    print("3. Show upload statistics")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == '1':
        uploader.run_once()
    elif choice == '2':
        uploader.run_continuous()
    elif choice == '3':
        uploader.show_status()
    elif choice == '4':
        print("Goodbye!")
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()
