"""
Video Quote Overlay Automation - ENHANCED with Advanced Effects
Compatible with MoviePy 2.x
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Optional
import json
from datetime import datetime
import numpy as np

try:
    from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, AudioFileClip, CompositeAudioClip
    from moviepy.video.fx import Resize
    from moviepy.audio.fx import MultiplyVolume, AudioLoop
except ImportError:
    from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, AudioFileClip, CompositeAudioClip
    from moviepy.video.fx.resize import resize as Resize
    from moviepy.audio.fx.volumex import volumex as MultiplyVolume
    AudioLoop = None

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

# Text-to-Speech - Using edge-tts for natural, human-like voices
try:
    import edge_tts
    import asyncio
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("⚠ edge-tts not available - TTS voiceover generation disabled")
    print("  Install with: pip install edge-tts")


def set_volume(clip, volume):
    """Compatible volume adjustment for MoviePy 1.x and 2.x"""
    try:
        return clip.with_effects([MultiplyVolume(volume)])
    except:
        return clip.volumex(volume)


def set_duration(clip, duration):
    """Compatible duration setting for MoviePy 1.x and 2.x"""
    try:
        return clip.with_duration(duration)
    except:
        return clip.set_duration(duration)


def subclip(clip, start, end):
    """Compatible subclipping for MoviePy 1.x and 2.x"""
    try:
        return clip.subclipped(start, end)
    except:
        return clip.subclip(start, end)


def set_audio(clip, audio):
    """Compatible audio setting for MoviePy 1.x and 2.x"""
    try:
        return clip.with_audio(audio)
    except:
        return clip.set_audio(audio)


def set_position(clip, position):
    """Compatible position setting for MoviePy 1.x and 2.x"""
    try:
        return clip.with_position(position)
    except:
        return clip.set_position(position)


class VideoEffects:
    """Advanced video effects module"""

    @staticmethod
    def apply_color_grade(frame, grade_type='warm', intensity=0.5):
        """Apply color grading to frame"""
        if grade_type == 'warm':
            frame[:,:,0] = np.clip(frame[:,:,0] * (1 + intensity * 0.2), 0, 255)
            frame[:,:,2] = np.clip(frame[:,:,2] * (1 - intensity * 0.1), 0, 255)
        elif grade_type == 'cold':
            frame[:,:,2] = np.clip(frame[:,:,2] * (1 + intensity * 0.2), 0, 255)
            frame[:,:,0] = np.clip(frame[:,:,0] * (1 - intensity * 0.1), 0, 255)
        elif grade_type == 'cinematic':
            frame = frame * 0.95
            frame[:,:,1] = np.clip(frame[:,:,1] * 1.05, 0, 255)
        elif grade_type == 'vintage':
            frame[:,:,0] = np.clip(frame[:,:,0] * 1.1, 0, 255)
            frame[:,:,1] = np.clip(frame[:,:,1] * 0.95, 0, 255)
            frame[:,:,2] = np.clip(frame[:,:,2] * 0.85, 0, 255)
        return frame.astype('uint8')

    @staticmethod
    def apply_vignette(frame, intensity=0.4):
        """Apply vignette darkening"""
        h, w = frame.shape[:2]
        y, x = np.ogrid[:h, :w]
        cx, cy = w / 2, h / 2
        max_dist = np.sqrt(cx**2 + cy**2)
        distance = np.sqrt((x - cx)**2 + (y - cy)**2)
        vignette = 1 - (distance / max_dist * intensity)
        vignette = np.clip(vignette, 0, 1)
        return (frame * vignette[:,:,np.newaxis]).astype('uint8')

    @staticmethod
    def apply_film_grain(frame, intensity=0.15):
        """Apply film grain overlay"""
        noise = np.random.normal(0, intensity * 255, frame.shape)
        return np.clip(frame + noise, 0, 255).astype('uint8')

    @staticmethod
    def apply_background_dim(frame, intensity=0.25):
        """Dim the background"""
        return (frame * (1 - intensity)).astype('uint8')


class ParticleEffects:
    """Animated particle overlays (glitter, stars, confetti, etc.)"""

    @staticmethod
    def create_glitter_overlay(width, height, duration, fps, intensity=0.5):
        """Create glitter/sparkle particle effect"""
        try:
            from moviepy import VideoClip
        except ImportError:
            from moviepy.editor import VideoClip

        def make_frame(t):
            # Create transparent frame (explicitly writable)
            frame = np.zeros((height, width, 4), dtype=np.uint8)
            frame.flags.writeable = True

            # Number of particles based on intensity
            num_particles = int(50 * intensity)

            # Generate random sparkles
            np.random.seed(int(t * 1000) % 10000)  # Different random seed per frame
            for _ in range(num_particles):
                x = np.random.randint(0, width)
                y = np.random.randint(0, height)
                size = np.random.randint(2, 6)

                # Twinkling effect using sine wave
                brightness = int(255 * abs(np.sin(t * 5 + np.random.random() * 10)))

                # Draw sparkle (white with alpha)
                y1, y2 = max(0, y-size), min(height, y+size)
                x1, x2 = max(0, x-size), min(width, x+size)

                frame[y1:y2, x1:x2, :3] = [255, 255, 255]  # White
                frame[y1:y2, x1:x2, 3] = brightness  # Alpha (twinkling)

            return frame

        clip = VideoClip(make_frame, duration=duration).with_fps(fps)
        return clip

    @staticmethod
    def create_stars_overlay(width, height, duration, fps, particle_type='star'):
        """Create falling stars/hearts/emojis effect"""
        try:
            from moviepy import VideoClip
        except ImportError:
            from moviepy.editor import VideoClip

        # Create particles with random positions and speeds
        num_particles = 20
        particles = []

        for i in range(num_particles):
            particles.append({
                'x': np.random.randint(0, width),
                'y_start': -np.random.randint(0, height),  # Start above screen
                'speed': np.random.uniform(50, 150),  # Pixels per second
                'size': np.random.randint(15, 40),
                'rotation': np.random.uniform(0, 360),
                'rotation_speed': np.random.uniform(-180, 180)
            })

        def make_frame(t):
            # Create transparent frame
            frame_pil = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(frame_pil)

            for particle in particles:
                # Update position
                y = int(particle['y_start'] + particle['speed'] * t)

                # Wrap around when particle goes off bottom
                if y > height + 50:
                    y = y % (height + 100) - 50

                x = int(particle['x'])
                size = particle['size']

                # Draw based on type
                if particle_type == 'star':
                    # Draw star shape
                    points = []
                    for i in range(10):
                        angle = (i * 36) * np.pi / 180
                        r = size if i % 2 == 0 else size // 2
                        px = x + r * np.cos(angle)
                        py = y + r * np.sin(angle)
                        points.append((px, py))
                    draw.polygon(points, fill=(255, 255, 100, 200))  # Yellow

                elif particle_type == 'heart':
                    # Draw heart (simplified circle-based)
                    draw.ellipse([x-size//2, y-size//2, x, y+size//2], fill=(255, 50, 50, 200))
                    draw.ellipse([x, y-size//2, x+size//2, y+size//2], fill=(255, 50, 50, 200))
                    draw.polygon([(x-size//2, y), (x+size//2, y), (x, y+size)], fill=(255, 50, 50, 200))

                elif particle_type == 'circle':
                    # Simple colorful circles
                    colors = [(255, 100, 100, 200), (100, 255, 100, 200),
                             (100, 100, 255, 200), (255, 255, 100, 200)]
                    color = colors[hash(str(particle['x'])) % len(colors)]
                    draw.ellipse([x-size//2, y-size//2, x+size//2, y+size//2], fill=color)

            # Convert to numpy array and ensure it's writable
            frame_array = np.array(frame_pil)
            frame_array.flags.writeable = True
            return frame_array

        clip = VideoClip(make_frame, duration=duration).with_fps(fps)
        return clip

    @staticmethod
    def create_confetti_overlay(width, height, duration, fps):
        """Create falling confetti effect"""
        return ParticleEffects.create_stars_overlay(width, height, duration, fps, particle_type='circle')


class TTSGenerator:
    """Text-to-Speech voiceover generator using Microsoft Edge TTS (natural voices)"""

    # Natural-sounding voice options with descriptions
    VOICES = {
        # US English - Female
        'aria': 'en-US-AriaNeural',           # Friendly, warm female
        'jenny': 'en-US-JennyNeural',         # Cheerful, energetic female
        'michelle': 'en-US-MichelleNeural',   # Professional, clear female
        'monica': 'en-US-MonicaNeural',       # Deep, mature female (DEEP)
        'nancy': 'en-US-NancyNeural',         # News anchor female, authoritative (DEEP)
        'amber': 'en-US-AmberNeural',         # Young, casual female
        'ashley': 'en-US-AshleyNeural',       # Bright, youthful female
        'sara': 'en-US-SaraNeural',           # Mature, calm female

        # US English - Male
        'guy': 'en-US-GuyNeural',             # Friendly, warm male
        'davis': 'en-US-DavisNeural',         # Professional, authoritative male
        'eric': 'en-US-EricNeural',           # Conversational, casual male
        'christopher': 'en-US-ChristopherNeural',  # Deep, mature male
        'jason': 'en-US-JasonNeural',         # Deep, powerful male (HEAVY)
        'tony': 'en-US-TonyNeural',           # News anchor, deep authoritative (HEAVY)
        'roger': 'en-US-RogerNeural',         # Older, wise male
        'steffan': 'en-US-SteffanNeural',     # Young, energetic male

        # British English
        'sonia': 'en-GB-SoniaNeural',         # British female
        'mia': 'en-GB-MiaNeural',             # British deeper, mature female (DEEP)
        'ryan': 'en-GB-RyanNeural',           # British male
        'thomas': 'en-GB-ThomasNeural',       # British deep, serious male (HEAVY)
        'libby': 'en-GB-LibbyNeural',         # British young female
        'alfie': 'en-GB-AlfieNeural',         # British young male

        # Australian English
        'natasha': 'en-AU-NatashaNeural',     # Australian female
        'annette': 'en-AU-AnnetteNeural',     # Australian deeper, professional female (DEEP)
        'william': 'en-AU-WilliamNeural',     # Australian male

        # Indian English
        'neerja': 'en-IN-NeerjaNeural',       # Indian female
        'prabhat': 'en-IN-PrabhatNeural',     # Indian male

        # Backward compatibility
        'female': 'en-US-AriaNeural',         # Default female
        'male': 'en-US-GuyNeural',            # Default male
    }

    # Voice display names for GUI
    VOICE_NAMES = {
        'aria': 'Aria - US Female (Friendly)',
        'jenny': 'Jenny - US Female (Cheerful)',
        'michelle': 'Michelle - US Female (Professional)',
        'monica': 'Monica - US Female (Deep & Mature) 💎',
        'nancy': 'Nancy - US Female (News Anchor, Deep) 💎',
        'amber': 'Amber - US Female (Young)',
        'ashley': 'Ashley - US Female (Bright)',
        'sara': 'Sara - US Female (Mature)',
        'guy': 'Guy - US Male (Friendly)',
        'davis': 'Davis - US Male (Professional)',
        'eric': 'Eric - US Male (Casual)',
        'christopher': 'Christopher - US Male (Deep)',
        'jason': 'Jason - US Male (Deep & Powerful) 🔥',
        'tony': 'Tony - US Male (News Anchor, Heavy) 🔥',
        'roger': 'Roger - US Male (Wise)',
        'steffan': 'Steffan - US Male (Energetic)',
        'sonia': 'Sonia - British Female',
        'mia': 'Mia - British Female (Deep & Mature) 💎',
        'ryan': 'Ryan - British Male',
        'thomas': 'Thomas - British Male (Deep & Serious) 🔥',
        'libby': 'Libby - British Female (Young)',
        'alfie': 'Alfie - British Male (Young)',
        'natasha': 'Natasha - Australian Female',
        'annette': 'Annette - Australian Female (Deep & Professional) 💎',
        'william': 'William - Australian Male',
        'neerja': 'Neerja - Indian Female',
        'prabhat': 'Prabhat - Indian Male',
    }

    @staticmethod
    async def _generate_async_with_timing(text: str, output_path: Path, voice: str, rate: str):
        """Async TTS generation with word-level timing data"""
        try:
            # Create TTS communicator
            communicate = edge_tts.Communicate(text, voice, rate=rate)

            # Collect word timings
            word_timings = []

            # Generate and save audio with word boundaries
            with open(str(output_path), 'wb') as audio_file:
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_file.write(chunk["data"])
                    elif chunk["type"] == "WordBoundary":
                        # Word timing info from edge-tts
                        word_timings.append({
                            'word': chunk['text'],
                            'offset': chunk['offset'] / 10000000.0,  # Convert to seconds
                            'duration': chunk['duration'] / 10000000.0  # Convert to seconds
                        })

            return True, word_timings
        except Exception as e:
            print(f"⚠ Async TTS generation error: {e}")
            return False, []

    @staticmethod
    async def _generate_async(text: str, output_path: Path, voice: str, rate: str) -> bool:
        """Async TTS generation using edge-tts (legacy - no timing)"""
        try:
            # Create TTS communicator
            communicate = edge_tts.Communicate(text, voice, rate=rate)

            # Generate and save audio
            await communicate.save(str(output_path))
            return True
        except Exception as e:
            print(f"⚠ Async TTS generation error: {e}")
            return False

    @staticmethod
    def generate_voiceover(text: str, output_path: Path, settings: dict = None):
        """Generate natural-sounding voiceover from text using Microsoft Edge TTS
        Returns: (success: bool, word_timings: list)
        """
        if not TTS_AVAILABLE:
            print("⚠ TTS not available - skipping voiceover generation")
            return False, []

        try:
            settings = settings or {}

            # Select voice based on preference (defaults to 'aria')
            voice_key = settings.get('tts_voice', 'aria').lower()
            voice = TTSGenerator.VOICES.get(voice_key, TTSGenerator.VOICES['aria'])

            # Calculate speech rate adjustment
            # Settings range: 100-250 (default 150)
            # edge-tts rate format: "+0%", "-20%", "+50%"
            speed = settings.get('tts_speed', 150)
            rate_percent = int((speed - 150) / 150 * 100)  # Convert to percentage
            rate = f"{rate_percent:+d}%" if rate_percent != 0 else "+0%"

            # Clean text for TTS (remove emojis and special characters)
            clean_text = re.sub(r'[\U0001F300-\U0001F9FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF\U00002600-\U000027BF\U0001F1E0-\U0001F1FF]+', '', text)
            clean_text = clean_text.strip()

            if not clean_text:
                print("⚠ No text to convert after cleaning")
                return False, []

            # Run async TTS generation with word timing
            try:
                # Try to get existing event loop
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is already running, create a new one in a thread
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            asyncio.run,
                            TTSGenerator._generate_async_with_timing(clean_text, output_path, voice, rate)
                        )
                        success, word_timings = future.result(timeout=30)
                else:
                    success, word_timings = loop.run_until_complete(
                        TTSGenerator._generate_async_with_timing(clean_text, output_path, voice, rate)
                    )
            except RuntimeError:
                # No event loop, create a new one
                success, word_timings = asyncio.run(
                    TTSGenerator._generate_async_with_timing(clean_text, output_path, voice, rate)
                )

            if success:
                print(f"✓ Generated natural TTS voiceover: {output_path.name} (voice: {voice})")
                print(f"  {len(word_timings)} words with timing data")
                return True, word_timings
            else:
                return False, []

        except Exception as e:
            print(f"⚠ TTS generation failed: {e}")
            return False, []


class CaptionRenderer:
    """Render synchronized captions/subtitles"""

    @staticmethod
    def create_word_captions(word_timings, video_width, video_height, settings):
        """Create synchronized caption clips for each word"""
        try:
            from moviepy import ImageClip
        except ImportError:
            from moviepy.editor import ImageClip

        caption_clips = []

        # Caption settings
        font_size = settings.get('caption_font_size', 60)
        text_color = (255, 255, 255)  # White
        bg_color = (0, 0, 0)  # Black
        position = settings.get('caption_position', 'bottom')  # top, center, bottom
        words_per_caption = settings.get('caption_words_per_line', 3)  # How many words to show at once

        # Load font
        try:
            font_path = str(Path(r"C:\Windows\Fonts") / 'arialbd.ttf')
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = ImageFont.load_default()

        # Group words into caption segments
        caption_segments = []
        for i in range(0, len(word_timings), words_per_caption):
            segment_words = word_timings[i:i+words_per_caption]
            if not segment_words:
                continue

            # Calculate start and end time for this segment
            start_time = segment_words[0]['offset']
            end_time = segment_words[-1]['offset'] + segment_words[-1]['duration']

            # Combine words
            text = ' '.join([w['word'] for w in segment_words])

            caption_segments.append({
                'text': text,
                'start': start_time,
                'end': end_time
            })

        print(f"✓ Creating {len(caption_segments)} caption segments")

        # Create caption clips
        for segment in caption_segments:
            try:
                text = segment['text']

                # Create PIL image with text
                # First, get text size
                dummy_img = Image.new('RGBA', (1, 1))
                dummy_draw = ImageDraw.Draw(dummy_img)
                bbox = dummy_draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

                # Add padding
                padding = 20
                img_width = min(text_width + padding * 2, int(video_width * 0.9))
                img_height = text_height + padding * 2

                # Create image with background
                img = Image.new('RGBA', (img_width, img_height), bg_color + (180,))  # Semi-transparent black
                draw = ImageDraw.Draw(img)

                # Draw text centered
                text_x = (img_width - text_width) // 2
                text_y = padding
                draw.text((text_x, text_y), text, font=font, fill=text_color + (255,))

                # Convert to numpy array
                frame = np.array(img)

                # Create ImageClip
                clip = ImageClip(frame)
                clip = clip.with_duration(segment['end'] - segment['start'])
                clip = clip.with_start(segment['start'])

                # Position based on settings
                if position == 'top':
                    clip = clip.with_position(('center', int(video_height * 0.1)))
                elif position == 'center':
                    clip = clip.with_position('center')
                else:  # bottom
                    clip = clip.with_position(('center', int(video_height * 0.75)))

                caption_clips.append(clip)

            except Exception as e:
                print(f"⚠ Error creating caption for '{segment['text']}': {e}")
                import traceback
                traceback.print_exc()
                continue

        return caption_clips


class AudioProcessor:
    """Audio processing module for BGM and voiceovers"""

    @staticmethod
    def get_voiceover_files(folder_path: Path) -> List[Path]:
        """Get audio files from voiceover folder sorted by number"""
        if not folder_path or not folder_path.exists():
            return []
        audio_extensions = {'.mp3', '.wav', '.m4a', '.aac', '.ogg'}
        files = [f for f in folder_path.iterdir()
                if f.suffix.lower() in audio_extensions and f.is_file()]

        # Sort by number in filename (1.mp3, 2.mp3, etc.)
        def extract_number(filepath):
            import re
            match = re.search(r'(\d+)', filepath.stem)
            return int(match.group(1)) if match else 999999

        return sorted(files, key=extract_number)

    @staticmethod
    def get_bgm_files(bgm_path: str) -> List[Path]:
        """Get BGM files - supports single file or folder with multiple files"""
        bgm_path = Path(bgm_path)

        if not bgm_path.exists():
            return []

        audio_extensions = {'.mp3', '.wav', '.m4a', '.aac', '.ogg'}

        # Single file
        if bgm_path.is_file() and bgm_path.suffix.lower() in audio_extensions:
            return [bgm_path]

        # Folder with multiple files
        if bgm_path.is_dir():
            files = [f for f in bgm_path.iterdir()
                    if f.suffix.lower() in audio_extensions and f.is_file()]
            return sorted(files)

        return []

    @staticmethod
    def create_looped_audio(audio_clip, target_duration):
        """Loop audio to match video duration"""
        if audio_clip.duration >= target_duration:
            return subclip(audio_clip, 0, target_duration)
        else:
            loops_needed = int(np.ceil(target_duration / audio_clip.duration))
            clips = [audio_clip] * loops_needed
            looped = set_duration(CompositeAudioClip(clips), target_duration)
            return looped

    @staticmethod
    def mix_audio_tracks(video_clip, settings, voiceover_file: Optional[Path] = None, bgm_file: Optional[Path] = None):
        """Mix original audio, BGM, and voiceover"""
        audio_tracks = []

        # Original audio
        if video_clip.audio and not settings.get('mute_original_audio', False):
            # Convert percentage (0-200) to decimal (0.0-2.0)
            volume_percent = settings.get('original_audio_volume', 100)
            original_volume = volume_percent / 100.0
            original_audio = set_volume(video_clip.audio, original_volume)
            audio_tracks.append(original_audio)
            print(f"✓ Original audio volume: {volume_percent}%")

        # Custom BGM (use provided bgm_file or fall back to settings)
        if settings.get('add_custom_bgm', False):
            bgm_path = bgm_file if bgm_file else (Path(settings['bgm_file']) if settings.get('bgm_file') else None)

            if bgm_path and bgm_path.exists():
                try:
                    bgm_audio = AudioFileClip(str(bgm_path))

                    if settings.get('bgm_loop', True):
                        bgm_audio = AudioProcessor.create_looped_audio(bgm_audio, video_clip.duration)
                    else:
                        bgm_audio = subclip(bgm_audio, 0, min(bgm_audio.duration, video_clip.duration))

                    bgm_volume = settings.get('bgm_volume', 0.3)
                    bgm_audio = set_volume(bgm_audio, bgm_volume)
                    audio_tracks.append(bgm_audio)
                    print(f"✓ Added BGM: {bgm_path.name}")
                except Exception as e:
                    print(f"⚠ Could not load BGM: {e}")

        # Voiceover
        if voiceover_file and voiceover_file.exists():
            try:
                voiceover_audio = AudioFileClip(str(voiceover_file))
                voiceover_volume = settings.get('voiceover_volume', 1.0)
                voiceover_delay = settings.get('voiceover_delay', 0.0)

                voiceover_audio = set_volume(voiceover_audio, voiceover_volume)

                if voiceover_delay > 0:
                    silence = set_volume(set_duration(AudioFileClip(str(voiceover_file)), voiceover_delay), 0)
                    try:
                        voiceover_audio = CompositeAudioClip([silence, voiceover_audio.set_start(voiceover_delay)])
                    except:
                        voiceover_audio = CompositeAudioClip([silence, voiceover_audio.with_start(voiceover_delay)])

                audio_tracks.append(voiceover_audio)
                print(f"✓ Added voiceover: {voiceover_file.name}")
            except Exception as e:
                print(f"⚠ Could not load voiceover: {e}")

        # Mix all tracks
        if audio_tracks:
            if len(audio_tracks) == 1:
                return audio_tracks[0]
            else:
                return CompositeAudioClip(audio_tracks)
        else:
            return None


class TextEffects:
    """Text animation and effects module"""

    @staticmethod
    def create_glow_image(img, glow_color=(255, 255, 255), intensity=8):
        """Add glow effect to text image"""
        glow = img.copy()
        for i in range(intensity):
            glow = glow.filter(ImageFilter.GaussianBlur(radius=2))

        result = Image.new('RGBA', img.size, (0, 0, 0, 0))
        result.paste(glow, (0, 0), glow)
        result.paste(img, (0, 0), img)
        return result

    @staticmethod
    def create_shadow_image(img, offset=6, blur=12):
        """Add drop shadow to image"""
        shadow = Image.new('RGBA',
                          (img.width + offset*2, img.height + offset*2),
                          (0, 0, 0, 0))
        shadow_mask = Image.new('RGBA', img.size, (0, 0, 0, 180))
        shadow.paste(shadow_mask, (offset, offset), img)
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur))

        result = Image.new('RGBA', shadow.size, (0, 0, 0, 0))
        result.paste(shadow, (0, 0), shadow)
        result.paste(img, (offset//2, offset//2), img)
        return result

    @staticmethod
    def create_neon_glow(img, neon_color=(0, 255, 136)):
        """Create neon glow effect"""
        glow = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(glow)

        for i in range(20, 0, -2):
            alpha = int(255 * (i / 20) * 0.3)
            color = neon_color + (alpha,)
            temp = img.copy()
            temp = temp.filter(ImageFilter.GaussianBlur(radius=i))

        result = Image.new('RGBA', img.size, (0, 0, 0, 0))
        for i in range(15):
            blur_img = img.filter(ImageFilter.GaussianBlur(radius=i))
            result = Image.alpha_composite(result, blur_img)
        result = Image.alpha_composite(result, img)
        return result

    @staticmethod
    def apply_gradient_overlay(img, gradient_type='top_to_bottom', intensity=0.3):
        """Apply gradient overlay"""
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        if gradient_type == 'top_to_bottom':
            for y in range(img.height):
                alpha = int(255 * intensity * (y / img.height))
                draw.line([(0, y), (img.width, y)], fill=(0, 0, 0, alpha))
        elif gradient_type == 'bottom_to_top':
            for y in range(img.height):
                alpha = int(255 * intensity * ((img.height - y) / img.height))
                draw.line([(0, y), (img.width, y)], fill=(0, 0, 0, alpha))

        return Image.alpha_composite(img, overlay)


class VideoQuoteAutomation:
    """Automate adding quotes to videos with advanced effects"""

    def __init__(self):
        self.video_folder = Path(r"E:\MyAutomations\ScriptAutomations\VideoFolder\SourceVideosToEdit\Libriana8")
        self.quotes_file = Path(r"E:\MyAutomations\ScriptAutomations\VideoFolder\Quotes.txt")
        self.output_folder = Path(r"E:\MyAutomations\ScriptAutomations\VideoFolder\FinalVideos")

        self.output_folder.mkdir(parents=True, exist_ok=True)

        self.settings = self.load_settings()

        self.log_file = self.output_folder / "processing_log.json"
        self.processing_log = self._load_log()

        # Load voiceover files if enabled
        self.voiceover_files = []
        if self.settings.get('add_voiceover', False) and self.settings.get('voiceover_folder'):
            voiceover_folder = Path(self.settings['voiceover_folder'])
            self.voiceover_files = AudioProcessor.get_voiceover_files(voiceover_folder)
            if self.voiceover_files:
                print(f"✓ Loaded {len(self.voiceover_files)} voiceover files (sorted by number)")
                for i, vf in enumerate(self.voiceover_files[:5], 1):
                    print(f"  {i}. {vf.name}")
            else:
                print(f"⚠ No voiceover files found in {voiceover_folder}")

        # Load BGM files if enabled
        self.bgm_files = []
        if self.settings.get('add_custom_bgm', False) and self.settings.get('bgm_file'):
            self.bgm_files = AudioProcessor.get_bgm_files(self.settings['bgm_file'])
            if self.bgm_files:
                if len(self.bgm_files) == 1:
                    print(f"✓ Loaded 1 BGM file: {self.bgm_files[0].name}")
                else:
                    print(f"✓ Loaded {len(self.bgm_files)} BGM files (will select randomly per video)")
                    for i, bf in enumerate(self.bgm_files[:5], 1):
                        print(f"  {i}. {bf.name}")
            else:
                print(f"⚠ No BGM files found")

    def load_settings(self) -> dict:
        """Load settings from GUI config file"""
        settings_file = Path('overlay_settings.json')

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
            'position': 'top',
            'text_fade_in': True,
            'text_fade_duration': 0.4,
            'text_glow': True,
            'glow_intensity': 8,
            'vignette': True,
            'vignette_intensity': 0.4,
            'video_zoom': True,
            'zoom_scale': 1.08,
            'drop_shadow': True,
            'shadow_offset': 6,
            'shadow_blur': 12
        }

        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    print("✓ Loaded enhanced settings from overlay_settings.json")
                    return loaded_settings
            except Exception as e:
                print(f"⚠ Could not load settings: {e}")
                return default_settings
        else:
            print("⚠ No settings file found")
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

        if re.match(r'^\s*\d+\.', content, re.MULTILINE):
            parts = re.split(r'\n\s*\d+\.\s*', content)
            quotes = [q.strip() for q in parts[1:] if q.strip()]
        elif '\n\n' in content:
            quotes = [q.strip() for q in content.split('\n\n') if q.strip()]
        elif '---' in content:
            quotes = [q.strip() for q in content.split('---') if q.strip()]
        else:
            quotes = [line.strip() for line in content.split('\n') if line.strip()]

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

    def create_text_overlay_image(self, video_width, video_height, main_text, emoji_line, cta_text):
        """Create text overlay with all effects applied"""
        img_width = video_width
        temp_img = Image.new('RGBA', (img_width, 1000), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)

        font_size = self.settings['font_size']
        cta_font_size = self.settings.get('cta_font_size', int(font_size * 0.95))

        try:
            main_font_file = self.settings.get('font_file', 'arialbd.ttf')
            if not Path(main_font_file).exists():
                main_font_file = str(Path(r"C:\Windows\Fonts") / Path(main_font_file).name)

            main_font = ImageFont.truetype(main_font_file, font_size)

            emoji_font_path = str(Path(r"C:\Windows\Fonts") / 'seguiemj.ttf')
            emoji_font = ImageFont.truetype(emoji_font_path, int(font_size * self.settings['emoji_size_multiplier']))

            cta_font_file = self.settings.get('cta_font_file', 'ariali.ttf')
            if not Path(cta_font_file).exists():
                cta_font_file = str(Path(r"C:\Windows\Fonts") / Path(cta_font_file).name)

            cta_font = ImageFont.truetype(cta_font_file, cta_font_size)

        except Exception as e:
            print(f"⚠ Font loading error: {e}")
            main_font = ImageFont.load_default()
            emoji_font = main_font
            cta_font = main_font

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

        sections = []
        if main_text_wrapped:
            sections.append((main_text_wrapped, main_font, True, 'main'))

        if self.settings.get('emoji_enabled', True) and emoji_line:
            sections.append((emoji_line, emoji_font, False, 'emoji'))

        if self.settings.get('cta_enabled', True) and cta_text:
            sections.append((cta_text, cta_font, False, 'cta'))

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

        total_height = sum(box['height'] for box in section_boxes)
        total_height += (len(section_boxes) - 1) * self.settings['section_spacing']
        total_height += self.settings['padding_vertical'] * 2
        total_height += len(section_boxes) * self.settings['inner_padding'] * 2

        box_height = int(total_height + 100)
        box_width = img_width

        extra_margin = 0
        if self.settings.get('drop_shadow', False):
            extra_margin = self.settings.get('shadow_offset', 6) * 2

        img = Image.new('RGBA', (box_width + extra_margin, box_height + extra_margin), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        bg_rgb = self.hex_to_rgb(self.settings['bg_color'])
        bg_alpha = int(255 * (self.settings['bg_opacity'] / 100))
        white_bg = bg_rgb + (bg_alpha,)

        cta_bg_rgb = self.hex_to_rgb(self.settings['cta_bg_color'])
        red_bg = cta_bg_rgb + (255,)

        if self.settings['position'] == 'top':
            current_y = self.settings['padding_vertical']
        elif self.settings['position'] == 'center':
            current_y = (box_height - total_height) // 2
        else:
            current_y = box_height - total_height - self.settings['padding_vertical']

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

            draw.rounded_rectangle(
                [(bubble_x, current_y), (bubble_x + bubble_width, current_y + bubble_height)],
                radius=self.settings['corner_radius'],
                fill=current_bg
            )

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

        if self.settings.get('drop_shadow', False):
            img = TextEffects.create_shadow_image(
                img,
                offset=self.settings.get('shadow_offset', 6),
                blur=self.settings.get('shadow_blur', 12)
            )

        if self.settings.get('text_glow', False):
            glow_rgb = self.hex_to_rgb(self.settings.get('glow_color', '#ffffff'))
            img = TextEffects.create_glow_image(
                img,
                glow_color=glow_rgb,
                intensity=self.settings.get('glow_intensity', 8)
            )

        if self.settings.get('neon_glow', False):
            neon_rgb = self.hex_to_rgb(self.settings.get('neon_color', '#00ff88'))
            img = TextEffects.create_neon_glow(img, neon_color=neon_rgb)

        if self.settings.get('gradient_overlay', False):
            img = TextEffects.apply_gradient_overlay(
                img,
                gradient_type=self.settings.get('gradient_type', 'top_to_bottom'),
                intensity=self.settings.get('gradient_intensity', 0.3)
            )

        return img

    def add_quote_to_video(self, video_path: Path, quote: str, video_index: int = 0) -> Tuple[Path, str]:
        """Add quote overlay with advanced effects"""
        print(f"\n{'='*70}")
        print(f"Processing: {video_path.name}")
        print(f"Quote: {quote[:80]}...")

        hashtags = self.generate_hashtags(quote)
        print(f"Hashtags: {', '.join(hashtags)}")

        output_filename = self.create_filename(quote, hashtags)
        print(f"Output: {output_filename}")

        video = VideoFileClip(str(video_path))

        emoji_pattern = re.compile(r'[\U0001F300-\U0001F9FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF\U00002600-\U000027BF\U0001F1E0-\U0001F1FF]+')

        emojis_found = emoji_pattern.findall(quote)
        text_without_emojis = emoji_pattern.sub(' ', quote).strip()

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

        img = self.create_text_overlay_image(video.w, video.h, main_text, emoji_line, cta_text)
        img_array = np.array(img)

        txt_clip = set_duration(ImageClip(img_array), video.duration)

        if self.settings.get('text_fade_in', False):
            fade_duration = self.settings.get('text_fade_duration', 0.4)
            txt_clip = txt_clip.fadein(fade_duration)

        if self.settings.get('text_slide_up', False):
            slide_distance = self.settings.get('text_slide_distance', 50)
            def slide_position(t):
                if t < 0.5:
                    offset = slide_distance * (1 - t / 0.5)
                    return ('center', video.h - txt_clip.h - offset) if self.settings['position'] == 'bottom' else ('center', offset)
                else:
                    if self.settings['position'] == 'top':
                        return ('center', 0)
                    elif self.settings['position'] == 'center':
                        return ('center', 'center')
                    else:
                        return ('center', video.h - txt_clip.h)
            txt_clip = set_position(txt_clip, slide_position)
        else:
            if self.settings['position'] == 'top':
                txt_clip = set_position(txt_clip, ('center', 0))
            elif self.settings['position'] == 'center':
                txt_clip = set_position(txt_clip, ('center', 'center'))
            else:
                txt_clip = set_position(txt_clip, ('center', video.h - txt_clip.h))

        if self.settings.get('video_zoom', False):
            zoom_scale = self.settings.get('zoom_scale', 1.08)
            def zoom_effect(get_frame, t):
                frame = get_frame(t)
                progress = t / video.duration
                current_scale = 1 + (zoom_scale - 1) * progress
                h, w = frame.shape[:2]
                new_h, new_w = int(h * current_scale), int(w * current_scale)
                from PIL import Image as PILImage
                pil_frame = PILImage.fromarray(frame)
                pil_frame = pil_frame.resize((new_w, new_h), PILImage.LANCZOS)
                crop_x = (new_w - w) // 2
                crop_y = (new_h - h) // 2
                pil_frame = pil_frame.crop((crop_x, crop_y, crop_x + w, crop_y + h))
                return np.array(pil_frame)
            try:
                video = video.transform(zoom_effect)
            except AttributeError:
                video = video.fl(zoom_effect)

        if self.settings.get('color_grade', 'none') != 'none':
            grade_type = self.settings.get('color_grade', 'warm')
            try:
                video = video.image_transform(lambda frame: VideoEffects.apply_color_grade(frame, grade_type))
            except AttributeError:
                video = video.fl_image(lambda frame: VideoEffects.apply_color_grade(frame, grade_type))

        if self.settings.get('vignette', False):
            intensity = self.settings.get('vignette_intensity', 0.4)
            try:
                video = video.image_transform(lambda frame: VideoEffects.apply_vignette(frame, intensity))
            except AttributeError:
                video = video.fl_image(lambda frame: VideoEffects.apply_vignette(frame, intensity))

        if self.settings.get('background_dim', False):
            intensity = self.settings.get('dim_intensity', 0.25)
            try:
                video = video.image_transform(lambda frame: VideoEffects.apply_background_dim(frame, intensity))
            except AttributeError:
                video = video.fl_image(lambda frame: VideoEffects.apply_background_dim(frame, intensity))

        if self.settings.get('film_grain', False):
            intensity = self.settings.get('grain_intensity', 0.15)
            try:
                video = video.image_transform(lambda frame: VideoEffects.apply_film_grain(frame, intensity))
            except AttributeError:
                video = video.fl_image(lambda frame: VideoEffects.apply_film_grain(frame, intensity))

        # Start with video and text overlay
        layers = [video, txt_clip]

        # Add particle effects if enabled
        if self.settings.get('add_glitter', False):
            try:
                intensity = self.settings.get('glitter_intensity', 0.5)
                glitter = ParticleEffects.create_glitter_overlay(
                    video.w, video.h, video.duration, video.fps, intensity
                )
                layers.append(glitter)
                print(f"✓ Added glitter effect (intensity: {intensity})")
            except Exception as e:
                print(f"⚠ Glitter effect failed: {e}")

        if self.settings.get('add_stars', False):
            try:
                stars = ParticleEffects.create_stars_overlay(
                    video.w, video.h, video.duration, video.fps, particle_type='star'
                )
                layers.append(stars)
                print("✓ Added falling stars effect")
            except Exception as e:
                print(f"⚠ Stars effect failed: {e}")

        if self.settings.get('add_hearts', False):
            try:
                hearts = ParticleEffects.create_stars_overlay(
                    video.w, video.h, video.duration, video.fps, particle_type='heart'
                )
                layers.append(hearts)
                print("✓ Added falling hearts effect")
            except Exception as e:
                print(f"⚠ Hearts effect failed: {e}")

        if self.settings.get('add_confetti', False):
            try:
                confetti = ParticleEffects.create_confetti_overlay(
                    video.w, video.h, video.duration, video.fps
                )
                layers.append(confetti)
                print("✓ Added confetti effect")
            except Exception as e:
                print(f"⚠ Confetti effect failed: {e}")

        final_video = CompositeVideoClip(layers)

        # Audio processing
        voiceover_file = None
        word_timings = []

        # Option 1: Generate TTS voiceover from text
        if self.settings.get('use_tts_voiceover', False) and TTS_AVAILABLE:
            tts_folder = self.output_folder / "tts_voiceovers"
            tts_folder.mkdir(exist_ok=True)

            tts_filename = f"tts_{video_index + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
            tts_path = tts_folder / tts_filename

            # Generate TTS from the quote text
            success, word_timings = TTSGenerator.generate_voiceover(quote, tts_path, self.settings)
            if success:
                voiceover_file = tts_path
                print(f"✓ Using TTS voiceover: {tts_filename}")

                # Save word timings for caption generation
                if word_timings:
                    timing_file = tts_path.with_suffix('.json')
                    with open(timing_file, 'w') as f:
                        json.dump(word_timings, f, indent=2)
                    print(f"✓ Saved {len(word_timings)} word timings")

        # Option 2: Use pre-recorded voiceover files
        elif self.settings.get('add_voiceover', False) and self.voiceover_files:
            if video_index < len(self.voiceover_files):
                voiceover_file = self.voiceover_files[video_index]
                print(f"✓ Using voiceover {video_index + 1}: {voiceover_file.name}")
            else:
                print(f"⚠ No voiceover file for video index {video_index + 1}")

        # Select BGM (random if multiple files)
        bgm_file = None
        if self.settings.get('add_custom_bgm', False) and self.bgm_files:
            if len(self.bgm_files) == 1:
                bgm_file = self.bgm_files[0]
            else:
                import random
                bgm_file = random.choice(self.bgm_files)
                print(f"🎵 Random BGM selected: {bgm_file.name}")

        final_audio = AudioProcessor.mix_audio_tracks(video, self.settings, voiceover_file, bgm_file)

        if final_audio:
            final_video = set_audio(final_video, final_audio)
        elif self.settings.get('mute_original_audio', False):
            final_video = final_video.without_audio()
            print("✓ Original audio muted")

        # Add synchronized captions if enabled and we have word timings
        if self.settings.get('enable_captions', False) and word_timings:
            try:
                print("Adding synchronized captions...")
                caption_clips = CaptionRenderer.create_word_captions(
                    word_timings,
                    video.w,
                    video.h,
                    self.settings
                )

                if caption_clips:
                    # Composite video with captions
                    all_clips = [final_video] + caption_clips
                    final_video = CompositeVideoClip(all_clips)
                    print(f"✓ Added {len(caption_clips)} synchronized caption segments")

            except Exception as e:
                print(f"⚠ Caption rendering failed: {e}")
                print("  Continuing without captions...")

        output_path = self.output_folder / output_filename
        counter = 1
        original_output_path = output_path
        while output_path.exists():
            stem = original_output_path.stem
            output_path = self.output_folder / f"{stem}_{counter}.mp4"
            counter += 1

        print(f"Rendering with effects... This may take a few minutes.")
        final_video.write_videofile(
            str(output_path),
            codec='libx264',
            audio_codec='aac',
            fps=video.fps,
            preset='medium',
            threads=4,
            logger=None
        )

        video.close()
        txt_clip.close()
        final_video.close()

        print(f"✓ Saved: {output_path.name}")
        print(f"{'='*70}")

        return output_path, output_filename

    def process_all(self, start_from: int = 0, sort_by: str = 'created'):
        """Process all videos with enhanced effects"""
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
        print(f"ENHANCED BATCH PROCESSING")
        print(f"{'='*70}")
        print(f"Settings: overlay_settings.json")
        print(f"Effects enabled:")
        if self.settings.get('text_fade_in'): print("  ✓ Text fade-in")
        if self.settings.get('text_glow'): print("  ✓ Text glow")
        if self.settings.get('vignette'): print("  ✓ Vignette")
        if self.settings.get('video_zoom'): print("  ✓ Video zoom")
        if self.settings.get('drop_shadow'): print("  ✓ Drop shadow")
        if self.settings.get('color_grade', 'none') != 'none':
            print(f"  ✓ Color grade: {self.settings['color_grade']}")
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
                output_path, filename = self.add_quote_to_video(video_path, quote, video_index=i)

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

        print(f"\n{'='*70}")
        print(f"PROCESSING COMPLETE!")
        print(f"{'='*70}")
        success_count = sum(1 for r in results if r['status'] == 'success')
        print(f"Success: {success_count}/{len(results)}")
        print(f"Output: {self.output_folder}")
        print(f"{'='*70}\n")

        return results


if __name__ == "__main__":
    print("Enhanced Video Quote Automation")
    print("="*70)

    automation = VideoQuoteAutomation()

    automation.process_all(
        start_from=0,
        sort_by='created'
    )

    print("\n✓ All done! Check FinalVideos folder.")
