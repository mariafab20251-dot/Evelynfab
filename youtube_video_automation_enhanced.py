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
    from moviepy.video.fx import Resize, FadeIn
    from moviepy.audio.fx import MultiplyVolume, AudioLoop
except ImportError:
    from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, AudioFileClip, CompositeAudioClip
    from moviepy.video.fx.resize import resize as Resize
    from moviepy.audio.fx.volumex import volumex as MultiplyVolume
    AudioLoop = None
    FadeIn = None

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
        # Work on a copy to avoid modifying read-only arrays
        frame = frame.copy()
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
        # Work on a copy to avoid modifying read-only arrays
        frame = frame.copy()
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
        # Work on a copy to avoid modifying read-only arrays
        frame = frame.copy()
        noise = np.random.normal(0, intensity * 255, frame.shape)
        return np.clip(frame + noise, 0, 255).astype('uint8')

    @staticmethod
    def apply_background_dim(frame, intensity=0.25):
        """Dim the background"""
        # Work on a copy to avoid modifying read-only arrays
        frame = frame.copy()
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
            # Create black frame (RGB)
            frame = np.zeros((height, width, 3), dtype=np.uint8).copy()

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

                # Draw sparkle (white with brightness)
                y1, y2 = max(0, y-size), min(height, y+size)
                x1, x2 = max(0, x-size), min(width, x+size)

                frame[y1:y2, x1:x2, :] = [brightness, brightness, brightness]  # White sparkle

            return frame.copy()

        def make_mask(t):
            # Create mask where white sparkles are opaque and black is transparent
            frame = make_frame(t)
            # Convert to grayscale for mask (bright areas = opaque, dark = transparent)
            mask = frame[:, :, 0].astype('uint8')  # Use any channel since it's grayscale
            return mask

        clip = VideoClip(make_frame, duration=duration)
        mask_clip = VideoClip(make_mask, duration=duration, is_mask=True)

        try:
            clip = clip.set_fps(fps)
            mask_clip = mask_clip.set_fps(fps)
            clip = clip.set_mask(mask_clip)
        except AttributeError:
            clip = clip.with_fps(fps)
            mask_clip = mask_clip.with_fps(fps)
            clip = clip.with_mask(mask_clip)

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
            # Create transparent RGBA frame
            frame_rgba = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(frame_rgba)

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
                    draw.polygon(points, fill=(255, 255, 100, 255))  # Yellow

                elif particle_type == 'heart':
                    # Draw heart (simplified circle-based)
                    draw.ellipse([x-size//2, y-size//2, x, y+size//2], fill=(255, 50, 50, 255))
                    draw.ellipse([x, y-size//2, x+size//2, y+size//2], fill=(255, 50, 50, 255))
                    draw.polygon([(x-size//2, y), (x+size//2, y), (x, y+size)], fill=(255, 50, 50, 255))

                elif particle_type == 'circle':
                    # Simple colorful circles
                    colors = [(255, 100, 100, 255), (100, 255, 100, 255),
                             (100, 100, 255, 255), (255, 255, 100, 255)]
                    color = colors[hash(str(particle['x'])) % len(colors)]
                    draw.ellipse([x-size//2, y-size//2, x+size//2, y+size//2], fill=color)

            # Convert RGBA to RGB for video, and create separate mask
            frame_rgb = Image.new('RGB', (width, height), (0, 0, 0))
            frame_rgb.paste(frame_rgba, mask=frame_rgba.split()[3])
            return np.array(frame_rgb).copy()

        def make_mask(t):
            # Extract alpha channel as mask
            frame_rgba = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(frame_rgba)

            for particle in particles:
                y = int(particle['y_start'] + particle['speed'] * t)
                if y > height + 50:
                    y = y % (height + 100) - 50
                x = int(particle['x'])
                size = particle['size']

                if particle_type == 'star':
                    points = []
                    for i in range(10):
                        angle = (i * 36) * np.pi / 180
                        r = size if i % 2 == 0 else size // 2
                        px = x + r * np.cos(angle)
                        py = y + r * np.sin(angle)
                        points.append((px, py))
                    draw.polygon(points, fill=(255, 255, 255, 255))
                elif particle_type == 'heart':
                    draw.ellipse([x-size//2, y-size//2, x, y+size//2], fill=(255, 255, 255, 255))
                    draw.ellipse([x, y-size//2, x+size//2, y+size//2], fill=(255, 255, 255, 255))
                    draw.polygon([(x-size//2, y), (x+size//2, y), (x, y+size)], fill=(255, 255, 255, 255))
                elif particle_type == 'circle':
                    draw.ellipse([x-size//2, y-size//2, x+size//2, y+size//2], fill=(255, 255, 255, 255))

            # Return alpha channel as grayscale mask
            alpha = frame_rgba.split()[3]
            return np.array(alpha).copy()

        clip = VideoClip(make_frame, duration=duration)
        mask_clip = VideoClip(make_mask, duration=duration, is_mask=True)

        try:
            clip = clip.set_fps(fps)
            mask_clip = mask_clip.set_fps(fps)
            clip = clip.set_mask(mask_clip)
        except AttributeError:
            clip = clip.with_fps(fps)
            mask_clip = mask_clip.with_fps(fps)
            clip = clip.with_mask(mask_clip)

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

        # Additional Professional Deep Voices
        'andrew': 'en-US-AndrewNeural',       # News anchor, very deep authoritative male (ULTRA DEEP)
        'brian': 'en-US-BrianNeural',         # Deep, serious male narrator (ULTRA DEEP)
        'ana': 'en-US-AnaNeural',             # Deep, professional female narrator (DEEP)
        'brandon': 'en-US-BrandonNeural',     # Deep, mature male (DEEP)
        'emma': 'en-US-EmmaNeural',           # Professional, warm female
        'jacob': 'en-US-JacobNeural',         # Deep, confident male (DEEP)

        # PREMIUM MOTIVATIONAL VOICES (Perfect for quotes & inspiration)
        'steffan_multi': 'en-US-SteffanMultilingualNeural',  # Powerful multilingual (MOTIVATION KING)
        'andrew_multi': 'en-US-AndrewMultilingualNeural',    # Deep motivational narrator (ULTRA POWERFUL)
        'ava_multi': 'en-US-AvaMultilingualNeural',          # Commanding female (POWERFUL MOTIVATION)
        'emma_multi': 'en-US-EmmaMultilingualNeural',        # Warm inspirational female (INSPIRING)
        'brian_multi': 'en-US-BrianMultilingualNeural',      # Deep powerful narrator (EPIC MOTIVATION)
        'alloy': 'en-US-AlloyMultilingualNeural',            # Smooth deep male (PREMIUM DEEP)
        'nova': 'en-US-NovaMultilingualNeural',              # Clear powerful female (PREMIUM)
        'shimmer': 'en-US-ShimmerMultilingualNeural',        # Energetic motivational (HIGH ENERGY)

        # Additional Powerful Voices
        'kai': 'en-US-KaiNeural',                            # Deep authoritative male (COMMAND)
        'luna': 'en-US-LunaNeural',                          # Rich warm female (INSPIRING)
        'jenny_multi': 'en-US-JennyMultilingualNeural',      # Energetic multilingual female (UPBEAT)
        'ryan_multi': 'en-US-RyanMultilingualNeural',        # Deep confident male (STRONG)

        # URDU VOICES (اردو آوازیں)
        # Pakistani Urdu (Best for Poetry & Motivation)
        'asad': 'ur-PK-AsadNeural',           # Pakistani Male (Deep Professional - BEST FOR MOTIVATION)
        'uzma': 'ur-PK-UzmaNeural',           # Pakistani Female (Clear Expressive - BEST FOR POETRY)

        # Indian Urdu (Rich & Cultural)
        'salman': 'ur-IN-SalmanNeural',       # Indian Male (Warm Poetic - GREAT FOR SHAYARI)
        'gul': 'ur-IN-GulNeural',             # Indian Female (Soft Melodious - POETRY)

        # Multilingual Urdu Support (Premium for Poetry)
        'asad_multi': 'ur-PK-AsadMultilingualNeural',    # Pakistani Multi (POWERFUL MOTIVATION)
        'uzma_multi': 'ur-PK-UzmaMultilingualNeural',    # Pakistani Multi (EXPRESSIVE POETRY)

        # Additional Regional Voices (Supporting Urdu)
        'faiz': 'ur-PK-AsadNeural',           # Alias for poetry (named after Faiz Ahmed Faiz)
        'parveen': 'ur-PK-UzmaNeural',        # Alias for female poetry (Parveen Shakir style)

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
        'andrew': 'Andrew - US Male (Ultra Deep News Anchor) 🎙️',
        'brian': 'Brian - US Male (Ultra Deep Narrator) 🎙️',
        'ana': 'Ana - US Female (Deep Professional Narrator) 💎',
        'brandon': 'Brandon - US Male (Deep & Mature) 🔥',
        'emma': 'Emma - US Female (Professional & Warm)',
        'jacob': 'Jacob - US Male (Deep & Confident) 🔥',

        # Premium Motivational Voices
        'steffan_multi': '⭐ Steffan Multi - US Male (MOTIVATION KING) 👑',
        'andrew_multi': '⭐ Andrew Multi - US Male (Ultra Powerful Motivation) 🚀',
        'ava_multi': '⭐ Ava Multi - US Female (Commanding & Powerful) 💪',
        'emma_multi': '⭐ Emma Multi - US Female (Warm & Inspiring) ✨',
        'brian_multi': '⭐ Brian Multi - US Male (Epic Deep Narrator) 🎬',
        'alloy': '⭐ Alloy - US Male (Premium Smooth Deep) 💎',
        'nova': '⭐ Nova - US Female (Premium Clear & Powerful) 🌟',
        'shimmer': '⭐ Shimmer - US Female (High Energy Motivation) ⚡',
        'kai': 'Kai - US Male (Deep Authoritative Command) 🎖️',
        'luna': 'Luna - US Female (Rich Warm Inspiring) 🌙',
        'jenny_multi': 'Jenny Multi - US Female (Energetic Upbeat) 🎉',
        'ryan_multi': 'Ryan Multi - US Male (Deep Confident Strong) 💪',

        # Urdu Voices - اردو آوازیں
        # Pakistani Urdu (پاکستانی اردو)
        'asad': '⭐ اسد Asad - Pakistani Male (MOTIVATION MASTER) 🇵🇰💪',
        'uzma': '⭐ عظمیٰ Uzma - Pakistani Female (POETRY QUEEN) 🇵🇰📖',
        'asad_multi': '🌟 اسد Multi - Pakistani (Powerful Motivation) 🇵🇰🚀',
        'uzma_multi': '🌟 عظمیٰ Multi - Pakistani (Expressive Poetry) 🇵🇰✨',

        # Indian Urdu (ہندوستانی اردو)
        'salman': '📜 سلمان Salman - Indian Male (Shayari Master) 🇮🇳',
        'gul': '🌺 گل Gul - Indian Female (Melodious Poetry) 🇮🇳',

        # Poetry Aliases (شاعری)
        'faiz': '🎭 فیض Faiz - Poetry Deep (Like Faiz Ahmed Faiz) 📖',
        'parveen': '💫 پروین Parveen - Female Poetry (Parveen Shakir) 🌹',
    }

    @staticmethod
    async def _generate_async_with_timing(text: str, output_path: Path, voice: str, rate: str):
        """Async TTS generation with word-level timing data"""
        try:
            # Create TTS communicator
            communicate = edge_tts.Communicate(text, voice, rate=rate)

            # Collect word timings
            word_timings = []
            chunk_count = 0
            audio_chunks = 0
            word_boundary_chunks = 0

            # Generate and save audio with word boundaries
            with open(str(output_path), 'wb') as audio_file:
                async for chunk in communicate.stream():
                    chunk_count += 1
                    chunk_type = chunk.get("type", "unknown")

                    if chunk_type == "audio":
                        audio_file.write(chunk["data"])
                        audio_chunks += 1
                    elif chunk_type == "WordBoundary":
                        word_boundary_chunks += 1
                        # Word timing info from edge-tts
                        word_info = {
                            'word': chunk.get('text', ''),
                            'offset': chunk.get('offset', 0) / 10000000.0,  # Convert to seconds
                            'duration': chunk.get('duration', 0) / 10000000.0  # Convert to seconds
                        }
                        word_timings.append(word_info)
                    # Also check for lowercase variant
                    elif chunk_type == "word_boundary":
                        word_boundary_chunks += 1
                        word_info = {
                            'word': chunk.get('text', ''),
                            'offset': chunk.get('offset', 0) / 10000000.0,
                            'duration': chunk.get('duration', 0) / 10000000.0
                        }
                        word_timings.append(word_info)

            print(f"  TTS Debug: {chunk_count} total chunks, {audio_chunks} audio, {word_boundary_chunks} word boundaries")

            # If no word boundaries, split text into words and estimate timing
            if not word_timings:
                print(f"  ⚠ No word boundaries from TTS - using text splitting for word-level captions")
                words = text.split()
                if words:
                    # Estimate word duration (total audio duration / number of words)
                    # We'll calculate actual duration after file is created
                    for i, word in enumerate(words):
                        word_timings.append({
                            'word': word,
                            'offset': i,  # Placeholder - will be calculated later
                            'duration': 1  # Placeholder
                        })

            return True, word_timings
        except Exception as e:
            print(f"⚠ Async TTS generation error: {e}")
            import traceback
            traceback.print_exc()
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
            # Settings range: 100-250 (default 130 - slower for better caption sync)
            # edge-tts rate format: "+0%", "-20%", "+50%"
            speed = settings.get('tts_speed', 130)
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
    def create_estimated_captions(text, audio_duration, video_width, video_height, settings):
        """Create captions with estimated timing when word-level timing is unavailable"""
        caption_clips = []

        # Extract emojis from text (CapCut-style emoji integration)
        import re
        emoji_pattern = re.compile(r'[\U0001F300-\U0001F9FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF\U00002600-\U000027BF\U0001F1E0-\U0001F1FF]+')
        emojis_found = emoji_pattern.findall(text)

        # Remove emojis from text for word counting
        clean_text = emoji_pattern.sub('', text).strip()

        if not clean_text or audio_duration <= 0:
            return []

        # Split into words
        words = clean_text.split()
        if not words:
            return []

        # Caption settings
        words_per_caption = settings.get('caption_words_per_line', 3)
        font_size = settings.get('caption_font_size', 60)
        position = settings.get('caption_position', 'bottom')
        emoji_in_captions = settings.get('emoji_in_captions', True)  # Enable/disable emoji feature

        # IMPROVED TIMING CALCULATION
        # Use natural speaking rate instead of spreading words across full audio duration
        # This fixes the issue when subtitle text is SHORT but voiceover is LONG

        # Use TTS speed setting from user (default 150 wpm)
        # Standard rates: Slow=100, Normal=150, Fast=200 words per minute
        speaking_rate_wpm = settings.get('tts_speed', 150)
        time_per_word = 60.0 / speaking_rate_wpm  # Convert WPM to seconds per word

        # Calculate natural duration for this text
        natural_duration = len(words) * time_per_word

        # If natural duration exceeds audio, use audio duration instead
        # This handles cases where text is very long relative to audio
        if natural_duration > audio_duration:
            time_per_word = audio_duration / len(words)
            caption_duration = audio_duration
        else:
            caption_duration = natural_duration

        print(f"  Caption timing: {len(words)} words, {caption_duration:.2f}s duration ({time_per_word:.2f}s per word)")

        # No timing offset - start at 0 for better sync
        timing_offset = 0.0

        # Load fonts
        try:
            # Text font (Arial Bold)
            font_path = str(Path(r"C:\Windows\Fonts") / 'arialbd.ttf')
            font = ImageFont.truetype(font_path, font_size)

            # Emoji font (Segoe UI Emoji for proper emoji rendering)
            emoji_font_path = str(Path(r"C:\Windows\Fonts") / 'seguiemj.ttf')
            emoji_font = ImageFont.truetype(emoji_font_path, int(font_size * 1.2))  # Slightly larger
        except:
            font = ImageFont.load_default()
            emoji_font = font

        # Distribute emojis across segments (1 emoji per 2-3 words, CapCut style)
        emoji_distribution = []
        if emoji_in_captions and emojis_found:
            total_segments = (len(words) + words_per_caption - 1) // words_per_caption
            emoji_interval = 2  # Show emoji every 2 segments (adjust based on preference)

            for seg_idx in range(total_segments):
                # Distribute emojis evenly
                if emojis_found and seg_idx % emoji_interval == 0:
                    emoji_idx = (seg_idx // emoji_interval) % len(emojis_found)
                    emoji_distribution.append(emojis_found[emoji_idx])
                else:
                    emoji_distribution.append('')  # No emoji for this segment

            print(f"  Emojis found: {emojis_found}, distributed across {len(emoji_distribution)} segments")

        # Create caption segments
        current_time = 0.0
        for i in range(0, len(words), words_per_caption):
            segment_words = words[i:i+words_per_caption]
            text_content = ' '.join(segment_words)

            # Add emoji for this segment (CapCut style)
            segment_index = i // words_per_caption
            emoji_for_segment = ''
            if emoji_in_captions and segment_index < len(emoji_distribution):
                emoji_for_segment = emoji_distribution[segment_index]

            # Calculate timing - start slightly early for better sync
            start_time = max(0, current_time - timing_offset)  # Don't go negative
            duration = len(segment_words) * time_per_word
            current_time += duration

            try:
                # Calculate dimensions for text + emoji
                dummy_img = Image.new('RGBA', (1, 1))
                dummy_draw = ImageDraw.Draw(dummy_img)

                # Measure text
                bbox = dummy_draw.textbbox((0, 0), text_content, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

                # Measure emoji if present
                emoji_width = 0
                emoji_height = 0
                emoji_spacing = 15  # Space between text and emoji
                if emoji_for_segment:
                    emoji_bbox = dummy_draw.textbbox((0, 0), emoji_for_segment, font=emoji_font)
                    emoji_width = (emoji_bbox[2] - emoji_bbox[0]) + emoji_spacing
                    emoji_height = emoji_bbox[3] - emoji_bbox[1]

                # Calculate total dimensions
                total_width = text_width + emoji_width
                padding = 20
                img_width = min(total_width + padding * 2, int(video_width * 0.9))
                img_height = max(text_height, emoji_height) + padding * 2

                # Create caption image with SOLID black background (no transparency)
                img_rgb = Image.new('RGB', (img_width, img_height), (0, 0, 0))  # Solid black
                draw = ImageDraw.Draw(img_rgb)

                # Draw text (left-aligned within center)
                content_start_x = (img_width - total_width) // 2
                text_y = padding
                draw.text((content_start_x, text_y), text_content, font=font, fill=(255, 255, 255))  # White text

                # Draw emoji next to text (CapCut style)
                if emoji_for_segment:
                    emoji_x = content_start_x + text_width + emoji_spacing
                    draw.text((emoji_x, text_y - 5), emoji_for_segment, font=emoji_font, fill=(255, 255, 255))

                # Create clip - no mask needed since background is solid
                frame = np.array(img_rgb).copy()

                try:
                    from moviepy import ImageClip
                except ImportError:
                    from moviepy.editor import ImageClip

                clip = ImageClip(frame, is_mask=False)

                try:
                    clip = clip.set_duration(duration)
                    clip = clip.set_start(start_time)
                except AttributeError:
                    clip = clip.with_duration(duration)
                    clip = clip.with_start(start_time)

                # Position
                if position == 'top':
                    y_pos = int(video_height * 0.1)
                elif position == 'center':
                    y_pos = 'center'
                else:  # bottom
                    y_pos = int(video_height * 0.75)

                try:
                    clip = clip.set_position(('center', y_pos))
                except AttributeError:
                    clip = clip.with_position(('center', y_pos))

                caption_clips.append(clip)

            except Exception as e:
                print(f"⚠ Error creating caption segment: {e}")

        print(f"✓ Created {len(caption_clips)} estimated caption segments")
        return caption_clips

    @staticmethod
    def create_word_captions(word_timings, video_width, video_height, settings):
        """Create synchronized caption clips for each word"""
        try:
            from moviepy import ImageClip
        except ImportError:
            from moviepy.editor import ImageClip

        caption_clips = []

        # Caption settings from config
        font_size = settings.get('caption_font_size', 70)

        # Parse hex color to RGB tuple
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        text_color = hex_to_rgb(settings.get('caption_text_color', '#FFFFFF'))
        bg_color = hex_to_rgb(settings.get('caption_bg_color', '#000000'))
        bg_opacity = settings.get('caption_bg_opacity', 180)  # 0-255
        bg_enabled = settings.get('caption_bg_enabled', True)  # Enable/disable background
        position = settings.get('caption_position', 'center')  # top, center, bottom
        words_per_caption = settings.get('caption_words_per_line', 3)  # Show 3 words at a time
        gap_between_captions = 0.0  # No gap - perfect sync with voiceover

        # Load font
        try:
            font_file = settings.get('caption_font_style', 'arialbd.ttf')
            font_path = str(Path(r"C:\Windows\Fonts") / font_file)
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

            # Add small gap before next caption (except for first caption)
            if i > 0:
                start_time += gap_between_captions
                end_time += gap_between_captions

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

                # Create image with or without background based on setting
                if bg_enabled:
                    # Create image with SOLID background color
                    img_rgb = Image.new('RGB', (img_width, img_height), bg_color)
                    draw = ImageDraw.Draw(img_rgb)

                    # Draw text centered
                    text_x = (img_width - text_width) // 2
                    text_y = padding
                    draw.text((text_x, text_y), text, font=font, fill=text_color)

                    # Convert to numpy array (writable copy)
                    frame = np.array(img_rgb).copy()
                else:
                    # Create image with TRANSPARENT background
                    img_rgba = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
                    draw = ImageDraw.Draw(img_rgba)

                    # Draw text centered with full opacity
                    text_x = (img_width - text_width) // 2
                    text_y = padding
                    draw.text((text_x, text_y), text, font=font, fill=text_color + (255,))  # Add alpha

                    # Convert to numpy array (writable copy)
                    frame = np.array(img_rgba).copy()

                print(f"  Caption frame shape: {frame.shape}, dtype: {frame.dtype}")
                print(f"  Caption text: '{text}' ({segment['start']:.2f}s - {segment['end']:.2f}s)")

                # Create ImageClip - no mask needed since background is solid
                try:
                    from moviepy import ImageClip
                except ImportError:
                    from moviepy.editor import ImageClip

                clip = ImageClip(frame, is_mask=False)

                duration = segment['end'] - segment['start']
                try:
                    clip = clip.with_duration(duration)
                    clip = clip.with_start(segment['start'])
                except AttributeError:
                    clip = clip.set_duration(duration)
                    clip = clip.set_start(segment['start'])

                # Position based on settings
                if position == 'top':
                    y_pos = int(video_height * 0.1)
                elif position == 'center':
                    y_pos = 'center'
                else:  # bottom
                    y_pos = int(video_height * 0.75)

                try:
                    clip = clip.with_position(('center', y_pos))
                except AttributeError:
                    clip = clip.set_position(('center', y_pos))

                print(f"  Caption positioned at: {clip.pos}, size: {clip.size}")
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


class QuoteImageGenerator:
    """Generate beautiful template-based background images for quotes"""

    TEMPLATES = {
        'gradient_sunset': {
            'colors': [(255, 94, 77), (255, 154, 158), (250, 208, 196)],
            'direction': 'diagonal',
            'text_color': '#FFFFFF',
            'description': 'Warm sunset gradient (motivational)'
        },
        'gradient_ocean': {
            'colors': [(26, 42, 108), (58, 96, 115), (107, 140, 140)],
            'direction': 'vertical',
            'text_color': '#FFFFFF',
            'description': 'Deep ocean gradient (calm, wisdom)'
        },
        'gradient_fire': {
            'colors': [(255, 65, 108), (255, 75, 43), (255, 168, 0)],
            'direction': 'radial',
            'text_color': '#FFFFFF',
            'description': 'Fire energy gradient (high energy)'
        },
        'gradient_purple_dream': {
            'colors': [(67, 67, 255), (156, 81, 182), (255, 109, 255)],
            'direction': 'diagonal',
            'text_color': '#FFFFFF',
            'description': 'Purple dream gradient (creative, spiritual)'
        },
        'gradient_mint_fresh': {
            'colors': [(11, 163, 96), (60, 186, 146), (130, 224, 170)],
            'direction': 'vertical',
            'text_color': '#FFFFFF',
            'description': 'Mint fresh gradient (growth, success)'
        },
        'solid_black': {
            'colors': [(0, 0, 0)],
            'direction': 'solid',
            'text_color': '#FFFFFF',
            'description': 'Minimalist black (bold, modern)'
        },
        'solid_navy': {
            'colors': [(20, 30, 48)],
            'direction': 'solid',
            'text_color': '#FFFFFF',
            'description': 'Deep navy (professional, trust)'
        },
        'gradient_golden_hour': {
            'colors': [(255, 195, 113), (251, 144, 98), (247, 106, 104)],
            'direction': 'horizontal',
            'text_color': '#FFFFFF',
            'description': 'Golden hour (warm, inspiring)'
        },
        'gradient_sky': {
            'colors': [(2, 170, 176), (0, 205, 172), (134, 253, 232)],
            'direction': 'vertical',
            'text_color': '#000000',
            'description': 'Sky blue gradient (hopeful, peaceful)'
        },
        'gradient_dark_purple': {
            'colors': [(35, 7, 77), (79, 46, 109), (117, 86, 142)],
            'direction': 'radial',
            'text_color': '#FFFFFF',
            'description': 'Dark purple (luxury, mystery)'
        }
    }

    @staticmethod
    def create_gradient(width, height, colors, direction='vertical'):
        """Create a gradient background image"""
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)

        if direction == 'solid':
            img.paste(colors[0], [0, 0, width, height])
            return img

        if direction == 'vertical':
            for y in range(height):
                # Calculate color interpolation
                position = y / height
                color = QuoteImageGenerator._interpolate_colors(colors, position)
                draw.line([(0, y), (width, y)], fill=color)

        elif direction == 'horizontal':
            for x in range(width):
                position = x / width
                color = QuoteImageGenerator._interpolate_colors(colors, position)
                draw.line([(x, 0), (x, height)], fill=color)

        elif direction == 'diagonal':
            for y in range(height):
                for x in range(width):
                    position = (x + y) / (width + height)
                    color = QuoteImageGenerator._interpolate_colors(colors, position)
                    draw.point((x, y), fill=color)

        elif direction == 'radial':
            center_x, center_y = width // 2, height // 2
            max_distance = np.sqrt(center_x**2 + center_y**2)

            for y in range(height):
                for x in range(width):
                    distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                    position = distance / max_distance
                    color = QuoteImageGenerator._interpolate_colors(colors, position)
                    draw.point((x, y), fill=color)

        return img

    @staticmethod
    def _interpolate_colors(colors, position):
        """Interpolate between multiple colors based on position (0.0 to 1.0)"""
        if len(colors) == 1:
            return colors[0]

        # Clamp position
        position = max(0.0, min(1.0, position))

        # Calculate which colors to interpolate between
        num_segments = len(colors) - 1
        segment = position * num_segments
        segment_index = int(segment)

        if segment_index >= num_segments:
            return colors[-1]

        # Interpolate between two adjacent colors
        local_position = segment - segment_index
        color1 = colors[segment_index]
        color2 = colors[segment_index + 1]

        r = int(color1[0] + (color2[0] - color1[0]) * local_position)
        g = int(color1[1] + (color2[1] - color1[1]) * local_position)
        b = int(color1[2] + (color2[2] - color1[2]) * local_position)

        return (r, g, b)

    @staticmethod
    def create_quote_image(quote, template_name='gradient_sunset', width=1080, height=1920):
        """Create a beautiful quote image using a template"""
        if template_name not in QuoteImageGenerator.TEMPLATES:
            print(f"⚠ Template '{template_name}' not found, using 'gradient_sunset'")
            template_name = 'gradient_sunset'

        template = QuoteImageGenerator.TEMPLATES[template_name]

        # Create gradient background
        img = QuoteImageGenerator.create_gradient(
            width, height,
            template['colors'],
            template['direction']
        )

        # Add text overlay
        draw = ImageDraw.Draw(img)

        # Detect if quote contains emojis
        emoji_pattern = re.compile(r'[\U0001F300-\U0001F9FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF\U00002600-\U000027BF\U0001F1E0-\U0001F1FF]+')
        has_emojis = bool(emoji_pattern.search(quote))

        # Try to load a font that supports emojis
        font_size = 80
        emoji_font = None
        text_font = None

        try:
            # For Windows: Use Segoe UI Emoji which supports emojis
            if has_emojis:
                emoji_font_path = "C:/Windows/Fonts/seguiemj.ttf"  # Segoe UI Emoji
                if os.path.exists(emoji_font_path):
                    emoji_font = ImageFont.truetype(emoji_font_path, font_size)
                    text_font = ImageFont.truetype(emoji_font_path, font_size)
                    print(f"✓ Using Segoe UI Emoji font for emoji support")
                else:
                    # Fallback: strip emojis if emoji font not available
                    print(f"⚠ Emoji font not found, removing emojis from text")
                    quote = emoji_pattern.sub(' ', quote).strip()
                    quote = ' '.join(quote.split())  # Remove extra spaces
                    has_emojis = False

            # If no emojis or couldn't load emoji font, use Arial Bold
            if not has_emojis:
                font_path = "C:/Windows/Fonts/arialbd.ttf"
                if not os.path.exists(font_path):
                    font_path = "C:/Windows/Fonts/arial.ttf"
                text_font = ImageFont.truetype(font_path, font_size)
        except Exception as e:
            print(f"⚠ Font loading error: {e}, using default font")
            text_font = ImageFont.load_default()

        # Use the loaded font
        font = text_font

        # Word wrap the quote
        words = quote.split()
        lines = []
        current_line = []
        max_width = width - 200  # 100px padding on each side

        for word in words:
            test_line = ' '.join(current_line + [word])
            try:
                bbox = draw.textbbox((0, 0), test_line, font=font)
                text_width = bbox[2] - bbox[0]
            except:
                # Fallback for older Pillow versions
                text_width = len(test_line) * (font_size // 2)

            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        # Calculate total text height
        line_height = font_size + 20
        total_text_height = len(lines) * line_height

        # Center text vertically
        start_y = (height - total_text_height) // 2

        # Parse text color
        text_color = tuple(int(template['text_color'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

        # Draw each line centered
        for i, line in enumerate(lines):
            try:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            except:
                # Fallback for older Pillow versions
                text_width = len(line) * (font_size // 2)
                text_height = font_size

            x = (width - text_width) // 2
            y = start_y + i * line_height

            # Add subtle shadow for better readability
            shadow_offset = 3
            shadow_color = (0, 0, 0, 128) if has_emojis else (0, 0, 0)
            try:
                draw.text((x + shadow_offset, y + shadow_offset), line, font=font, fill=shadow_color)
            except:
                pass  # Skip shadow if it causes issues

            # Draw main text
            draw.text((x, y), line, font=font, fill=text_color)

        return img

    @staticmethod
    def generate_images_from_quotes(quotes_list, output_folder, template_name='auto'):
        """Generate images for a list of quotes"""
        output_folder = Path(output_folder)
        output_folder.mkdir(exist_ok=True, parents=True)

        # Auto-select templates based on quote content
        template_keywords = {
            'gradient_fire': ['energy', 'power', 'passion', 'motivation', 'action', 'hustle'],
            'gradient_ocean': ['calm', 'peace', 'wisdom', 'deep', 'think', 'mind'],
            'gradient_purple_dream': ['dream', 'creative', 'spiritual', 'soul', 'art', 'imagine'],
            'gradient_mint_fresh': ['success', 'growth', 'money', 'wealth', 'win', 'achieve'],
            'gradient_sunset': ['inspire', 'hope', 'life', 'love', 'beautiful', 'happy'],
            'gradient_dark_purple': ['luxury', 'mystery', 'secret', 'truth', 'deep'],
            'solid_black': ['bold', 'strong', 'power', 'minimal', 'modern']
        }

        generated_images = []

        for i, quote in enumerate(quotes_list):
            # Auto-select template based on quote content
            if template_name == 'auto':
                quote_lower = quote.lower()
                selected_template = 'gradient_sunset'  # default

                for tmpl, keywords in template_keywords.items():
                    if any(keyword in quote_lower for keyword in keywords):
                        selected_template = tmpl
                        break
            else:
                selected_template = template_name

            # Generate image
            img = QuoteImageGenerator.create_quote_image(quote, selected_template)

            # Save image
            filename = f"quote_{i+1}_{selected_template}.png"
            filepath = output_folder / filename
            img.save(filepath)

            generated_images.append(filepath)
            print(f"✓ Generated image {i+1}/{len(quotes_list)}: {filename} (template: {selected_template})")

        return generated_images


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

    def read_quotes(self) -> List[dict]:
        """
        Read quotes from file(s) with support for separate subtitle and voiceover text.

        Format options:
        1. Single file (Quotes.txt only): Same text for subtitle and voiceover
        2. Two separate files: Quotes.txt for subtitles, VoiceoverText.txt for voiceover
           - Line 1 in Quotes.txt pairs with line 1 in VoiceoverText.txt
           - Line 2 in Quotes.txt pairs with line 2 in VoiceoverText.txt, etc.

        Returns list of dicts with 'subtitle' and 'voiceover' keys.
        """
        if not self.quotes_file.exists():
            print(f"✗ Quotes file not found: {self.quotes_file}")
            return []

        # Read subtitle text (from Quotes.txt)
        with open(self.quotes_file, 'r', encoding='utf-8') as f:
            subtitle_content = f.read()

        subtitle_lines = []
        if re.match(r'^\s*\d+\.', subtitle_content, re.MULTILINE):
            parts = re.split(r'\n\s*\d+\.\s*', subtitle_content)
            subtitle_lines = [q.strip() for q in parts[1:] if q.strip()]
        elif '\n\n' in subtitle_content:
            subtitle_lines = [q.strip() for q in subtitle_content.split('\n\n') if q.strip()]
        elif '---' in subtitle_content:
            subtitle_lines = [q.strip() for q in subtitle_content.split('---') if q.strip()]
        else:
            subtitle_lines = [line.strip() for line in subtitle_content.split('\n') if line.strip()]

        # Clean subtitle lines
        subtitle_lines = [re.sub(r'^\d+\.\s*', '', line).strip() for line in subtitle_lines if line.strip()]

        # Check for separate voiceover text file
        voiceover_text_file = self.settings.get('voiceover_text_file', '')
        voiceover_lines = []

        if voiceover_text_file and Path(voiceover_text_file).exists():
            print(f"✓ Using separate voiceover text file: {Path(voiceover_text_file).name}")
            with open(voiceover_text_file, 'r', encoding='utf-8') as f:
                voiceover_content = f.read()

            # Parse voiceover file same way as subtitle file
            if re.match(r'^\s*\d+\.', voiceover_content, re.MULTILINE):
                parts = re.split(r'\n\s*\d+\.\s*', voiceover_content)
                voiceover_lines = [q.strip() for q in parts[1:] if q.strip()]
            elif '\n\n' in voiceover_content:
                voiceover_lines = [q.strip() for q in voiceover_content.split('\n\n') if q.strip()]
            elif '---' in voiceover_content:
                voiceover_lines = [q.strip() for q in voiceover_content.split('---') if q.strip()]
            else:
                voiceover_lines = [line.strip() for line in voiceover_content.split('\n') if line.strip()]

            # Clean voiceover lines
            voiceover_lines = [re.sub(r'^\d+\.\s*', '', line).strip() for line in voiceover_lines if line.strip()]

            if len(voiceover_lines) != len(subtitle_lines):
                print(f"⚠ Warning: Subtitle file has {len(subtitle_lines)} lines, Voiceover file has {len(voiceover_lines)} lines")
                print(f"  → Will use minimum count: {min(len(subtitle_lines), len(voiceover_lines))}")
        else:
            print(f"✓ Using Quotes.txt for both subtitle and voiceover")
            voiceover_lines = subtitle_lines  # Use same text for both

        # Pair subtitle and voiceover lines
        processed_quotes = []
        min_count = min(len(subtitle_lines), len(voiceover_lines)) if voiceover_lines else len(subtitle_lines)

        for i in range(min_count):
            subtitle_text = subtitle_lines[i]
            voiceover_text = voiceover_lines[i] if voiceover_lines else subtitle_text

            processed_quotes.append({
                'subtitle': subtitle_text,
                'voiceover': voiceover_text
            })

        print(f"✓ Loaded {len(processed_quotes)} quotes")

        if processed_quotes:
            print(f"\nFirst 3 quotes:")
            for i, quote_data in enumerate(processed_quotes[:3], 1):
                subtitle_preview = quote_data['subtitle'][:80] + "..." if len(quote_data['subtitle']) > 80 else quote_data['subtitle']
                print(f"  {i}. Subtitle: {subtitle_preview}")
                if quote_data['subtitle'] != quote_data['voiceover']:
                    voiceover_preview = quote_data['voiceover'][:80] + "..." if len(quote_data['voiceover']) > 80 else quote_data['voiceover']
                    print(f"     Voiceover: {voiceover_preview}")

        return processed_quotes

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

    def add_quote_to_video(self, video_path: Path, quote: dict, video_index: int = 0) -> Tuple[Path, str]:
        """
        Add quote overlay with advanced effects.

        Args:
            video_path: Path to video file
            quote: Dictionary with 'subtitle' and 'voiceover' keys
                   - subtitle: Text shown in captions/overlay (short)
                   - voiceover: Text spoken in TTS (can include explanations)
            video_index: Index of current video

        Returns:
            Tuple of (output_path, output_filename)
        """
        # Extract subtitle and voiceover text
        # Support both dict format and legacy string format for backward compatibility
        if isinstance(quote, dict):
            subtitle_text = quote['subtitle']
            voiceover_text = quote['voiceover']
        else:
            # Backward compatible: treat as single string
            subtitle_text = quote
            voiceover_text = quote

        print(f"\n{'='*70}")
        print(f"Processing: {video_path.name}")
        print(f"Subtitle: {subtitle_text[:80]}...")
        if subtitle_text != voiceover_text:
            print(f"Voiceover: {voiceover_text[:80]}...")

        # Use subtitle text for hashtags and filename (visual elements)
        hashtags = self.generate_hashtags(subtitle_text)
        print(f"Hashtags: {', '.join(hashtags)}")

        output_filename = self.create_filename(subtitle_text, hashtags)
        print(f"Output: {output_filename}")

        video = VideoFileClip(str(video_path))

        emoji_pattern = re.compile(r'[\U0001F300-\U0001F9FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF\U00002600-\U000027BF\U0001F1E0-\U0001F1FF]+')

        # Parse subtitle text for visual display
        emojis_found = emoji_pattern.findall(subtitle_text)
        text_without_emojis = emoji_pattern.sub(' ', subtitle_text).strip()

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

        # Create static text overlay (quote bubble with emoji and CTA)
        # This is SEPARATE from word-by-word captions and both can be shown together
        img = self.create_text_overlay_image(video.w, video.h, main_text, emoji_line, cta_text)
        img_array = np.array(img).copy()

        txt_clip = set_duration(ImageClip(img_array), video.duration)

        if self.settings.get('text_fade_in', False):
            fade_duration = self.settings.get('text_fade_duration', 0.4)
            if FadeIn:
                txt_clip = txt_clip.with_effects([FadeIn(fade_duration)])
            else:
                try:
                    txt_clip = txt_clip.fadein(fade_duration)
                except AttributeError:
                    pass  # Skip fade if not available

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

        print(f"✓ Static text overlay created at position: {self.settings['position']}")

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
                return np.array(pil_frame).copy()
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

        # Start with video and static text overlay
        layers = [video, txt_clip]
        print(f"DEBUG: txt_clip size={txt_clip.size}, position={txt_clip.pos if hasattr(txt_clip, 'pos') else 'N/A'}, duration={txt_clip.duration}")
        print(f"DEBUG: video size={video.size}, duration={video.duration}")

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

        print(f"DEBUG: Compositing {len(layers)} layers...")
        final_video = CompositeVideoClip(layers)
        print(f"DEBUG: Composite created - size={final_video.size}, duration={final_video.duration:.2f}s")

        # Audio processing
        voiceover_file = None
        word_timings = []

        # Debug: Check caption and TTS settings
        print(f"DEBUG: enable_captions={self.settings.get('enable_captions', False)}, use_tts_voiceover={self.settings.get('use_tts_voiceover', False)}, TTS_AVAILABLE={TTS_AVAILABLE}")

        # Option 1: Generate TTS voiceover from text
        if self.settings.get('use_tts_voiceover', False) and TTS_AVAILABLE:
            tts_folder = self.output_folder / "tts_voiceovers"
            tts_folder.mkdir(exist_ok=True)

            tts_filename = f"tts_{video_index + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
            tts_path = tts_folder / tts_filename

            # Generate TTS from the voiceover text (can include explanations)
            success, word_timings = TTSGenerator.generate_voiceover(voiceover_text, tts_path, self.settings)
            print(f"  → TTS generated from voiceover text ({len(voiceover_text)} chars)")
            if success:
                voiceover_file = tts_path
                print(f"✓ Using TTS voiceover: {tts_filename}")

                # Fix placeholder timing values if needed
                if word_timings and word_timings[0]['offset'] < 100:  # Placeholder detection
                    try:
                        # Get actual audio duration
                        tts_audio = AudioFileClip(str(tts_path))
                        total_duration = tts_audio.duration
                        tts_audio.close()

                        # Weight words by length for more natural timing
                        # Longer words typically take longer to say
                        total_chars = sum(len(w['word']) for w in word_timings)
                        if total_chars == 0:
                            total_chars = 1

                        # Use even distribution - simple and accurate
                        # Most TTS engines speak at consistent pace
                        word_count = len(word_timings)
                        avg_word_duration = total_duration / word_count

                        current_time = 0.0
                        for word_info in word_timings:
                            word_info['offset'] = current_time
                            word_info['duration'] = avg_word_duration
                            current_time += avg_word_duration

                        print(f"✓ Calculated weighted word timing: {len(word_timings)} words, {total_duration:.2f}s total")
                    except Exception as e:
                        print(f"⚠ Could not calculate word timing: {e}")

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

        # Add synchronized captions if enabled
        if self.settings.get('enable_captions', False):
            try:
                caption_clips = []

                # IMPORTANT: Captions display subtitle_text (short), but sync with voiceover audio
                # We need to create timing for subtitle words based on voiceover duration
                if voiceover_file and voiceover_file.exists():
                    print(f"Adding synchronized captions for subtitle text...")
                    try:
                        tts_audio = AudioFileClip(str(voiceover_file))
                        audio_duration = tts_audio.duration
                        tts_audio.close()

                        # Use subtitle_text for captions (short heading)
                        # Timing is estimated based on voiceover duration
                        caption_clips = CaptionRenderer.create_estimated_captions(
                            subtitle_text,
                            audio_duration,
                            video.w,
                            video.h,
                            self.settings
                        )
                        print(f"  → Captions show: {subtitle_text[:60]}...")
                        print(f"  → Synced to {audio_duration:.2f}s voiceover")
                    except Exception as e:
                        print(f"⚠ Could not get TTS audio duration: {e}")
                elif word_timings:
                    # If we have word timings but they're for voiceover_text,
                    # we still need to use subtitle_text for display
                    print(f"⚠ Word timings from voiceover don't match subtitle - using estimated timing")
                    # Try to estimate timing
                    if voiceover_file and voiceover_file.exists():
                        try:
                            tts_audio = AudioFileClip(str(voiceover_file))
                            audio_duration = tts_audio.duration
                            tts_audio.close()

                            caption_clips = CaptionRenderer.create_estimated_captions(
                                subtitle_text,
                                audio_duration,
                                video.w,
                                video.h,
                                self.settings
                            )
                        except Exception as e:
                            print(f"⚠ Could not create captions: {e}")

                if caption_clips:
                    print(f"Compositing {len(caption_clips)} caption clips with video...")
                    # Composite video with captions
                    all_clips = [final_video] + caption_clips
                    final_video = CompositeVideoClip(all_clips)
                    print(f"✓ Added {len(caption_clips)} caption segments")
                else:
                    print("⚠ No caption clips were created")

            except Exception as e:
                print(f"⚠ Caption rendering failed: {e}")
                import traceback
                traceback.print_exc()

        output_path = self.output_folder / output_filename
        counter = 1
        original_output_path = output_path
        while output_path.exists():
            stem = original_output_path.stem
            output_path = self.output_folder / f"{stem}_{counter}.mp4"
            counter += 1

        print(f"Rendering with effects to: {output_path.name}")
        print(f"Video details: size={final_video.size}, duration={final_video.duration:.2f}s, fps={video.fps}")

        try:
            final_video.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                fps=video.fps,
                preset='medium',
                threads=4,
                logger='bar'  # Show progress bar
            )
            print(f"✓ Rendering complete!")
        except Exception as e:
            print(f"✗ Rendering failed: {e}")
            import traceback
            traceback.print_exc()
            raise

        video.close()
        if txt_clip is not None:
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

                # Store subtitle and voiceover separately in log
                if isinstance(quote, dict):
                    quote_log = {
                        'subtitle': quote['subtitle'],
                        'voiceover': quote['voiceover']
                    }
                else:
                    quote_log = quote

                result = {
                    'index': i,
                    'original_video': video_path.name,
                    'quote': quote_log,
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
