#!/usr/bin/env python3
"""
Viral Research Agent - Advanced GUI with Outlier Detection
Enhanced with: Country filter, Shorts filter, Word Cloud, Category filter,
CSV export, Channel analyzer, Tags extractor, Best posting time, Related keywords
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
import csv
import webbrowser
from collections import Counter
from datetime import datetime

from youtube_search import search_youtube_videos, analyze_channel
from engagement import (
    calculate_engagement_ratios,
    filter_by_engagement,
    remove_duplicates,
    sort_by_engagement
)
from outlier_analysis import (
    filter_by_outlier_score,
    filter_by_channel_size,
    filter_by_velocity,
    filter_by_duration,
    analyze_title_patterns,
    calculate_viral_score,
    sort_by_viral_score,
    get_content_opportunities,
    format_number
)
from google_sheets_storage import store_to_google_sheets
from config import YOUTUBE_API_KEY, GOOGLE_SHEETS_SPREADSHEET_ID
from transcript_extractor import extract_video_content, batch_extract_content, export_content_report

# YouTube categories
YOUTUBE_CATEGORIES = {
    "": "All Categories",
    "1": "Film & Animation",
    "2": "Autos & Vehicles",
    "10": "Music",
    "15": "Pets & Animals",
    "17": "Sports",
    "19": "Travel & Events",
    "20": "Gaming",
    "22": "People & Blogs",
    "23": "Comedy",
    "24": "Entertainment",
    "25": "News & Politics",
    "26": "Howto & Style",
    "27": "Education",
    "28": "Science & Technology",
}

# Country codes
COUNTRY_CODES = {
    "": "All Regions",
    "US": "United States",
    "GB": "United Kingdom",
    "CA": "Canada",
    "AU": "Australia",
    "IN": "India",
    "PK": "Pakistan",
    "DE": "Germany",
    "FR": "France",
    "BR": "Brazil",
    "MX": "Mexico",
}


class ViralResearchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Viral Research Agent - Pro")
        self.root.geometry("1300x900")
        self.root.configure(bg="#1e1e1e")
        self.results = []
        self.create_widgets()

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[10, 5])

        # Header
        header = tk.Frame(self.root, bg="#1e1e1e")
        header.pack(fill="x", padx=20, pady=10)
        tk.Label(header, text="Viral Research Agent Pro", bg="#1e1e1e", fg="#00d4aa",
                 font=("Segoe UI", 20, "bold")).pack()
        tk.Label(header, text="Find viral videos, analyze trends, discover opportunities",
                 bg="#1e1e1e", fg="#ffffff", font=("Segoe UI", 10)).pack()

        # Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)

        self.create_youtube_tab()
        self.create_channel_tab()
        self.create_analysis_tab()
        self.create_trends_tab()

        # Status
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(self.root, textvariable=self.status_var, bg="#2d2d2d", fg="#888888",
                 font=("Segoe UI", 9)).pack(fill="x", padx=20, pady=(0, 10))

    def create_youtube_tab(self):
        tab = tk.Frame(self.notebook, bg="#1e1e1e")
        self.notebook.add(tab, text=" YouTube Outliers ")

        # Search frame
        sf = tk.LabelFrame(tab, text="Search", bg="#2d2d2d", fg="#ffffff", font=("Segoe UI", 10, "bold"))
        sf.pack(fill="x", padx=10, pady=5)

        r1 = tk.Frame(sf, bg="#2d2d2d")
        r1.pack(fill="x", padx=10, pady=5)
        tk.Label(r1, text="Topics:", bg="#2d2d2d", fg="#ffffff").pack(side="left")
        self.yt_topic = tk.Entry(r1, font=("Segoe UI", 11), width=40)
        self.yt_topic.pack(side="left", padx=10)
        self.yt_topic.insert(0, "celebrity, hollywood, gossip")
        tk.Label(r1, text="(comma separated)", bg="#2d2d2d", fg="#888888",
                 font=("Segoe UI", 8)).pack(side="left")

        r2 = tk.Frame(sf, bg="#2d2d2d")
        r2.pack(fill="x", padx=10, pady=5)

        tk.Label(r2, text="Days:", bg="#2d2d2d", fg="#ffffff").pack(side="left")
        self.yt_days = tk.Entry(r2, width=5)
        self.yt_days.pack(side="left", padx=5)
        self.yt_days.insert(0, "7")

        tk.Label(r2, text="Min Views:", bg="#2d2d2d", fg="#ffffff").pack(side="left", padx=(15, 0))
        self.yt_views = tk.Entry(r2, width=8)
        self.yt_views.pack(side="left", padx=5)
        self.yt_views.insert(0, "1000")

        tk.Label(r2, text="Country:", bg="#2d2d2d", fg="#ffffff").pack(side="left", padx=(15, 0))
        self.country_var = tk.StringVar(value="")
        country_combo = ttk.Combobox(r2, textvariable=self.country_var, width=15,
                                      values=list(COUNTRY_CODES.values()))
        country_combo.pack(side="left", padx=5)
        country_combo.current(0)

        tk.Label(r2, text="Category:", bg="#2d2d2d", fg="#ffffff").pack(side="left", padx=(15, 0))
        self.category_var = tk.StringVar(value="")
        cat_combo = ttk.Combobox(r2, textvariable=self.category_var, width=15,
                                  values=list(YOUTUBE_CATEGORIES.values()))
        cat_combo.pack(side="left", padx=5)
        cat_combo.current(0)

        # Advanced filters
        af = tk.LabelFrame(tab, text="Advanced Filters", bg="#2d2d2d", fg="#00d4aa", font=("Segoe UI", 10, "bold"))
        af.pack(fill="x", padx=10, pady=5)

        r3 = tk.Frame(af, bg="#2d2d2d")
        r3.pack(fill="x", padx=10, pady=5)

        tk.Label(r3, text="Min Outlier:", bg="#2d2d2d", fg="#ffffff").pack(side="left")
        self.min_outlier = ttk.Combobox(r3, values=["1x", "2x", "3x", "5x", "10x", "20x"], width=6)
        self.min_outlier.pack(side="left", padx=5)
        self.min_outlier.set("2x")

        tk.Label(r3, text="Min Views/Day:", bg="#2d2d2d", fg="#ffffff").pack(side="left", padx=(15, 0))
        self.min_velocity = tk.Entry(r3, width=8)
        self.min_velocity.pack(side="left", padx=5)
        self.min_velocity.insert(0, "100")

        tk.Label(r3, text="Duration:", bg="#2d2d2d", fg="#ffffff").pack(side="left", padx=(15, 0))
        self.duration_type = ttk.Combobox(r3, values=["Any", "Short", "Medium", "Long"], width=10)
        self.duration_type.pack(side="left", padx=5)
        self.duration_type.set("Any")

        # Shorts filter
        self.shorts_only = tk.BooleanVar(value=False)
        tk.Checkbutton(r3, text="Shorts Only", variable=self.shorts_only,
                       bg="#2d2d2d", fg="#ff6b6b", selectcolor="#3d3d3d").pack(side="left", padx=10)

        r4 = tk.Frame(af, bg="#2d2d2d")
        r4.pack(fill="x", padx=10, pady=5)

        tk.Label(r4, text="Channel Size:", bg="#2d2d2d", fg="#ffffff").pack(side="left")
        self.size_micro = tk.BooleanVar(value=True)
        self.size_small = tk.BooleanVar(value=True)
        self.size_medium = tk.BooleanVar(value=True)
        self.size_large = tk.BooleanVar(value=True)

        tk.Checkbutton(r4, text="Micro", variable=self.size_micro, bg="#2d2d2d", fg="#ffffff", selectcolor="#3d3d3d").pack(side="left", padx=3)
        tk.Checkbutton(r4, text="Small", variable=self.size_small, bg="#2d2d2d", fg="#ffffff", selectcolor="#3d3d3d").pack(side="left", padx=3)
        tk.Checkbutton(r4, text="Medium", variable=self.size_medium, bg="#2d2d2d", fg="#ffffff", selectcolor="#3d3d3d").pack(side="left", padx=3)
        tk.Checkbutton(r4, text="Large", variable=self.size_large, bg="#2d2d2d", fg="#ffffff", selectcolor="#3d3d3d").pack(side="left", padx=3)

        tk.Label(r4, text="Sort:", bg="#2d2d2d", fg="#ffffff").pack(side="left", padx=(15, 0))
        self.sort_by = ttk.Combobox(r4, values=["Viral Score", "Outlier Score", "Views/Day", "Views"], width=12)
        self.sort_by.pack(side="left", padx=5)
        self.sort_by.set("Viral Score")

        self.opps_only = tk.BooleanVar(value=False)
        tk.Checkbutton(r4, text="Opportunities Only", variable=self.opps_only,
                       bg="#2d2d2d", fg="#00ff00", selectcolor="#3d3d3d").pack(side="left", padx=10)

        # Buttons
        bf = tk.Frame(tab, bg="#1e1e1e")
        bf.pack(fill="x", padx=10, pady=5)

        self.yt_btn = tk.Button(bf, text="Find Viral Videos", command=self.search_youtube,
                                bg="#ff0000", fg="#ffffff", font=("Segoe UI", 11, "bold"), width=18)
        self.yt_btn.pack(side="left")

        tk.Button(bf, text="Export JSON", command=lambda: self.export_results("json"),
                  bg="#4a9eff", fg="#000000").pack(side="left", padx=5)

        tk.Button(bf, text="Export CSV", command=lambda: self.export_results("csv"),
                  bg="#34a853", fg="#000000").pack(side="left", padx=5)

        self.sheets_var = tk.BooleanVar(value=False)
        tk.Checkbutton(bf, text="Save to Sheets", variable=self.sheets_var,
                       bg="#1e1e1e", fg="#ffffff", selectcolor="#3d3d3d").pack(side="left", padx=5)

        tk.Button(bf, text="Show Tags", command=self.show_tags,
                  bg="#9b59b6", fg="#ffffff").pack(side="left", padx=5)

        tk.Button(bf, text="Word Cloud", command=self.show_word_cloud,
                  bg="#f39c12", fg="#000000").pack(side="left", padx=5)

        tk.Button(bf, text="Extract Content", command=self.extract_transcripts,
                  bg="#e74c3c", fg="#ffffff").pack(side="left", padx=5)

        # Results
        cols = ("Title", "Views", "Outlier", "V/Day", "Viral", "Subs", "Size", "Dur", "Type")
        self.yt_tree = ttk.Treeview(tab, columns=cols, show="headings", height=12)

        widths = [250, 70, 60, 70, 50, 70, 60, 60, 50]
        for col, w in zip(cols, widths):
            self.yt_tree.heading(col, text=col)
            self.yt_tree.column(col, width=w)

        sb = ttk.Scrollbar(tab, orient="vertical", command=self.yt_tree.yview)
        self.yt_tree.configure(yscrollcommand=sb.set)
        self.yt_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        sb.pack(side="right", fill="y", pady=10, padx=(0, 10))

        self.yt_tree.bind("<Double-1>", lambda e: self.open_url())

    def create_channel_tab(self):
        tab = tk.Frame(self.notebook, bg="#1e1e1e")
        self.notebook.add(tab, text=" Channel Analyzer ")

        sf = tk.LabelFrame(tab, text="Analyze Channel", bg="#2d2d2d", fg="#ffffff", font=("Segoe UI", 10, "bold"))
        sf.pack(fill="x", padx=10, pady=10)

        r1 = tk.Frame(sf, bg="#2d2d2d")
        r1.pack(fill="x", padx=10, pady=10)

        tk.Label(r1, text="Channel ID or URL:", bg="#2d2d2d", fg="#ffffff").pack(side="left")
        self.channel_input = tk.Entry(r1, font=("Segoe UI", 11), width=50)
        self.channel_input.pack(side="left", padx=10)

        self.channel_btn = tk.Button(r1, text="Analyze", command=self.analyze_channel,
                                     bg="#9b59b6", fg="#ffffff", font=("Segoe UI", 10, "bold"))
        self.channel_btn.pack(side="left", padx=5)

        # Channel info
        self.channel_info = tk.Label(sf, text="", bg="#2d2d2d", fg="#00d4aa",
                                     font=("Segoe UI", 10), justify="left")
        self.channel_info.pack(fill="x", padx=10, pady=5)

        # Results
        cols = ("Title", "Views", "Outlier", "V/Day", "Dur", "Published")
        self.channel_tree = ttk.Treeview(tab, columns=cols, show="headings", height=15)

        widths = [300, 80, 70, 80, 70, 120]
        for col, w in zip(cols, widths):
            self.channel_tree.heading(col, text=col)
            self.channel_tree.column(col, width=w)

        sb = ttk.Scrollbar(tab, orient="vertical", command=self.channel_tree.yview)
        self.channel_tree.configure(yscrollcommand=sb.set)
        self.channel_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        sb.pack(side="right", fill="y", pady=10, padx=(0, 10))

    def create_analysis_tab(self):
        tab = tk.Frame(self.notebook, bg="#1e1e1e")
        self.notebook.add(tab, text=" Insights ")

        # Best posting time
        tf = tk.LabelFrame(tab, text="Best Posting Times (from search results)", bg="#2d2d2d", fg="#ffffff", font=("Segoe UI", 10, "bold"))
        tf.pack(fill="x", padx=10, pady=10)

        self.time_label = tk.Label(tf, text="Run a search first to see posting time analysis",
                                   bg="#2d2d2d", fg="#888888", font=("Segoe UI", 10), justify="left")
        self.time_label.pack(fill="x", padx=10, pady=10)

        # Related keywords
        kf = tk.LabelFrame(tab, text="Suggested Keywords (based on results)", bg="#2d2d2d", fg="#ffffff", font=("Segoe UI", 10, "bold"))
        kf.pack(fill="x", padx=10, pady=10)

        self.keywords_label = tk.Label(kf, text="Run a search first to see keyword suggestions",
                                       bg="#2d2d2d", fg="#888888", font=("Segoe UI", 10), justify="left")
        self.keywords_label.pack(fill="x", padx=10, pady=10)

        # Word frequency
        wf = tk.LabelFrame(tab, text="Top Title Words", bg="#2d2d2d", fg="#ffffff", font=("Segoe UI", 10, "bold"))
        wf.pack(fill="both", expand=True, padx=10, pady=10)

        self.words_text = tk.Text(wf, bg="#1e1e1e", fg="#ffffff", font=("Consolas", 10),
                                   height=10, wrap="word")
        self.words_text.pack(fill="both", expand=True, padx=10, pady=10)

    def create_trends_tab(self):
        tab = tk.Frame(self.notebook, bg="#1e1e1e")
        self.notebook.add(tab, text=" Google Trends ")

        sf = tk.LabelFrame(tab, text="Google Trends", bg="#2d2d2d", fg="#ffffff", font=("Segoe UI", 10, "bold"))
        sf.pack(fill="x", padx=10, pady=10)

        r1 = tk.Frame(sf, bg="#2d2d2d")
        r1.pack(fill="x", padx=10, pady=5)

        tk.Label(r1, text="Country:", bg="#2d2d2d", fg="#ffffff").pack(side="left")
        self.trends_country = ttk.Combobox(r1, values=[
            "united_states", "united_kingdom", "canada", "australia", "india", "pakistan"
        ], width=20)
        self.trends_country.pack(side="left", padx=10)
        self.trends_country.set("united_states")

        tk.Label(r1, text="Keyword:", bg="#2d2d2d", fg="#ffffff").pack(side="left", padx=(15, 0))
        self.trends_kw = tk.Entry(r1, width=25)
        self.trends_kw.pack(side="left", padx=5)

        bf = tk.Frame(sf, bg="#2d2d2d")
        bf.pack(fill="x", padx=10, pady=10)

        self.trends_btn = tk.Button(bf, text="Get Trending", command=self.get_trends,
                                    bg="#4285f4", fg="#ffffff", font=("Segoe UI", 11, "bold"), width=18)
        self.trends_btn.pack(side="left")

        tk.Button(bf, text="Related", command=self.get_related, bg="#34a853", fg="#ffffff").pack(side="left", padx=10)

        cols = ("Rank", "Topic", "Info", "Type")
        self.trends_tree = ttk.Treeview(tab, columns=cols, show="headings", height=15)
        for col in cols:
            self.trends_tree.heading(col, text=col)
        self.trends_tree.column("Rank", width=50)
        self.trends_tree.column("Topic", width=400)

        sb = ttk.Scrollbar(tab, orient="vertical", command=self.trends_tree.yview)
        self.trends_tree.configure(yscrollcommand=sb.set)
        self.trends_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        sb.pack(side="right", fill="y", pady=10, padx=(0, 10))

    def search_youtube(self):
        if not YOUTUBE_API_KEY:
            messagebox.showerror("Error", "YouTube API key not configured!")
            return

        topics_str = self.yt_topic.get().strip()
        if not topics_str:
            messagebox.showerror("Error", "Enter at least one topic!")
            return

        topics = [t.strip() for t in topics_str.split(",") if t.strip()]
        if not topics:
            messagebox.showerror("Error", "Enter at least one topic!")
            return

        self.yt_btn.config(state="disabled", text="Searching...")
        for item in self.yt_tree.get_children():
            self.yt_tree.delete(item)

        threading.Thread(target=self._search_yt, args=(topics,), daemon=True).start()

    def _search_yt(self, topics):
        try:
            min_views = int(self.yt_views.get())
            min_outlier = float(self.min_outlier.get().replace("x", ""))
            min_vel = int(self.min_velocity.get())
            days = int(self.yt_days.get())

            # Get country code
            country_name = self.country_var.get()
            region_code = None
            for code, name in COUNTRY_CODES.items():
                if name == country_name:
                    region_code = code if code else None
                    break

            # Get category
            cat_name = self.category_var.get()
            category_id = None
            for cid, name in YOUTUBE_CATEGORIES.items():
                if name == cat_name:
                    category_id = cid if cid else None
                    break

            sizes = []
            if self.size_micro.get(): sizes.append("Micro")
            if self.size_small.get(): sizes.append("Small")
            if self.size_medium.get(): sizes.append("Medium")
            if self.size_large.get(): sizes.append("Large")

            dur_map = {"Any": None, "Short": "short", "Medium": "medium", "Long": "long"}
            dur = dur_map.get(self.duration_type.get())

            # Search for each keyword
            all_videos = []
            for i, topic in enumerate(topics):
                self.status_var.set(f"Searching '{topic}' ({i+1}/{len(topics)})...")
                videos = search_youtube_videos(topic, region_code=region_code, days_ago=days)
                all_videos.extend(videos)

            # Remove duplicates
            seen_ids = set()
            videos = []
            for v in all_videos:
                if v.get("video_id") not in seen_ids:
                    seen_ids.add(v.get("video_id"))
                    videos.append(v)

            if not videos:
                self.root.after(0, lambda: messagebox.showinfo("Info", "No videos found"))
                return

            self.status_var.set(f"Processing {len(videos)} videos...")

            # Filter by category if specified
            if category_id:
                videos = [v for v in videos if v.get("category_id") == category_id]

            # Filter by shorts if specified
            if self.shorts_only.get():
                videos = [v for v in videos if v.get("is_short", False)]

            videos = calculate_engagement_ratios(videos)
            videos = filter_by_engagement(videos, 0.01, 0.001, min_views)
            videos = filter_by_outlier_score(videos, min_outlier)
            videos = filter_by_velocity(videos, min_vel)

            if sizes:
                videos = filter_by_channel_size(videos, sizes)
            if dur:
                videos = filter_by_duration(videos, duration_type=dur)

            videos = remove_duplicates(videos)
            videos = analyze_title_patterns(videos)
            videos = calculate_viral_score(videos)

            if self.opps_only.get():
                videos = get_content_opportunities(videos)

            # Sort
            sort_opt = self.sort_by.get()
            if sort_opt == "Viral Score":
                videos = sort_by_viral_score(videos)
            elif sort_opt == "Outlier Score":
                videos = sorted(videos, key=lambda v: v.get("outlier_score", 0), reverse=True)
            elif sort_opt == "Views/Day":
                videos = sorted(videos, key=lambda v: v.get("views_per_day", 0), reverse=True)
            else:
                videos = sorted(videos, key=lambda v: v.get("views", 0), reverse=True)

            if self.sheets_var.get() and GOOGLE_SHEETS_SPREADSHEET_ID:
                store_to_google_sheets(videos)

            self.results = videos
            self.root.after(0, lambda: self._display_yt(videos))
            self.root.after(0, lambda: self._update_insights(videos))
            self.status_var.set(f"Found {len(videos)} viral videos!")

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, lambda: self.yt_btn.config(state="normal", text="Find Viral Videos"))

    def _display_yt(self, videos):
        for v in videos:
            vid_type = "Short" if v.get("is_short", False) else "Video"
            self.yt_tree.insert("", "end", values=(
                v.get("title", "")[:35],
                format_number(v.get("views", 0)),
                f"{v.get('outlier_score', 0)}x",
                format_number(v.get("views_per_day", 0)),
                f"{v.get('viral_score', 0)}",
                format_number(v.get("channel_subscribers", 0)),
                v.get("channel_size", ""),
                v.get("duration_formatted", ""),
                vid_type
            ))

    def _update_insights(self, videos):
        if not videos:
            return

        # Best posting times
        hours = [v.get("publish_hour", 0) for v in videos if v.get("publish_hour") is not None]
        days = [v.get("publish_day", "") for v in videos if v.get("publish_day")]

        if hours:
            hour_counts = Counter(hours)
            top_hours = hour_counts.most_common(3)
            hours_text = "Best hours: " + ", ".join([f"{h}:00 ({c} videos)" for h, c in top_hours])
        else:
            hours_text = "No timing data"

        if days:
            day_counts = Counter(days)
            top_days = day_counts.most_common(3)
            days_text = "Best days: " + ", ".join([f"{d} ({c})" for d, c in top_days])
        else:
            days_text = ""

        self.time_label.config(text=f"{hours_text}\n{days_text}")

        # Extract keywords from titles
        all_words = []
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'to', 'for',
                      'of', 'and', 'or', 'but', 'with', 'this', 'that', 'it', 'i', 'you', 'he',
                      'she', 'we', 'they', 'my', 'your', 'his', 'her', 'its', '|', '-', '&'}

        for v in videos:
            title = v.get("title", "").lower()
            words = [w.strip('.,!?()[]"\'') for w in title.split()]
            words = [w for w in words if len(w) > 2 and w not in stop_words and w.isalpha()]
            all_words.extend(words)

        word_counts = Counter(all_words)
        top_words = word_counts.most_common(15)

        if top_words:
            keywords_text = "Trending words: " + ", ".join([f"{w} ({c})" for w, c in top_words[:10]])
            self.keywords_label.config(text=keywords_text)

            # Update words text area
            self.words_text.delete(1.0, tk.END)
            for word, count in top_words:
                bar = "█" * min(count, 20)
                self.words_text.insert(tk.END, f"{word:15} {bar} ({count})\n")

    def show_tags(self):
        if not self.results:
            messagebox.showinfo("No Results", "Run a search first")
            return

        # Collect all tags
        all_tags = []
        for v in self.results:
            all_tags.extend(v.get("tags", []))

        if not all_tags:
            messagebox.showinfo("No Tags", "No tags found in results")
            return

        tag_counts = Counter(all_tags)
        top_tags = tag_counts.most_common(30)

        # Create popup
        popup = tk.Toplevel(self.root)
        popup.title("Top Tags from Viral Videos")
        popup.geometry("500x400")
        popup.configure(bg="#1e1e1e")

        tk.Label(popup, text="Copy these tags for your videos:", bg="#1e1e1e", fg="#00d4aa",
                 font=("Segoe UI", 12, "bold")).pack(pady=10)

        text = tk.Text(popup, bg="#2d2d2d", fg="#ffffff", font=("Consolas", 10), wrap="word")
        text.pack(fill="both", expand=True, padx=10, pady=10)

        for tag, count in top_tags:
            text.insert(tk.END, f"{tag} ({count})\n")

        # Copy button
        def copy_tags():
            tags_text = ", ".join([t for t, c in top_tags])
            popup.clipboard_clear()
            popup.clipboard_append(tags_text)
            messagebox.showinfo("Copied", "Tags copied to clipboard!")

        tk.Button(popup, text="Copy All Tags", command=copy_tags,
                  bg="#4a9eff", fg="#000000").pack(pady=10)

    def show_word_cloud(self):
        if not self.results:
            messagebox.showinfo("No Results", "Run a search first")
            return

        # Switch to Insights tab
        self.notebook.select(2)

    def analyze_channel(self):
        channel_input = self.channel_input.get().strip()
        if not channel_input:
            messagebox.showerror("Error", "Enter a channel ID or URL")
            return

        # Extract channel ID from URL if needed
        if "youtube.com" in channel_input:
            if "/channel/" in channel_input:
                channel_id = channel_input.split("/channel/")[1].split("/")[0].split("?")[0]
            elif "/@" in channel_input:
                messagebox.showerror("Error", "Please use channel ID, not handle. Find it in channel URL.")
                return
            else:
                channel_id = channel_input
        else:
            channel_id = channel_input

        self.channel_btn.config(state="disabled", text="Analyzing...")
        for item in self.channel_tree.get_children():
            self.channel_tree.delete(item)

        threading.Thread(target=self._analyze_channel, args=(channel_id,), daemon=True).start()

    def _analyze_channel(self, channel_id):
        try:
            self.status_var.set(f"Analyzing channel {channel_id}...")
            result = analyze_channel(channel_id)

            if "error" in result:
                self.root.after(0, lambda: messagebox.showerror("Error", result["error"]))
                return

            # Update channel info
            info_text = f"Channel: {result['channel_name']}\n"
            info_text += f"Subscribers: {format_number(result['subscribers'])} | "
            info_text += f"Total Views: {format_number(result['total_views'])} | "
            info_text += f"Videos: {result['video_count']}"

            self.root.after(0, lambda: self.channel_info.config(text=info_text))

            # Display videos sorted by outlier
            videos = sorted(result["videos"], key=lambda v: v.get("outlier_score", 0), reverse=True)

            def display():
                for v in videos:
                    self.channel_tree.insert("", "end", values=(
                        v.get("title", "")[:40],
                        format_number(v.get("views", 0)),
                        f"{v.get('outlier_score', 0)}x",
                        format_number(v.get("views_per_day", 0)),
                        v.get("duration_formatted", ""),
                        v.get("published_at", "")[:10]
                    ))

            self.root.after(0, display)
            self.status_var.set(f"Found {len(videos)} videos from channel")

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, lambda: self.channel_btn.config(state="normal", text="Analyze"))

    def get_trends(self):
        self.trends_btn.config(state="disabled", text="Loading...")
        for item in self.trends_tree.get_children():
            self.trends_tree.delete(item)
        threading.Thread(target=self._get_trends, daemon=True).start()

    def _get_trends(self):
        try:
            from google_trends import get_trending_now
            country = self.trends_country.get()
            self.status_var.set(f"Getting trends for {country}...")
            trends = get_trending_now(country)
            self.root.after(0, lambda: self._display_trends(trends))
            self.status_var.set(f"Found {len(trends)} trends")
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, lambda: self.trends_btn.config(state="normal", text="Get Trending"))

    def _display_trends(self, trends):
        for i, t in enumerate(trends, 1):
            self.trends_tree.insert("", "end", values=(i, t, "", "Trending"))

    def get_related(self):
        kw = self.trends_kw.get().strip()
        if not kw:
            messagebox.showinfo("Info", "Enter a keyword")
            return
        for item in self.trends_tree.get_children():
            self.trends_tree.delete(item)
        threading.Thread(target=self._get_related, args=(kw,), daemon=True).start()

    def _get_related(self, kw):
        try:
            from google_trends import get_related_topics
            self.status_var.set(f"Getting related for '{kw}'...")
            data = get_related_topics(kw)
            self.root.after(0, lambda: self._display_related(data))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

    def _display_related(self, data):
        for i, item in enumerate(data.get("top", [])[:15], 1):
            self.trends_tree.insert("", "end", values=(i, item.get("query", ""), f"Score: {item.get('value', 0)}", "Top"))
        for i, item in enumerate(data.get("rising", [])[:10], 1):
            self.trends_tree.insert("", "end", values=(f"↑{i}", item.get("query", ""), f"{item.get('value', '')}%", "Rising"))

    def open_url(self):
        sel = self.yt_tree.selection()
        if sel:
            idx = self.yt_tree.index(sel[0])
            if idx < len(self.results):
                url = self.results[idx].get("url", "")
                if url:
                    webbrowser.open(url)

    def export_results(self, format_type):
        if not self.results:
            messagebox.showwarning("No Results", "Run a search first")
            return

        if format_type == "json":
            filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
            if filename:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(self.results, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Exported", f"Saved to {filename}")

        elif format_type == "csv":
            filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
            if filename:
                with open(filename, "w", newline="", encoding="utf-8") as f:
                    if self.results:
                        # Select key fields for CSV
                        fields = ["title", "url", "views", "outlier_score", "views_per_day",
                                  "viral_score", "channel_title", "channel_subscribers",
                                  "channel_size", "duration_formatted", "is_short", "tags"]
                        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
                        writer.writeheader()
                        for v in self.results:
                            row = v.copy()
                            row["tags"] = ", ".join(v.get("tags", [])[:10])
                            writer.writerow(row)
                messagebox.showinfo("Exported", f"Saved to {filename}")

    def extract_transcripts(self):
        if not self.results:
            messagebox.showwarning("No Results", "Run a search first")
            return

        # Ask user for options
        popup = tk.Toplevel(self.root)
        popup.title("Extract Video Content")
        popup.geometry("400x300")
        popup.configure(bg="#1e1e1e")

        tk.Label(popup, text="Extract Transcripts & Summaries", bg="#1e1e1e", fg="#00d4aa",
                 font=("Segoe UI", 14, "bold")).pack(pady=10)

        tk.Label(popup, text=f"Found {len(self.results)} videos to process",
                 bg="#1e1e1e", fg="#ffffff").pack(pady=5)

        include_summary = tk.BooleanVar(value=True)
        tk.Checkbutton(popup, text="Include AI Summary (uses OpenRouter)",
                       variable=include_summary, bg="#1e1e1e", fg="#ffffff",
                       selectcolor="#3d3d3d").pack(pady=5)

        tk.Label(popup, text="Note: This may take a few minutes",
                 bg="#1e1e1e", fg="#888888").pack(pady=5)

        progress_var = tk.StringVar(value="")
        progress_label = tk.Label(popup, textvariable=progress_var,
                                   bg="#1e1e1e", fg="#4a9eff")
        progress_label.pack(pady=10)

        def start_extraction():
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Report", "*.txt"), ("JSON", "*.json")]
            )
            if not filename:
                return

            popup.grab_set()

            def extract():
                def progress_callback(current, total, title):
                    progress_var.set(f"Processing {current}/{total}: {title[:30]}...")

                results = batch_extract_content(
                    self.results,
                    include_summary.get(),
                    progress_callback
                )

                if filename.endswith(".json"):
                    import json
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(results, f, indent=2, ensure_ascii=False)
                else:
                    export_content_report(results, filename)

                self.root.after(0, lambda: progress_var.set("Done!"))
                self.root.after(0, lambda: messagebox.showinfo("Exported",
                    f"Content extracted to {filename}\n\nIncludes:\n- Titles\n- Tags\n- Transcripts\n- AI Summaries"))
                self.root.after(1000, popup.destroy)

            threading.Thread(target=extract, daemon=True).start()

        tk.Button(popup, text="Start Extraction", command=start_extraction,
                  bg="#e74c3c", fg="#ffffff", font=("Segoe UI", 11, "bold"),
                  width=20).pack(pady=20)


def main():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except:
        pass
    root = tk.Tk()
    app = ViralResearchGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
