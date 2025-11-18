"""
Video Automation Studio - Professional Dashboard with Live Preview
Single dashboard with popup settings for each feature
"""

import tkinter as tk
from tkinter import ttk, colorchooser, messagebox, filedialog, scrolledtext, font
import json
from pathlib import Path
import threading
import sys
import os
from PIL import Image, ImageDraw, ImageFont, ImageTk
import numpy as np
import queue
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

# Import configuration
try:
    from config import config
except ImportError:
    config = None
    print("⚠ Could not import config - using default paths")

# Import the video automation processor
try:
    from youtube_video_automation_enhanced import VideoQuoteAutomation, TTSGenerator
except ImportError:
    VideoQuoteAutomation = None
    TTSGenerator = None
    print("⚠ Could not import VideoQuoteAutomation - processing will not be available")


class ModernStyles:
    """Professional color scheme"""
    BG_DARK = '#0f172a'
    BG_CARD = '#1e293b'
    BG_CARD_HOVER = '#334155'
    ACCENT_BLUE = '#3b82f6'
    ACCENT_GREEN = '#10b981'
    ACCENT_PURPLE = '#8b5cf6'
    ACCENT_ORANGE = '#f59e0b'
    ACCENT_RED = '#ef4444'
    TEXT_WHITE = '#f8fafc'
    TEXT_GRAY = '#cbd5e1'
    BORDER = '#475569'


def get_windows_fonts():
    """Scan Windows fonts folder and return available font families"""
    # Use config if available, otherwise fallback to Windows default
    if config:
        fonts_folder = config.SYSTEM_FONTS_FOLDER
    else:
        fonts_folder = Path(r"C:\Windows\Fonts")

    font_files = {}

    if not fonts_folder.exists():
        return ['Arial', 'Arial Bold', 'Impact', 'Verdana']

    # Scan for TTF and OTF fonts
    for font_file in fonts_folder.glob("*.ttf"):
        try:
            # Try to load font to get name
            font_name = font_file.stem
            # Clean up common naming patterns
            font_name = font_name.replace('bd', ' Bold').replace('bi', ' Bold Italic')
            font_name = font_name.replace('i', ' Italic').replace('z', '')
            font_files[font_name] = str(font_file)
        except:
            pass

    # Add common system fonts with their actual file paths
    common_fonts = {
        'Arial': 'arial.ttf',
        'Arial Bold': 'arialbd.ttf',
        'Arial Italic': 'ariali.ttf',
        'Arial Bold Italic': 'arialbi.ttf',
        'Impact': 'impact.ttf',
        'Times New Roman': 'times.ttf',
        'Times New Roman Bold': 'timesbd.ttf',
        'Verdana': 'verdana.ttf',
        'Verdana Bold': 'verdanab.ttf',
        'Calibri': 'calibri.ttf',
        'Calibri Bold': 'calibrib.ttf',
        'Comic Sans MS': 'comic.ttf',
        'Comic Sans MS Bold': 'comicbd.ttf',
        'Georgia': 'georgia.ttf',
        'Georgia Bold': 'georgiab.ttf',
        'Courier New': 'cour.ttf',
        'Courier New Bold': 'courbd.ttf',
        'Tahoma': 'tahoma.ttf',
        'Tahoma Bold': 'tahomabd.ttf',
        'Trebuchet MS': 'trebuc.ttf',
        'Trebuchet MS Bold': 'trebucbd.ttf'
    }

    result = {}
    for name, filename in common_fonts.items():
        full_path = fonts_folder / filename
        if full_path.exists():
            result[name] = str(full_path)

    # Combine and sort
    result.update(font_files)
    return sorted(result.keys())


def get_font_path(font_name):
    """Get full path for a font name"""
    # Use config if available, otherwise fallback to Windows default
    if config:
        fonts_folder = config.SYSTEM_FONTS_FOLDER
    else:
        fonts_folder = Path(r"C:\Windows\Fonts")

    font_map = {
        'Arial': 'arial.ttf',
        'Arial Bold': 'arialbd.ttf',
        'Arial Italic': 'ariali.ttf',
        'Arial Bold Italic': 'arialbi.ttf',
        'Impact': 'impact.ttf',
        'Times New Roman': 'times.ttf',
        'Times New Roman Bold': 'timesbd.ttf',
        'Verdana': 'verdana.ttf',
        'Verdana Bold': 'verdanab.ttf',
        'Calibri': 'calibri.ttf',
        'Calibri Bold': 'calibrib.ttf',
        'Comic Sans MS': 'comic.ttf',
        'Comic Sans MS Bold': 'comicbd.ttf',
        'Georgia': 'georgia.ttf',
        'Georgia Bold': 'georgiab.ttf',
        'Courier New': 'cour.ttf',
        'Courier New Bold': 'courbd.ttf',
        'Tahoma': 'tahoma.ttf',
        'Tahoma Bold': 'tahomabd.ttf',
        'Trebuchet MS': 'trebuc.ttf',
        'Trebuchet MS Bold': 'trebucbd.ttf'
    }

    if font_name in font_map:
        return str(fonts_folder / font_map[font_name])

    # Try to find by scanning
    for font_file in fonts_folder.glob("*.ttf"):
        if font_name.lower() in font_file.stem.lower():
            return str(font_file)

    return str(fonts_folder / 'arial.ttf')


class TextSettingsPopup:
    """Popup window for text settings with live preview"""

    def __init__(self, parent, settings, on_save):
        self.settings = settings.copy()
        self.on_save = on_save

        self.window = tk.Toplevel(parent)
        self.window.title("📝 Text & Font Settings")
        self.window.geometry("850x680")
        self.window.configure(bg=ModernStyles.BG_DARK)
        # Removed grab_set to allow minimize

        self.setup_ui()
        self.update_preview()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.window, bg=ModernStyles.ACCENT_BLUE, height=60)
        header.pack(fill='x')
        header.pack_propagate(False)

        tk.Label(header, text="📝 Text & Font Configuration",
                bg=ModernStyles.ACCENT_BLUE, fg='white',
                font=('Segoe UI', 16, 'bold')).pack(side='left', padx=20, pady=15)

        # Main container
        main = tk.Frame(self.window, bg=ModernStyles.BG_DARK)
        main.pack(fill='both', expand=True, padx=20, pady=20)

        # Left: Settings
        left = tk.Frame(main, bg=ModernStyles.BG_CARD, width=450)
        left.pack(side='left', fill='both', expand=True, padx=(0,10))

        # Scrollable settings
        canvas = tk.Canvas(left, bg=ModernStyles.BG_CARD, highlightthickness=0)
        scrollbar = ttk.Scrollbar(left, orient="vertical", command=canvas.yview)
        settings_frame = tk.Frame(canvas, bg=ModernStyles.BG_CARD)

        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=settings_frame, anchor="nw")
        settings_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Preset Management Section
        preset_header = tk.Frame(settings_frame, bg=ModernStyles.ACCENT_PURPLE, height=3)
        preset_header.pack(fill='x', pady=(15,0))
        tk.Label(preset_header, text="💾 Caption Presets", bg=ModernStyles.ACCENT_PURPLE, fg='white',
                font=('Segoe UI', 11, 'bold'), pady=6).pack(padx=15)

        preset_frame = tk.Frame(settings_frame, bg=ModernStyles.BG_DARK)
        preset_frame.pack(fill='x', padx=15, pady=10)

        # Preset dropdown
        tk.Label(preset_frame, text="Select Preset:", bg=ModernStyles.BG_DARK,
                fg=ModernStyles.TEXT_GRAY, font=('Segoe UI', 9)).pack(anchor='w', pady=(0,5))

        self.preset_var = tk.StringVar(value="Current Settings")
        self.preset_combo = ttk.Combobox(preset_frame, textvariable=self.preset_var,
                                        state='readonly', font=('Segoe UI', 9), width=35)
        self.preset_combo.pack(fill='x', pady=(0,10))
        self.preset_combo.bind('<<ComboboxSelected>>', self.load_preset)

        # Preset buttons
        preset_btns = tk.Frame(preset_frame, bg=ModernStyles.BG_DARK)
        preset_btns.pack(fill='x')

        tk.Button(preset_btns, text="💾 Save as Preset", command=self.save_preset,
                 bg=ModernStyles.ACCENT_GREEN, fg='white', font=('Segoe UI', 9),
                 relief='flat', padx=10, pady=6, cursor='hand2').pack(side='left', padx=(0,5))

        tk.Button(preset_btns, text="🗑️ Delete", command=self.delete_preset,
                 bg=ModernStyles.ACCENT_RED, fg='white', font=('Segoe UI', 9),
                 relief='flat', padx=10, pady=6, cursor='hand2').pack(side='left')

        # Load presets
        self.refresh_preset_list()

        # Divider
        tk.Frame(settings_frame, bg=ModernStyles.BORDER, height=1).pack(fill='x', pady=15)

        # Font settings
        self.create_label(settings_frame, "Font Family", pady=(15,5))
        self.font_var = tk.StringVar(value=self.settings.get('font_style', 'Arial Bold'))
        font_combo = ttk.Combobox(settings_frame, textvariable=self.font_var, width=40, height=15)
        font_combo['values'] = get_windows_fonts()
        font_combo.pack(padx=15, pady=(0,10))
        font_combo.bind('<<ComboboxSelected>>', lambda e: self.update_preview())

        # Font size
        self.create_label(settings_frame, "Font Size")
        self.font_size_var = tk.IntVar(value=self.settings.get('font_size', 45))
        size_frame = tk.Frame(settings_frame, bg=ModernStyles.BG_CARD)
        size_frame.pack(fill='x', padx=15, pady=(0,10))

        tk.Scale(size_frame, from_=20, to=100, orient='horizontal',
                variable=self.font_size_var, bg=ModernStyles.BG_CARD,
                fg=ModernStyles.TEXT_WHITE, highlightthickness=0,
                command=lambda v: self.update_preview()).pack(side='left', fill='x', expand=True)

        tk.Label(size_frame, textvariable=self.font_size_var, bg=ModernStyles.BG_CARD,
                fg=ModernStyles.TEXT_WHITE, width=3).pack(side='left', padx=5)

        # Colors
        self.create_label(settings_frame, "Text Color")
        self.text_color = self.settings.get('text_color', '#000000')
        tk.Button(settings_frame, text=f"  {self.text_color}  ",
                 bg=self.text_color, fg='white', width=20,
                 command=lambda: self.pick_color('text_color')).pack(padx=15, pady=(0,10))

        self.create_label(settings_frame, "Background Color")
        self.bg_color = self.settings.get('bg_color', '#ffffff')
        tk.Button(settings_frame, text=f"  {self.bg_color}  ",
                 bg=self.bg_color, width=20,
                 command=lambda: self.pick_color('bg_color')).pack(padx=15, pady=(0,10))

        # Background opacity
        self.create_label(settings_frame, "Background Opacity (%)")
        self.bg_opacity_var = tk.IntVar(value=self.settings.get('bg_opacity', 90))
        opacity_frame = tk.Frame(settings_frame, bg=ModernStyles.BG_CARD)
        opacity_frame.pack(fill='x', padx=15, pady=(0,10))

        tk.Scale(opacity_frame, from_=0, to=100, orient='horizontal',
                variable=self.bg_opacity_var, bg=ModernStyles.BG_CARD,
                fg=ModernStyles.TEXT_WHITE, highlightthickness=0,
                command=lambda v: self.update_preview()).pack(side='left', fill='x', expand=True)

        tk.Label(opacity_frame, textvariable=self.bg_opacity_var, bg=ModernStyles.BG_CARD,
                fg=ModernStyles.TEXT_WHITE, width=3).pack(side='left', padx=5)

        # Position
        self.create_label(settings_frame, "Text Position")
        self.position_var = tk.StringVar(value=self.settings.get('position', 'top'))
        pos_frame = tk.Frame(settings_frame, bg=ModernStyles.BG_CARD)
        pos_frame.pack(padx=15, pady=(0,15))

        for pos in ['top', 'center', 'bottom']:
            tk.Radiobutton(pos_frame, text=pos.capitalize(), variable=self.position_var,
                          value=pos, bg=ModernStyles.BG_CARD, fg=ModernStyles.TEXT_WHITE,
                          selectcolor=ModernStyles.BG_DARK, activebackground=ModernStyles.BG_CARD,
                          command=self.update_preview).pack(side='left', padx=10)

        # Right: Preview
        right = tk.Frame(main, bg=ModernStyles.BG_CARD, width=400)
        right.pack(side='right', fill='both')

        tk.Label(right, text="🎬 Live Preview (1080x1920)", bg=ModernStyles.BG_CARD,
                fg=ModernStyles.TEXT_WHITE, font=('Segoe UI', 12, 'bold')).pack(pady=15)

        # Preview scaled down to fit (maintaining 9:16 aspect ratio)
        preview_frame = tk.Frame(right, bg='#000000')
        preview_frame.pack(padx=15, pady=(0,15))

        self.preview_label = tk.Label(preview_frame, bg='#000000')
        self.preview_label.pack()

        # Bottom buttons
        btn_frame = tk.Frame(self.window, bg=ModernStyles.BG_DARK, height=70)
        btn_frame.pack(fill='x', side='bottom')
        btn_frame.pack_propagate(False)

        buttons = tk.Frame(btn_frame, bg=ModernStyles.BG_DARK)
        buttons.pack(expand=True)

        tk.Button(buttons, text="💾  Save Changes", command=self.save_settings,
                 bg=ModernStyles.ACCENT_GREEN, fg='white', font=('Segoe UI', 11, 'bold'),
                 relief='flat', padx=30, pady=12, cursor='hand2').pack(side='left', padx=5)

        tk.Button(buttons, text="✕  Cancel", command=self.window.destroy,
                 bg=ModernStyles.ACCENT_RED, fg='white', font=('Segoe UI', 11, 'bold'),
                 relief='flat', padx=30, pady=12, cursor='hand2').pack(side='left', padx=5)

    def create_label(self, parent, text, pady=(10,5)):
        tk.Label(parent, text=text, bg=ModernStyles.BG_CARD,
                fg=ModernStyles.TEXT_GRAY, font=('Segoe UI', 10)).pack(anchor='w', padx=15, pady=pady)

    def pick_color(self, color_type):
        color = colorchooser.askcolor(title=f"Choose {color_type}")[1]
        if color:
            if color_type == 'text_color':
                self.text_color = color
            else:
                self.bg_color = color
            self.update_preview()

    def update_preview(self):
        """Generate live preview of text overlay at 1080x1920"""
        try:
            # Create preview image at full resolution (9:16 aspect ratio)
            width, height = 1080, 1920
            img = Image.new('RGB', (width, height), '#000000')
            draw = ImageDraw.Draw(img, 'RGBA')

            # Sample text
            text = "Sample Quote\nWith Multiple Lines"

            # Get font - use selected font from dropdown
            font_size = self.font_size_var.get()
            selected_font = self.font_var.get()

            try:
                # Get the actual font file path
                font_path = get_font_path(selected_font)
                font_obj = ImageFont.truetype(font_path, font_size)
            except Exception as e:
                print(f"Font loading error: {e}, using Arial as fallback")
                try:
                    font_obj = ImageFont.truetype(get_font_path("Arial"), font_size)
                except:
                    font_obj = ImageFont.load_default()

            # Calculate text size
            bbox = draw.multiline_textbbox((0, 0), text, font=font_obj, align='center')
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # Background
            padding = 30
            bg_width = text_width + padding * 2
            bg_height = text_height + padding * 2

            # Position
            if self.position_var.get() == 'top':
                bg_y = 50
            elif self.position_var.get() == 'center':
                bg_y = (height - bg_height) // 2
            else:
                bg_y = height - bg_height - 50

            bg_x = (width - bg_width) // 2

            # Draw background with opacity
            bg_rgb = self.hex_to_rgb(self.bg_color)
            opacity = int(255 * (self.bg_opacity_var.get() / 100))
            draw.rounded_rectangle(
                [(bg_x, bg_y), (bg_x + bg_width, bg_y + bg_height)],
                radius=15,
                fill=bg_rgb + (opacity,)
            )

            # Draw text
            text_x = width // 2
            text_y = bg_y + padding
            draw.multiline_text(
                (text_x, text_y),
                text,
                font=font_obj,
                fill=self.text_color,
                align='center',
                anchor='ma'
            )

            # Scale down for display (maintain aspect ratio)
            # Target display height: 540px (half of 1080 to fit in GUI)
            display_width = 270  # 540 * 9/16
            display_height = 480  # 9:16 ratio
            img_display = img.resize((display_width, display_height), Image.Resampling.LANCZOS)

            # Convert to PhotoImage
            img_tk = ImageTk.PhotoImage(img_display)
            self.preview_label.config(image=img_tk)
            self.preview_label.image = img_tk

        except Exception as e:
            print(f"Preview error: {e}")

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def get_current_text_settings(self):
        """Get all current text settings as a dictionary"""
        return {
            'font_style': self.font_var.get(),
            'font_size': self.font_size_var.get(),
            'text_color': self.text_color,
            'bg_color': self.bg_color,
            'bg_opacity': self.bg_opacity_var.get(),
            'position': self.position_var.get()
        }

    def apply_text_settings(self, settings):
        """Apply text settings from a preset"""
        self.font_var.set(settings.get('font_style', 'Arial Bold'))
        self.font_size_var.set(settings.get('font_size', 45))
        self.text_color = settings.get('text_color', '#000000')
        self.bg_color = settings.get('bg_color', '#ffffff')
        self.bg_opacity_var.set(settings.get('bg_opacity', 90))
        self.position_var.set(settings.get('position', 'top'))
        self.update_preview()

    def refresh_preset_list(self):
        """Load and refresh the preset dropdown"""
        preset_file = Path('caption_presets.json')
        presets = {}

        if preset_file.exists():
            try:
                with open(preset_file, 'r') as f:
                    presets = json.load(f)
            except:
                presets = {}

        preset_names = ['Current Settings'] + list(presets.keys())
        self.preset_combo['values'] = preset_names
        self.preset_var.set('Current Settings')

    def save_preset(self):
        """Save current settings as a preset"""
        from tkinter import simpledialog

        preset_name = simpledialog.askstring("Save Preset", "Enter preset name:",
                                            parent=self.window)

        if not preset_name:
            return

        # Load existing presets
        preset_file = Path('caption_presets.json')
        presets = {}

        if preset_file.exists():
            try:
                with open(preset_file, 'r') as f:
                    presets = json.load(f)
            except:
                presets = {}

        # Save current settings
        presets[preset_name] = self.get_current_text_settings()

        # Write to file
        with open(preset_file, 'w') as f:
            json.dump(presets, f, indent=2)

        self.refresh_preset_list()
        self.preset_var.set(preset_name)
        messagebox.showinfo("Success", f"Preset '{preset_name}' saved successfully!")

    def load_preset(self, event=None):
        """Load selected preset"""
        preset_name = self.preset_var.get()

        if preset_name == 'Current Settings':
            return

        preset_file = Path('caption_presets.json')

        if not preset_file.exists():
            messagebox.showerror("Error", "No presets found!")
            return

        try:
            with open(preset_file, 'r') as f:
                presets = json.load(f)

            if preset_name in presets:
                self.apply_text_settings(presets[preset_name])
                messagebox.showinfo("Success", f"Preset '{preset_name}' loaded!")
            else:
                messagebox.showerror("Error", f"Preset '{preset_name}' not found!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load preset: {e}")

    def delete_preset(self):
        """Delete selected preset"""
        preset_name = self.preset_var.get()

        if preset_name == 'Current Settings':
            messagebox.showwarning("Warning", "Cannot delete 'Current Settings'!")
            return

        preset_file = Path('caption_presets.json')

        if not preset_file.exists():
            messagebox.showerror("Error", "No presets found!")
            return

        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete",
                                   f"Are you sure you want to delete preset '{preset_name}'?",
                                   parent=self.window):
            return

        try:
            with open(preset_file, 'r') as f:
                presets = json.load(f)

            if preset_name in presets:
                del presets[preset_name]

                with open(preset_file, 'w') as f:
                    json.dump(presets, f, indent=2)

                self.refresh_preset_list()
                messagebox.showinfo("Success", f"Preset '{preset_name}' deleted!")
            else:
                messagebox.showerror("Error", f"Preset '{preset_name}' not found!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete preset: {e}")

    def save_settings(self):
        self.settings['font_style'] = self.font_var.get()
        self.settings['font_size'] = self.font_size_var.get()
        self.settings['text_color'] = self.text_color
        self.settings['bg_color'] = self.bg_color
        self.settings['bg_opacity'] = self.bg_opacity_var.get()
        self.settings['position'] = self.position_var.get()

        self.on_save(self.settings)
        self.window.destroy()


class EffectsSettingsPopup:
    """Popup for visual effects settings"""

    def __init__(self, parent, settings, on_save):
        self.settings = settings.copy()
        self.on_save = on_save

        self.window = tk.Toplevel(parent)
        self.window.title("✨ Visual Effects")
        self.window.geometry("680x630")
        self.window.configure(bg=ModernStyles.BG_DARK)
        # Removed grab_set to allow minimize

        self.setup_ui()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.window, bg=ModernStyles.ACCENT_PURPLE, height=60)
        header.pack(fill='x')
        header.pack_propagate(False)

        tk.Label(header, text="✨ Visual Effects Configuration",
                bg=ModernStyles.ACCENT_PURPLE, fg='white',
                font=('Segoe UI', 16, 'bold')).pack(side='left', padx=20, pady=15)

        # Bottom buttons - PACK FIRST before scrollable content
        btn_frame = tk.Frame(self.window, bg=ModernStyles.BG_DARK, height=70)
        btn_frame.pack(fill='x', side='bottom')
        btn_frame.pack_propagate(False)

        buttons = tk.Frame(btn_frame, bg=ModernStyles.BG_DARK)
        buttons.pack(expand=True)

        tk.Button(buttons, text="💾  Save Changes", command=self.save_settings,
                 bg=ModernStyles.ACCENT_GREEN, fg='white', font=('Segoe UI', 11, 'bold'),
                 relief='flat', padx=30, pady=12, cursor='hand2').pack(side='left', padx=5)

        tk.Button(buttons, text="✕  Cancel", command=self.window.destroy,
                 bg=ModernStyles.ACCENT_RED, fg='white', font=('Segoe UI', 11, 'bold'),
                 relief='flat', padx=30, pady=12, cursor='hand2').pack(side='left', padx=5)

        # Scrollable content - pack AFTER buttons
        canvas = tk.Canvas(self.window, bg=ModernStyles.BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        content = tk.Frame(canvas, bg=ModernStyles.BG_DARK)

        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        canvas.create_window((0, 0), window=content, anchor="nw")
        content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Text animations
        self.create_section(content, "Text Animations", ModernStyles.ACCENT_PURPLE)

        self.fade_var = tk.BooleanVar(value=self.settings.get('text_fade_in', True))
        self.create_checkbox(content, "Fade In Animation", self.fade_var)

        self.glow_var = tk.BooleanVar(value=self.settings.get('text_glow', True))
        self.create_checkbox(content, "Text Glow Effect", self.glow_var)

        self.shadow_var = tk.BooleanVar(value=self.settings.get('drop_shadow', True))
        self.create_checkbox(content, "Drop Shadow", self.shadow_var)

        # Video effects
        self.create_section(content, "Video Effects", ModernStyles.ACCENT_BLUE)

        self.vignette_var = tk.BooleanVar(value=self.settings.get('vignette', True))
        self.create_checkbox(content, "Vignette (darkened edges)", self.vignette_var)

        self.dim_var = tk.BooleanVar(value=self.settings.get('background_dim', True))
        self.create_checkbox(content, "Background Dimming", self.dim_var)

        self.zoom_var = tk.BooleanVar(value=self.settings.get('video_zoom', True))
        self.create_checkbox(content, "Slow Zoom Effect", self.zoom_var)

        # Color grading
        self.create_section(content, "Color Grading", ModernStyles.ACCENT_ORANGE)

        self.grade_var = tk.StringVar(value=self.settings.get('color_grade', 'warm'))
        grade_frame = tk.Frame(content, bg=ModernStyles.BG_CARD)
        grade_frame.pack(fill='x', padx=20, pady=10)

        for text, value in [('None', 'none'), ('Warm', 'warm'), ('Cold', 'cold'), ('Cinematic', 'cinematic')]:
            tk.Radiobutton(grade_frame, text=text, variable=self.grade_var, value=value,
                          bg=ModernStyles.BG_CARD, fg=ModernStyles.TEXT_WHITE,
                          selectcolor=ModernStyles.BG_DARK, activebackground=ModernStyles.BG_CARD).pack(side='left', padx=15)

        # Particle Effects (NEW!)
        self.create_section(content, "✨ Particle Effects (Glitter, Stars, etc.)", ModernStyles.ACCENT_GREEN)

        self.glitter_var = tk.BooleanVar(value=self.settings.get('add_glitter', False))
        self.create_checkbox(content, "✨ Glitter / Sparkles (Twinkling)", self.glitter_var)

        # Glitter intensity slider
        glitter_label = tk.Label(content, text="Glitter Intensity:", bg=ModernStyles.BG_DARK,
                                fg=ModernStyles.TEXT_GRAY, font=('Segoe UI', 9))
        glitter_label.pack(anchor='w', padx=20, pady=(10,2))

        glitter_intensity_frame = tk.Frame(content, bg=ModernStyles.BG_CARD)
        glitter_intensity_frame.pack(fill='x', padx=20, pady=5)

        self.glitter_intensity_var = tk.DoubleVar(value=self.settings.get('glitter_intensity', 0.5))
        tk.Scale(glitter_intensity_frame, from_=0.1, to=1.0, resolution=0.1, orient='horizontal',
                variable=self.glitter_intensity_var, bg=ModernStyles.BG_CARD,
                fg=ModernStyles.TEXT_WHITE, highlightthickness=0,
                font=('Segoe UI', 9)).pack(side='left', fill='x', expand=True, padx=15, pady=10)

        tk.Label(glitter_intensity_frame, textvariable=self.glitter_intensity_var, bg=ModernStyles.BG_CARD,
                fg=ModernStyles.TEXT_WHITE, width=4, font=('Segoe UI', 10)).pack(side='left', padx=10)

        self.stars_var = tk.BooleanVar(value=self.settings.get('add_stars', False))
        self.create_checkbox(content, "⭐ Falling Stars (Animated)", self.stars_var)

        self.hearts_var = tk.BooleanVar(value=self.settings.get('add_hearts', False))
        self.create_checkbox(content, "❤️ Falling Hearts (Romantic)", self.hearts_var)

        self.confetti_var = tk.BooleanVar(value=self.settings.get('add_confetti', False))
        self.create_checkbox(content, "🎉 Confetti (Celebration)", self.confetti_var)

        info_particles = tk.Frame(content, bg=ModernStyles.BG_CARD)
        info_particles.pack(fill='x', padx=20, pady=(0,10))
        tk.Label(info_particles, text="ℹ️ Particle effects overlay on top of video. Great for celebrations!",
                bg=ModernStyles.BG_CARD, fg=ModernStyles.TEXT_GRAY,
                font=('Segoe UI', 9), justify='left').pack(anchor='w', padx=15, pady=10)

    def create_section(self, parent, title, color):
        header = tk.Frame(parent, bg=color, height=3)
        header.pack(fill='x', pady=(20,0))

        tk.Label(header, text=title, bg=color, fg='white',
                font=('Segoe UI', 12, 'bold'), pady=8).pack(padx=15)

    def create_checkbox(self, parent, text, variable):
        frame = tk.Frame(parent, bg=ModernStyles.BG_CARD)
        frame.pack(fill='x', padx=20, pady=5)

        tk.Checkbutton(frame, text=text, variable=variable,
                      bg=ModernStyles.BG_CARD, fg=ModernStyles.TEXT_WHITE,
                      selectcolor=ModernStyles.BG_DARK, activebackground=ModernStyles.BG_CARD,
                      font=('Segoe UI', 10)).pack(anchor='w', padx=15, pady=10)

    def save_settings(self):
        self.settings['text_fade_in'] = self.fade_var.get()
        self.settings['text_glow'] = self.glow_var.get()
        self.settings['drop_shadow'] = self.shadow_var.get()
        self.settings['vignette'] = self.vignette_var.get()
        self.settings['background_dim'] = self.dim_var.get()
        self.settings['video_zoom'] = self.zoom_var.get()
        self.settings['color_grade'] = self.grade_var.get()

        # Particle effects
        self.settings['add_glitter'] = self.glitter_var.get()
        self.settings['glitter_intensity'] = self.glitter_intensity_var.get()
        self.settings['add_stars'] = self.stars_var.get()
        self.settings['add_hearts'] = self.hearts_var.get()
        self.settings['add_confetti'] = self.confetti_var.get()

        self.on_save(self.settings)
        self.window.destroy()


class AudioSettingsPopup:
    """Popup for audio settings"""

    def __init__(self, parent, settings, on_save):
        self.settings = settings.copy()
        self.on_save = on_save

        self.window = tk.Toplevel(parent)
        self.window.title("🔊 Audio Settings")
        self.window.geometry("720x950")  # Increased height for caption controls
        self.window.configure(bg=ModernStyles.BG_DARK)
        # Removed grab_set to allow minimize

        self.setup_ui()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.window, bg=ModernStyles.ACCENT_GREEN, height=60)
        header.pack(fill='x')
        header.pack_propagate(False)

        tk.Label(header, text="🔊 Audio Configuration",
                bg=ModernStyles.ACCENT_GREEN, fg='white',
                font=('Segoe UI', 16, 'bold')).pack(side='left', padx=20, pady=15)

        # Bottom buttons - PACK FIRST before scrollable content
        btn_frame = tk.Frame(self.window, bg=ModernStyles.BG_DARK, height=70)
        btn_frame.pack(fill='x', side='bottom')
        btn_frame.pack_propagate(False)

        buttons = tk.Frame(btn_frame, bg=ModernStyles.BG_DARK)
        buttons.pack(expand=True)

        tk.Button(buttons, text="💾  Save Changes", command=self.save_settings,
                 bg=ModernStyles.ACCENT_GREEN, fg='white', font=('Segoe UI', 11, 'bold'),
                 relief='flat', padx=30, pady=12, cursor='hand2').pack(side='left', padx=5)

        tk.Button(buttons, text="✕  Cancel", command=self.window.destroy,
                 bg=ModernStyles.ACCENT_RED, fg='white', font=('Segoe UI', 11, 'bold'),
                 relief='flat', padx=30, pady=12, cursor='hand2').pack(side='left', padx=5)

        # Scrollable content - pack AFTER buttons
        canvas = tk.Canvas(self.window, bg=ModernStyles.BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        content = tk.Frame(canvas, bg=ModernStyles.BG_DARK)

        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        canvas.create_window((0, 0), window=content, anchor="nw")
        content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Original Audio
        self.create_section(content, "Original Audio", ModernStyles.ACCENT_BLUE)
        self.mute_var = tk.BooleanVar(value=self.settings.get('mute_original_audio', False))
        self.create_checkbox(content, "Mute Original Video Audio", self.mute_var)

        # Original audio volume
        self.create_label(content, "Original Audio Volume (%):")
        volume_frame = tk.Frame(content, bg=ModernStyles.BG_CARD)
        volume_frame.pack(fill='x', padx=20, pady=5)

        self.original_volume_var = tk.IntVar(value=self.settings.get('original_audio_volume', 100))
        tk.Scale(volume_frame, from_=0, to=200, orient='horizontal',
                variable=self.original_volume_var, bg=ModernStyles.BG_CARD,
                fg=ModernStyles.TEXT_WHITE, highlightthickness=0,
                font=('Segoe UI', 9)).pack(side='left', fill='x', expand=True, padx=15, pady=10)

        tk.Label(volume_frame, textvariable=self.original_volume_var, bg=ModernStyles.BG_CARD,
                fg=ModernStyles.TEXT_WHITE, width=4, font=('Segoe UI', 10)).pack(side='left', padx=10)

        # BGM
        self.create_section(content, "Background Music", ModernStyles.ACCENT_PURPLE)
        self.bgm_var = tk.BooleanVar(value=self.settings.get('add_custom_bgm', False))
        self.create_checkbox(content, "Enable Background Music", self.bgm_var)

        self.create_label(content, "BGM File/Folder:")
        self.bgm_path_var = tk.StringVar(value=self.settings.get('bgm_file', ''))
        path_frame = tk.Frame(content, bg=ModernStyles.BG_CARD)
        path_frame.pack(fill='x', padx=20, pady=5)

        tk.Entry(path_frame, textvariable=self.bgm_path_var, width=40,
                bg='#0f172a', fg=ModernStyles.TEXT_WHITE, relief='flat').pack(side='left', fill='x', expand=True, padx=10, pady=10)

        tk.Button(path_frame, text="📄 File", command=self.browse_bgm_file,
                 bg=ModernStyles.ACCENT_BLUE, fg='white', relief='flat', cursor='hand2', padx=10).pack(side='left', padx=2)
        tk.Button(path_frame, text="📁 Folder", command=self.browse_bgm_folder,
                 bg=ModernStyles.ACCENT_PURPLE, fg='white', relief='flat', cursor='hand2', padx=10).pack(side='left', padx=2)

        # Voiceover
        self.create_section(content, "Voiceover", ModernStyles.ACCENT_ORANGE)
        self.vo_var = tk.BooleanVar(value=self.settings.get('add_voiceover', False))
        self.create_checkbox(content, "Enable Voiceover", self.vo_var)

        self.create_label(content, "Voiceover Folder (Files: 1.mp3, 2.mp3...):")
        self.vo_path_var = tk.StringVar(value=self.settings.get('voiceover_folder', ''))
        vo_frame = tk.Frame(content, bg=ModernStyles.BG_CARD)
        vo_frame.pack(fill='x', padx=20, pady=5)

        tk.Entry(vo_frame, textvariable=self.vo_path_var, width=40,
                bg='#0f172a', fg=ModernStyles.TEXT_WHITE, relief='flat').pack(side='left', fill='x', expand=True, padx=10, pady=10)

        tk.Button(vo_frame, text="📁 Browse", command=self.browse_voiceover,
                 bg=ModernStyles.ACCENT_GREEN, fg='white', relief='flat', cursor='hand2', padx=15).pack(side='left', padx=5)

        # TTS Voiceover
        self.create_section(content, "Text-to-Speech Voiceover (Auto-Generate)", ModernStyles.ACCENT_RED)

        self.tts_var = tk.BooleanVar(value=self.settings.get('use_tts_voiceover', False))
        self.create_checkbox(content, "Generate Voiceover from Text (TTS)", self.tts_var)

        info_frame = tk.Frame(content, bg=ModernStyles.BG_CARD)
        info_frame.pack(fill='x', padx=20, pady=(0,10))
        tk.Label(info_frame, text="ℹ️ Automatically converts quote text to speech using natural AI voices. \nRequires edge-tts library (pip install edge-tts)",
                bg=ModernStyles.BG_CARD, fg=ModernStyles.TEXT_GRAY,
                font=('Segoe UI', 9), justify='left').pack(anchor='w', padx=15, pady=10)

        # TTS Voice selection
        self.create_label(content, "TTS Voice:")
        voice_frame = tk.Frame(content, bg=ModernStyles.BG_CARD)
        voice_frame.pack(fill='x', padx=20, pady=5)

        # Get voice options from TTSGenerator
        voice_options = []
        voice_keys = []
        if TTSGenerator:
            # Group voices by category (⭐ = Premium Motivation, 💎🔥🎙️ = Deep voices)
            voice_keys = [
                # PREMIUM MOTIVATIONAL VOICES (Top of list!)
                'steffan_multi', 'andrew_multi', 'brian_multi', 'ava_multi', 'emma_multi',
                'alloy', 'nova', 'shimmer', 'kai', 'luna', 'jenny_multi', 'ryan_multi',

                # US Female Deep
                'monica', 'nancy', 'ana', 'aria', 'jenny', 'michelle', 'amber', 'ashley', 'sara', 'emma',

                # US Male Deep
                'andrew', 'brian', 'tony', 'jason', 'brandon', 'jacob', 'christopher', 'guy', 'davis', 'eric', 'roger', 'steffan',

                # British
                'thomas', 'mia', 'ryan', 'sonia', 'libby', 'alfie',

                # Australian
                'annette', 'natasha', 'william',

                # Indian English
                'neerja', 'prabhat',

                # URDU VOICES (اردو)
                'asad', 'uzma', 'salman', 'gul', 'asad_multi', 'uzma_multi', 'faiz', 'parveen'
            ]
            voice_options = [TTSGenerator.VOICE_NAMES.get(k, k) for k in voice_keys]
        else:
            voice_keys = ['aria', 'guy']
            voice_options = ['Aria - US Female (Friendly)', 'Guy - US Male (Friendly)']

        # Get current voice (with backward compatibility)
        current_voice = self.settings.get('tts_voice', 'aria')
        # Convert old 'female'/'male' to new keys
        if current_voice == 'female':
            current_voice = 'aria'
        elif current_voice == 'male':
            current_voice = 'guy'

        # Find display name for current voice
        try:
            current_index = voice_keys.index(current_voice)
            current_display = voice_options[current_index]
        except (ValueError, IndexError):
            current_display = voice_options[0]

        self.tts_voice_var = tk.StringVar(value=current_display)
        self.tts_voice_keys = voice_keys  # Store keys for saving

        voice_dropdown = ttk.Combobox(voice_frame, textvariable=self.tts_voice_var,
                                     values=voice_options, state='readonly',
                                     font=('Segoe UI', 10), width=35)
        voice_dropdown.pack(side='left', padx=15, pady=10, fill='x', expand=True)

        # TTS Speed
        self.create_label(content, "Speech Speed (words per minute):")
        speed_frame = tk.Frame(content, bg=ModernStyles.BG_CARD)
        speed_frame.pack(fill='x', padx=20, pady=5)

        self.tts_speed_var = tk.IntVar(value=self.settings.get('tts_speed', 150))
        tk.Scale(speed_frame, from_=100, to=250, orient='horizontal',
                variable=self.tts_speed_var, bg=ModernStyles.BG_CARD,
                fg=ModernStyles.TEXT_WHITE, highlightthickness=0,
                font=('Segoe UI', 9)).pack(side='left', fill='x', expand=True, padx=15, pady=10)

        tk.Label(speed_frame, textvariable=self.tts_speed_var, bg=ModernStyles.BG_CARD,
                fg=ModernStyles.TEXT_WHITE, width=4, font=('Segoe UI', 10)).pack(side='left', padx=10)

        # Synchronized Captions (NEW!)
        self.create_section(content, "Synchronized Captions (with TTS)", ModernStyles.ACCENT_ORANGE)

        self.captions_var = tk.BooleanVar(value=self.settings.get('enable_captions', False))
        self.create_checkbox(content, "Enable Word-by-Word Captions (Synced with Voiceover)", self.captions_var)

        info_frame2 = tk.Frame(content, bg=ModernStyles.BG_CARD)
        info_frame2.pack(fill='x', padx=20, pady=(0,10))
        tk.Label(info_frame2, text="ℹ️ Captions appear word-by-word synchronized with TTS audio. \nLike TikTok/YouTube auto-captions!",
                bg=ModernStyles.BG_CARD, fg=ModernStyles.TEXT_GRAY,
                font=('Segoe UI', 9), justify='left').pack(anchor='w', padx=15, pady=10)

        # Caption Style Presets (Like CapCut)
        self.create_label(content, "Caption Style Preset:")
        preset_frame = tk.Frame(content, bg=ModernStyles.BG_CARD)
        preset_frame.pack(fill='x', padx=20, pady=5)

        self.caption_preset_var = tk.StringVar(value="Custom")
        caption_presets = [
            "Custom",
            # VIRAL TRENDING STYLES
            "🚀 MrBeast Style (Yellow/Black Viral)",
            "💰 Alex Hormozi (Bold Red)",
            "👑 Andrew Tate (Aggressive Red/Black)",
            "🎯 Subway Surfers (Bright Colorful)",
            "💪 Fitness Motivation (Orange Energy)",
            "🧠 Psychology Facts (Purple Deep)",
            "💸 Money Mindset (Green Dollar)",
            "🎤 Podcast Clips (Navy Professional)",
            "😂 Meme Style (Comic Sans Fun)",
            "🌟 Instagram Viral (Gradient Pink)",
            "⚡ High Energy Shorts (Yellow Thunder)",
            "🔴 Breaking News Alert (Red Urgent)",
            "💎 Luxury Brand (Gold Elegant)",
            "🌊 Calm & Chill (Blue Peaceful)",
            "🎨 Artistic Creative (Multi-color)",

            # ORIGINAL STYLES
            "🔥 Bold Impact (TikTok Style)",
            "✨ Minimal Clean",
            "💎 Neon Glow",
            "🎬 Cinematic",
            "🎮 Gaming Style",
            "📰 News Anchor",
            "🌅 Vintage Film",
            "🎯 Corporate Pro",
            "🌈 Colorful Pop",
            "🖤 Dark Mode"
        ]
        preset_dropdown = ttk.Combobox(preset_frame, textvariable=self.caption_preset_var,
                                     values=caption_presets, state='readonly', width=35)
        preset_dropdown.pack(side='left', padx=15, pady=10, fill='x', expand=True)
        preset_dropdown.bind('<<ComboboxSelected>>', lambda e: self.apply_caption_preset())

        tk.Button(preset_frame, text="Apply Preset", command=self.apply_caption_preset,
                 bg=ModernStyles.ACCENT_ORANGE, fg='white', relief='flat',
                 font=('Segoe UI', 9, 'bold'), padx=15, pady=5).pack(side='left', padx=5)

        # Caption font size
        self.create_label(content, "Caption Font Size:")
        caption_size_frame = tk.Frame(content, bg=ModernStyles.BG_CARD)
        caption_size_frame.pack(fill='x', padx=20, pady=5)

        self.caption_size_var = tk.IntVar(value=self.settings.get('caption_font_size', 60))
        tk.Scale(caption_size_frame, from_=30, to=100, orient='horizontal',
                variable=self.caption_size_var, bg=ModernStyles.BG_CARD,
                fg=ModernStyles.TEXT_WHITE, highlightthickness=0,
                font=('Segoe UI', 9)).pack(side='left', fill='x', expand=True, padx=15, pady=10)

        tk.Label(caption_size_frame, textvariable=self.caption_size_var, bg=ModernStyles.BG_CARD,
                fg=ModernStyles.TEXT_WHITE, width=4, font=('Segoe UI', 10)).pack(side='left', padx=10)

        # Caption position
        self.create_label(content, "Caption Position:")
        caption_pos_frame = tk.Frame(content, bg=ModernStyles.BG_CARD)
        caption_pos_frame.pack(fill='x', padx=20, pady=5)

        self.caption_position_var = tk.StringVar(value=self.settings.get('caption_position', 'bottom'))
        for pos in ['top', 'center', 'bottom']:
            tk.Radiobutton(caption_pos_frame, text=pos.capitalize(), variable=self.caption_position_var,
                          value=pos, bg=ModernStyles.BG_CARD, fg=ModernStyles.TEXT_WHITE,
                          selectcolor=ModernStyles.BG_DARK, activebackground=ModernStyles.BG_CARD,
                          font=('Segoe UI', 10)).pack(side='left', padx=15, pady=10)

        # Words per caption line
        self.create_label(content, "Words Per Caption Line:")
        words_frame = tk.Frame(content, bg=ModernStyles.BG_CARD)
        words_frame.pack(fill='x', padx=20, pady=5)

        self.caption_words_var = tk.IntVar(value=self.settings.get('caption_words_per_line', 3))
        tk.Scale(words_frame, from_=1, to=5, orient='horizontal',
                variable=self.caption_words_var, bg=ModernStyles.BG_CARD,
                fg=ModernStyles.TEXT_WHITE, highlightthickness=0,
                font=('Segoe UI', 9)).pack(side='left', fill='x', expand=True, padx=15, pady=10)

        tk.Label(words_frame, textvariable=self.caption_words_var, bg=ModernStyles.BG_CARD,
                fg=ModernStyles.TEXT_WHITE, width=4, font=('Segoe UI', 10)).pack(side='left', padx=10)

        # Caption font style
        print("DEBUG: Adding caption font style control")
        self.create_label(content, "Caption Font Style:")
        font_frame = tk.Frame(content, bg=ModernStyles.BG_CARD)
        font_frame.pack(fill='x', padx=20, pady=5)

        # Get all available Windows fonts
        caption_fonts = self.get_windows_fonts()

        self.caption_font_var = tk.StringVar(value=self.settings.get('caption_font_style', 'arialbd.ttf'))
        font_dropdown = ttk.Combobox(font_frame, textvariable=self.caption_font_var,
                                     values=caption_fonts, state='readonly', width=30)
        font_dropdown.pack(side='left', padx=15, pady=10, fill='x', expand=True)

        # Caption text color
        self.create_label(content, "Caption Text Color:")
        text_color_frame = tk.Frame(content, bg=ModernStyles.BG_CARD)
        text_color_frame.pack(fill='x', padx=20, pady=5)

        self.caption_text_color_var = tk.StringVar(value=self.settings.get('caption_text_color', '#FFFFFF'))
        tk.Entry(text_color_frame, textvariable=self.caption_text_color_var, width=10,
                bg=ModernStyles.BG_DARK, fg=ModernStyles.TEXT_WHITE,
                font=('Segoe UI', 10)).pack(side='left', padx=(15,5), pady=10)

        tk.Button(text_color_frame, text="Choose Color", command=self.choose_caption_text_color,
                 bg=ModernStyles.ACCENT_BLUE, fg='white', relief='flat',
                 font=('Segoe UI', 9, 'bold'), padx=10, pady=5).pack(side='left', padx=5)

        # Caption background enable/disable
        print("DEBUG: Adding caption background enable/disable checkbox")
        self.caption_bg_enabled_var = tk.BooleanVar(value=self.settings.get('caption_bg_enabled', True))
        self.create_checkbox(content, "Enable Caption Background", self.caption_bg_enabled_var)

        # Caption background color
        print("DEBUG: Adding caption background color picker")
        self.create_label(content, "Caption Background Color:")
        bg_color_frame = tk.Frame(content, bg=ModernStyles.BG_CARD)
        bg_color_frame.pack(fill='x', padx=20, pady=5)

        self.caption_bg_color_var = tk.StringVar(value=self.settings.get('caption_bg_color', '#000000'))
        tk.Entry(bg_color_frame, textvariable=self.caption_bg_color_var, width=10,
                bg=ModernStyles.BG_DARK, fg=ModernStyles.TEXT_WHITE,
                font=('Segoe UI', 10)).pack(side='left', padx=(15,5), pady=10)

        tk.Button(bg_color_frame, text="Choose Color", command=self.choose_caption_bg_color,
                 bg=ModernStyles.ACCENT_BLUE, fg='white', relief='flat',
                 font=('Segoe UI', 9, 'bold'), padx=10, pady=5).pack(side='left', padx=5)

        # Caption background opacity
        self.create_label(content, "Caption Background Opacity:")
        opacity_frame = tk.Frame(content, bg=ModernStyles.BG_CARD)
        opacity_frame.pack(fill='x', padx=20, pady=5)

        self.caption_opacity_var = tk.IntVar(value=self.settings.get('caption_bg_opacity', 180))
        tk.Scale(opacity_frame, from_=0, to=255, orient='horizontal',
                variable=self.caption_opacity_var, bg=ModernStyles.BG_CARD,
                fg=ModernStyles.TEXT_WHITE, highlightthickness=0,
                font=('Segoe UI', 9)).pack(side='left', fill='x', expand=True, padx=15, pady=10)

        tk.Label(opacity_frame, textvariable=self.caption_opacity_var, bg=ModernStyles.BG_CARD,
                fg=ModernStyles.TEXT_WHITE, width=4, font=('Segoe UI', 10)).pack(side='left', padx=10)

        info_frame3 = tk.Frame(content, bg=ModernStyles.BG_CARD)
        info_frame3.pack(fill='x', padx=20, pady=(0,10))
        tk.Label(info_frame3, text="💡 Tip: Use hex colors (#FFFFFF = white, #000000 = black, #FFFF00 = yellow)",
                bg=ModernStyles.BG_CARD, fg=ModernStyles.TEXT_GRAY,
                font=('Segoe UI', 8), justify='left').pack(anchor='w', padx=15, pady=5)

    def create_section(self, parent, title, color):
        header = tk.Frame(parent, bg=color, height=3)
        header.pack(fill='x', pady=(20,0))

        tk.Label(header, text=title, bg=color, fg='white',
                font=('Segoe UI', 11, 'bold'), pady=6).pack(padx=15)

    def create_checkbox(self, parent, text, variable):
        frame = tk.Frame(parent, bg=ModernStyles.BG_CARD)
        frame.pack(fill='x', padx=20, pady=5)

        tk.Checkbutton(frame, text=text, variable=variable,
                      bg=ModernStyles.BG_CARD, fg=ModernStyles.TEXT_WHITE,
                      selectcolor=ModernStyles.BG_DARK, activebackground=ModernStyles.BG_CARD,
                      font=('Segoe UI', 10)).pack(anchor='w', padx=15, pady=10)

    def create_label(self, parent, text):
        tk.Label(parent, text=text, bg=ModernStyles.BG_DARK,
                fg=ModernStyles.TEXT_GRAY, font=('Segoe UI', 9)).pack(anchor='w', padx=20, pady=(10,2))

    def get_windows_fonts(self):
        """Get all TrueType fonts from Windows Fonts folder"""
        fonts_dir = Path(r"C:\Windows\Fonts")
        font_files = []

        if fonts_dir.exists():
            try:
                # Get all .ttf files
                ttf_files = list(fonts_dir.glob("*.ttf"))
                # Sort and get just the filename
                font_files = sorted([f.name for f in ttf_files])
                print(f"Found {len(font_files)} fonts in Windows Fonts folder")
            except Exception as e:
                print(f"Error scanning fonts folder: {e}")
                # Fallback to default fonts
                font_files = ['arial.ttf', 'arialbd.ttf', 'impact.ttf', 'comic.ttf',
                             'times.ttf', 'timesbd.ttf', 'calibri.ttf', 'calibrib.ttf',
                             'verdana.ttf', 'verdanab.ttf']
        else:
            # Fallback if Windows Fonts folder not accessible
            font_files = ['arial.ttf', 'arialbd.ttf', 'impact.ttf', 'comic.ttf',
                         'times.ttf', 'timesbd.ttf', 'calibri.ttf', 'calibrib.ttf',
                         'verdana.ttf', 'verdanab.ttf']

        return font_files

    def browse_bgm_file(self):
        filename = filedialog.askopenfilename(title="Select BGM File",
                                             filetypes=[("Audio", "*.mp3 *.wav *.m4a *.aac *.ogg")])
        if filename:
            self.bgm_path_var.set(filename)

    def browse_bgm_folder(self):
        folder = filedialog.askdirectory(title="Select BGM Folder")
        if folder:
            self.bgm_path_var.set(folder)

    def browse_voiceover(self):
        folder = filedialog.askdirectory(title="Select Voiceover Folder")
        if folder:
            self.vo_path_var.set(folder)

    def apply_caption_preset(self):
        """Apply professional caption preset styles (CapCut-inspired)"""
        preset = self.caption_preset_var.get()

        # Define preset configurations
        presets = {
            # VIRAL TRENDING PRESETS
            "🚀 MrBeast Style (Yellow/Black Viral)": {
                'font': 'impact.ttf',
                'size': 90,
                'text_color': '#000000',
                'bg_enabled': True,
                'bg_color': '#FFD700',
                'opacity': 255,
                'position': 'center',
                'words': 1
            },
            "💰 Alex Hormozi (Bold Red)": {
                'font': 'arialbd.ttf',
                'size': 85,
                'text_color': '#FFFFFF',
                'bg_enabled': True,
                'bg_color': '#DC143C',
                'opacity': 240,
                'position': 'center',
                'words': 2
            },
            "👑 Andrew Tate (Aggressive Red/Black)": {
                'font': 'impact.ttf',
                'size': 88,
                'text_color': '#FF0000',
                'bg_enabled': True,
                'bg_color': '#000000',
                'opacity': 255,
                'position': 'center',
                'words': 1
            },
            "🎯 Subway Surfers (Bright Colorful)": {
                'font': 'comic.ttf',
                'size': 78,
                'text_color': '#FFFF00',
                'bg_enabled': True,
                'bg_color': '#FF1493',
                'opacity': 220,
                'position': 'top',
                'words': 2
            },
            "💪 Fitness Motivation (Orange Energy)": {
                'font': 'impact.ttf',
                'size': 82,
                'text_color': '#FFFFFF',
                'bg_enabled': True,
                'bg_color': '#FF6600',
                'opacity': 230,
                'position': 'center',
                'words': 2
            },
            "🧠 Psychology Facts (Purple Deep)": {
                'font': 'arialbd.ttf',
                'size': 72,
                'text_color': '#FFFFFF',
                'bg_enabled': True,
                'bg_color': '#6A0DAD',
                'opacity': 220,
                'position': 'center',
                'words': 3
            },
            "💸 Money Mindset (Green Dollar)": {
                'font': 'impact.ttf',
                'size': 85,
                'text_color': '#FFFFFF',
                'bg_enabled': True,
                'bg_color': '#228B22',
                'opacity': 240,
                'position': 'center',
                'words': 2
            },
            "🎤 Podcast Clips (Navy Professional)": {
                'font': 'calibrib.ttf',
                'size': 68,
                'text_color': '#FFFFFF',
                'bg_enabled': True,
                'bg_color': '#1E3A8A',
                'opacity': 230,
                'position': 'bottom',
                'words': 4
            },
            "😂 Meme Style (Comic Sans Fun)": {
                'font': 'comic.ttf',
                'size': 75,
                'text_color': '#000000',
                'bg_enabled': True,
                'bg_color': '#FFFFFF',
                'opacity': 220,
                'position': 'center',
                'words': 2
            },
            "🌟 Instagram Viral (Gradient Pink)": {
                'font': 'arialbd.ttf',
                'size': 76,
                'text_color': '#FFFFFF',
                'bg_enabled': True,
                'bg_color': '#E1306C',
                'opacity': 225,
                'position': 'center',
                'words': 2
            },
            "⚡ High Energy Shorts (Yellow Thunder)": {
                'font': 'impact.ttf',
                'size': 88,
                'text_color': '#000000',
                'bg_enabled': True,
                'bg_color': '#FFFF00',
                'opacity': 245,
                'position': 'center',
                'words': 1
            },
            "🔴 Breaking News Alert (Red Urgent)": {
                'font': 'arialbd.ttf',
                'size': 74,
                'text_color': '#FFFFFF',
                'bg_enabled': True,
                'bg_color': '#FF0000',
                'opacity': 250,
                'position': 'bottom',
                'words': 3
            },
            "💎 Luxury Brand (Gold Elegant)": {
                'font': 'georgia.ttf',
                'size': 70,
                'text_color': '#FFD700',
                'bg_enabled': True,
                'bg_color': '#000000',
                'opacity': 235,
                'position': 'center',
                'words': 3
            },
            "🌊 Calm & Chill (Blue Peaceful)": {
                'font': 'calibri.ttf',
                'size': 65,
                'text_color': '#FFFFFF',
                'bg_enabled': True,
                'bg_color': '#4682B4',
                'opacity': 200,
                'position': 'bottom',
                'words': 4
            },
            "🎨 Artistic Creative (Multi-color)": {
                'font': 'comic.ttf',
                'size': 73,
                'text_color': '#FF1493',
                'bg_enabled': True,
                'bg_color': '#00CED1',
                'opacity': 210,
                'position': 'center',
                'words': 2
            },

            # ORIGINAL PRESETS
            "🔥 Bold Impact (TikTok Style)": {
                'font': 'impact.ttf',
                'size': 80,
                'text_color': '#FFFFFF',
                'bg_enabled': True,
                'bg_color': '#000000',
                'opacity': 200,
                'position': 'center',
                'words': 2
            },
            "✨ Minimal Clean": {
                'font': 'calibrib.ttf',
                'size': 60,
                'text_color': '#FFFFFF',
                'bg_enabled': False,
                'bg_color': '#000000',
                'opacity': 0,
                'position': 'bottom',
                'words': 3
            },
            "💎 Neon Glow": {
                'font': 'arialbd.ttf',
                'size': 75,
                'text_color': '#00FFFF',
                'bg_enabled': True,
                'bg_color': '#FF00FF',
                'opacity': 180,
                'position': 'center',
                'words': 2
            },
            "🎬 Cinematic": {
                'font': 'garamond.ttf',
                'size': 65,
                'text_color': '#F5F5DC',
                'bg_enabled': True,
                'bg_color': '#1C1C1C',
                'opacity': 220,
                'position': 'bottom',
                'words': 4
            },
            "🎮 Gaming Style": {
                'font': 'impact.ttf',
                'size': 85,
                'text_color': '#00FF00',
                'bg_enabled': True,
                'bg_color': '#000000',
                'opacity': 240,
                'position': 'top',
                'words': 2
            },
            "📰 News Anchor": {
                'font': 'arialbd.ttf',
                'size': 70,
                'text_color': '#FFFFFF',
                'bg_enabled': True,
                'bg_color': '#003366',
                'opacity': 230,
                'position': 'bottom',
                'words': 4
            },
            "🌅 Vintage Film": {
                'font': 'georgia.ttf',
                'size': 65,
                'text_color': '#FFE4B5',
                'bg_enabled': True,
                'bg_color': '#8B4513',
                'opacity': 150,
                'position': 'center',
                'words': 3
            },
            "🎯 Corporate Pro": {
                'font': 'calibrib.ttf',
                'size': 65,
                'text_color': '#2C3E50',
                'bg_enabled': True,
                'bg_color': '#ECF0F1',
                'opacity': 220,
                'position': 'bottom',
                'words': 4
            },
            "🌈 Colorful Pop": {
                'font': 'comic.ttf',
                'size': 75,
                'text_color': '#FF1493',
                'bg_enabled': True,
                'bg_color': '#FFFF00',
                'opacity': 200,
                'position': 'center',
                'words': 2
            },
            "🖤 Dark Mode": {
                'font': 'arialbd.ttf',
                'size': 70,
                'text_color': '#E0E0E0',
                'bg_enabled': True,
                'bg_color': '#121212',
                'opacity': 240,
                'position': 'bottom',
                'words': 3
            }
        }

        if preset in presets:
            config = presets[preset]
            # Apply all preset values to the UI controls
            self.caption_font_var.set(config['font'])
            self.caption_size_var.set(config['size'])
            self.caption_text_color_var.set(config['text_color'])
            self.caption_bg_enabled_var.set(config['bg_enabled'])
            self.caption_bg_color_var.set(config['bg_color'])
            self.caption_opacity_var.set(config['opacity'])
            self.caption_position_var.set(config['position'])
            self.caption_words_var.set(config['words'])

            messagebox.showinfo("Preset Applied", f"✓ Applied '{preset}' style to captions!\n\nYou can still customize individual settings.")

    def choose_caption_text_color(self):
        color = colorchooser.askcolor(title="Choose Caption Text Color",
                                      initialcolor=self.caption_text_color_var.get())
        if color[1]:  # color[1] is the hex value
            self.caption_text_color_var.set(color[1])
            self.caption_preset_var.set("Custom")  # Mark as custom when manually changed

    def choose_caption_bg_color(self):
        color = colorchooser.askcolor(title="Choose Caption Background Color",
                                      initialcolor=self.caption_bg_color_var.get())
        if color[1]:  # color[1] is the hex value
            self.caption_bg_color_var.set(color[1])
            self.caption_preset_var.set("Custom")  # Mark as custom when manually changed

    def save_settings(self):
        self.settings['mute_original_audio'] = self.mute_var.get()
        self.settings['original_audio_volume'] = self.original_volume_var.get()
        self.settings['add_custom_bgm'] = self.bgm_var.get()
        self.settings['bgm_file'] = self.bgm_path_var.get()
        self.settings['add_voiceover'] = self.vo_var.get()
        self.settings['voiceover_folder'] = self.vo_path_var.get()

        # TTS settings
        self.settings['use_tts_voiceover'] = self.tts_var.get()

        # Convert display name back to voice key
        display_name = self.tts_voice_var.get()
        if TTSGenerator:
            voice_options = [TTSGenerator.VOICE_NAMES.get(k, k) for k in self.tts_voice_keys]
            try:
                voice_index = voice_options.index(display_name)
                self.settings['tts_voice'] = self.tts_voice_keys[voice_index]
            except (ValueError, IndexError):
                self.settings['tts_voice'] = 'aria'  # Default
        else:
            self.settings['tts_voice'] = 'aria'

        self.settings['tts_speed'] = self.tts_speed_var.get()

        # Caption settings
        self.settings['enable_captions'] = self.captions_var.get()
        self.settings['caption_font_size'] = self.caption_size_var.get()
        self.settings['caption_position'] = self.caption_position_var.get()
        self.settings['caption_words_per_line'] = self.caption_words_var.get()
        self.settings['caption_font_style'] = self.caption_font_var.get()
        self.settings['caption_text_color'] = self.caption_text_color_var.get()
        self.settings['caption_bg_enabled'] = self.caption_bg_enabled_var.get()
        self.settings['caption_bg_color'] = self.caption_bg_color_var.get()
        self.settings['caption_bg_opacity'] = self.caption_opacity_var.get()

        self.on_save(self.settings)
        self.window.destroy()


class VideoProcessingWindow:
    """Window for running video processing with live progress"""

    def __init__(self, parent, settings):
        self.settings = settings
        self.processing = False
        self.log_queue = queue.Queue()

        self.window = tk.Toplevel(parent)
        self.window.title("▶️ Video Processing")
        self.window.geometry("950x700")
        self.window.configure(bg=ModernStyles.BG_DARK)
        # Removed transient and grab_set to allow minimize button
        # self.window.transient(parent)
        # self.window.grab_set()

        self.setup_ui()
        self.load_paths()
        self.update_log()

    def setup_ui(self):
        # Initialize path variables (loaded from saved config, not shown in UI)
        self.video_folder_var = tk.StringVar()
        self.quotes_file_var = tk.StringVar()
        self.output_folder_var = tk.StringVar()

        # Header
        header = tk.Frame(self.window, bg=ModernStyles.ACCENT_GREEN, height=60)
        header.pack(fill='x')
        header.pack_propagate(False)

        tk.Label(header, text="▶️ Video Processing",
                bg=ModernStyles.ACCENT_GREEN, fg='white',
                font=('Segoe UI', 16, 'bold')).pack(side='left', padx=20, pady=15)

        # Content
        content = tk.Frame(self.window, bg=ModernStyles.BG_DARK)
        content.pack(fill='both', expand=True, padx=20, pady=20)

        # Progress section
        self.create_section(content, "Progress", ModernStyles.ACCENT_GREEN)

        progress_frame = tk.Frame(content, bg=ModernStyles.BG_CARD)
        progress_frame.pack(fill='x', padx=20, pady=10)

        self.progress_var = tk.StringVar(value="Ready to start processing")
        tk.Label(progress_frame, textvariable=self.progress_var, bg=ModernStyles.BG_CARD,
                fg=ModernStyles.TEXT_WHITE, font=('Segoe UI', 10)).pack(pady=10)

        self.progress = ttk.Progressbar(progress_frame, mode='determinate', length=400)
        self.progress.pack(pady=(0,10), padx=20)

        # Log section
        self.create_section(content, "Processing Log", ModernStyles.ACCENT_PURPLE)

        log_frame = tk.Frame(content, bg=ModernStyles.BG_CARD)
        log_frame.pack(fill='both', expand=True, padx=20, pady=10)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=18, bg='#0f172a',
                                                  fg=ModernStyles.TEXT_WHITE, font=('Consolas', 9),
                                                  relief='flat', state='disabled')
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)

        # Bottom buttons
        btn_frame = tk.Frame(self.window, bg=ModernStyles.BG_DARK, height=70)
        btn_frame.pack(fill='x', side='bottom')
        btn_frame.pack_propagate(False)

        buttons = tk.Frame(btn_frame, bg=ModernStyles.BG_DARK)
        buttons.pack(expand=True)

        self.start_btn = tk.Button(buttons, text="▶️  Start Processing", command=self.start_processing,
                                   bg=ModernStyles.ACCENT_GREEN, fg='white', font=('Segoe UI', 11, 'bold'),
                                   relief='flat', padx=30, pady=12, cursor='hand2')
        self.start_btn.pack(side='left', padx=5)

        self.stop_btn = tk.Button(buttons, text="⏹️  Stop", command=self.stop_processing,
                                 bg=ModernStyles.ACCENT_RED, fg='white', font=('Segoe UI', 11, 'bold'),
                                 relief='flat', padx=30, pady=12, cursor='hand2', state='disabled')
        self.stop_btn.pack(side='left', padx=5)

        tk.Button(buttons, text="✕  Close", command=self.window.destroy,
                 bg=ModernStyles.ACCENT_ORANGE, fg='white', font=('Segoe UI', 11, 'bold'),
                 relief='flat', padx=30, pady=12, cursor='hand2').pack(side='left', padx=5)

    def create_section(self, parent, title, color):
        header = tk.Frame(parent, bg=color, height=3)
        header.pack(fill='x', pady=(20,0))

        tk.Label(header, text=title, bg=color, fg='white',
                font=('Segoe UI', 11, 'bold'), pady=6).pack(padx=15)

    def load_paths(self):
        """Load previously saved paths or use config defaults"""
        # Default paths from config
        default_video_folder = ''
        default_quotes_file = ''
        default_output_folder = ''

        if config:
            default_video_folder = str(config.VIDEO_FOLDER)
            default_quotes_file = str(config.QUOTES_FILE)
            default_output_folder = str(config.OUTPUT_FOLDER)

        # Try loading from saved file
        paths_file = Path('processing_paths.json')
        loaded_video = default_video_folder
        loaded_quotes = default_quotes_file
        loaded_output = default_output_folder

        if paths_file.exists():
            try:
                with open(paths_file, 'r') as f:
                    paths = json.load(f)
                    loaded_video = paths.get('video_folder', default_video_folder)
                    loaded_quotes = paths.get('quotes_file', default_quotes_file)
                    loaded_output = paths.get('output_folder', default_output_folder)
            except:
                pass

        # Validate paths exist, otherwise use defaults
        if loaded_video and Path(loaded_video).exists():
            self.video_folder_var.set(loaded_video)
        else:
            self.video_folder_var.set(default_video_folder)

        if loaded_quotes and Path(loaded_quotes).exists():
            self.quotes_file_var.set(loaded_quotes)
        else:
            self.quotes_file_var.set(default_quotes_file)

        # Output folder - use loaded if specified, otherwise default
        if loaded_output:
            self.output_folder_var.set(loaded_output)
        else:
            self.output_folder_var.set(default_output_folder)

    def save_paths(self):
        """Save paths for next time"""
        paths = {
            'video_folder': self.video_folder_var.get(),
            'quotes_file': self.quotes_file_var.get(),
            'output_folder': self.output_folder_var.get()
        }
        with open('processing_paths.json', 'w') as f:
            json.dump(paths, f, indent=2)

    def log(self, message):
        """Add message to log queue"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_queue.put(f"[{timestamp}] {message}")

    def update_log(self):
        """Update log display from queue"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.config(state='normal')
                self.log_text.insert(tk.END, message + '\n')
                self.log_text.see(tk.END)
                self.log_text.config(state='disabled')
        except queue.Empty:
            pass
        self.window.after(100, self.update_log)

    def start_processing(self):
        """Start video processing in background thread"""
        if VideoQuoteAutomation is None:
            messagebox.showerror("Error", "Video automation module not available!")
            return

        # Validate paths
        video_folder = self.video_folder_var.get()
        quotes_file = self.quotes_file_var.get()
        output_folder = self.output_folder_var.get()

        if not video_folder or not Path(video_folder).exists():
            messagebox.showerror("Error", "Please select a valid video folder!")
            return

        if not quotes_file or not Path(quotes_file).exists():
            messagebox.showerror("Error", "Please select a valid quotes file!")
            return

        if not output_folder:
            messagebox.showerror("Error", "Please select an output folder!")
            return

        # Save paths
        self.save_paths()

        # Disable start button
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.processing = True

        # Clear log
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')

        # Start processing thread
        thread = threading.Thread(target=self.process_videos, daemon=True)
        thread.start()

    def process_videos(self):
        """Process videos in background thread"""
        try:
            self.log("=" * 70)
            self.log("Starting Video Processing...")
            self.log("=" * 70)

            # Create custom automation instance with user-specified paths
            video_folder = Path(self.video_folder_var.get())
            quotes_file = Path(self.quotes_file_var.get())
            output_folder = Path(self.output_folder_var.get())

            self.log(f"Video folder: {video_folder}")
            self.log(f"Quotes file: {quotes_file}")
            self.log(f"Output folder: {output_folder}")
            self.log("")

            # Create output folder if it doesn't exist
            output_folder.mkdir(parents=True, exist_ok=True)

            # Create automation instance
            automation = VideoQuoteAutomation()
            automation.video_folder = video_folder
            automation.quotes_file = quotes_file
            automation.output_folder = output_folder
            automation.settings = self.settings

            # Get videos and quotes
            videos = automation.get_video_files(sort_by='created')
            quotes = automation.read_quotes()

            if not videos:
                self.log("✗ No videos found!")
                self.progress_var.set("Error: No videos found")
                return

            if not quotes:
                self.log("✗ No quotes found!")
                self.progress_var.set("Error: No quotes found")
                return

            num_to_process = min(len(videos), len(quotes))
            self.log(f"Processing {num_to_process} videos...")
            self.log("")

            # Set progress bar maximum
            self.progress['maximum'] = num_to_process

            # Process each video
            success_count = 0
            for i in range(num_to_process):
                if not self.processing:
                    self.log("⏹️ Processing stopped by user")
                    break

                video_path = videos[i]
                quote = quotes[i]

                self.log(f"Processing {i+1}/{num_to_process}: {video_path.name}")
                self.progress_var.set(f"Processing {i+1}/{num_to_process}: {video_path.name}")
                self.progress['value'] = i

                try:
                    output_path, filename = automation.add_quote_to_video(video_path, quote, video_index=i)
                    self.log(f"✓ Success: {filename}")
                    success_count += 1
                except Exception as e:
                    self.log(f"✗ Error: {str(e)}")

                self.log("")

            # Complete
            self.progress['value'] = num_to_process
            self.progress_var.set(f"Complete: {success_count}/{num_to_process} videos processed")
            self.log("=" * 70)
            self.log(f"Processing Complete! {success_count}/{num_to_process} successful")
            self.log(f"Output folder: {output_folder}")
            self.log("=" * 70)

            # Re-enable buttons
            self.window.after(0, lambda: self.start_btn.config(state='normal'))
            self.window.after(0, lambda: self.stop_btn.config(state='disabled'))

            # Show completion message
            self.window.after(0, lambda: messagebox.showinfo(
                "Complete",
                f"Processing complete!\n\n{success_count}/{num_to_process} videos processed successfully.\n\nOutput: {output_folder}"
            ))

        except Exception as e:
            self.log(f"✗ Fatal error: {str(e)}")
            self.progress_var.set("Error occurred")
            self.window.after(0, lambda: messagebox.showerror("Error", f"Processing error:\n{str(e)}"))
            self.window.after(0, lambda: self.start_btn.config(state='normal'))
            self.window.after(0, lambda: self.stop_btn.config(state='disabled'))

    def stop_processing(self):
        """Stop processing"""
        self.processing = False
        self.stop_btn.config(state='disabled')
        self.log("⏹️ Stopping after current video...")


class ProcessingPopup:
    """Popup for configuring processing paths"""

    def __init__(self, parent, settings):
        self.settings = settings

        self.window = tk.Toplevel(parent)
        self.window.title("⚙️ Processing Configuration")
        self.window.geometry("680x480")
        self.window.configure(bg=ModernStyles.BG_DARK)
        # Removed grab_set to allow minimize

        self.setup_ui()
        self.load_paths()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.window, bg=ModernStyles.ACCENT_ORANGE, height=60)
        header.pack(fill='x')
        header.pack_propagate(False)

        tk.Label(header, text="⚙️ Video Processing Configuration",
                bg=ModernStyles.ACCENT_ORANGE, fg='white',
                font=('Segoe UI', 16, 'bold')).pack(side='left', padx=20, pady=15)

        # Content
        content = tk.Frame(self.window, bg=ModernStyles.BG_DARK)
        content.pack(fill='both', expand=True, padx=20, pady=20)

        # Path configurations
        self.create_section(content, "File Paths", ModernStyles.ACCENT_BLUE)

        # Video folder
        self.create_label(content, "Video Folder (source videos):")
        self.video_folder_var = tk.StringVar()
        self.create_path_selector(content, self.video_folder_var, self.browse_video_folder)

        # Quotes file
        self.create_label(content, "Quotes File (.txt):")
        self.quotes_file_var = tk.StringVar()
        self.create_path_selector(content, self.quotes_file_var, self.browse_quotes_file, is_file=True)

        # Output folder
        self.create_label(content, "Output Folder (final videos):")
        self.output_folder_var = tk.StringVar()
        self.create_path_selector(content, self.output_folder_var, self.browse_output_folder)

        # Archive folder
        self.create_label(content, "Archive Folder (for uploaded videos - optional):")
        self.archive_folder_var = tk.StringVar()
        self.create_path_selector(content, self.archive_folder_var, self.browse_archive_folder)

        # Bottom buttons
        btn_frame = tk.Frame(self.window, bg=ModernStyles.BG_DARK, height=70)
        btn_frame.pack(fill='x', side='bottom')
        btn_frame.pack_propagate(False)

        buttons = tk.Frame(btn_frame, bg=ModernStyles.BG_DARK)
        buttons.pack(expand=True)

        tk.Button(buttons, text="💾  Save Paths", command=self.save_paths_only,
                 bg=ModernStyles.ACCENT_BLUE, fg='white', font=('Segoe UI', 11, 'bold'),
                 relief='flat', padx=30, pady=12, cursor='hand2').pack(side='left', padx=5)

        tk.Button(buttons, text="✕  Close", command=self.window.destroy,
                 bg=ModernStyles.ACCENT_RED, fg='white', font=('Segoe UI', 11, 'bold'),
                 relief='flat', padx=30, pady=12, cursor='hand2').pack(side='left', padx=5)

    def create_section(self, parent, title, color):
        header = tk.Frame(parent, bg=color, height=3)
        header.pack(fill='x', pady=(20,0))

        tk.Label(header, text=title, bg=color, fg='white',
                font=('Segoe UI', 11, 'bold'), pady=6).pack(padx=15)

    def create_label(self, parent, text):
        tk.Label(parent, text=text, bg=ModernStyles.BG_DARK,
                fg=ModernStyles.TEXT_GRAY, font=('Segoe UI', 9)).pack(anchor='w', padx=20, pady=(10,2))

    def create_path_selector(self, parent, var, browse_cmd, is_file=False):
        frame = tk.Frame(parent, bg=ModernStyles.BG_CARD)
        frame.pack(fill='x', padx=20, pady=5)

        tk.Entry(frame, textvariable=var, width=60,
                bg='#0f172a', fg=ModernStyles.TEXT_WHITE, relief='flat', font=('Segoe UI', 9)).pack(
            side='left', fill='x', expand=True, padx=10, pady=10)

        icon = "📄" if is_file else "📁"
        tk.Button(frame, text=f"{icon} Browse", command=browse_cmd,
                 bg=ModernStyles.ACCENT_BLUE, fg='white', relief='flat', cursor='hand2', padx=15).pack(
            side='left', padx=5)

    def browse_video_folder(self):
        folder = filedialog.askdirectory(title="Select Video Folder")
        if folder:
            self.video_folder_var.set(folder)

    def browse_quotes_file(self):
        filename = filedialog.askopenfilename(title="Select Quotes File",
                                             filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filename:
            self.quotes_file_var.set(filename)

    def browse_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder_var.set(folder)

    def browse_archive_folder(self):
        folder = filedialog.askdirectory(title="Select Archive Folder")
        if folder:
            self.archive_folder_var.set(folder)

    def load_paths(self):
        """Load previously saved paths"""
        paths_file = Path('processing_paths.json')
        if paths_file.exists():
            try:
                with open(paths_file, 'r') as f:
                    paths = json.load(f)
                    self.video_folder_var.set(paths.get('video_folder', ''))
                    self.quotes_file_var.set(paths.get('quotes_file', ''))
                    self.output_folder_var.set(paths.get('output_folder', ''))
                    self.archive_folder_var.set(paths.get('archive_folder', ''))
            except:
                pass

    def save_paths(self):
        """Save paths for next time"""
        paths = {
            'video_folder': self.video_folder_var.get(),
            'quotes_file': self.quotes_file_var.get(),
            'output_folder': self.output_folder_var.get(),
            'archive_folder': self.archive_folder_var.get()
        }
        with open('processing_paths.json', 'w') as f:
            json.dump(paths, f, indent=2)

    def save_paths_only(self):
        """Save paths and show confirmation"""
        self.save_paths()
        messagebox.showinfo("Saved", "Processing paths saved successfully!")


class DashboardGUI:
    """Main dashboard interface"""

    def __init__(self, root):
        self.root = root
        self.root.title("🎬 Video Automation Studio - Dashboard")
        self.root.geometry("1100x700")  # More compact
        self.root.configure(bg=ModernStyles.BG_DARK)
        self.root.resizable(True, True)
        self.root.minsize(900, 600)  # Minimum window size

        self.settings = self.load_settings()
        self.processing = False

        self.setup_ui()

    def load_settings(self):
        settings_file = Path('overlay_settings.json')
        if settings_file.exists():
            with open(settings_file, 'r') as f:
                return json.load(f)
        return {}

    def save_settings(self):
        with open('overlay_settings.json', 'w') as f:
            json.dump(self.settings, f, indent=2)
        messagebox.showinfo("Success", "Settings saved successfully!")

    def setup_ui(self):
        # Top header - more compact
        header = tk.Frame(self.root, bg=ModernStyles.ACCENT_BLUE, height=65)
        header.pack(fill='x')
        header.pack_propagate(False)

        header_content = tk.Frame(header, bg=ModernStyles.ACCENT_BLUE)
        header_content.pack(expand=True, fill='both', padx=30, pady=12)

        tk.Label(header_content, text="🎬 Video Automation Studio",
                bg=ModernStyles.ACCENT_BLUE, fg='white',
                font=('Segoe UI', 20, 'bold')).pack(side='left')

        tk.Label(header_content, text="Professional Dashboard",
                bg=ModernStyles.ACCENT_BLUE, fg='#e0f2fe',
                font=('Segoe UI', 11)).pack(side='left', padx=(12,0))

        # Main dashboard - reduced padding
        dashboard = tk.Frame(self.root, bg=ModernStyles.BG_DARK)
        dashboard.pack(fill='both', expand=True, padx=25, pady=20)

        # Feature cards grid - more compact layout
        cards_container = tk.Frame(dashboard, bg=ModernStyles.BG_DARK)
        cards_container.pack(expand=True, fill='both')

        # Row 1 - reduced spacing
        row1 = tk.Frame(cards_container, bg=ModernStyles.BG_DARK)
        row1.pack(fill='both', expand=True, pady=(0,15))

        # Configure grid for equal spacing
        row1.grid_columnconfigure(0, weight=1)
        row1.grid_columnconfigure(1, weight=1)
        row1.grid_rowconfigure(0, weight=1)

        card1 = self.create_card(row1, "📝", "Text & Fonts",
                                "Configure text style, fonts, colors and position",
                                ModernStyles.ACCENT_BLUE, lambda: self.open_text_settings())
        card1.grid(row=0, column=0, sticky='nsew', padx=(0,8))

        card2 = self.create_card(row1, "✨", "Visual Effects",
                                "Add animations, glow, shadows and color grading",
                                ModernStyles.ACCENT_PURPLE, lambda: self.open_effects_settings())
        card2.grid(row=0, column=1, sticky='nsew', padx=(8,0))

        # Row 2
        row2 = tk.Frame(cards_container, bg=ModernStyles.BG_DARK)
        row2.pack(fill='both', expand=True)

        row2.grid_columnconfigure(0, weight=1)
        row2.grid_columnconfigure(1, weight=1)
        row2.grid_rowconfigure(0, weight=1)

        card3 = self.create_card(row2, "🔊", "Audio & Music",
                                "BGM, voiceover and audio mixing settings",
                                ModernStyles.ACCENT_GREEN, lambda: self.open_audio_settings())
        card3.grid(row=0, column=0, sticky='nsew', padx=(0,8))

        card4 = self.create_card(row2, "⚙️", "Processing",
                                "Configure paths and process videos",
                                ModernStyles.ACCENT_ORANGE, lambda: self.show_processing())
        card4.grid(row=0, column=1, sticky='nsew', padx=(8,0))

        # Control buttons at bottom - more compact
        controls = tk.Frame(self.root, bg=ModernStyles.BG_DARK, height=70)
        controls.pack(fill='x', side='bottom', pady=(15,0))
        controls.pack_propagate(False)

        btn_frame = tk.Frame(controls, bg=ModernStyles.BG_DARK)
        btn_frame.pack(expand=True)

        tk.Button(btn_frame, text="💾  Save All Settings", command=self.save_settings,
                 bg=ModernStyles.ACCENT_BLUE, fg='white', font=('Segoe UI', 13, 'bold'),
                 relief='flat', padx=45, pady=16, cursor='hand2',
                 borderwidth=0, highlightthickness=0).pack(side='left', padx=8)

        self.process_btn = tk.Button(btn_frame, text="▶️  Start Processing", command=self.start_processing,
                                     bg=ModernStyles.ACCENT_GREEN, fg='white', font=('Segoe UI', 13, 'bold'),
                                     relief='flat', padx=45, pady=16, cursor='hand2',
                                     borderwidth=0, highlightthickness=0)
        self.process_btn.pack(side='left', padx=8)

    def create_card(self, parent, emoji, title, description, color, command):
        card = tk.Frame(parent, bg=ModernStyles.BG_CARD, relief='flat', bd=0, cursor='hand2',
                       highlightbackground=ModernStyles.BORDER, highlightthickness=1)

        # Hover effect
        def on_enter(e):
            card.config(bg=ModernStyles.BG_CARD_HOVER, highlightbackground=color)
            for widget in card.winfo_children():
                if isinstance(widget, tk.Label) and widget != border:
                    widget.config(bg=ModernStyles.BG_CARD_HOVER)

        def on_leave(e):
            card.config(bg=ModernStyles.BG_CARD, highlightbackground=ModernStyles.BORDER)
            for widget in card.winfo_children():
                if isinstance(widget, tk.Label) and widget != border:
                    widget.config(bg=ModernStyles.BG_CARD)

        card.bind('<Enter>', on_enter)
        card.bind('<Leave>', on_leave)
        card.bind('<Button-1>', lambda e: command())

        # Content container - more compact
        content = tk.Frame(card, bg=ModernStyles.BG_CARD)
        content.pack(expand=True, fill='both', pady=25, padx=25)

        tk.Label(content, text=emoji, bg=ModernStyles.BG_CARD,
                font=('Segoe UI', 48)).pack(pady=(0,10))

        tk.Label(content, text=title, bg=ModernStyles.BG_CARD, fg=color,
                font=('Segoe UI', 16, 'bold')).pack(pady=(0,8))

        tk.Label(content, text=description, bg=ModernStyles.BG_CARD, fg=ModernStyles.TEXT_GRAY,
                font=('Segoe UI', 11), wraplength=280, justify='center').pack(pady=(0,0))

        # Border
        border = tk.Frame(card, bg=color, height=5)
        border.pack(fill='x', side='bottom')

        # Make all child labels clickable
        for widget in content.winfo_children():
            if isinstance(widget, tk.Label):
                widget.bind('<Button-1>', lambda e: command())

        return card

    def open_text_settings(self):
        TextSettingsPopup(self.root, self.settings, self.update_settings)

    def open_effects_settings(self):
        EffectsSettingsPopup(self.root, self.settings, self.update_settings)

    def open_audio_settings(self):
        AudioSettingsPopup(self.root, self.settings, self.update_settings)

    def show_processing(self):
        """Open processing popup"""
        ProcessingPopup(self.root, self.settings)

    def update_settings(self, new_settings):
        self.settings.update(new_settings)
        self.save_settings()

    def start_processing(self):
        """Open video processing window with live progress"""
        VideoProcessingWindow(self.root, self.settings)

    def stop_processing(self):
        self.processing = False


if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardGUI(root)
    root.mainloop()
