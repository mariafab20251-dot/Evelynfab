"""
Enhanced Video Effects Settings GUI
Select which effects to apply to your videos
"""

import tkinter as tk
from tkinter import ttk, colorchooser, messagebox, filedialog
import json
from pathlib import Path


class EffectsSettingsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Effects Settings - Enhanced Automation")
        self.root.geometry("800x900")

        # Load current settings
        self.settings = self.load_settings()

        self.setup_ui()

    def load_settings(self):
        """Load settings from JSON file"""
        settings_file = Path('overlay_settings.json')
        if settings_file.exists():
            with open(settings_file, 'r') as f:
                return json.load(f)
        return {}

    def save_settings(self):
        """Save settings to JSON file"""
        # Remove comment fields before saving
        clean_settings = {k: v for k, v in self.settings.items() if not k.startswith('_comment')}

        # Re-add comments
        output = {}
        for key, value in self.settings.items():
            output[key] = value

        with open('overlay_settings.json', 'w') as f:
            json.dump(output, f, indent=2)

        messagebox.showinfo("Success", "Settings saved to overlay_settings.json")

    def setup_ui(self):
        """Setup the user interface"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Tab 1: Text Animations
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="Text Animations")
        self.setup_text_animations(tab1)

        # Tab 2: Visual Effects
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="Visual Effects")
        self.setup_visual_effects(tab2)

        # Tab 3: Motion Effects
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="Motion Effects")
        self.setup_motion_effects(tab3)

        # Tab 4: Lighting & Polish
        tab4 = ttk.Frame(notebook)
        notebook.add(tab4, text="Lighting & Polish")
        self.setup_lighting(tab4)

        # Tab 5: Audio Settings
        tab5 = ttk.Frame(notebook)
        notebook.add(tab5, text="Audio Settings")
        self.setup_audio(tab5)

        # Save button at bottom
        save_btn = tk.Button(self.root, text="💾 Save Settings", command=self.save_settings,
                            bg='#00ff40', font=('Arial', 14, 'bold'), pady=10)
        save_btn.pack(fill='x', padx=10, pady=10)

    def setup_text_animations(self, parent):
        """Setup text animation controls"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Text Entrance Animations", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 10))

        # Fade in
        self.text_fade_in_var = tk.BooleanVar(value=self.settings.get('text_fade_in', True))
        cb1 = ttk.Checkbutton(frame, text="Fade In", variable=self.text_fade_in_var,
                             command=lambda: self.update_setting('text_fade_in', self.text_fade_in_var.get()))
        cb1.pack(anchor='w', pady=5)

        ttk.Label(frame, text="Fade Duration (seconds):").pack(anchor='w', padx=20)
        fade_dur = tk.Scale(frame, from_=0.1, to=1.0, resolution=0.1, orient='horizontal',
                           command=lambda v: self.update_setting('text_fade_duration', float(v)))
        fade_dur.set(self.settings.get('text_fade_duration', 0.4))
        fade_dur.pack(fill='x', padx=20)

        # Slide up
        self.text_slide_up_var = tk.BooleanVar(value=self.settings.get('text_slide_up', False))
        cb2 = ttk.Checkbutton(frame, text="Slide Up", variable=self.text_slide_up_var,
                             command=lambda: self.update_setting('text_slide_up', self.text_slide_up_var.get()))
        cb2.pack(anchor='w', pady=5)

        ttk.Label(frame, text="Slide Distance (pixels):").pack(anchor='w', padx=20)
        slide_dist = tk.Scale(frame, from_=10, to=100, orient='horizontal',
                             command=lambda v: self.update_setting('text_slide_distance', int(v)))
        slide_dist.set(self.settings.get('text_slide_distance', 50))
        slide_dist.pack(fill='x', padx=20)

        # Other animations
        self.text_bounce_var = tk.BooleanVar(value=self.settings.get('text_bounce', False))
        cb3 = ttk.Checkbutton(frame, text="Bounce Effect", variable=self.text_bounce_var,
                             command=lambda: self.update_setting('text_bounce', self.text_bounce_var.get()))
        cb3.pack(anchor='w', pady=5)

        self.text_kinetic_var = tk.BooleanVar(value=self.settings.get('text_kinetic', False))
        cb4 = ttk.Checkbutton(frame, text="Kinetic Text (word-by-word)", variable=self.text_kinetic_var,
                             command=lambda: self.update_setting('text_kinetic', self.text_kinetic_var.get()))
        cb4.pack(anchor='w', pady=5)

        self.text_glitch_var = tk.BooleanVar(value=self.settings.get('text_glitch', False))
        cb5 = ttk.Checkbutton(frame, text="Glitch Effect", variable=self.text_glitch_var,
                             command=lambda: self.update_setting('text_glitch', self.text_glitch_var.get()))
        cb5.pack(anchor='w', pady=5)

    def setup_visual_effects(self, parent):
        """Setup visual effects controls"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Visual Effects", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 10))

        # Text glow
        self.text_glow_var = tk.BooleanVar(value=self.settings.get('text_glow', True))
        cb1 = ttk.Checkbutton(frame, text="Text Glow", variable=self.text_glow_var,
                             command=lambda: self.update_setting('text_glow', self.text_glow_var.get()))
        cb1.pack(anchor='w', pady=5)

        ttk.Label(frame, text="Glow Intensity:").pack(anchor='w', padx=20)
        glow_int = tk.Scale(frame, from_=1, to=20, orient='horizontal',
                           command=lambda v: self.update_setting('glow_intensity', int(v)))
        glow_int.set(self.settings.get('glow_intensity', 8))
        glow_int.pack(fill='x', padx=20)

        # Vignette
        self.vignette_var = tk.BooleanVar(value=self.settings.get('vignette', True))
        cb2 = ttk.Checkbutton(frame, text="Vignette (darkened edges)", variable=self.vignette_var,
                             command=lambda: self.update_setting('vignette', self.vignette_var.get()))
        cb2.pack(anchor='w', pady=5)

        ttk.Label(frame, text="Vignette Intensity:").pack(anchor='w', padx=20)
        vig_int = tk.Scale(frame, from_=0.1, to=1.0, resolution=0.1, orient='horizontal',
                          command=lambda v: self.update_setting('vignette_intensity', float(v)))
        vig_int.set(self.settings.get('vignette_intensity', 0.4))
        vig_int.pack(fill='x', padx=20)

        # Background dim
        self.bg_dim_var = tk.BooleanVar(value=self.settings.get('background_dim', True))
        cb3 = ttk.Checkbutton(frame, text="Background Dim", variable=self.bg_dim_var,
                             command=lambda: self.update_setting('background_dim', self.bg_dim_var.get()))
        cb3.pack(anchor='w', pady=5)

        ttk.Label(frame, text="Dim Intensity:").pack(anchor='w', padx=20)
        dim_int = tk.Scale(frame, from_=0.1, to=0.5, resolution=0.05, orient='horizontal',
                          command=lambda v: self.update_setting('dim_intensity', float(v)))
        dim_int.set(self.settings.get('dim_intensity', 0.25))
        dim_int.pack(fill='x', padx=20)

        # Film grain
        self.grain_var = tk.BooleanVar(value=self.settings.get('film_grain', False))
        cb4 = ttk.Checkbutton(frame, text="Film Grain", variable=self.grain_var,
                             command=lambda: self.update_setting('film_grain', self.grain_var.get()))
        cb4.pack(anchor='w', pady=5)

        # Color grading
        ttk.Label(frame, text="Color Grading:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 5))
        self.color_grade_var = tk.StringVar(value=self.settings.get('color_grade', 'warm'))

        grades = [('None', 'none'), ('Warm', 'warm'), ('Cold', 'cold'), ('Cinematic', 'cinematic'), ('Vintage', 'vintage')]
        for text, value in grades:
            rb = ttk.Radiobutton(frame, text=text, variable=self.color_grade_var, value=value,
                                command=lambda: self.update_setting('color_grade', self.color_grade_var.get()))
            rb.pack(anchor='w', padx=20)

    def setup_motion_effects(self, parent):
        """Setup motion effects controls"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Motion Effects", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 10))

        # Video zoom
        self.video_zoom_var = tk.BooleanVar(value=self.settings.get('video_zoom', True))
        cb1 = ttk.Checkbutton(frame, text="Slow Zoom", variable=self.video_zoom_var,
                             command=lambda: self.update_setting('video_zoom', self.video_zoom_var.get()))
        cb1.pack(anchor='w', pady=5)

        ttk.Label(frame, text="Zoom Scale (1.0 = no zoom, 1.1 = 10% zoom):").pack(anchor='w', padx=20)
        zoom_scale = tk.Scale(frame, from_=1.0, to=1.2, resolution=0.01, orient='horizontal',
                             command=lambda v: self.update_setting('zoom_scale', float(v)))
        zoom_scale.set(self.settings.get('zoom_scale', 1.08))
        zoom_scale.pack(fill='x', padx=20)

        # Ken Burns
        self.ken_burns_var = tk.BooleanVar(value=self.settings.get('ken_burns', False))
        cb2 = ttk.Checkbutton(frame, text="Ken Burns Effect (pan + zoom)", variable=self.ken_burns_var,
                             command=lambda: self.update_setting('ken_burns', self.ken_burns_var.get()))
        cb2.pack(anchor='w', pady=5)

        # Parallax text
        self.parallax_var = tk.BooleanVar(value=self.settings.get('parallax_text', False))
        cb3 = ttk.Checkbutton(frame, text="Parallax Text (floating)", variable=self.parallax_var,
                             command=lambda: self.update_setting('parallax_text', self.parallax_var.get()))
        cb3.pack(anchor='w', pady=5)

    def setup_lighting(self, parent):
        """Setup lighting and polish controls"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Lighting & Polish", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 10))

        # Drop shadow
        self.shadow_var = tk.BooleanVar(value=self.settings.get('drop_shadow', True))
        cb1 = ttk.Checkbutton(frame, text="Drop Shadow", variable=self.shadow_var,
                             command=lambda: self.update_setting('drop_shadow', self.shadow_var.get()))
        cb1.pack(anchor='w', pady=5)

        ttk.Label(frame, text="Shadow Offset:").pack(anchor='w', padx=20)
        shadow_off = tk.Scale(frame, from_=0, to=20, orient='horizontal',
                             command=lambda v: self.update_setting('shadow_offset', int(v)))
        shadow_off.set(self.settings.get('shadow_offset', 6))
        shadow_off.pack(fill='x', padx=20)

        ttk.Label(frame, text="Shadow Blur:").pack(anchor='w', padx=20)
        shadow_blur = tk.Scale(frame, from_=0, to=30, orient='horizontal',
                              command=lambda v: self.update_setting('shadow_blur', int(v)))
        shadow_blur.set(self.settings.get('shadow_blur', 12))
        shadow_blur.pack(fill='x', padx=20)

        # Neon glow
        self.neon_var = tk.BooleanVar(value=self.settings.get('neon_glow', False))
        cb2 = ttk.Checkbutton(frame, text="Neon Glow", variable=self.neon_var,
                             command=lambda: self.update_setting('neon_glow', self.neon_var.get()))
        cb2.pack(anchor='w', pady=5)

        # Gradient overlay
        self.gradient_var = tk.BooleanVar(value=self.settings.get('gradient_overlay', False))
        cb3 = ttk.Checkbutton(frame, text="Gradient Overlay", variable=self.gradient_var,
                             command=lambda: self.update_setting('gradient_overlay', self.gradient_var.get()))
        cb3.pack(anchor='w', pady=5)

        # Light leaks
        self.leaks_var = tk.BooleanVar(value=self.settings.get('light_leaks', False))
        cb4 = ttk.Checkbutton(frame, text="Light Leaks", variable=self.leaks_var,
                             command=lambda: self.update_setting('light_leaks', self.leaks_var.get()))
        cb4.pack(anchor='w', pady=5)

    def setup_audio(self, parent):
        """Setup audio controls"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Audio Settings", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 10))

        # Mute original
        self.mute_var = tk.BooleanVar(value=self.settings.get('mute_original_audio', False))
        cb1 = ttk.Checkbutton(frame, text="Mute Original Video Audio", variable=self.mute_var,
                             command=lambda: self.update_setting('mute_original_audio', self.mute_var.get()))
        cb1.pack(anchor='w', pady=5)

        # Custom BGM
        ttk.Label(frame, text="Background Music (BGM)", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 5))

        self.bgm_var = tk.BooleanVar(value=self.settings.get('add_custom_bgm', False))
        cb2 = ttk.Checkbutton(frame, text="Add Custom BGM", variable=self.bgm_var,
                             command=lambda: self.update_setting('add_custom_bgm', self.bgm_var.get()))
        cb2.pack(anchor='w', pady=5)

        ttk.Label(frame, text="BGM File:").pack(anchor='w', padx=20)
        bgm_frame = ttk.Frame(frame)
        bgm_frame.pack(fill='x', padx=20, pady=5)

        self.bgm_file_var = tk.StringVar(value=self.settings.get('bgm_file', ''))
        bgm_entry = ttk.Entry(bgm_frame, textvariable=self.bgm_file_var, width=40)
        bgm_entry.pack(side='left', fill='x', expand=True)

        bgm_btn = ttk.Button(bgm_frame, text="Browse...", command=self.browse_bgm)
        bgm_btn.pack(side='left', padx=5)

        ttk.Label(frame, text="BGM Volume:").pack(anchor='w', padx=20)
        bgm_vol = tk.Scale(frame, from_=0.0, to=1.0, resolution=0.1, orient='horizontal',
                          command=lambda v: self.update_setting('bgm_volume', float(v)))
        bgm_vol.set(self.settings.get('bgm_volume', 0.3))
        bgm_vol.pack(fill='x', padx=20)

        self.bgm_loop_var = tk.BooleanVar(value=self.settings.get('bgm_loop', True))
        cb3 = ttk.Checkbutton(frame, text="Loop BGM", variable=self.bgm_loop_var,
                             command=lambda: self.update_setting('bgm_loop', self.bgm_loop_var.get()))
        cb3.pack(anchor='w', padx=20, pady=5)

        # Voiceover
        ttk.Label(frame, text="Voiceover", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 5))

        self.voiceover_var = tk.BooleanVar(value=self.settings.get('add_voiceover', False))
        cb4 = ttk.Checkbutton(frame, text="Add Voiceover", variable=self.voiceover_var,
                             command=lambda: self.update_setting('add_voiceover', self.voiceover_var.get()))
        cb4.pack(anchor='w', pady=5)

        ttk.Label(frame, text="Voiceover Folder:").pack(anchor='w', padx=20)
        vo_frame = ttk.Frame(frame)
        vo_frame.pack(fill='x', padx=20, pady=5)

        self.vo_folder_var = tk.StringVar(value=self.settings.get('voiceover_folder', ''))
        vo_entry = ttk.Entry(vo_frame, textvariable=self.vo_folder_var, width=40)
        vo_entry.pack(side='left', fill='x', expand=True)

        vo_btn = ttk.Button(vo_frame, text="Browse...", command=self.browse_voiceover)
        vo_btn.pack(side='left', padx=5)

        ttk.Label(frame, text="Voiceover Volume:").pack(anchor='w', padx=20)
        vo_vol = tk.Scale(frame, from_=0.0, to=1.0, resolution=0.1, orient='horizontal',
                         command=lambda v: self.update_setting('voiceover_volume', float(v)))
        vo_vol.set(self.settings.get('voiceover_volume', 1.0))
        vo_vol.pack(fill='x', padx=20)

        # Mix audio
        ttk.Label(frame, text="Audio Mixing", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 5))

        self.mix_var = tk.BooleanVar(value=self.settings.get('mix_audio', True))
        cb5 = ttk.Checkbutton(frame, text="Mix Original + BGM + Voiceover", variable=self.mix_var,
                             command=lambda: self.update_setting('mix_audio', self.mix_var.get()))
        cb5.pack(anchor='w', pady=5)

        ttk.Label(frame, text="Original Audio Volume (when mixed):").pack(anchor='w', padx=20)
        orig_vol = tk.Scale(frame, from_=0.0, to=1.0, resolution=0.1, orient='horizontal',
                           command=lambda v: self.update_setting('original_audio_volume', float(v)))
        orig_vol.set(self.settings.get('original_audio_volume', 0.5))
        orig_vol.pack(fill='x', padx=20)

    def browse_bgm(self):
        """Browse for BGM file"""
        filename = filedialog.askopenfilename(
            title="Select Background Music",
            filetypes=[("Audio Files", "*.mp3 *.wav *.m4a *.aac *.ogg"), ("All Files", "*.*")]
        )
        if filename:
            self.bgm_file_var.set(filename)
            self.update_setting('bgm_file', filename)

    def browse_voiceover(self):
        """Browse for voiceover folder"""
        folder = filedialog.askdirectory(title="Select Voiceover Folder")
        if folder:
            self.vo_folder_var.set(folder)
            self.update_setting('voiceover_folder', folder)

    def update_setting(self, key, value):
        """Update a setting value"""
        self.settings[key] = value


if __name__ == "__main__":
    root = tk.Tk()
    app = EffectsSettingsGUI(root)
    root.mainloop()
