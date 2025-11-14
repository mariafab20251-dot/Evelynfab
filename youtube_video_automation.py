"""
Video Quote Overlay Automation - With GUI Settings Integration
Compatible with MoviePy 2.x
"""

import os
import re
from pathlib import Path
from typing import List, Tuple
import json
from datetime import datetime

# MoviePy 2.x imports
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip


class VideoQuoteAutomation:
    """Automate adding quotes to videos using GUI settings"""
    
    def __init__(self):
        # Your specific paths
        self.video_folder = Path(r"E:\MyAutomations\ScriptAutomations\VideoFolder\SourceVideosToEdit\Libriana8")
        self.quotes_file = Path(r"E:\MyAutomations\ScriptAutomations\VideoFolder\Quotes.txt")
        self.output_folder = Path(r"E:\MyAutomations\ScriptAutomations\VideoFolder\FinalVideos")
        
        # Create output folder
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
        # Load settings from GUI
        self.settings = self.load_settings()
        
        # Processing log
        self.log_file = self.output_folder / "processing_log.json"
        self.processing_log = self._load_log()
    
    def load_settings(self) -> dict:
        """Load settings from GUI config file"""
        settings_file = Path('overlay_settings.json')
        
        # Default settings if file doesn't exist
        default_settings = {
            'font_size': 45,
            'font_style': 'Arial Bold',
            'text_color': '#000000',
            'bg_color': '#FFFFFF',
            'bg_opacity': 90,
            'cta_enabled': True,
            'cta_font_size': 43,
            'cta_font_style': 'Arial Italic',
            'cta_bg_color': '#DC2626',
            'cta_text_color': '#FFFFFF',
            'emoji_enabled': True,
            'emoji_size_multiplier': 1.2,
            'bubble_width': 75,
            'padding_horizontal': 40,
            'padding_vertical': 20,
            'inner_padding': 15,
            'section_spacing': 15,
            'corner_radius': 15,
            'position': 'top'
        }
        
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    print("✓ Loaded settings from overlay_settings.json")
                    return loaded_settings
            except Exception as e:
                print(f"⚠ Could not load settings: {e}")
                print("Using default settings...")
                return default_settings
        else:
            print("⚠ No settings file found. Please run overlay_settings_gui.py first!")
            print("Using default settings for now...")
            return default_settings
    
    def _load_log(self) -> dict:
        """Load processing log"""
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"processed_count": 0, "processed_videos": []}
    
    def _save_log(self):
        """Save processing log"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.processing_log, f, indent=2, ensure_ascii=False)
    
    def hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def read_quotes(self) -> List[str]:
        """Read quotes from file"""
        if not self.quotes_file.exists():
            print(f"✗ Quotes file not found: {self.quotes_file}")
            return []
        
        with open(self.quotes_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        quotes = []
        
        # Try numbered format
        if re.match(r'^\s*\d+\.', content, re.MULTILINE):
            parts = re.split(r'\n\s*\d+\.\s*', content)
            quotes = [q.strip() for q in parts[1:] if q.strip()]
        # Try double newline
        elif '\n\n' in content:
            quotes = [q.strip() for q in content.split('\n\n') if q.strip()]
        # Try triple dash
        elif '---' in content:
            quotes = [q.strip() for q in content.split('---') if q.strip()]
        # Each line is a quote
        else:
            quotes = [line.strip() for line in content.split('\n') if line.strip()]
        
        # Clean quotes
        cleaned_quotes = []
        for quote in quotes:
            cleaned = re.sub(r'^\d+\.\s*', '', quote).strip()
            if cleaned:
                cleaned_quotes.append(cleaned)
        
        print(f"✓ Loaded {len(cleaned_quotes)} quotes")
        
        if cleaned_quotes:
            print(f"\nFirst 3 quotes:")
            for i, quote in enumerate(cleaned_quotes[:3], 1):
                preview = quote[:80] + "..." if len(quote) > 80 else quote
                print(f"  {i}. {preview}")
        
        return cleaned_quotes
    
    def get_video_files(self, sort_by: str = 'created') -> List[Path]:
        """Get video files from folder"""
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm'}
        
        if not self.video_folder.exists():
            print(f"✗ Video folder not found: {self.video_folder}")
            return []
        
        videos = [f for f in self.video_folder.iterdir() 
                 if f.suffix.lower() in video_extensions and f.is_file()]
        
        if sort_by == 'created':
            videos = sorted(videos, key=lambda x: x.stat().st_ctime)
            print(f"✓ Found {len(videos)} videos (sorted by creation date)")
        elif sort_by == 'modified':
            videos = sorted(videos, key=lambda x: x.stat().st_mtime)
            print(f"✓ Found {len(videos)} videos (sorted by modification date)")
        else:
            videos = sorted(videos)
            print(f"✓ Found {len(videos)} videos (sorted alphabetically)")
        
        if videos:
            print(f"\nFirst 5 videos:")
            for i, video in enumerate(videos[:5], 1):
                print(f"  {i}. {video.name}")
        
        return videos
    
    def generate_hashtags(self, quote: str) -> List[str]:
        """Generate relevant hashtags from quote"""
        quote_lower = quote.lower()
        
        hashtag_map = {
            'success': '#Success', 'motivation': '#Motivation', 'inspire': '#Inspiration',
            'life': '#Life', 'love': '#Love', 'happy': '#Happiness', 'dream': '#Dreams',
            'work': '#Work', 'business': '#Business', 'money': '#Money', 'goal': '#Goals',
            'achieve': '#Achievement', 'believe': '#Believe', 'hope': '#Hope',
            'strength': '#Strength', 'courage': '#Courage', 'change': '#Change',
            'wisdom': '#Wisdom', 'mindset': '#Mindset', 'grow': '#Growth',
            'leader': '#Leadership', 'hustle': '#Hustle', 'focus': '#Focus',
            'passion': '#Passion', 'gratitude': '#Gratitude', 'positive': '#Positivity'
        }
        
        found = []
        for keyword, hashtag in hashtag_map.items():
            if keyword in quote_lower and hashtag not in found:
                found.append(hashtag)
                if len(found) == 2:
                    break
        
        if len(found) < 2:
            defaults = ['#Motivation', '#Quotes', '#Inspiration', '#Wisdom']
            for tag in defaults:
                if tag not in found:
                    found.append(tag)
                    if len(found) == 2:
                        break
        
        return found[:2]
    
    def sanitize_filename(self, text: str, max_length: int = 100) -> str:
        """Convert text to valid filename"""
        text = re.sub(r'[<>:"/\\|?*]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        if len(text) > max_length - 4:
            text = text[:max_length - 4]
        return text
    
    def create_filename(self, quote: str, hashtags: List[str]) -> str:
        """Create filename from quote and hashtags"""
        filename_text = f"{quote} {' '.join(hashtags)}"
        filename = self.sanitize_filename(filename_text, max_length=96)
        return filename + ".mp4"
    
    def add_quote_to_video(self, video_path: Path, quote: str) -> Tuple[Path, str]:
        """Add quote overlay to video using GUI settings"""
        print(f"\n{'='*70}")
        print(f"Processing: {video_path.name}")
        print(f"Quote: {quote[:80]}...")
        
        # Generate hashtags
        hashtags = self.generate_hashtags(quote)
        print(f"Hashtags: {', '.join(hashtags)}")
        
        # Create filename
        output_filename = self.create_filename(quote, hashtags)
        print(f"Output: {output_filename}")
        
        # Load video
        video = VideoFileClip(str(video_path))
        
        # Create overlay using PIL
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np
        
        # Parse quote into sections
        emoji_pattern = re.compile(r'[\U0001F300-\U0001F9FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF\U00002600-\U000027BF\U0001F1E0-\U0001F1FF]+')
        
        emojis_found = emoji_pattern.findall(quote)
        text_without_emojis = emoji_pattern.sub(' ', quote).strip()
        
        # Extract CTA
        cta_patterns = [
            r'\s+(Agree\s+or\s+not\?)', r'\s+(True\?)', r'\s+(Relatable\?)',
            r'\s+(Been\s+there\?)', r'\s+(Deep\s+or\s+not\?)', r'\s+(Agree\?)'
        ]
        
        main_text = text_without_emojis
        cta_text = ""
        
        for pattern in cta_patterns:
            match = re.search(pattern, text_without_emojis, re.IGNORECASE)
            if match:
                cta_text = match.group(1)
                main_text = text_without_emojis[:match.start()].strip()
                break
        
        emoji_line = ' '.join(emojis_found) if emojis_found else ""
        
        print(f"Main: {main_text[:60]}...")
        print(f"Emojis: {emoji_line}")
        print(f"CTA: {cta_text}")
        
        # Create overlay image
        img_width = video.w
        temp_img = Image.new('RGBA', (img_width, 1000), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        
        # Load fonts with settings - use saved font file paths
        font_size = self.settings['font_size']
        cta_font_size = self.settings.get('cta_font_size', int(font_size * 0.95))
        
        try:
            # Use font_file paths saved from GUI
            main_font_file = self.settings.get('font_file', 'arialbd.ttf')
            if not Path(main_font_file).exists():
                # Fallback to Windows Fonts folder
                main_font_file = str(Path(r"C:\Windows\Fonts") / Path(main_font_file).name)
            
            main_font = ImageFont.truetype(main_font_file, font_size)
            print(f"✓ Loaded main font: {main_font_file}")
            
            # Emoji font
            emoji_font_path = str(Path(r"C:\Windows\Fonts") / 'seguiemj.ttf')
            emoji_font = ImageFont.truetype(emoji_font_path, int(font_size * self.settings['emoji_size_multiplier']))
            
            # CTA font
            cta_font_file = self.settings.get('cta_font_file', 'ariali.ttf')
            if not Path(cta_font_file).exists():
                cta_font_file = str(Path(r"C:\Windows\Fonts") / Path(cta_font_file).name)
            
            cta_font = ImageFont.truetype(cta_font_file, cta_font_size)
            print(f"✓ Loaded CTA font: {cta_font_file}")
            
        except Exception as e:
            print(f"⚠ Font loading error: {e}")
            print(f"⚠ Using default font")
            main_font = ImageFont.load_default()
            emoji_font = main_font
            cta_font = main_font
        
        # Word wrap main text
        max_text_width = int(img_width * (self.settings['bubble_width'] / 100))
        words = main_text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = temp_draw.textbbox((0, 0), test_line, font=main_font)
            if bbox[2] - bbox[0] <= max_text_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        main_text_wrapped = '\n'.join(lines)
        
        # Build sections based on enabled settings
        sections = []
        if main_text_wrapped:
            sections.append((main_text_wrapped, main_font, True, 'main'))
        
        if self.settings.get('emoji_enabled', True) and emoji_line:
            sections.append((emoji_line, emoji_font, False, 'emoji'))
        
        if self.settings.get('cta_enabled', True) and cta_text:
            sections.append((cta_text, cta_font, False, 'cta'))
        
        # Calculate section sizes
        section_boxes = []
        for text, font, is_multiline, section_type in sections:
            if is_multiline:
                bbox = temp_draw.multiline_textbbox((0, 0), text, font=font, align='center')
            else:
                bbox = temp_draw.textbbox((0, 0), text, font=font)
            section_boxes.append({
                'text': text,
                'font': font,
                'is_multiline': is_multiline,
                'type': section_type,
                'width': bbox[2] - bbox[0],
                'height': bbox[3] - bbox[1]
            })
        
        # Calculate total height
        total_height = sum(box['height'] for box in section_boxes)
        total_height += (len(section_boxes) - 1) * self.settings['section_spacing']
        total_height += self.settings['padding_vertical'] * 2
        total_height += len(section_boxes) * self.settings['inner_padding'] * 2
        
        box_height = int(total_height + 100)
        box_width = img_width
        
        # Create overlay image
        img = Image.new('RGBA', (box_width, box_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Get colors from settings
        bg_rgb = self.hex_to_rgb(self.settings['bg_color'])
        bg_alpha = int(255 * (self.settings['bg_opacity'] / 100))
        white_bg = bg_rgb + (bg_alpha,)
        
        cta_bg_rgb = self.hex_to_rgb(self.settings['cta_bg_color'])
        red_bg = cta_bg_rgb + (255,)
        
        # Starting Y
        if self.settings['position'] == 'top':
            current_y = self.settings['padding_vertical']
        elif self.settings['position'] == 'center':
            current_y = (box_height - total_height) // 2
        else:  # bottom
            current_y = box_height - total_height - self.settings['padding_vertical']
        
        # Draw sections
        for i, box_info in enumerate(section_boxes):
            text = box_info['text']
            font = box_info['font']
            is_multiline = box_info['is_multiline']
            section_type = box_info['type']
            
            is_cta = (section_type == 'cta')
            
            current_bg = red_bg if is_cta else white_bg
            current_text_color = self.settings['cta_text_color'] if is_cta else self.settings['text_color']
            
            bubble_width = box_info['width'] + (self.settings['padding_horizontal'] * 2)
            bubble_height = box_info['height'] + (self.settings['inner_padding'] * 2)
            bubble_x = (box_width - bubble_width) // 2
            
            # Draw bubble
            draw.rounded_rectangle(
                [(bubble_x, current_y), (bubble_x + bubble_width, current_y + bubble_height)],
                radius=self.settings['corner_radius'],
                fill=current_bg
            )
            
            # Draw text
            if is_multiline:
                text_x = bubble_x + (bubble_width // 2)
                text_y = current_y + self.settings['inner_padding']
                draw.multiline_text(
                    (text_x, text_y),
                    text,
                    font=font,
                    fill=current_text_color,
                    align='center',
                    anchor='ma'
                )
            else:
                text_x = bubble_x + (bubble_width // 2)
                text_y = current_y + (bubble_height // 2)
                draw.text(
                    (text_x, text_y),
                    text,
                    font=font,
                    fill=current_text_color,
                    anchor='mm'
                )
            
            current_y += bubble_height + self.settings['section_spacing']
        
        # Convert to clip
        img_array = np.array(img)
        txt_clip = ImageClip(img_array).with_duration(video.duration)
        
        # Position based on settings
        if self.settings['position'] == 'top':
            txt_clip = txt_clip.with_position(('center', 0))
        elif self.settings['position'] == 'center':
            txt_clip = txt_clip.with_position(('center', 'center'))
        else:  # bottom
            txt_clip = txt_clip.with_position(('center', video.h - txt_clip.h))
        
        # Composite
        final_video = CompositeVideoClip([video, txt_clip])
        
        # Output path
        output_path = self.output_folder / output_filename
        counter = 1
        original_output_path = output_path
        while output_path.exists():
            stem = original_output_path.stem
            output_path = self.output_folder / f"{stem}_{counter}.mp4"
            counter += 1
        
        # Render
        print(f"Rendering... This may take a few minutes.")
        final_video.write_videofile(
            str(output_path),
            codec='libx264',
            audio_codec='aac',
            fps=video.fps,
            preset='medium',
            threads=4,
            logger=None
        )
        
        # Cleanup
        video.close()
        txt_clip.close()
        final_video.close()
        
        print(f"✓ Saved: {output_path.name}")
        print(f"{'='*70}")
        
        return output_path, output_filename
    
    def process_all(self, start_from: int = 0, sort_by: str = 'created'):
        """Process all videos with settings from GUI"""
        videos = self.get_video_files(sort_by=sort_by)
        quotes = self.read_quotes()
        
        if not videos:
            print("✗ No videos found!")
            return
        
        if not quotes:
            print("✗ No quotes found!")
            return
        
        num_to_process = min(len(videos), len(quotes))
        
        if start_from >= num_to_process:
            print(f"✗ start_from ({start_from}) >= available pairs ({num_to_process})")
            return
        
        print(f"\n{'='*70}")
        print(f"BATCH PROCESSING")
        print(f"{'='*70}")
        print(f"Settings loaded from: overlay_settings.json")
        print(f"Font: {self.settings['font_style']}, Size: {self.settings['font_size']}")
        print(f"Position: {self.settings['position']}")
        print(f"Videos: {len(videos)}")
        print(f"Quotes: {len(quotes)}")
        print(f"Processing: {num_to_process - start_from} video(s)")
        print(f"{'='*70}\n")
        
        results = []
        for i in range(start_from, num_to_process):
            video_path = videos[i]
            quote = quotes[i]
            
            print(f"\nProcessing {i + 1}/{num_to_process}")
            
            try:
                output_path, filename = self.add_quote_to_video(video_path, quote)
                
                result = {
                    'index': i,
                    'original_video': video_path.name,
                    'quote': quote,
                    'output_file': filename,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success'
                }
                results.append(result)
                
                self.processing_log['processed_count'] += 1
                self.processing_log['processed_videos'].append(result)
                self._save_log()
                
            except Exception as e:
                print(f"✗ Error: {str(e)}")
                result = {
                    'index': i,
                    'original_video': video_path.name,
                    'quote': quote,
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                results.append(result)
                continue
        
        # Summary
        print(f"\n{'='*70}")
        print(f"PROCESSING COMPLETE!")
        print(f"{'='*70}")
        success_count = sum(1 for r in results if r['status'] == 'success')
        print(f"Success: {success_count}/{len(results)}")
        print(f"Output: {self.output_folder}")
        print(f"{'='*70}\n")
        
        return results


if __name__ == "__main__":
    print("Video Quote Automation with GUI Settings")
    print("="*70)
    print("\n⚠ IMPORTANT: Run overlay_settings_gui.py first to configure settings!")
    print("="*70)
    
    automation = VideoQuoteAutomation()
    
    # Process videos using settings from GUI
    automation.process_all(
        start_from=0,
        sort_by='created'
    )
    
    print("\n✓ All done! Check FinalVideos folder.")