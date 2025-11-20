#!/usr/bin/env python3
"""
Viral Research Agent - Advanced GUI with Outlier Detection
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
import webbrowser

from youtube_search import search_youtube_videos
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


class ViralResearchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Viral Research Agent - Advanced")
        self.root.geometry("1200x850")
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
        tk.Label(header, text="Viral Research Agent", bg="#1e1e1e", fg="#00d4aa",
                 font=("Segoe UI", 20, "bold")).pack()
        tk.Label(header, text="Find outlier videos with viral potential",
                 bg="#1e1e1e", fg="#ffffff", font=("Segoe UI", 10)).pack()

        # Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)

        self.create_youtube_tab()
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
        tk.Label(r1, text="Topic:", bg="#2d2d2d", fg="#ffffff").pack(side="left")
        self.yt_topic = tk.Entry(r1, font=("Segoe UI", 11), width=50)
        self.yt_topic.pack(side="left", padx=10)
        self.yt_topic.insert(0, "viral celebrities USA")

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

        tk.Label(r2, text="Min Like%:", bg="#2d2d2d", fg="#ffffff").pack(side="left", padx=(15, 0))
        self.yt_likes = tk.Entry(r2, width=5)
        self.yt_likes.pack(side="left", padx=5)
        self.yt_likes.insert(0, "3")

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
        tk.Checkbutton(r4, text="🎯 Opportunities Only", variable=self.opps_only,
                       bg="#2d2d2d", fg="#00ff00", selectcolor="#3d3d3d").pack(side="left", padx=10)

        # Buttons
        bf = tk.Frame(tab, bg="#1e1e1e")
        bf.pack(fill="x", padx=10, pady=5)

        self.yt_btn = tk.Button(bf, text="🔍 Find Viral Videos", command=self.search_youtube,
                                bg="#ff0000", fg="#ffffff", font=("Segoe UI", 12, "bold"), width=20)
        self.yt_btn.pack(side="left")

        tk.Button(bf, text="📁 Export", command=lambda: self.export_results("yt"),
                  bg="#4a9eff", fg="#000000").pack(side="left", padx=10)

        self.sheets_var = tk.BooleanVar(value=False)
        tk.Checkbutton(bf, text="Save to Sheets", variable=self.sheets_var,
                       bg="#1e1e1e", fg="#ffffff", selectcolor="#3d3d3d").pack(side="left")

        # Results
        cols = ("Title", "Views", "Outlier", "V/Day", "Viral", "Subs", "Size", "Dur")
        self.yt_tree = ttk.Treeview(tab, columns=cols, show="headings", height=15)

        widths = [280, 70, 60, 70, 60, 70, 60, 60]
        for col, w in zip(cols, widths):
            self.yt_tree.heading(col, text=col)
            self.yt_tree.column(col, width=w)

        sb = ttk.Scrollbar(tab, orient="vertical", command=self.yt_tree.yview)
        self.yt_tree.configure(yscrollcommand=sb.set)
        self.yt_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        sb.pack(side="right", fill="y", pady=10, padx=(0, 10))

        self.yt_tree.bind("<Double-1>", lambda e: self.open_url())

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

        self.trends_btn = tk.Button(bf, text="📈 Get Trending", command=self.get_trends,
                                    bg="#4285f4", fg="#ffffff", font=("Segoe UI", 11, "bold"), width=18)
        self.trends_btn.pack(side="left")

        tk.Button(bf, text="🔍 Related", command=self.get_related, bg="#34a853", fg="#ffffff").pack(side="left", padx=10)

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

        topic = self.yt_topic.get().strip()
        if not topic:
            messagebox.showerror("Error", "Enter a topic!")
            return

        self.yt_btn.config(state="disabled", text="Searching...")
        for item in self.yt_tree.get_children():
            self.yt_tree.delete(item)

        threading.Thread(target=self._search_yt, args=(topic,), daemon=True).start()

    def _search_yt(self, topic):
        try:
            min_views = int(self.yt_views.get())
            min_likes = float(self.yt_likes.get()) / 100
            min_outlier = float(self.min_outlier.get().replace("x", ""))
            min_vel = int(self.min_velocity.get())

            sizes = []
            if self.size_micro.get(): sizes.append("Micro")
            if self.size_small.get(): sizes.append("Small")
            if self.size_medium.get(): sizes.append("Medium")
            if self.size_large.get(): sizes.append("Large")

            dur_map = {"Any": None, "Short": "short", "Medium": "medium", "Long": "long"}
            dur = dur_map.get(self.duration_type.get())

            self.status_var.set("Searching...")
            videos = search_youtube_videos(topic)

            if not videos:
                self.root.after(0, lambda: messagebox.showinfo("Info", "No videos found"))
                return

            self.status_var.set(f"Processing {len(videos)} videos...")

            videos = calculate_engagement_ratios(videos)
            videos = filter_by_engagement(videos, min_likes, 0.001, min_views)
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
            self.status_var.set(f"Found {len(videos)} viral videos!")

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, lambda: self.yt_btn.config(state="normal", text="🔍 Find Viral Videos"))

    def _display_yt(self, videos):
        for v in videos:
            self.yt_tree.insert("", "end", values=(
                v.get("title", "")[:40],
                format_number(v.get("views", 0)),
                f"{v.get('outlier_score', 0)}x",
                format_number(v.get("views_per_day", 0)),
                f"{v.get('viral_score', 0)}",
                format_number(v.get("channel_subscribers", 0)),
                v.get("channel_size", ""),
                v.get("duration_formatted", "")
            ))

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
            self.results = [{"topic": t, "rank": i+1} for i, t in enumerate(trends)]
            self.root.after(0, lambda: self._display_trends(trends))
            self.status_var.set(f"Found {len(trends)} trends")
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, lambda: self.trends_btn.config(state="normal", text="📈 Get Trending"))

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
            self.results = data.get("top", [])
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

    def export_results(self, platform):
        if not self.results:
            messagebox.showwarning("No Results", "Run a search first")
            return
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Exported", f"Saved to {filename}")


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
