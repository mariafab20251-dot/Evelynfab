"""
Complete Video Automation GUI - All Settings + Processing in One Window
Configure everything and process videos without touching console
"""

import tkinter as tk
from tkinter import ttk, colorchooser, messagebox, filedialog, scrolledtext
import json
from pathlib import Path
import threading
import sys
import os

# Import the automation class
sys.path.insert(0, str(Path(__file__).parent))


class UnifiedVideoAutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Complete Video Automation - Settings & Processing")
        self.root.geometry("1000x800")

        self.settings = self.load_settings()
        self.available_fonts = self.get_system_fonts()
        self.processing = False

        self.setup_ui()

    def get_system_fonts(self):
        """Get available system fonts"""
        fonts_dict = {}
        fonts_folder = Path(r"C:\Windows\Fonts")

        if not fonts_folder.exists():
            return {'Arial': 'arial.ttf', 'Arial Bold': 'arialbd.ttf'}

        try:
            for font_file in fonts_folder.glob("*.ttf"):
                font_name = font_file.stem
                display_name = font_name

                if font_name.endswith('bd'):
                    display_name = font_name[:-2] + ' Bold'
                elif font_name.endswith('bi'):
                    display_name = font_name[:-2] + ' Bold Italic'
                elif font_name.endswith('i'):
                    display_name = font_name[:-1] + ' Italic'

                display_name = ' '.join(word.capitalize() for word in display_name.split())
                fonts_dict[display_name] = str(font_file)

            return fonts_dict if fonts_dict else {'Arial': 'arial.ttf'}
        except:
            return {'Arial': 'arial.ttf', 'Arial Bold': 'arialbd.ttf'}

    def load_settings(self):
        """Load settings from JSON"""
        settings_file = Path('overlay_settings.json')
        if settings_file.exists():
            with open(settings_file, 'r') as f:
                return json.load(f)
        return {}

    def save_settings(self):
        """Save all settings to JSON"""
        with open('overlay_settings.json', 'w') as f:
            json.dump(self.settings, f, indent=2)
        self.log("✓ Settings saved to overlay_settings.json\n")

    def setup_ui(self):
        """Create the complete UI"""
        # Main notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Tab 1: Text & Basic Settings
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="📝 Text Settings")
        self.setup_text_settings(tab1)

        # Tab 2: Text Effects
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="✨ Text Effects")
        self.setup_text_effects(tab2)

        # Tab 3: Video Effects
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="🎬 Video Effects")
        self.setup_video_effects(tab3)

        # Tab 4: Audio Settings
        tab4 = ttk.Frame(notebook)
        notebook.add(tab4, text="🔊 Audio")
        self.setup_audio_settings(tab4)

        # Tab 5: Processing & Output
        tab5 = ttk.Frame(notebook)
        notebook.add(tab5, text="▶️ Process Videos")
        self.setup_processing(tab5)

        # Bottom control bar
        control_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        control_frame.pack(fill='x', side='bottom')
        control_frame.pack_propagate(False)

        save_btn = tk.Button(control_frame, text="💾 Save Settings",
                            command=self.save_settings,
                            bg='#3498db', fg='white',
                            font=('Arial', 11, 'bold'),
                            padx=20, pady=10)
        save_btn.pack(side='left', padx=10, pady=10)

        self.process_btn = tk.Button(control_frame, text="▶️ Start Processing",
                                     command=self.start_processing,
                                     bg='#27ae60', fg='white',
                                     font=('Arial', 11, 'bold'),
                                     padx=20, pady=10)
        self.process_btn.pack(side='left', padx=10, pady=10)

        stop_btn = tk.Button(control_frame, text="⏹️ Stop",
                            command=self.stop_processing,
                            bg='#e74c3c', fg='white',
                            font=('Arial', 11, 'bold'),
                            padx=20, pady=10)
        stop_btn.pack(side='left', padx=10, pady=10)

    def setup_text_settings(self, parent):
        """Text and CTA settings"""
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        frame = ttk.Frame(canvas)

        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Main text settings
        ttk.Label(frame, text="Main Text Settings", font=('Arial', 12, 'bold')).pack(anchor='w', padx=20, pady=(20,10))

        ttk.Label(frame, text="Font:").pack(anchor='w', padx=20)
        font_combo = ttk.Combobox(frame, values=list(self.available_fonts.keys()), width=40)
        font_combo.set(self.settings.get('font_style', 'Arial Bold'))
        font_combo.bind('<<ComboboxSelected>>', lambda e: self.update_font('font_style', 'font_file', font_combo.get()))
        font_combo.pack(anchor='w', padx=20, pady=5)

        ttk.Label(frame, text="Font Size:").pack(anchor='w', padx=20)
        size_scale = tk.Scale(frame, from_=20, to=100, orient='horizontal',
                             command=lambda v: self.update_setting('font_size', int(v)))
        size_scale.set(self.settings.get('font_size', 45))
        size_scale.pack(fill='x', padx=20)

        ttk.Label(frame, text="Text Color:").pack(anchor='w', padx=20)
        color_frame = tk.Frame(frame)
        color_frame.pack(anchor='w', padx=20, pady=5)
        self.text_color_btn = tk.Button(color_frame, text="     ", bg=self.settings.get('text_color', '#000000'),
                                       command=lambda: self.pick_color('text_color', self.text_color_btn))
        self.text_color_btn.pack(side='left')

        ttk.Label(frame, text="Background Color:").pack(anchor='w', padx=20)
        bg_frame = tk.Frame(frame)
        bg_frame.pack(anchor='w', padx=20, pady=5)
        self.bg_color_btn = tk.Button(bg_frame, text="     ", bg=self.settings.get('bg_color', '#ffffff'),
                                     command=lambda: self.pick_color('bg_color', self.bg_color_btn))
        self.bg_color_btn.pack(side='left')

        ttk.Label(frame, text="Background Opacity (%):").pack(anchor='w', padx=20)
        opacity_scale = tk.Scale(frame, from_=0, to=100, orient='horizontal',
                                command=lambda v: self.update_setting('bg_opacity', int(v)))
        opacity_scale.set(self.settings.get('bg_opacity', 90))
        opacity_scale.pack(fill='x', padx=20)

        ttk.Label(frame, text="Position:").pack(anchor='w', padx=20, pady=(10,5))
        pos_var = tk.StringVar(value=self.settings.get('position', 'top'))
        for pos in ['top', 'center', 'bottom']:
            rb = ttk.Radiobutton(frame, text=pos.capitalize(), variable=pos_var, value=pos,
                               command=lambda: self.update_setting('position', pos_var.get()))
            rb.pack(anchor='w', padx=40)

        # CTA Settings
        ttk.Label(frame, text="CTA (Call-to-Action) Settings", font=('Arial', 12, 'bold')).pack(anchor='w', padx=20, pady=(20,10))

        cta_var = tk.BooleanVar(value=self.settings.get('cta_enabled', True))
        ttk.Checkbutton(frame, text="Enable CTA", variable=cta_var,
                       command=lambda: self.update_setting('cta_enabled', cta_var.get())).pack(anchor='w', padx=20)

        ttk.Label(frame, text="CTA Font Size:").pack(anchor='w', padx=20)
        cta_size = tk.Scale(frame, from_=20, to=80, orient='horizontal',
                           command=lambda v: self.update_setting('cta_font_size', int(v)))
        cta_size.set(self.settings.get('cta_font_size', 43))
        cta_size.pack(fill='x', padx=20)

        ttk.Label(frame, text="CTA Background Color:").pack(anchor='w', padx=20)
        cta_bg_frame = tk.Frame(frame)
        cta_bg_frame.pack(anchor='w', padx=20, pady=5)
        self.cta_bg_btn = tk.Button(cta_bg_frame, text="     ", bg=self.settings.get('cta_bg_color', '#00ff40'),
                                   command=lambda: self.pick_color('cta_bg_color', self.cta_bg_btn))
        self.cta_bg_btn.pack(side='left')

        # Emoji Settings
        ttk.Label(frame, text="Emoji Settings", font=('Arial', 12, 'bold')).pack(anchor='w', padx=20, pady=(20,10))

        emoji_var = tk.BooleanVar(value=self.settings.get('emoji_enabled', True))
        ttk.Checkbutton(frame, text="Enable Emoji", variable=emoji_var,
                       command=lambda: self.update_setting('emoji_enabled', emoji_var.get())).pack(anchor='w', padx=20)

        ttk.Label(frame, text="Emoji Size Multiplier:").pack(anchor='w', padx=20)
        emoji_size = tk.Scale(frame, from_=0.5, to=2.0, resolution=0.1, orient='horizontal',
                             command=lambda v: self.update_setting('emoji_size_multiplier', float(v)))
        emoji_size.set(self.settings.get('emoji_size_multiplier', 1.2))
        emoji_size.pack(fill='x', padx=20, pady=(5,20))

    def setup_text_effects(self, parent):
        """Text animation and effects"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Text Animations", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0,10))

        fade_var = tk.BooleanVar(value=self.settings.get('text_fade_in', True))
        ttk.Checkbutton(frame, text="Fade In", variable=fade_var,
                       command=lambda: self.update_setting('text_fade_in', fade_var.get())).pack(anchor='w')

        ttk.Label(frame, text="Fade Duration (seconds):").pack(anchor='w', padx=20)
        fade_dur = tk.Scale(frame, from_=0.1, to=1.0, resolution=0.1, orient='horizontal',
                           command=lambda v: self.update_setting('text_fade_duration', float(v)))
        fade_dur.set(self.settings.get('text_fade_duration', 0.4))
        fade_dur.pack(fill='x', padx=20, pady=(0,10))

        slide_var = tk.BooleanVar(value=self.settings.get('text_slide_up', False))
        ttk.Checkbutton(frame, text="Slide Up", variable=slide_var,
                       command=lambda: self.update_setting('text_slide_up', slide_var.get())).pack(anchor='w')

        bounce_var = tk.BooleanVar(value=self.settings.get('text_bounce', False))
        ttk.Checkbutton(frame, text="Bounce", variable=bounce_var,
                       command=lambda: self.update_setting('text_bounce', bounce_var.get())).pack(anchor='w')

        ttk.Label(frame, text="Text Styling", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(20,10))

        glow_var = tk.BooleanVar(value=self.settings.get('text_glow', True))
        ttk.Checkbutton(frame, text="Text Glow", variable=glow_var,
                       command=lambda: self.update_setting('text_glow', glow_var.get())).pack(anchor='w')

        ttk.Label(frame, text="Glow Intensity:").pack(anchor='w', padx=20)
        glow_int = tk.Scale(frame, from_=1, to=20, orient='horizontal',
                           command=lambda v: self.update_setting('glow_intensity', int(v)))
        glow_int.set(self.settings.get('glow_intensity', 8))
        glow_int.pack(fill='x', padx=20, pady=(0,10))

        shadow_var = tk.BooleanVar(value=self.settings.get('drop_shadow', True))
        ttk.Checkbutton(frame, text="Drop Shadow", variable=shadow_var,
                       command=lambda: self.update_setting('drop_shadow', shadow_var.get())).pack(anchor='w')

        neon_var = tk.BooleanVar(value=self.settings.get('neon_glow', False))
        ttk.Checkbutton(frame, text="Neon Glow", variable=neon_var,
                       command=lambda: self.update_setting('neon_glow', neon_var.get())).pack(anchor='w')

    def setup_video_effects(self, parent):
        """Video effects settings"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Visual Effects", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0,10))

        vig_var = tk.BooleanVar(value=self.settings.get('vignette', True))
        ttk.Checkbutton(frame, text="Vignette (darkened edges)", variable=vig_var,
                       command=lambda: self.update_setting('vignette', vig_var.get())).pack(anchor='w')

        ttk.Label(frame, text="Vignette Intensity:").pack(anchor='w', padx=20)
        vig_int = tk.Scale(frame, from_=0.1, to=1.0, resolution=0.1, orient='horizontal',
                          command=lambda v: self.update_setting('vignette_intensity', float(v)))
        vig_int.set(self.settings.get('vignette_intensity', 0.4))
        vig_int.pack(fill='x', padx=20, pady=(0,10))

        dim_var = tk.BooleanVar(value=self.settings.get('background_dim', True))
        ttk.Checkbutton(frame, text="Background Dim", variable=dim_var,
                       command=lambda: self.update_setting('background_dim', dim_var.get())).pack(anchor='w')

        grain_var = tk.BooleanVar(value=self.settings.get('film_grain', False))
        ttk.Checkbutton(frame, text="Film Grain", variable=grain_var,
                       command=lambda: self.update_setting('film_grain', grain_var.get())).pack(anchor='w', pady=(0,10))

        ttk.Label(frame, text="Color Grading:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10,5))
        grade_var = tk.StringVar(value=self.settings.get('color_grade', 'warm'))

        for text, value in [('None', 'none'), ('Warm', 'warm'), ('Cold', 'cold'), ('Cinematic', 'cinematic'), ('Vintage', 'vintage')]:
            rb = ttk.Radiobutton(frame, text=text, variable=grade_var, value=value,
                               command=lambda: self.update_setting('color_grade', grade_var.get()))
            rb.pack(anchor='w', padx=20)

        ttk.Label(frame, text="Motion Effects", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(20,10))

        zoom_var = tk.BooleanVar(value=self.settings.get('video_zoom', True))
        ttk.Checkbutton(frame, text="Slow Zoom", variable=zoom_var,
                       command=lambda: self.update_setting('video_zoom', zoom_var.get())).pack(anchor='w')

        ttk.Label(frame, text="Zoom Scale:").pack(anchor='w', padx=20)
        zoom_scale = tk.Scale(frame, from_=1.0, to=1.2, resolution=0.01, orient='horizontal',
                             command=lambda v: self.update_setting('zoom_scale', float(v)))
        zoom_scale.set(self.settings.get('zoom_scale', 1.08))
        zoom_scale.pack(fill='x', padx=20)

    def setup_audio_settings(self, parent):
        """Audio settings"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Audio Settings", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0,10))

        mute_var = tk.BooleanVar(value=self.settings.get('mute_original_audio', False))
        ttk.Checkbutton(frame, text="Mute Original Video Audio", variable=mute_var,
                       command=lambda: self.update_setting('mute_original_audio', mute_var.get())).pack(anchor='w', pady=5)

        ttk.Label(frame, text="Background Music (BGM)", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(15,5))

        bgm_var = tk.BooleanVar(value=self.settings.get('add_custom_bgm', False))
        ttk.Checkbutton(frame, text="Add Custom BGM", variable=bgm_var,
                       command=lambda: self.update_setting('add_custom_bgm', bgm_var.get())).pack(anchor='w')

        ttk.Label(frame, text="BGM File/Folder:", font=('Arial', 9)).pack(anchor='w', padx=20, pady=(5,0))
        ttk.Label(frame, text="(Single file = same BGM all videos | Folder = random BGM per video)",
                 font=('Arial', 8), foreground='gray').pack(anchor='w', padx=20)

        bgm_frame = tk.Frame(frame)
        bgm_frame.pack(fill='x', padx=20, pady=5)

        self.bgm_var = tk.StringVar(value=self.settings.get('bgm_file', ''))
        bgm_entry = ttk.Entry(bgm_frame, textvariable=self.bgm_var, width=40)
        bgm_entry.pack(side='left', fill='x', expand=True)

        ttk.Button(bgm_frame, text="Browse File", command=self.browse_bgm_file).pack(side='left', padx=2)
        ttk.Button(bgm_frame, text="Browse Folder", command=self.browse_bgm_folder).pack(side='left', padx=2)

        ttk.Label(frame, text="BGM Volume:").pack(anchor='w', padx=20)
        bgm_vol = tk.Scale(frame, from_=0.0, to=1.0, resolution=0.1, orient='horizontal',
                          command=lambda v: self.update_setting('bgm_volume', float(v)))
        bgm_vol.set(self.settings.get('bgm_volume', 0.3))
        bgm_vol.pack(fill='x', padx=20)

        bgm_loop_var = tk.BooleanVar(value=self.settings.get('bgm_loop', True))
        ttk.Checkbutton(frame, text="Loop BGM", variable=bgm_loop_var,
                       command=lambda: self.update_setting('bgm_loop', bgm_loop_var.get())).pack(anchor='w', padx=20)

        ttk.Label(frame, text="Voiceover", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(15,5))

        vo_var = tk.BooleanVar(value=self.settings.get('add_voiceover', False))
        ttk.Checkbutton(frame, text="Add Voiceover", variable=vo_var,
                       command=lambda: self.update_setting('add_voiceover', vo_var.get())).pack(anchor='w')

        ttk.Label(frame, text="Voiceover Folder:", font=('Arial', 9)).pack(anchor='w', padx=20, pady=(5,0))
        ttk.Label(frame, text="(Files named: 1.mp3, 2.mp3, 3.mp3... matching video order)",
                 font=('Arial', 8), foreground='gray').pack(anchor='w', padx=20)

        vo_frame = tk.Frame(frame)
        vo_frame.pack(fill='x', padx=20, pady=5)

        self.vo_var = tk.StringVar(value=self.settings.get('voiceover_folder', ''))
        vo_entry = ttk.Entry(vo_frame, textvariable=self.vo_var, width=40)
        vo_entry.pack(side='left', fill='x', expand=True)

        ttk.Button(vo_frame, text="Browse", command=self.browse_voiceover).pack(side='left', padx=5)

        ttk.Label(frame, text="Voiceover Volume:").pack(anchor='w', padx=20)
        vo_vol = tk.Scale(frame, from_=0.0, to=1.0, resolution=0.1, orient='horizontal',
                         command=lambda v: self.update_setting('voiceover_volume', float(v)))
        vo_vol.set(self.settings.get('voiceover_volume', 1.0))
        vo_vol.pack(fill='x', padx=20)

    def setup_processing(self, parent):
        """Processing tab with file selection and progress"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Video Processing", font=('Arial', 14, 'bold')).pack(anchor='w', pady=(0,15))

        # Input video folder
        ttk.Label(frame, text="Video Folder:", font=('Arial', 10, 'bold')).pack(anchor='w')
        video_frame = tk.Frame(frame)
        video_frame.pack(fill='x', pady=5)

        self.video_folder_var = tk.StringVar(value=r"E:\MyAutomations\ScriptAutomations\VideoFolder\SourceVideosToEdit\Libriana8")
        video_entry = ttk.Entry(video_frame, textvariable=self.video_folder_var, width=60)
        video_entry.pack(side='left', fill='x', expand=True)
        ttk.Button(video_frame, text="Browse", command=self.browse_video_folder).pack(side='left', padx=5)

        # Quotes file
        ttk.Label(frame, text="Quotes File:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10,0))
        quotes_frame = tk.Frame(frame)
        quotes_frame.pack(fill='x', pady=5)

        self.quotes_file_var = tk.StringVar(value=r"E:\MyAutomations\ScriptAutomations\VideoFolder\Quotes.txt")
        quotes_entry = ttk.Entry(quotes_frame, textvariable=self.quotes_file_var, width=60)
        quotes_entry.pack(side='left', fill='x', expand=True)
        ttk.Button(quotes_frame, text="Browse", command=self.browse_quotes_file).pack(side='left', padx=5)

        # Output folder
        ttk.Label(frame, text="Output Folder:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10,0))
        output_frame = tk.Frame(frame)
        output_frame.pack(fill='x', pady=5)

        self.output_folder_var = tk.StringVar(value=r"E:\MyAutomations\ScriptAutomations\VideoFolder\FinalVideos")
        output_entry = ttk.Entry(output_frame, textvariable=self.output_folder_var, width=60)
        output_entry.pack(side='left', fill='x', expand=True)
        ttk.Button(output_frame, text="Browse", command=self.browse_output_folder).pack(side='left', padx=5)

        # Progress section
        ttk.Label(frame, text="Progress:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(20,5))

        self.progress_var = tk.StringVar(value="Ready to process")
        ttk.Label(frame, textvariable=self.progress_var).pack(anchor='w')

        self.progress_bar = ttk.Progressbar(frame, mode='determinate', length=400)
        self.progress_bar.pack(fill='x', pady=10)

        # Log output
        ttk.Label(frame, text="Log:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10,5))
        self.log_text = scrolledtext.ScrolledText(frame, height=12, width=80, wrap=tk.WORD)
        self.log_text.pack(fill='both', expand=True)

    def browse_bgm_file(self):
        """Browse for single BGM file"""
        filename = filedialog.askopenfilename(title="Select BGM File", filetypes=[("Audio", "*.mp3 *.wav *.m4a *.aac *.ogg")])
        if filename:
            self.bgm_var.set(filename)
            self.update_setting('bgm_file', filename)

    def browse_bgm_folder(self):
        """Browse for BGM folder (random selection)"""
        folder = filedialog.askdirectory(title="Select BGM Folder (for random BGM per video)")
        if folder:
            self.bgm_var.set(folder)
            self.update_setting('bgm_file', folder)

    def browse_voiceover(self):
        folder = filedialog.askdirectory(title="Select Voiceover Folder")
        if folder:
            self.vo_var.set(folder)
            self.update_setting('voiceover_folder', folder)

    def browse_video_folder(self):
        folder = filedialog.askdirectory(title="Select Video Folder")
        if folder:
            self.video_folder_var.set(folder)

    def browse_quotes_file(self):
        filename = filedialog.askopenfilename(title="Select Quotes File", filetypes=[("Text", "*.txt")])
        if filename:
            self.quotes_file_var.set(filename)

    def browse_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder_var.set(folder)

    def update_setting(self, key, value):
        self.settings[key] = value

    def update_font(self, style_key, file_key, font_name):
        self.settings[style_key] = font_name
        if font_name in self.available_fonts:
            self.settings[file_key] = self.available_fonts[font_name]

    def pick_color(self, key, button):
        color = colorchooser.askcolor(title=f"Choose {key}")[1]
        if color:
            self.settings[key] = color
            button.config(bg=color)

    def log(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.root.update()

    def start_processing(self):
        """Start video processing in background thread"""
        if self.processing:
            messagebox.showwarning("Processing", "Already processing videos!")
            return

        # Save settings first
        self.save_settings()

        # Start processing thread
        self.processing = True
        self.process_btn.config(state='disabled', bg='#95a5a6')
        thread = threading.Thread(target=self.process_videos, daemon=True)
        thread.start()

    def stop_processing(self):
        """Stop processing"""
        self.processing = False
        self.process_btn.config(state='normal', bg='#27ae60')
        self.log("⏹️ Processing stopped by user\n")

    def process_videos(self):
        """Process videos using the automation class"""
        try:
            from youtube_video_automation_enhanced import VideoQuoteAutomation

            # Update paths in automation
            self.log("="*70 + "\n")
            self.log("🚀 Starting Enhanced Video Processing\n")
            self.log("="*70 + "\n")

            # Create custom automation instance
            automation = VideoQuoteAutomation()
            automation.video_folder = Path(self.video_folder_var.get())
            automation.quotes_file = Path(self.quotes_file_var.get())
            automation.output_folder = Path(self.output_folder_var.get())
            automation.output_folder.mkdir(parents=True, exist_ok=True)

            # Reload settings
            automation.settings = self.settings

            # Get videos and quotes
            videos = automation.get_video_files()
            quotes = automation.read_quotes()

            if not videos:
                self.log("✗ No videos found!\n")
                self.processing = False
                self.process_btn.config(state='normal', bg='#27ae60')
                return

            if not quotes:
                self.log("✗ No quotes found!\n")
                self.processing = False
                self.process_btn.config(state='normal', bg='#27ae60')
                return

            num_to_process = min(len(videos), len(quotes))
            self.progress_bar['maximum'] = num_to_process

            self.log(f"\n📊 Found {len(videos)} videos and {len(quotes)} quotes\n")
            self.log(f"🎬 Processing {num_to_process} videos...\n\n")

            # Process each video
            for i in range(num_to_process):
                if not self.processing:
                    break

                video_path = videos[i]
                quote = quotes[i]

                self.progress_var.set(f"Processing {i+1}/{num_to_process}: {video_path.name}")
                self.progress_bar['value'] = i

                self.log(f"▶️ Video {i+1}/{num_to_process}: {video_path.name}\n")
                self.log(f"📝 Quote: {quote[:60]}...\n")

                try:
                    output_path, filename = automation.add_quote_to_video(video_path, quote, video_index=i)
                    self.log(f"✅ Saved: {filename}\n\n")
                except Exception as e:
                    self.log(f"❌ Error: {str(e)}\n\n")

            self.progress_bar['value'] = num_to_process
            self.progress_var.set("✅ Processing complete!")
            self.log("="*70 + "\n")
            self.log("🎉 ALL PROCESSING COMPLETE!\n")
            self.log("="*70 + "\n")

            messagebox.showinfo("Success", f"Processed {num_to_process} videos successfully!")

        except Exception as e:
            self.log(f"❌ Critical Error: {str(e)}\n")
            messagebox.showerror("Error", f"Processing failed: {str(e)}")

        finally:
            self.processing = False
            self.process_btn.config(state='normal', bg='#27ae60')


if __name__ == "__main__":
    root = tk.Tk()
    app = UnifiedVideoAutomationGUI(root)
    root.mainloop()
