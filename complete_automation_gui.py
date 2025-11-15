"""
Complete Video Automation GUI - Professional Modern Design
All Settings + Processing in One Window
"""

import tkinter as tk
from tkinter import ttk, colorchooser, messagebox, filedialog, scrolledtext
import json
from pathlib import Path
import threading
import sys
import os

sys.path.insert(0, str(Path(__file__).parent))


class ModernStyles:
    """Modern color scheme and styling"""
    # Colors
    BG_PRIMARY = '#1e293b'        # Dark slate
    BG_SECONDARY = '#334155'      # Lighter slate
    BG_CARD = '#475569'           # Card background
    TEXT_PRIMARY = '#f8fafc'      # White
    TEXT_SECONDARY = '#cbd5e1'    # Light gray
    ACCENT_BLUE = '#3b82f6'       # Blue
    ACCENT_GREEN = '#10b981'      # Green
    ACCENT_RED = '#ef4444'        # Red
    ACCENT_PURPLE = '#8b5cf6'     # Purple
    ACCENT_ORANGE = '#f59e0b'     # Orange

    # Fonts
    FONT_TITLE = ('Segoe UI', 14, 'bold')
    FONT_HEADING = ('Segoe UI', 11, 'bold')
    FONT_NORMAL = ('Segoe UI', 10)
    FONT_SMALL = ('Segoe UI', 9)


class UnifiedVideoAutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 Video Automation Studio - Professional Edition")
        self.root.geometry("1100x850")
        self.root.configure(bg=ModernStyles.BG_PRIMARY)

        self.settings = self.load_settings()
        self.available_fonts = self.get_system_fonts()
        self.processing = False

        self.setup_styles()
        self.setup_ui()

    def setup_styles(self):
        """Setup modern ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure notebook
        style.configure('TNotebook', background=ModernStyles.BG_PRIMARY, borderwidth=0)
        style.configure('TNotebook.Tab',
                       background=ModernStyles.BG_SECONDARY,
                       foreground=ModernStyles.TEXT_SECONDARY,
                       padding=[20, 10],
                       font=ModernStyles.FONT_NORMAL)
        style.map('TNotebook.Tab',
                 background=[('selected', ModernStyles.BG_CARD)],
                 foreground=[('selected', ModernStyles.TEXT_PRIMARY)])

        # Configure frames
        style.configure('Card.TFrame', background=ModernStyles.BG_CARD)
        style.configure('TFrame', background=ModernStyles.BG_SECONDARY)

        # Configure labels
        style.configure('TLabel',
                       background=ModernStyles.BG_SECONDARY,
                       foreground=ModernStyles.TEXT_PRIMARY,
                       font=ModernStyles.FONT_NORMAL)
        style.configure('Heading.TLabel',
                       font=ModernStyles.FONT_HEADING,
                       foreground=ModernStyles.ACCENT_BLUE)
        style.configure('Small.TLabel',
                       font=ModernStyles.FONT_SMALL,
                       foreground=ModernStyles.TEXT_SECONDARY)

        # Configure checkbuttons
        style.configure('TCheckbutton',
                       background=ModernStyles.BG_SECONDARY,
                       foreground=ModernStyles.TEXT_PRIMARY,
                       font=ModernStyles.FONT_NORMAL)

        # Configure radiobuttons
        style.configure('TRadiobutton',
                       background=ModernStyles.BG_SECONDARY,
                       foreground=ModernStyles.TEXT_PRIMARY,
                       font=ModernStyles.FONT_NORMAL)

        # Configure entry
        style.configure('TEntry',
                       fieldbackground='#1e293b',
                       foreground=ModernStyles.TEXT_PRIMARY,
                       borderwidth=1)

        # Configure combobox
        style.configure('TCombobox',
                       fieldbackground='#1e293b',
                       background=ModernStyles.BG_SECONDARY,
                       foreground=ModernStyles.TEXT_PRIMARY)

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
        self.log("✅ Settings saved successfully\n", ModernStyles.ACCENT_GREEN)

    def create_section_header(self, parent, text, emoji, color):
        """Create a modern section header"""
        header_frame = tk.Frame(parent, bg=color, height=3)
        header_frame.pack(fill='x', pady=(0, 15))

        label = tk.Label(header_frame, text=f"{emoji}  {text}",
                        bg=color, fg=ModernStyles.TEXT_PRIMARY,
                        font=ModernStyles.FONT_HEADING, pady=10)
        label.pack(fill='x', padx=15)

    def setup_ui(self):
        """Create the complete UI"""
        # Header
        header = tk.Frame(self.root, bg=ModernStyles.ACCENT_BLUE, height=70)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)

        title = tk.Label(header, text="🎬 Video Automation Studio",
                        bg=ModernStyles.ACCENT_BLUE, fg='white',
                        font=('Segoe UI', 18, 'bold'))
        title.pack(side='left', padx=20, pady=15)

        subtitle = tk.Label(header, text="Professional Video Processing & Effects",
                           bg=ModernStyles.ACCENT_BLUE, fg='#e0f2fe',
                           font=ModernStyles.FONT_NORMAL)
        subtitle.pack(side='left', padx=5, pady=15)

        # Main notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Tab 1: Text Settings
        tab1 = tk.Frame(notebook, bg=ModernStyles.BG_SECONDARY)
        notebook.add(tab1, text="📝 Text & Style")
        self.setup_text_settings(tab1)

        # Tab 2: Effects
        tab2 = tk.Frame(notebook, bg=ModernStyles.BG_SECONDARY)
        notebook.add(tab2, text="✨ Visual Effects")
        self.setup_effects(tab2)

        # Tab 3: Audio
        tab3 = tk.Frame(notebook, bg=ModernStyles.BG_SECONDARY)
        notebook.add(tab3, text="🔊 Audio & Music")
        self.setup_audio_settings(tab3)

        # Tab 4: Processing
        tab4 = tk.Frame(notebook, bg=ModernStyles.BG_SECONDARY)
        notebook.add(tab4, text="▶️ Process Videos")
        self.setup_processing(tab4)

        # Bottom control bar
        control_frame = tk.Frame(self.root, bg=ModernStyles.BG_PRIMARY, height=70)
        control_frame.pack(fill='x', side='bottom')
        control_frame.pack_propagate(False)

        # Buttons with modern styling
        btn_frame = tk.Frame(control_frame, bg=ModernStyles.BG_PRIMARY)
        btn_frame.pack(expand=True)

        save_btn = tk.Button(btn_frame, text="💾  Save Settings",
                            command=self.save_settings,
                            bg=ModernStyles.ACCENT_BLUE, fg='white',
                            font=ModernStyles.FONT_HEADING,
                            relief='flat', cursor='hand2',
                            padx=30, pady=12)
        save_btn.pack(side='left', padx=5)
        save_btn.bind('<Enter>', lambda e: e.widget.config(bg='#2563eb'))
        save_btn.bind('<Leave>', lambda e: e.widget.config(bg=ModernStyles.ACCENT_BLUE))

        self.process_btn = tk.Button(btn_frame, text="▶️  Start Processing",
                                     command=self.start_processing,
                                     bg=ModernStyles.ACCENT_GREEN, fg='white',
                                     font=ModernStyles.FONT_HEADING,
                                     relief='flat', cursor='hand2',
                                     padx=30, pady=12)
        self.process_btn.pack(side='left', padx=5)
        self.process_btn.bind('<Enter>', lambda e: e.widget.config(bg='#059669'))
        self.process_btn.bind('<Leave>', lambda e: e.widget.config(bg=ModernStyles.ACCENT_GREEN))

        stop_btn = tk.Button(btn_frame, text="⏹️  Stop",
                            command=self.stop_processing,
                            bg=ModernStyles.ACCENT_RED, fg='white',
                            font=ModernStyles.FONT_HEADING,
                            relief='flat', cursor='hand2',
                            padx=30, pady=12)
        stop_btn.pack(side='left', padx=5)
        stop_btn.bind('<Enter>', lambda e: e.widget.config(bg='#dc2626'))
        stop_btn.bind('<Leave>', lambda e: e.widget.config(bg=ModernStyles.ACCENT_RED))

    def setup_text_settings(self, parent):
        """Text and style settings with modern design"""
        canvas = tk.Canvas(parent, bg=ModernStyles.BG_SECONDARY, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas, bg=ModernStyles.BG_SECONDARY)

        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=frame, anchor="nw")
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Main Text Section
        self.create_section_header(frame, "Main Text Settings", "📝", ModernStyles.ACCENT_BLUE)

        # Font selection
        font_card = tk.Frame(frame, bg=ModernStyles.BG_CARD, relief='flat', bd=0)
        font_card.pack(fill='x', padx=20, pady=5)

        tk.Label(font_card, text="Font Family", bg=ModernStyles.BG_CARD,
                fg=ModernStyles.TEXT_PRIMARY, font=ModernStyles.FONT_NORMAL).pack(anchor='w', padx=15, pady=(15,5))

        font_combo = ttk.Combobox(font_card, values=list(self.available_fonts.keys()), width=50)
        font_combo.set(self.settings.get('font_style', 'Arial Bold'))
        font_combo.bind('<<ComboboxSelected>>', lambda e: self.update_font('font_style', 'font_file', font_combo.get()))
        font_combo.pack(anchor='w', padx=15, pady=(0,15))

        # Font size
        size_card = tk.Frame(frame, bg=ModernStyles.BG_CARD, relief='flat')
        size_card.pack(fill='x', padx=20, pady=5)

        tk.Label(size_card, text="Font Size", bg=ModernStyles.BG_CARD,
                fg=ModernStyles.TEXT_PRIMARY, font=ModernStyles.FONT_NORMAL).pack(anchor='w', padx=15, pady=(15,5))

        size_scale = tk.Scale(size_card, from_=20, to=100, orient='horizontal',
                             bg=ModernStyles.BG_CARD, fg=ModernStyles.TEXT_PRIMARY,
                             highlightthickness=0, troughcolor=ModernStyles.BG_SECONDARY,
                             activebackground=ModernStyles.ACCENT_BLUE,
                             command=lambda v: self.update_setting('font_size', int(v)))
        size_scale.set(self.settings.get('font_size', 45))
        size_scale.pack(fill='x', padx=15, pady=(0,15))

        # Colors
        color_card = tk.Frame(frame, bg=ModernStyles.BG_CARD, relief='flat')
        color_card.pack(fill='x', padx=20, pady=5)

        tk.Label(color_card, text="Colors", bg=ModernStyles.BG_CARD,
                fg=ModernStyles.TEXT_PRIMARY, font=ModernStyles.FONT_NORMAL).pack(anchor='w', padx=15, pady=(15,5))

        colors_row = tk.Frame(color_card, bg=ModernStyles.BG_CARD)
        colors_row.pack(fill='x', padx=15, pady=(0,15))

        tk.Label(colors_row, text="Text:", bg=ModernStyles.BG_CARD, fg=ModernStyles.TEXT_SECONDARY).pack(side='left')
        self.text_color_btn = tk.Button(colors_row, text="  ", bg=self.settings.get('text_color', '#000000'),
                                       width=8, relief='flat', cursor='hand2',
                                       command=lambda: self.pick_color('text_color', self.text_color_btn))
        self.text_color_btn.pack(side='left', padx=10)

        tk.Label(colors_row, text="Background:", bg=ModernStyles.BG_CARD, fg=ModernStyles.TEXT_SECONDARY).pack(side='left', padx=(20,0))
        self.bg_color_btn = tk.Button(colors_row, text="  ", bg=self.settings.get('bg_color', '#ffffff'),
                                     width=8, relief='flat', cursor='hand2',
                                     command=lambda: self.pick_color('bg_color', self.bg_color_btn))
        self.bg_color_btn.pack(side='left', padx=10)

        # CTA Section
        self.create_section_header(frame, "Call-to-Action (CTA)", "🎯", ModernStyles.ACCENT_PURPLE)

        cta_card = tk.Frame(frame, bg=ModernStyles.BG_CARD, relief='flat')
        cta_card.pack(fill='x', padx=20, pady=5)

        cta_var = tk.BooleanVar(value=self.settings.get('cta_enabled', True))
        ttk.Checkbutton(cta_card, text="Enable CTA", variable=cta_var,
                       command=lambda: self.update_setting('cta_enabled', cta_var.get())).pack(anchor='w', padx=15, pady=15)

        # Position
        self.create_section_header(frame, "Text Position", "📍", ModernStyles.ACCENT_ORANGE)

        pos_card = tk.Frame(frame, bg=ModernStyles.BG_CARD, relief='flat')
        pos_card.pack(fill='x', padx=20, pady=5)

        pos_var = tk.StringVar(value=self.settings.get('position', 'top'))
        pos_frame = tk.Frame(pos_card, bg=ModernStyles.BG_CARD)
        pos_frame.pack(pady=15, padx=15)

        for pos in ['top', 'center', 'bottom']:
            rb = ttk.Radiobutton(pos_frame, text=pos.capitalize(), variable=pos_var, value=pos,
                               command=lambda: self.update_setting('position', pos_var.get()))
            rb.pack(side='left', padx=15)

        # Spacer
        tk.Frame(frame, bg=ModernStyles.BG_SECONDARY, height=20).pack()

    def setup_effects(self, parent):
        """Visual effects with modern cards"""
        canvas = tk.Canvas(parent, bg=ModernStyles.BG_SECONDARY, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas, bg=ModernStyles.BG_SECONDARY)

        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=frame, anchor="nw")
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Text Animations
        self.create_section_header(frame, "Text Animations", "✨", ModernStyles.ACCENT_PURPLE)

        anim_card = tk.Frame(frame, bg=ModernStyles.BG_CARD, relief='flat')
        anim_card.pack(fill='x', padx=20, pady=5)

        fade_var = tk.BooleanVar(value=self.settings.get('text_fade_in', True))
        ttk.Checkbutton(anim_card, text="Fade In Animation", variable=fade_var,
                       command=lambda: self.update_setting('text_fade_in', fade_var.get())).pack(anchor='w', padx=15, pady=(15,5))

        glow_var = tk.BooleanVar(value=self.settings.get('text_glow', True))
        ttk.Checkbutton(anim_card, text="Text Glow Effect", variable=glow_var,
                       command=lambda: self.update_setting('text_glow', glow_var.get())).pack(anchor='w', padx=15, pady=5)

        shadow_var = tk.BooleanVar(value=self.settings.get('drop_shadow', True))
        ttk.Checkbutton(anim_card, text="Drop Shadow", variable=shadow_var,
                       command=lambda: self.update_setting('drop_shadow', shadow_var.get())).pack(anchor='w', padx=15, pady=(5,15))

        # Video Effects
        self.create_section_header(frame, "Video Effects", "🎬", ModernStyles.ACCENT_BLUE)

        video_card = tk.Frame(frame, bg=ModernStyles.BG_CARD, relief='flat')
        video_card.pack(fill='x', padx=20, pady=5)

        vig_var = tk.BooleanVar(value=self.settings.get('vignette', True))
        ttk.Checkbutton(video_card, text="Vignette (darkened edges)", variable=vig_var,
                       command=lambda: self.update_setting('vignette', vig_var.get())).pack(anchor='w', padx=15, pady=(15,5))

        dim_var = tk.BooleanVar(value=self.settings.get('background_dim', True))
        ttk.Checkbutton(video_card, text="Background Dimming", variable=dim_var,
                       command=lambda: self.update_setting('background_dim', dim_var.get())).pack(anchor='w', padx=15, pady=5)

        zoom_var = tk.BooleanVar(value=self.settings.get('video_zoom', True))
        ttk.Checkbutton(video_card, text="Slow Zoom Effect", variable=zoom_var,
                       command=lambda: self.update_setting('video_zoom', zoom_var.get())).pack(anchor='w', padx=15, pady=(5,15))

        # Color Grading
        self.create_section_header(frame, "Color Grading", "🎨", ModernStyles.ACCENT_ORANGE)

        grade_card = tk.Frame(frame, bg=ModernStyles.BG_CARD, relief='flat')
        grade_card.pack(fill='x', padx=20, pady=5)

        grade_var = tk.StringVar(value=self.settings.get('color_grade', 'warm'))
        grade_frame = tk.Frame(grade_card, bg=ModernStyles.BG_CARD)
        grade_frame.pack(pady=15, padx=15)

        for text, value in [('None', 'none'), ('Warm', 'warm'), ('Cold', 'cold'), ('Cinematic', 'cinematic')]:
            rb = ttk.Radiobutton(grade_frame, text=text, variable=grade_var, value=value,
                               command=lambda: self.update_setting('color_grade', grade_var.get()))
            rb.pack(side='left', padx=10)

        tk.Frame(frame, bg=ModernStyles.BG_SECONDARY, height=20).pack()

    def setup_audio_settings(self, parent):
        """Audio settings with modern design"""
        canvas = tk.Canvas(parent, bg=ModernStyles.BG_SECONDARY, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas, bg=ModernStyles.BG_SECONDARY)

        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=frame, anchor="nw")
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Original Audio
        self.create_section_header(frame, "Original Audio", "🎵", ModernStyles.ACCENT_BLUE)

        orig_card = tk.Frame(frame, bg=ModernStyles.BG_CARD, relief='flat')
        orig_card.pack(fill='x', padx=20, pady=5)

        mute_var = tk.BooleanVar(value=self.settings.get('mute_original_audio', False))
        ttk.Checkbutton(orig_card, text="Mute Original Video Audio", variable=mute_var,
                       command=lambda: self.update_setting('mute_original_audio', mute_var.get())).pack(anchor='w', padx=15, pady=15)

        # BGM
        self.create_section_header(frame, "Background Music (BGM)", "🎶", ModernStyles.ACCENT_PURPLE)

        bgm_card = tk.Frame(frame, bg=ModernStyles.BG_CARD, relief='flat')
        bgm_card.pack(fill='x', padx=20, pady=5)

        bgm_var = tk.BooleanVar(value=self.settings.get('add_custom_bgm', False))
        ttk.Checkbutton(bgm_card, text="Enable Background Music", variable=bgm_var,
                       command=lambda: self.update_setting('add_custom_bgm', bgm_var.get())).pack(anchor='w', padx=15, pady=(15,10))

        tk.Label(bgm_card, text="📂 BGM Source:", bg=ModernStyles.BG_CARD,
                fg=ModernStyles.TEXT_SECONDARY, font=ModernStyles.FONT_SMALL).pack(anchor='w', padx=15)
        tk.Label(bgm_card, text="Single file = same BGM | Folder = random BGM per video",
                fg='#94a3b8', bg=ModernStyles.BG_CARD, font=('Segoe UI', 8)).pack(anchor='w', padx=15)

        bgm_path_frame = tk.Frame(bgm_card, bg=ModernStyles.BG_CARD)
        bgm_path_frame.pack(fill='x', padx=15, pady=10)

        self.bgm_var = tk.StringVar(value=self.settings.get('bgm_file', ''))
        bgm_entry = tk.Entry(bgm_path_frame, textvariable=self.bgm_var, width=45,
                            bg='#1e293b', fg=ModernStyles.TEXT_PRIMARY,
                            relief='flat', font=ModernStyles.FONT_SMALL)
        bgm_entry.pack(side='left', fill='x', expand=True, ipady=5)

        btn_frame = tk.Frame(bgm_card, bg=ModernStyles.BG_CARD)
        btn_frame.pack(fill='x', padx=15, pady=(0,15))

        tk.Button(btn_frame, text="📄 Browse File", command=self.browse_bgm_file,
                 bg=ModernStyles.ACCENT_BLUE, fg='white', relief='flat',
                 cursor='hand2', font=ModernStyles.FONT_SMALL, padx=15, pady=5).pack(side='left', padx=5)

        tk.Button(btn_frame, text="📁 Browse Folder", command=self.browse_bgm_folder,
                 bg=ModernStyles.ACCENT_PURPLE, fg='white', relief='flat',
                 cursor='hand2', font=ModernStyles.FONT_SMALL, padx=15, pady=5).pack(side='left')

        # Voiceover
        self.create_section_header(frame, "Voiceover", "🎤", ModernStyles.ACCENT_GREEN)

        vo_card = tk.Frame(frame, bg=ModernStyles.BG_CARD, relief='flat')
        vo_card.pack(fill='x', padx=20, pady=5)

        vo_var = tk.BooleanVar(value=self.settings.get('add_voiceover', False))
        ttk.Checkbutton(vo_card, text="Enable Voiceover", variable=vo_var,
                       command=lambda: self.update_setting('add_voiceover', vo_var.get())).pack(anchor='w', padx=15, pady=(15,10))

        tk.Label(vo_card, text="📂 Voiceover Folder (Files: 1.mp3, 2.mp3, 3.mp3...)",
                bg=ModernStyles.BG_CARD, fg=ModernStyles.TEXT_SECONDARY,
                font=ModernStyles.FONT_SMALL).pack(anchor='w', padx=15)

        vo_path_frame = tk.Frame(vo_card, bg=ModernStyles.BG_CARD)
        vo_path_frame.pack(fill='x', padx=15, pady=10)

        self.vo_var = tk.StringVar(value=self.settings.get('voiceover_folder', ''))
        vo_entry = tk.Entry(vo_path_frame, textvariable=self.vo_var, width=45,
                           bg='#1e293b', fg=ModernStyles.TEXT_PRIMARY,
                           relief='flat', font=ModernStyles.FONT_SMALL)
        vo_entry.pack(side='left', fill='x', expand=True, ipady=5)

        tk.Button(vo_path_frame, text="📁 Browse", command=self.browse_voiceover,
                 bg=ModernStyles.ACCENT_GREEN, fg='white', relief='flat',
                 cursor='hand2', font=ModernStyles.FONT_SMALL, padx=15, pady=5).pack(side='left', padx=5)

        tk.Frame(vo_card, height=15, bg=ModernStyles.BG_CARD).pack()

        tk.Frame(frame, bg=ModernStyles.BG_SECONDARY, height=20).pack()

    def setup_processing(self, parent):
        """Processing tab with modern design"""
        frame = tk.Frame(parent, bg=ModernStyles.BG_SECONDARY)
        frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Title
        title_frame = tk.Frame(frame, bg=ModernStyles.ACCENT_GREEN, height=60)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="▶️ Video Processing Center",
                bg=ModernStyles.ACCENT_GREEN, fg='white',
                font=('Segoe UI', 16, 'bold')).pack(pady=15, padx=20)

        # Paths section
        paths_card = tk.Frame(frame, bg=ModernStyles.BG_CARD, relief='flat')
        paths_card.pack(fill='x', pady=10)

        # Video folder
        tk.Label(paths_card, text="📁 Video Folder", bg=ModernStyles.BG_CARD,
                fg=ModernStyles.TEXT_PRIMARY, font=ModernStyles.FONT_HEADING).pack(anchor='w', padx=15, pady=(15,5))

        video_frame = tk.Frame(paths_card, bg=ModernStyles.BG_CARD)
        video_frame.pack(fill='x', padx=15, pady=(0,10))

        self.video_folder_var = tk.StringVar(value=r"E:\MyAutomations\ScriptAutomations\VideoFolder\SourceVideosToEdit\Libriana8")
        tk.Entry(video_frame, textvariable=self.video_folder_var, width=60,
                bg='#1e293b', fg=ModernStyles.TEXT_PRIMARY, relief='flat',
                font=ModernStyles.FONT_SMALL).pack(side='left', fill='x', expand=True, ipady=6)

        tk.Button(video_frame, text="Browse", command=self.browse_video_folder,
                 bg=ModernStyles.ACCENT_BLUE, fg='white', relief='flat',
                 font=ModernStyles.FONT_SMALL, padx=15, pady=5, cursor='hand2').pack(side='left', padx=5)

        # Quotes file
        tk.Label(paths_card, text="📝 Quotes File", bg=ModernStyles.BG_CARD,
                fg=ModernStyles.TEXT_PRIMARY, font=ModernStyles.FONT_HEADING).pack(anchor='w', padx=15, pady=(10,5))

        quotes_frame = tk.Frame(paths_card, bg=ModernStyles.BG_CARD)
        quotes_frame.pack(fill='x', padx=15, pady=(0,10))

        self.quotes_file_var = tk.StringVar(value=r"E:\MyAutomations\ScriptAutomations\VideoFolder\Quotes.txt")
        tk.Entry(quotes_frame, textvariable=self.quotes_file_var, width=60,
                bg='#1e293b', fg=ModernStyles.TEXT_PRIMARY, relief='flat',
                font=ModernStyles.FONT_SMALL).pack(side='left', fill='x', expand=True, ipady=6)

        tk.Button(quotes_frame, text="Browse", command=self.browse_quotes_file,
                 bg=ModernStyles.ACCENT_BLUE, fg='white', relief='flat',
                 font=ModernStyles.FONT_SMALL, padx=15, pady=5, cursor='hand2').pack(side='left', padx=5)

        # Output folder
        tk.Label(paths_card, text="💾 Output Folder", bg=ModernStyles.BG_CARD,
                fg=ModernStyles.TEXT_PRIMARY, font=ModernStyles.FONT_HEADING).pack(anchor='w', padx=15, pady=(10,5))

        output_frame = tk.Frame(paths_card, bg=ModernStyles.BG_CARD)
        output_frame.pack(fill='x', padx=15, pady=(0,15))

        self.output_folder_var = tk.StringVar(value=r"E:\MyAutomations\ScriptAutomations\VideoFolder\FinalVideos")
        tk.Entry(output_frame, textvariable=self.output_folder_var, width=60,
                bg='#1e293b', fg=ModernStyles.TEXT_PRIMARY, relief='flat',
                font=ModernStyles.FONT_SMALL).pack(side='left', fill='x', expand=True, ipady=6)

        tk.Button(output_frame, text="Browse", command=self.browse_output_folder,
                 bg=ModernStyles.ACCENT_BLUE, fg='white', relief='flat',
                 font=ModernStyles.FONT_SMALL, padx=15, pady=5, cursor='hand2').pack(side='left', padx=5)

        # Progress section
        progress_card = tk.Frame(frame, bg=ModernStyles.BG_CARD, relief='flat')
        progress_card.pack(fill='both', expand=True, pady=10)

        tk.Label(progress_card, text="⏱️ Progress", bg=ModernStyles.BG_CARD,
                fg=ModernStyles.TEXT_PRIMARY, font=ModernStyles.FONT_HEADING).pack(anchor='w', padx=15, pady=(15,10))

        self.progress_var = tk.StringVar(value="Ready to process")
        tk.Label(progress_card, textvariable=self.progress_var, bg=ModernStyles.BG_CARD,
                fg=ModernStyles.TEXT_SECONDARY, font=ModernStyles.FONT_NORMAL).pack(anchor='w', padx=15)

        self.progress_bar = ttk.Progressbar(progress_card, mode='determinate', length=400)
        self.progress_bar.pack(fill='x', padx=15, pady=10)

        tk.Label(progress_card, text="📋 Processing Log", bg=ModernStyles.BG_CARD,
                fg=ModernStyles.TEXT_PRIMARY, font=ModernStyles.FONT_HEADING).pack(anchor='w', padx=15, pady=(10,5))

        self.log_text = scrolledtext.ScrolledText(progress_card, height=10, width=80, wrap=tk.WORD,
                                                  bg='#0f172a', fg='#e2e8f0',
                                                  font=('Consolas', 9), relief='flat')
        self.log_text.pack(fill='both', expand=True, padx=15, pady=(0,15))

    def browse_bgm_file(self):
        filename = filedialog.askopenfilename(title="Select BGM File", filetypes=[("Audio", "*.mp3 *.wav *.m4a *.aac *.ogg")])
        if filename:
            self.bgm_var.set(filename)
            self.update_setting('bgm_file', filename)

    def browse_bgm_folder(self):
        folder = filedialog.askdirectory(title="Select BGM Folder")
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

    def log(self, message, color=None):
        """Add colored message to log"""
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.root.update()

    def start_processing(self):
        """Start processing"""
        if self.processing:
            messagebox.showwarning("Processing", "Already processing videos!")
            return

        self.save_settings()
        self.processing = True
        self.process_btn.config(state='disabled', bg='#6b7280')
        thread = threading.Thread(target=self.process_videos, daemon=True)
        thread.start()

    def stop_processing(self):
        """Stop processing"""
        self.processing = False
        self.process_btn.config(state='normal', bg=ModernStyles.ACCENT_GREEN)
        self.log("⏹️ Processing stopped by user\n")

    def process_videos(self):
        """Process videos"""
        try:
            from youtube_video_automation_enhanced import VideoQuoteAutomation

            self.log("="*70 + "\n")
            self.log("🚀 Starting Enhanced Video Processing\n")
            self.log("="*70 + "\n")

            automation = VideoQuoteAutomation()
            automation.video_folder = Path(self.video_folder_var.get())
            automation.quotes_file = Path(self.quotes_file_var.get())
            automation.output_folder = Path(self.output_folder_var.get())
            automation.output_folder.mkdir(parents=True, exist_ok=True)
            automation.settings = self.settings

            videos = automation.get_video_files()
            quotes = automation.read_quotes()

            if not videos:
                self.log("✗ No videos found!\n")
                self.processing = False
                self.process_btn.config(state='normal', bg=ModernStyles.ACCENT_GREEN)
                return

            if not quotes:
                self.log("✗ No quotes found!\n")
                self.processing = False
                self.process_btn.config(state='normal', bg=ModernStyles.ACCENT_GREEN)
                return

            num_to_process = min(len(videos), len(quotes))
            self.progress_bar['maximum'] = num_to_process

            self.log(f"\n📊 Found {len(videos)} videos and {len(quotes)} quotes\n")
            self.log(f"🎬 Processing {num_to_process} videos...\n\n")

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
            self.process_btn.config(state='normal', bg=ModernStyles.ACCENT_GREEN)


if __name__ == "__main__":
    root = tk.Tk()
    app = UnifiedVideoAutomationGUI(root)
    root.mainloop()
