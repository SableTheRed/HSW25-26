import tkinter as tk
from tkinter import ttk, messagebox
import threading
import datetime
import random

from auth import login as oidc_login


class BasePage(tk.Frame):
    """Base class for content pages with a back button."""

    def __init__(self, parent, title, navigate_callback):
        super().__init__(parent, bg="#1a1a2e")
        self.navigate_callback = navigate_callback
        self._create_header(title)

    def _create_header(self, title):
        header_frame = tk.Frame(self, bg="#1a1a2e")
        header_frame.pack(fill="x", padx=40, pady=(30, 20))

        back_btn = tk.Frame(header_frame, bg="#252542", cursor="hand2")
        back_btn.pack(side="left")

        back_inner = tk.Label(
            back_btn,
            text="\u2190  Back",
            font=("Segoe UI", 11),
            bg="#252542",
            fg="#4ecca3",
            padx=15,
            pady=8,
            cursor="hand2"
        )
        back_inner.pack()

        def on_enter(e):
            back_btn.configure(bg="#2f2f52")
            back_inner.configure(bg="#2f2f52")

        def on_leave(e):
            back_btn.configure(bg="#252542")
            back_inner.configure(bg="#252542")

        for widget in [back_btn, back_inner]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", lambda e: self.navigate_callback("home"))

        title_label = tk.Label(
            header_frame,
            text=title,
            font=("Segoe UI", 28, "bold"),
            bg="#1a1a2e",
            fg="#eee"
        )
        title_label.pack(side="left", padx=(25, 0))


class JournalPage(BasePage):
    """Journal page."""

    def __init__(self, parent, navigate_callback):
        super().__init__(parent, "Journal", navigate_callback)
        self._create_content()

    def _create_content(self):
        # Content container
        content = tk.Frame(self, bg="#1a1a2e")
        content.pack(fill="both", expand=True, padx=40, pady=(10, 30))

        # New entry section
        entry_frame = tk.Frame(content, bg="#252542")
        entry_frame.pack(fill="both", expand=True)

        entry_inner = tk.Frame(entry_frame, bg="#252542")
        entry_inner.pack(fill="both", expand=True, padx=30, pady=25)

        entry_label = tk.Label(
            entry_inner,
            text="New Journal Entry",
            font=("Segoe UI", 18, "bold"),
            bg="#252542",
            fg="#eee"
        )
        entry_label.pack(anchor="w", pady=(0, 5))

        entry_sublabel = tk.Label(
            entry_inner,
            text="Express your thoughts and feelings freely",
            font=("Segoe UI", 11),
            bg="#252542",
            fg="#888"
        )
        entry_sublabel.pack(anchor="w", pady=(0, 20))

        # Text box for journal entry
        text_container = tk.Frame(entry_inner, bg="#1a1a2e", padx=2, pady=2)
        text_container.pack(fill="both", expand=True, pady=(0, 20))

        self.entry_text = tk.Text(
            text_container,
            font=("Segoe UI", 12),
            bg="#1a1a2e",
            fg="#eee",
            insertbackground="#4ecca3",
            relief="flat",
            padx=15,
            pady=15,
            wrap="word",
            highlightthickness=0
        )
        self.entry_text.pack(fill="both", expand=True)
        self.entry_text.insert("1.0", "How are you feeling today?")
        self.entry_text.config(fg="#666")
        self.entry_text.bind("<FocusIn>", self._clear_placeholder)

        # Button row
        btn_frame = tk.Frame(entry_inner, bg="#252542")
        btn_frame.pack(fill="x")

        # Submit button
        submit_btn = tk.Button(
            btn_frame,
            text="Save Entry",
            font=("Segoe UI", 12, "bold"),
            bg="#4ecca3",
            fg="#1a1a2e",
            activebackground="#3dbb92",
            activeforeground="#1a1a2e",
            relief="flat",
            padx=30,
            pady=12,
            cursor="hand2"
        )
        submit_btn.pack(side="right")

        # Character count (optional enhancement)
        char_label = tk.Label(
            btn_frame,
            text="Take your time...",
            font=("Segoe UI", 10),
            bg="#252542",
            fg="#666"
        )
        char_label.pack(side="left")

    def _clear_placeholder(self, event):
        if self.entry_text.get("1.0", "end-1c") == "How are you feeling today?":
            self.entry_text.delete("1.0", "end")
            self.entry_text.config(fg="#eee")


class InsightsPage(BasePage):
    """Insights page."""

    def __init__(self, parent, navigate_callback):
        super().__init__(parent, "Insights", navigate_callback)
        self._create_content()

    def _create_content(self):
        # Content container
        content = tk.Frame(self, bg="#1a1a2e")
        content.pack(fill="both", expand=True, padx=40, pady=(10, 30))

        # Stats row
        stats_frame = tk.Frame(content, bg="#1a1a2e")
        stats_frame.pack(fill="x", pady=(0, 20))

        stats_frame.grid_columnconfigure(0, weight=1, uniform="stat")
        stats_frame.grid_columnconfigure(1, weight=1, uniform="stat")
        stats_frame.grid_columnconfigure(2, weight=1, uniform="stat")

        stats = [
            ("7", "Day Streak", "#4ecca3"),
            ("23", "Total Entries", "#4361ee"),
            ("85%", "Positive Days", "#f9c74f"),
        ]

        for i, (value, label, color) in enumerate(stats):
            stat_card = tk.Frame(stats_frame, bg="#252542")
            stat_card.grid(row=0, column=i, padx=8, pady=5, sticky="nsew")

            inner = tk.Frame(stat_card, bg="#252542")
            inner.pack(expand=True, pady=25)

            val_label = tk.Label(
                inner,
                text=value,
                font=("Segoe UI", 36, "bold"),
                bg="#252542",
                fg=color
            )
            val_label.pack()

            desc_label = tk.Label(
                inner,
                text=label,
                font=("Segoe UI", 12),
                bg="#252542",
                fg="#888"
            )
            desc_label.pack(pady=(5, 0))

        # Insights section
        insights_label = tk.Label(
            content,
            text="Recent Patterns",
            font=("Segoe UI", 16, "bold"),
            bg="#1a1a2e",
            fg="#eee"
        )
        insights_label.pack(anchor="w", pady=(20, 15))

        patterns = [
            ("You tend to feel more positive on weekends", "\u2605"),
            ("Morning journaling correlates with better mood", "\u263C"),
            ("Exercise days show 40% more positive entries", "\u2665"),
        ]

        for text, icon in patterns:
            pattern_frame = tk.Frame(content, bg="#252542")
            pattern_frame.pack(fill="x", pady=5)

            inner = tk.Frame(pattern_frame, bg="#252542")
            inner.pack(fill="x", padx=20, pady=15)

            icon_label = tk.Label(
                inner,
                text=icon,
                font=("DejaVu Sans", 18),
                bg="#252542",
                fg="#4ecca3"
            )
            icon_label.pack(side="left", padx=(0, 15))

            text_label = tk.Label(
                inner,
                text=text,
                font=("Segoe UI", 12),
                bg="#252542",
                fg="#eee"
            )
            text_label.pack(side="left")


class HistoryPage(BasePage):
    """History page."""

    CARD_BG = "#252542"
    CARD_HOVER = "#2f2f52"

    def __init__(self, parent, navigate_callback):
        super().__init__(parent, "History", navigate_callback)
        self._create_content()

    def _create_content(self):
        # Sample journal entries (most recent first)
        sample_entries = [
            {"date": "January 31, 2026", "preview": "Today was a productive day. I managed to complete all my tasks and even had time for some self-care."},
            {"date": "January 30, 2026", "preview": "Feeling a bit tired but optimistic about the week ahead. Planning to focus on balance."},
            {"date": "January 29, 2026", "preview": "Had a great conversation with a friend today. It reminded me how important connections are."},
            {"date": "January 28, 2026", "preview": "Started a new project at work. Excited about the possibilities and challenges ahead."},
            {"date": "January 27, 2026", "preview": "Took some time for self-reflection. I realized that I need to prioritize what matters most."},
            {"date": "January 26, 2026", "preview": "Went for a long walk in the park. Nature always helps me think more clearly."},
            {"date": "January 25, 2026", "preview": "Challenging day but I learned a lot from the experience. Growth comes from discomfort."},
        ]

        # Content container
        content = tk.Frame(self, bg="#1a1a2e")
        content.pack(fill="both", expand=True, padx=40, pady=(10, 30))

        # Subtitle
        subtitle = tk.Label(
            content,
            text=f"{len(sample_entries)} journal entries",
            font=("Segoe UI", 12),
            bg="#1a1a2e",
            fg="#888"
        )
        subtitle.pack(anchor="w", pady=(0, 15))

        # Create scrollable container
        container = tk.Frame(content, bg="#1a1a2e")
        container.pack(fill="both", expand=True)

        # Canvas for scrolling
        canvas = tk.Canvas(container, bg="#1a1a2e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1a1a2e")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _on_mousewheel_linux(event):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", _on_mousewheel_linux)
        canvas.bind_all("<Button-5>", _on_mousewheel_linux)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add entries to scrollable frame
        for i, entry in enumerate(sample_entries):
            entry_frame = tk.Frame(scrollable_frame, bg=self.CARD_BG, cursor="hand2")
            entry_frame.pack(fill="x", pady=6)

            entry_inner = tk.Frame(entry_frame, bg=self.CARD_BG)
            entry_inner.pack(fill="x", padx=25, pady=20)

            # Header row with date and day indicator
            header = tk.Frame(entry_inner, bg=self.CARD_BG)
            header.pack(fill="x")

            date_label = tk.Label(
                header,
                text=entry["date"],
                font=("Segoe UI", 14, "bold"),
                bg=self.CARD_BG,
                fg="#4ecca3"
            )
            date_label.pack(side="left")

            if i == 0:
                today_badge = tk.Label(
                    header,
                    text="Today",
                    font=("Segoe UI", 9, "bold"),
                    bg="#4ecca3",
                    fg="#1a1a2e",
                    padx=8,
                    pady=2
                )
                today_badge.pack(side="right")

            preview_label = tk.Label(
                entry_inner,
                text=entry["preview"],
                font=("Segoe UI", 12),
                bg=self.CARD_BG,
                fg="#aaa",
                wraplength=800,
                justify="left",
                anchor="w"
            )
            preview_label.pack(anchor="w", pady=(10, 0), fill="x")

            # Hover effects
            all_widgets = [entry_frame, entry_inner, header, date_label, preview_label]

            def on_enter(e, widgets=all_widgets):
                for w in widgets:
                    try:
                        w.configure(bg=self.CARD_HOVER)
                    except:
                        pass

            def on_leave(e, widgets=all_widgets):
                for w in widgets:
                    try:
                        w.configure(bg=self.CARD_BG)
                    except:
                        pass

            for widget in all_widgets:
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)

        # Update canvas width when container resizes
        def _configure_canvas(event):
            canvas.itemconfig(canvas.find_all()[0], width=event.width)

        canvas.bind("<Configure>", _configure_canvas)


class HomePage(tk.Frame):
    """Home page displayed after successful login."""

    CARD_BG = "#252542"
    CARD_HOVER = "#2f2f52"

    def __init__(self, parent, user_name, navigate_callback=None):
        super().__init__(parent, bg="#1a1a2e")
        self.user_name = user_name
        self.navigate_callback = navigate_callback
        self._create_widgets()

    def _create_card(self, parent, icon, icon_color, label_text, nav_target):
        """Create a styled navigation card."""
        card = tk.Frame(parent, bg=self.CARD_BG, cursor="hand2")

        # Inner container for padding
        inner = tk.Frame(card, bg=self.CARD_BG)
        inner.pack(fill="both", expand=True, padx=25, pady=30)

        icon_label = tk.Label(
            inner,
            text=icon,
            font=("DejaVu Sans", 42),
            bg=self.CARD_BG,
            fg=icon_color,
            cursor="hand2"
        )
        icon_label.pack(expand=True)

        text_label = tk.Label(
            inner,
            text=label_text,
            font=("Segoe UI", 16, "bold"),
            bg=self.CARD_BG,
            fg="#eee",
            cursor="hand2"
        )
        text_label.pack(pady=(15, 0))

        # Hover effects
        def on_enter(e):
            card.configure(bg=self.CARD_HOVER)
            inner.configure(bg=self.CARD_HOVER)
            icon_label.configure(bg=self.CARD_HOVER)
            text_label.configure(bg=self.CARD_HOVER)

        def on_leave(e):
            card.configure(bg=self.CARD_BG)
            inner.configure(bg=self.CARD_BG)
            icon_label.configure(bg=self.CARD_BG)
            text_label.configure(bg=self.CARD_BG)

        for widget in [card, inner, icon_label, text_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", lambda e, t=nav_target: self._navigate(t))

        return card

    def _create_widgets(self):
        # Main content container with padding
        content = tk.Frame(self, bg="#1a1a2e")
        content.pack(fill="both", expand=True, padx=50, pady=30)

        # Hello header
        header_frame = tk.Frame(content, bg="#1a1a2e")
        header_frame.pack(fill="x", pady=(10, 20))

        hello_label = tk.Label(
            header_frame,
            text=f"Hello, {self.user_name}",
            font=("Segoe UI", 32, "bold"),
            bg="#1a1a2e",
            fg="#eee"
        )
        hello_label.pack(anchor="w")

        subtitle = tk.Label(
            header_frame,
            text="What would you like to do today?",
            font=("Segoe UI", 14),
            bg="#1a1a2e",
            fg="#888"
        )
        subtitle.pack(anchor="w", pady=(5, 0))

        # Action for today section - NOW ON TOP
        action_frame = tk.Frame(content, bg="#1e3a5f")
        action_frame.pack(fill="x", pady=(0, 20))

        action_inner = tk.Frame(action_frame, bg="#1e3a5f")
        action_inner.pack(fill="x", padx=30, pady=20)

        # Left side - icon and label
        left_frame = tk.Frame(action_inner, bg="#1e3a5f")
        left_frame.pack(side="left", fill="y")

        action_icon = tk.Label(
            left_frame,
            text="\u2714",  # Checkmark
            font=("DejaVu Sans", 24),
            bg="#1e3a5f",
            fg="#4ecca3"
        )
        action_icon.pack(side="left", padx=(0, 15))

        text_frame = tk.Frame(left_frame, bg="#1e3a5f")
        text_frame.pack(side="left", fill="y")

        action_title = tk.Label(
            text_frame,
            text="Action for Today",
            font=("Segoe UI", 10, "bold"),
            bg="#1e3a5f",
            fg="#4ecca3"
        )
        action_title.pack(anchor="w")

        action_text = tk.Label(
            text_frame,
            text="Take a moment to reflect on your goals and write about your feelings",
            font=("Segoe UI", 13),
            bg="#1e3a5f",
            fg="#eee",
            wraplength=500,
            justify="left"
        )
        action_text.pack(anchor="w", pady=(3, 0))

        # Right side - button
        action_btn = tk.Button(
            action_inner,
            text="Start Now",
            font=("Segoe UI", 11, "bold"),
            bg="#4ecca3",
            fg="#1a1a2e",
            activebackground="#3dbb92",
            activeforeground="#1a1a2e",
            relief="flat",
            padx=25,
            pady=8,
            cursor="hand2",
            command=lambda: self._navigate("journal")
        )
        action_btn.pack(side="right", padx=(20, 0))

        # Sections container - takes up available space
        sections_frame = tk.Frame(content, bg="#1a1a2e")
        sections_frame.pack(fill="both", expand=True, pady=(0, 15))

        # Configure grid for responsive layout
        sections_frame.grid_columnconfigure(0, weight=1, uniform="card")
        sections_frame.grid_columnconfigure(1, weight=1, uniform="card")
        sections_frame.grid_columnconfigure(2, weight=1, uniform="card")
        sections_frame.grid_rowconfigure(0, weight=1)

        # Create cards
        journal_card = self._create_card(
            sections_frame, "\u270D", "#4ecca3", "Journal", "journal"
        )
        journal_card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        insights_card = self._create_card(
            sections_frame, "\u2605", "#f9c74f", "Insights", "insights"
        )
        insights_card.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        history_card = self._create_card(
            sections_frame, "\u25F4", "#4361ee", "History", "history"
        )
        history_card.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        # GitHub-style activity tracker
        self._create_activity_tracker(content)

    def _create_activity_tracker(self, parent):
        """Create a GitHub-style activity tracker showing journal activity."""
        tracker_frame = tk.Frame(parent, bg="#252542")
        tracker_frame.pack(fill="x", pady=(5, 0))

        # Center container
        center_container = tk.Frame(tracker_frame, bg="#252542")
        center_container.pack(pady=15)

        # Header
        header = tk.Frame(center_container, bg="#252542")
        header.pack(pady=(0, 12))

        title = tk.Label(
            header,
            text="Journal Activity",
            font=("Segoe UI", 12, "bold"),
            bg="#252542",
            fg="#eee"
        )
        title.pack()

        # Sample data: days with journal entries (1 = journaled, 0 = no entry)
        # Last 52 weeks worth of data for a full year view
        random.seed(42)  # Consistent pattern

        # Generate sample activity data (more recent = more likely to have entries)
        today = datetime.date.today()
        activity_data = {}
        for i in range(365):
            date = today - datetime.timedelta(days=i)
            # Higher chance of journaling in recent days
            probability = 0.7 if i < 30 else (0.5 if i < 90 else 0.3)
            activity_data[date] = random.random() < probability

        # Activity grid container (centered)
        grid_frame = tk.Frame(center_container, bg="#252542")
        grid_frame.pack()

        # Month labels row
        months_row = tk.Frame(grid_frame, bg="#252542")
        months_row.pack(anchor="w", pady=(0, 3))

        # Spacer for day labels column
        spacer = tk.Label(months_row, text="", width=4, bg="#252542")
        spacer.pack(side="left")

        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        # Calculate which months to show based on weeks
        today = datetime.date.today()
        days_since_sunday = (today.weekday() + 1) % 7
        start_date = today - datetime.timedelta(days=days_since_sunday + 52*7)

        # Place month labels at correct positions
        last_month = -1
        month_positions = []
        for week in range(53):
            week_start = start_date + datetime.timedelta(days=week*7)
            if week_start.month != last_month:
                month_positions.append((week, week_start.month))
                last_month = week_start.month

        # Create month label with proper spacing
        current_pos = 0
        for week_num, month in month_positions:
            gap = week_num - current_pos
            if gap > 0:
                spacer = tk.Frame(months_row, bg="#252542", width=gap*13)
                spacer.pack(side="left")
                spacer.pack_propagate(False)
            month_lbl = tk.Label(
                months_row,
                text=month_names[month - 1],
                font=("Segoe UI", 8),
                bg="#252542",
                fg="#666"
            )
            month_lbl.pack(side="left")
            current_pos = week_num + 3  # Account for label width

        # Day labels and squares row
        content_row = tk.Frame(grid_frame, bg="#252542")
        content_row.pack()

        # Day labels (Sun-Sat, showing Mon, Wed, Fri)
        day_labels_frame = tk.Frame(content_row, bg="#252542")
        day_labels_frame.pack(side="left", padx=(0, 3))

        for i, day in enumerate(["", "M", "", "W", "", "F", ""]):
            lbl = tk.Label(
                day_labels_frame,
                text=day,
                font=("Segoe UI", 7),
                bg="#252542",
                fg="#666",
                width=2,
                height=1
            )
            lbl.pack()

        # Activity squares grid
        squares_frame = tk.Frame(content_row, bg="#252542")
        squares_frame.pack(side="left")

        cell_size = 11

        for week in range(53):
            week_frame = tk.Frame(squares_frame, bg="#252542")
            week_frame.pack(side="left", padx=1)

            for day in range(7):
                current_date = start_date + datetime.timedelta(days=week*7 + day)

                if current_date > today:
                    color = "#252542"
                elif current_date in activity_data and activity_data[current_date]:
                    color = "#4ecca3"
                else:
                    color = "#1a1a2e"

                cell = tk.Frame(
                    week_frame,
                    bg=color,
                    width=cell_size,
                    height=cell_size
                )
                cell.pack(pady=1)
                cell.pack_propagate(False)

        # Legend row (centered)
        legend_frame = tk.Frame(center_container, bg="#252542")
        legend_frame.pack(pady=(12, 0))

        # Stats on left
        total_entries = sum(1 for v in activity_data.values() if v)
        stats_label = tk.Label(
            legend_frame,
            text=f"{total_entries} entries in the last year",
            font=("Segoe UI", 9),
            bg="#252542",
            fg="#888"
        )
        stats_label.pack(side="left", padx=(0, 30))

        less_label = tk.Label(
            legend_frame,
            text="Less",
            font=("Segoe UI", 8),
            bg="#252542",
            fg="#666"
        )
        less_label.pack(side="left")

        # Legend squares
        for color in ["#1a1a2e", "#2d6a4f", "#40916c", "#4ecca3"]:
            sq = tk.Frame(legend_frame, bg=color, width=10, height=10)
            sq.pack(side="left", padx=2)
            sq.pack_propagate(False)

        more_label = tk.Label(
            legend_frame,
            text="More",
            font=("Segoe UI", 8),
            bg="#252542",
            fg="#666"
        )
        more_label.pack(side="left", padx=(3, 0))

    def _navigate(self, page):
        if self.navigate_callback:
            self.navigate_callback(page)


class WelcomePage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("InsideOut")
        self.geometry("800x600")
        self.configure(bg="#1a1a2e")
        self.resizable(False, False)

        self.user_info = None
        self.user_name = None
        self._setup_styles()
        self._create_widgets()
        self._center_window()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Main frame style
        style.configure(
            "Main.TFrame",
            background="#1a1a2e"
        )

        # Title label style
        style.configure(
            "Title.TLabel",
            background="#1a1a2e",
            foreground="#eee",
            font=("Segoe UI", 32, "bold")
        )

        # Subtitle label style
        style.configure(
            "Subtitle.TLabel",
            background="#1a1a2e",
            foreground="#888",
            font=("Segoe UI", 12)
        )

        # Status label style
        style.configure(
            "Status.TLabel",
            background="#1a1a2e",
            foreground="#4ecca3",
            font=("Segoe UI", 11)
        )

        # Login button style
        style.configure(
            "Login.TButton",
            font=("Segoe UI", 12, "bold"),
            padding=(30, 15)
        )
        style.map(
            "Login.TButton",
            background=[("active", "#3a86ff"), ("!active", "#4361ee")],
            foreground=[("active", "#fff"), ("!active", "#fff")]
        )

    def _create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self, style="Main.TFrame")
        main_frame.pack(fill="both", expand=True, padx=40, pady=40)

        # Logo/icon placeholder
        icon_label = tk.Label(
            main_frame,
            text="\u2302",  # House symbol
            font=("DejaVu Sans", 48),
            bg="#1a1a2e",
            fg="#4ecca3"
        )
        icon_label.pack(pady=(20, 10))

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Welcome to InsideOut",
            style="Title.TLabel"
        )
        title_label.pack(pady=(10, 5))

        # Subtitle
        subtitle_label = ttk.Label(
            main_frame,
            text="Sign in to access your account",
            style="Subtitle.TLabel"
        )
        subtitle_label.pack(pady=(0, 30))

        # Login button
        self.login_btn = ttk.Button(
            main_frame,
            text="Sign In with SSO",
            style="Login.TButton",
            command=self._handle_login
        )
        self.login_btn.pack(pady=20)

        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="",
            style="Status.TLabel"
        )
        self.status_label.pack(pady=(20, 0))

    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _handle_login(self):
        self.login_btn.configure(state="disabled")
        self.status_label.configure(text="Opening browser for sign-in...")

        # Run login in background thread to not block UI
        thread = threading.Thread(target=self._perform_login, daemon=True)
        thread.start()

    def _perform_login(self):
        try:
            sub, name, access_token, refresh_token, id_token, expires_in = oidc_login()
            self.user_info = {
                "sub": sub,
                "name": name,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "id_token": id_token,
                "expires_in": expires_in
            }
            # Update UI from main thread
            self.after(0, self._on_login_success, name)
        except ValueError as e:
            self.after(0, self._on_login_error, str(e))
        except Exception as e:
            self.after(0, self._on_login_error, f"Login failed: {e}")

    def _on_login_success(self, name):
        self.user_name = name
        self._navigate_to("home")

    def _navigate_to(self, page):
        # Clear current page
        for widget in self.winfo_children():
            widget.destroy()

        # Set minimum size on first navigation (after login)
        if not hasattr(self, '_navigated'):
            self._navigated = True
            self.geometry("900x700")
            self.minsize(900, 750)
            self.resizable(True, True)
            self._center_window()

        # Show the requested page
        if page == "home":
            new_page = HomePage(self, self.user_name, self._navigate_to)
        elif page == "journal":
            new_page = JournalPage(self, self._navigate_to)
        elif page == "insights":
            new_page = InsightsPage(self, self._navigate_to)
        elif page == "history":
            new_page = HistoryPage(self, self._navigate_to)
        else:
            return

        new_page.pack(fill="both", expand=True)

    def _on_login_error(self, error_msg):
        self.status_label.configure(
            text="",
            foreground="#ff6b6b"
        )
        self.login_btn.configure(state="normal")
        messagebox.showerror("Login Error", error_msg)


def main():
    app = WelcomePage()
    app.mainloop()


if __name__ == "__main__":
    main()
