"""
Video Text Overlay GUI - Visual Settings Editor with Live Preview
Run this to configure your video text overlay settings visually
"""

import tkinter as tk
from tkinter import ttk, colorchooser, messagebox, filedialog
from PIL import Image, ImageDraw, ImageFont, ImageTk
import json
from pathlib import Path
import os


class VideoOverlayGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Text Overlay - Settings & Preview")
        self.root.geometry("1200x900")
        
        # Get available system fonts
        self.available_fonts = self.get_system_fonts()
        
        # Default settings
        self.settings = {
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
        
        # Load saved settings if exists
        self.load_settings()
        
        # Sample text for preview
        self.sample_main_text = "Every \"I'm fine\" hides a full season of emotional chaos, overthinking, and imaginary arguments that the other person will never even know about"
        self.sample_emoji = "😅💭💬"
        self.sample_cta = "Been there?"
        
        self.setup_ui()
        self.update_preview()
    
    def get_system_fonts(self):
        """Get all available TrueType fonts from Windows fonts folder"""
        fonts_dict = {}
        
        # Windows fonts folder
        fonts_folder = Path(r"C:\Windows\Fonts")
        
        if not fonts_folder.exists():
            # Fallback to common fonts
            return {
                'Arial': 'arial.ttf',
                'Arial Bold': 'arialbd.ttf',
                'Arial Italic': 'ariali.ttf',
                'Arial Bold Italic': 'arialbi.ttf',
                'Impact': 'impact.ttf',
                'Calibri': 'calibri.ttf',
                'Calibri Bold': 'calibrib.ttf',
                'Verdana': 'verdana.ttf',
                'Verdana Bold': 'verdanab.ttf'
            }
        
        # Scan for .ttf files
        try:
            for font_file in fonts_folder.glob("*.ttf"):
                # Store with full path as value
                font_name = font_file.stem
                
                # Create readable font name
                # Handle common patterns
                display_name = font_name
                
                # Replace common suffixes
                if font_name.endswith('bd'):
                    display_name = font_name[:-2] + ' Bold'
                elif font_name.endswith('bi'):
                    display_name = font_name[:-2] + ' Bold Italic'
                elif font_name.endswith('i'):
                    display_name = font_name[:-1] + ' Italic'
                elif font_name.endswith('z'):
                    display_name = font_name[:-1] + ' Italic'
                
                # Capitalize each word
                display_name = ' '.join(word.capitalize() for word in display_name.split())
                
                # Store full path
                fonts_dict[display_name] = str(font_file)
            
            # If we found fonts, return them sorted
            if fonts_dict:
                return dict(sorted(fonts_dict.items()))
            
        except Exception as e:
            print(f"Error scanning fonts: {e}")
        
        # Fallback fonts with full paths
        fallback = {}
        for name, filename in [
            ('Arial', 'arial.ttf'),
            ('Arial Bold', 'arialbd.ttf'),
            ('Arial Italic', 'ariali.ttf'),
            ('Impact', 'impact.ttf'),
            ('Calibri Bold', 'calibrib.ttf'),
            ('Verdana Bold', 'verdanab.ttf')
        ]:
            full_path = fonts_folder / filename
            if full_path.exists():
                fallback[name] = str(full_path)
            else:
                fallback[name] = filename
        
        return fallback
    
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Left side - Settings (with scrollbar)
        settings_container = ttk.Frame(main_frame)
        settings_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # Create canvas and scrollbar for settings
        canvas = tk.Canvas(settings_container, width=350)
        scrollbar = ttk.Scrollbar(settings_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        settings_frame = ttk.LabelFrame(scrollable_frame, text="Settings", padding="10")
        settings_frame.pack(fill="both", expand=True)
        
        # Right side - Preview
        preview_frame = ttk.LabelFrame(main_frame, text="Live Preview", padding="10")
        preview_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)
        
        # SETTINGS CONTROLS
        row = 0
        
        # ========== MAIN TEXT SETTINGS ==========
        ttk.Label(settings_frame, text="━━━ MAIN TEXT ━━━", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=3, pady=(0, 10))
        row += 1
        
        # Font Size
        ttk.Label(settings_frame, text="Font Size:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.font_size_var = tk.IntVar(value=self.settings['font_size'])
        font_size_slider = ttk.Scale(settings_frame, from_=30, to=80, variable=self.font_size_var, 
                                     orient=tk.HORIZONTAL, command=self.on_setting_change)
        font_size_slider.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.font_size_label = ttk.Label(settings_frame, text=str(self.settings['font_size']))
        self.font_size_label.grid(row=row, column=2, padx=5)
        row += 1
        
        # Font Style
        ttk.Label(settings_frame, text="Font Style:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.font_style_var = tk.StringVar(value=self.settings['font_style'])
        font_styles = list(self.available_fonts.keys())
        font_combo = ttk.Combobox(settings_frame, textvariable=self.font_style_var, values=font_styles, state='readonly', width=20)
        font_combo.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        font_combo.bind('<<ComboboxSelected>>', self.on_setting_change)
        row += 1
        
        # Text Color
        ttk.Label(settings_frame, text="Text Color:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.text_color_btn = tk.Button(settings_frame, text="Choose Color", 
                                        bg=self.settings['text_color'],
                                        command=lambda: self.choose_color('text_color'))
        self.text_color_btn.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Background Color
        ttk.Label(settings_frame, text="BG Color:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.bg_color_btn = tk.Button(settings_frame, text="Choose Color", 
                                      bg=self.settings['bg_color'],
                                      command=lambda: self.choose_color('bg_color'))
        self.bg_color_btn.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Background Opacity
        ttk.Label(settings_frame, text="BG Opacity:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.bg_opacity_var = tk.IntVar(value=self.settings['bg_opacity'])
        opacity_slider = ttk.Scale(settings_frame, from_=50, to=100, variable=self.bg_opacity_var, 
                                   orient=tk.HORIZONTAL, command=self.on_setting_change)
        opacity_slider.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.opacity_label = ttk.Label(settings_frame, text=f"{self.settings['bg_opacity']}%")
        self.opacity_label.grid(row=row, column=2, padx=5)
        row += 1
        
        # Separator
        ttk.Separator(settings_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15)
        row += 1
        
        # ========== EMOJI SETTINGS ==========
        ttk.Label(settings_frame, text="━━━ EMOJI ━━━", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=3, pady=(0, 10))
        row += 1
        
        # Emoji Enable/Disable
        self.emoji_enabled_var = tk.BooleanVar(value=self.settings['emoji_enabled'])
        emoji_check = ttk.Checkbutton(settings_frame, text="Enable Emoji Bubble", 
                                      variable=self.emoji_enabled_var, 
                                      command=self.on_setting_change)
        emoji_check.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=5)
        row += 1
        
        # Emoji Size Multiplier
        ttk.Label(settings_frame, text="Emoji Size:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.emoji_mult_var = tk.DoubleVar(value=self.settings['emoji_size_multiplier'])
        emoji_slider = ttk.Scale(settings_frame, from_=0.8, to=2.0, variable=self.emoji_mult_var, 
                                orient=tk.HORIZONTAL, command=self.on_setting_change)
        emoji_slider.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.emoji_label = ttk.Label(settings_frame, text=f"{self.settings['emoji_size_multiplier']:.1f}x")
        self.emoji_label.grid(row=row, column=2, padx=5)
        row += 1
        
        # Separator
        ttk.Separator(settings_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15)
        row += 1
        
        # ========== CTA SETTINGS ==========
        ttk.Label(settings_frame, text="━━━ CALL TO ACTION (CTA) ━━━", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=3, pady=(0, 10))
        row += 1
        
        # CTA Enable/Disable
        self.cta_enabled_var = tk.BooleanVar(value=self.settings['cta_enabled'])
        cta_check = ttk.Checkbutton(settings_frame, text="Enable CTA Bubble", 
                                    variable=self.cta_enabled_var, 
                                    command=self.on_setting_change)
        cta_check.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=5)
        row += 1
        
        # CTA Font Size
        ttk.Label(settings_frame, text="CTA Font Size:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.cta_font_size_var = tk.IntVar(value=self.settings['cta_font_size'])
        cta_font_size_slider = ttk.Scale(settings_frame, from_=30, to=80, variable=self.cta_font_size_var, 
                                        orient=tk.HORIZONTAL, command=self.on_setting_change)
        cta_font_size_slider.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.cta_font_size_label = ttk.Label(settings_frame, text=str(self.settings['cta_font_size']))
        self.cta_font_size_label.grid(row=row, column=2, padx=5)
        row += 1
        
        # CTA Font Style
        ttk.Label(settings_frame, text="CTA Font Style:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.cta_font_style_var = tk.StringVar(value=self.settings['cta_font_style'])
        cta_font_combo = ttk.Combobox(settings_frame, textvariable=self.cta_font_style_var, 
                                     values=font_styles, state='readonly', width=20)
        cta_font_combo.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        cta_font_combo.bind('<<ComboboxSelected>>', self.on_setting_change)
        row += 1
        
        # CTA Background Color
        ttk.Label(settings_frame, text="CTA BG Color:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.cta_bg_btn = tk.Button(settings_frame, text="Choose Color", 
                                    bg=self.settings['cta_bg_color'],
                                    command=lambda: self.choose_color('cta_bg_color'))
        self.cta_bg_btn.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # CTA Text Color
        ttk.Label(settings_frame, text="CTA Text Color:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.cta_text_btn = tk.Button(settings_frame, text="Choose Color", 
                                      bg=self.settings['cta_text_color'],
                                      command=lambda: self.choose_color('cta_text_color'))
        self.cta_text_btn.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Separator
        ttk.Separator(settings_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15)
        row += 1
        
        # ========== LAYOUT SETTINGS ==========
        ttk.Label(settings_frame, text="━━━ LAYOUT ━━━", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=3, pady=(0, 10))
        row += 1
        
        # Bubble Width
        ttk.Label(settings_frame, text="Bubble Width %:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.bubble_width_var = tk.IntVar(value=self.settings['bubble_width'])
        width_slider = ttk.Scale(settings_frame, from_=60, to=90, variable=self.bubble_width_var, 
                                orient=tk.HORIZONTAL, command=self.on_setting_change)
        width_slider.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.width_label = ttk.Label(settings_frame, text=f"{self.settings['bubble_width']}%")
        self.width_label.grid(row=row, column=2, padx=5)
        row += 1
        
        # Corner Radius
        ttk.Label(settings_frame, text="Corner Radius:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.corner_radius_var = tk.IntVar(value=self.settings['corner_radius'])
        radius_slider = ttk.Scale(settings_frame, from_=5, to=30, variable=self.corner_radius_var, 
                                 orient=tk.HORIZONTAL, command=self.on_setting_change)
        radius_slider.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.radius_label = ttk.Label(settings_frame, text=str(self.settings['corner_radius']))
        self.radius_label.grid(row=row, column=2, padx=5)
        row += 1
        
        # Section Spacing
        ttk.Label(settings_frame, text="Bubble Spacing:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.spacing_var = tk.IntVar(value=self.settings['section_spacing'])
        spacing_slider = ttk.Scale(settings_frame, from_=5, to=30, variable=self.spacing_var, 
                                  orient=tk.HORIZONTAL, command=self.on_setting_change)
        spacing_slider.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.spacing_label = ttk.Label(settings_frame, text=str(self.settings['section_spacing']))
        self.spacing_label.grid(row=row, column=2, padx=5)
        row += 1
        
        # Padding Horizontal
        ttk.Label(settings_frame, text="Padding H:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.padding_h_var = tk.IntVar(value=self.settings['padding_horizontal'])
        padding_h_slider = ttk.Scale(settings_frame, from_=20, to=70, variable=self.padding_h_var, 
                                     orient=tk.HORIZONTAL, command=self.on_setting_change)
        padding_h_slider.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.padding_h_label = ttk.Label(settings_frame, text=str(self.settings['padding_horizontal']))
        self.padding_h_label.grid(row=row, column=2, padx=5)
        row += 1
        
        # Padding Vertical
        ttk.Label(settings_frame, text="Padding V:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.padding_v_var = tk.IntVar(value=self.settings['padding_vertical'])
        padding_v_slider = ttk.Scale(settings_frame, from_=10, to=40, variable=self.padding_v_var, 
                                     orient=tk.HORIZONTAL, command=self.on_setting_change)
        padding_v_slider.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.padding_v_label = ttk.Label(settings_frame, text=str(self.settings['padding_vertical']))
        self.padding_v_label.grid(row=row, column=2, padx=5)
        row += 1
        
        # Position
        ttk.Label(settings_frame, text="Position:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.position_var = tk.StringVar(value=self.settings['position'])
        positions = ['top', 'center', 'bottom']
        pos_combo = ttk.Combobox(settings_frame, textvariable=self.position_var, values=positions, state='readonly')
        pos_combo.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        pos_combo.bind('<<ComboboxSelected>>', self.on_setting_change)
        row += 1
        
        # Buttons frame
        button_frame = ttk.Frame(settings_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="💾 Save Settings", command=self.save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Reset to Default", command=self.reset_settings).pack(side=tk.LEFT, padx=5)
        
        # PREVIEW AREA
        self.preview_canvas = tk.Canvas(preview_frame, width=600, height=700, bg='#1a1a1a')
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Sample text editor
        text_edit_frame = ttk.LabelFrame(preview_frame, text="Edit Sample Text", padding="10")
        text_edit_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(text_edit_frame, text="Main Text:").pack(anchor=tk.W)
        self.main_text_entry = tk.Text(text_edit_frame, height=3, wrap=tk.WORD)
        self.main_text_entry.insert('1.0', self.sample_main_text)
        self.main_text_entry.pack(fill=tk.X, pady=5)
        self.main_text_entry.bind('<KeyRelease>', self.on_text_change)
        
        ttk.Label(text_edit_frame, text="Emojis:").pack(anchor=tk.W)
        self.emoji_entry = ttk.Entry(text_edit_frame)
        self.emoji_entry.insert(0, self.sample_emoji)
        self.emoji_entry.pack(fill=tk.X, pady=5)
        self.emoji_entry.bind('<KeyRelease>', self.on_text_change)
        
        ttk.Label(text_edit_frame, text="CTA:").pack(anchor=tk.W)
        self.cta_entry = ttk.Entry(text_edit_frame)
        self.cta_entry.insert(0, self.sample_cta)
        self.cta_entry.pack(fill=tk.X, pady=5)
        self.cta_entry.bind('<KeyRelease>', self.on_text_change)
    
    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def choose_color(self, setting_key):
        """Open color chooser dialog"""
        color = colorchooser.askcolor(initialcolor=self.settings[setting_key])
        if color[1]:  # If user didn't cancel
            self.settings[setting_key] = color[1]
            
            # Update button color
            if setting_key == 'text_color':
                self.text_color_btn.config(bg=color[1])
            elif setting_key == 'bg_color':
                self.bg_color_btn.config(bg=color[1])
            elif setting_key == 'cta_bg_color':
                self.cta_bg_btn.config(bg=color[1])
            elif setting_key == 'cta_text_color':
                self.cta_text_btn.config(bg=color[1])
            
            self.update_preview()
    
    def on_setting_change(self, event=None):
        """Update settings when slider or dropdown changes"""
        self.settings['font_size'] = self.font_size_var.get()
        self.font_size_label.config(text=str(self.settings['font_size']))
        
        self.settings['bg_opacity'] = self.bg_opacity_var.get()
        self.opacity_label.config(text=f"{self.settings['bg_opacity']}%")
        
        self.settings['bubble_width'] = self.bubble_width_var.get()
        self.width_label.config(text=f"{self.settings['bubble_width']}%")
        
        self.settings['corner_radius'] = self.corner_radius_var.get()
        self.radius_label.config(text=str(self.settings['corner_radius']))
        
        self.settings['section_spacing'] = self.spacing_var.get()
        self.spacing_label.config(text=str(self.settings['section_spacing']))
        
        self.settings['padding_horizontal'] = self.padding_h_var.get()
        self.padding_h_label.config(text=str(self.settings['padding_horizontal']))
        
        self.settings['padding_vertical'] = self.padding_v_var.get()
        self.padding_v_label.config(text=str(self.settings['padding_vertical']))
        
        self.settings['emoji_size_multiplier'] = round(self.emoji_mult_var.get(), 1)
        self.emoji_label.config(text=f"{self.settings['emoji_size_multiplier']:.1f}x")
        
        self.settings['emoji_enabled'] = self.emoji_enabled_var.get()
        self.settings['cta_enabled'] = self.cta_enabled_var.get()
        
        self.settings['cta_font_size'] = self.cta_font_size_var.get()
        self.cta_font_size_label.config(text=str(self.settings['cta_font_size']))
        
        self.settings['font_style'] = self.font_style_var.get()
        self.settings['cta_font_style'] = self.cta_font_style_var.get()
        self.settings['position'] = self.position_var.get()
        
        self.update_preview()
    
    def on_text_change(self, event=None):
        """Update preview when sample text changes"""
        self.sample_main_text = self.main_text_entry.get('1.0', tk.END).strip()
        self.sample_emoji = self.emoji_entry.get()
        self.sample_cta = self.cta_entry.get()
        self.update_preview()
    
    def update_preview(self):
        """Generate and display preview image"""
        preview_width = 540
        preview_height = 960
        
        img = Image.new('RGB', (preview_width, preview_height), color='#2a4a5a')
        draw = ImageDraw.Draw(img, 'RGBA')
        
        # Add background gradient
        for i in range(0, preview_height, 40):
            draw.rectangle([(0, i), (preview_width, i+20)], fill=(42 + i//20, 74 + i//40, 90 + i//30))
        
        # Get fonts
        font_size = self.settings['font_size']
        cta_font_size = self.settings['cta_font_size']
        
        try:
            # Main font - use full path from available_fonts
            main_font_file = self.available_fonts.get(self.settings['font_style'], 'arialbd.ttf')
            main_font = ImageFont.truetype(main_font_file, font_size)
            
            # Emoji font
            emoji_font_path = str(Path(r"C:\Windows\Fonts") / 'seguiemj.ttf')
            emoji_font = ImageFont.truetype(emoji_font_path, int(font_size * self.settings['emoji_size_multiplier']))
            
            # CTA font - use full path from available_fonts
            cta_font_file = self.available_fonts.get(self.settings['cta_font_style'], 'ariali.ttf')
            cta_font = ImageFont.truetype(cta_font_file, cta_font_size)
        except Exception as e:
            print(f"Font loading error: {e}")
            main_font = ImageFont.load_default()
            emoji_font = main_font
            cta_font = main_font
        
        # Word wrap
        max_width = int(preview_width * (self.settings['bubble_width'] / 100))
        words = self.sample_main_text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=main_font)
            if bbox[2] - bbox[0] <= max_width - 60:
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
        sections.append((main_text_wrapped, main_font, True, 'main'))
        
        if self.settings['emoji_enabled'] and self.sample_emoji:
            sections.append((self.sample_emoji, emoji_font, False, 'emoji'))
        
        if self.settings['cta_enabled'] and self.sample_cta:
            sections.append((self.sample_cta, cta_font, False, 'cta'))
        
        section_boxes = []
        for text, font, is_multiline, section_type in sections:
            if is_multiline:
                bbox = draw.multiline_textbbox((0, 0), text, font=font, align='center')
            else:
                bbox = draw.textbbox((0, 0), text, font=font)
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
        
        # Starting Y position
        if self.settings['position'] == 'top':
            current_y = 30
        elif self.settings['position'] == 'center':
            current_y = (preview_height - total_height) // 2
        else:  # bottom
            current_y = preview_height - total_height - 30
        
        # Draw bubbles
        for box_info in section_boxes:
            text = box_info['text']
            font = box_info['font']
            is_multiline = box_info['is_multiline']
            section_type = box_info['type']
            
            if section_type == 'cta':
                bg_rgb = self.hex_to_rgb(self.settings['cta_bg_color'])
                bg_color = bg_rgb + (255,)
                txt_color = self.settings['cta_text_color']
            else:
                bg_rgb = self.hex_to_rgb(self.settings['bg_color'])
                alpha = int(255 * (self.settings['bg_opacity'] / 100))
                bg_color = bg_rgb + (alpha,)
                txt_color = self.settings['text_color']
            
            bubble_width = box_info['width'] + (self.settings['padding_horizontal'] * 2)
            bubble_height = box_info['height'] + (self.settings['inner_padding'] * 2)
            bubble_x = (preview_width - bubble_width) // 2
            
            draw.rounded_rectangle(
                [(bubble_x, current_y), (bubble_x + bubble_width, current_y + bubble_height)],
                radius=self.settings['corner_radius'],
                fill=bg_color
            )
            
            if is_multiline:
                text_x = bubble_x + (bubble_width // 2)
                text_y = current_y + self.settings['inner_padding']
                draw.multiline_text(
                    (text_x, text_y),
                    text,
                    font=font,
                    fill=txt_color,
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
                    fill=txt_color,
                    anchor='mm'
                )
            
            current_y += bubble_height + self.settings['section_spacing']
        
        # Display
        img_resized = img.resize((540, 810), Image.Resampling.LANCZOS)
        self.preview_image = ImageTk.PhotoImage(img_resized)
        self.preview_canvas.delete('all')
        self.preview_canvas.create_image(300, 405, image=self.preview_image)
    
    def save_settings(self):
        """Save settings to file"""
        settings_file = Path('overlay_settings.json')
        
        # Add font file paths to settings
        settings_to_save = self.settings.copy()
        settings_to_save['font_file'] = self.available_fonts.get(self.settings['font_style'], 'arialbd.ttf')
        settings_to_save['cta_font_file'] = self.available_fonts.get(self.settings.get('cta_font_style', 'Arial Italic'), 'ariali.ttf')
        
        with open(settings_file, 'w') as f:
            json.dump(settings_to_save, f, indent=2)
        messagebox.showinfo("Success", "✓ Settings saved successfully!\n\nNow run process_videos.bat to apply these settings to your videos.")
    
    def load_settings(self):
        """Load settings from file"""
        settings_file = Path('overlay_settings.json')
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)
            except (json.JSONDecodeError, FileNotFoundError, IOError, KeyError) as e:
                print(f"Warning: Could not load settings from {settings_file}: {e}")
                print("Using default settings instead.")
    
    def reset_settings(self):
        """Reset to default settings"""
        self.settings = {
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
        
        # Update UI
        self.font_size_var.set(self.settings['font_size'])
        self.font_style_var.set(self.settings['font_style'])
        self.bg_opacity_var.set(self.settings['bg_opacity'])
        self.bubble_width_var.set(self.settings['bubble_width'])
        self.corner_radius_var.set(self.settings['corner_radius'])
        self.spacing_var.set(self.settings['section_spacing'])
        self.padding_h_var.set(self.settings['padding_horizontal'])
        self.padding_v_var.set(self.settings['padding_vertical'])
        self.emoji_mult_var.set(self.settings['emoji_size_multiplier'])
        self.emoji_enabled_var.set(self.settings['emoji_enabled'])
        self.cta_enabled_var.set(self.settings['cta_enabled'])
        self.cta_font_size_var.set(self.settings['cta_font_size'])
        self.cta_font_style_var.set(self.settings['cta_font_style'])
        self.position_var.set(self.settings['position'])
        
        self.text_color_btn.config(bg=self.settings['text_color'])
        self.bg_color_btn.config(bg=self.settings['bg_color'])
        self.cta_bg_btn.config(bg=self.settings['cta_bg_color'])
        self.cta_text_btn.config(bg=self.settings['cta_text_color'])
        
        self.update_preview()
        messagebox.showinfo("Reset", "Settings reset to default values")


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoOverlayGUI(root)
    root.mainloop()