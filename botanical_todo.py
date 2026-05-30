"""
╔══════════════════════════════════════════════════════════════╗
║          🌿  BOTANICAL TODO — A Pinterest-worthy App  🌿     ║
║   Soft pastel mint · sage · cream · peach · botanical leaf   ║
║   Built with CustomTkinter · Python-only dependencies        ║
╚══════════════════════════════════════════════════════════════╝

Author  : Botanical Todo
Requires: customtkinter >= 5.2.2, pillow >= 9.0
Run     : python botanical_todo.py
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import font as tkfont
import time
import math
import random
import json
import os
from datetime import datetime

# ──────────────────────────────────────────────────────────────
#  THEME PALETTES
# ──────────────────────────────────────────────────────────────
LIGHT = {
    "bg_gradient_top":    "#E8F5F0",   # very pale mint
    "bg_gradient_bot":    "#FFF5ED",   # cream-peach
    "sidebar_bg":         "#D4EAE0",   # sage-mint
    "sidebar_hover":      "#C2DDD4",   # deeper sage
    "sidebar_active":     "#A8CDBE",   # active sage
    "card_bg":            "#F7FDF9",   # near-white with mint tint
    "card_border":        "#C8E6D4",   # mint border
    "card_hover":         "#F0FAF5",   # hover mint
    "text_primary":       "#3D5A4C",   # deep botanical green
    "text_secondary":     "#6B8F7E",   # medium sage
    "text_muted":         "#9DBFAE",   # muted sage
    "accent_mint":        "#7BCFAB",   # vibrant mint
    "accent_peach":       "#F4A96A",   # warm peach
    "accent_sage":        "#8DB8A0",   # calm sage
    "accent_cream":       "#FBF3E8",   # warm cream
    "btn_primary_bg":     "#7BCFAB",   # mint button
    "btn_primary_fg":     "#FFFFFF",
    "btn_primary_hover":  "#5BB893",
    "btn_danger_bg":      "#F4A96A",
    "btn_danger_hover":   "#E0925A",
    "entry_bg":           "#FFFFFF",
    "entry_border":       "#C8E6D4",
    "entry_focus":        "#7BCFAB",
    "done_strike":        "#9DBFAE",
    "shadow":             "#D0E8DC",
    "toggle_bg":          "#7BCFAB",
    "scrollbar":          "#C8E6D4",
    "priority_high":      "#F4A96A",
    "priority_med":       "#F7C98B",
    "priority_low":       "#7BCFAB",
    "tag_bg":             "#D4EAE0",
    "tag_fg":             "#3D5A4C",
    "header_title":       "#3D5A4C",
    "leaf_opacity":       "55",
}

DARK = {
    "bg_gradient_top":    "#1A2B24",   # deep forest
    "bg_gradient_bot":    "#251C14",   # deep espresso
    "sidebar_bg":         "#1F3329",   # dark sage
    "sidebar_hover":      "#263D31",   # hover dark sage
    "sidebar_active":     "#2F4D3C",   # active dark sage
    "card_bg":            "#243029",   # deep forest card
    "card_border":        "#2E4D3C",   # dark mint border
    "card_hover":         "#2A3D32",
    "text_primary":       "#D4EDE0",   # pale mint text
    "text_secondary":     "#8DB8A0",   # sage text
    "text_muted":         "#4E7063",   # muted dark
    "accent_mint":        "#5BB893",   # mint (slightly dimmed)
    "accent_peach":       "#C87D4A",   # muted peach
    "accent_sage":        "#6B9880",
    "accent_cream":       "#2E251A",
    "btn_primary_bg":     "#5BB893",
    "btn_primary_fg":     "#FFFFFF",
    "btn_primary_hover":  "#4AA07E",
    "btn_danger_bg":      "#C87D4A",
    "btn_danger_hover":   "#B06A38",
    "entry_bg":           "#1F2E28",
    "entry_border":       "#2E4D3C",
    "entry_focus":        "#5BB893",
    "done_strike":        "#3D5A4C",
    "shadow":             "#111D16",
    "toggle_bg":          "#5BB893",
    "scrollbar":          "#2E4D3C",
    "priority_high":      "#C87D4A",
    "priority_med":       "#B8945A",
    "priority_low":       "#5BB893",
    "tag_bg":             "#1F3329",
    "tag_fg":             "#8DB8A0",
    "header_title":       "#D4EDE0",
    "leaf_opacity":       "30",
}

# ──────────────────────────────────────────────────────────────
#  CONSTANTS
# ──────────────────────────────────────────────────────────────
CATEGORIES  = ["All", "🌿 Work", "🌸 Personal", "📚 Study", "🍃 Health"]
CAT_ICONS   = {"All": "🌱", "🌿 Work": "🌿", "🌸 Personal": "🌸",
                "📚 Study": "📚", "🍃 Health": "🍃"}
PRIORITIES  = ["Low", "Medium", "High"]
LEAF_EMOJIS = ["🌿", "🍃", "🌱", "🍀", "🌾", "☘️", "🌻", "🌼"]

DATA_FILE   = os.path.join(os.path.expanduser("~"), ".botanical_todo_data.json")

# ──────────────────────────────────────────────────────────────
#  PERSISTENCE
# ──────────────────────────────────────────────────────────────
def load_data():
    """Load tasks from JSON on disk."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_data(tasks):
    """Persist tasks to JSON on disk."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

# ──────────────────────────────────────────────────────────────
#  FLOATING LEAF CANVAS (decorative background)
# ──────────────────────────────────────────────────────────────
class FloatingLeaves:
    """Animates floating leaf emojis on a tk.Canvas as a decorative background."""

    def __init__(self, parent, theme):
        self.theme = theme
        self.canvas = tk.Canvas(parent, highlightthickness=0, bd=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.parent = parent
        self.leaves = []
        self._running = True
        self._setup_leaves()
        self._draw_gradient()
        self._animate()

    def _setup_leaves(self):
        w, h = 1100, 700
        for _ in range(18):
            self.leaves.append({
                "emoji": random.choice(LEAF_EMOJIS),
                "x": random.uniform(0, w),
                "y": random.uniform(-50, h + 50),
                "size": random.randint(16, 36),
                "speed": random.uniform(0.15, 0.55),
                "drift": random.uniform(-0.3, 0.3),
                "phase": random.uniform(0, math.pi * 2),
                "amp":   random.uniform(12, 40),
                "id":    None,
            })

    def _draw_gradient(self):
        """Draw a vertical gradient rectangle by drawing many thin strips."""
        self.canvas.delete("gradient")
        w = self.parent.winfo_width()  or 1100
        h = self.parent.winfo_height() or 700
        top = self.theme["bg_gradient_top"]
        bot = self.theme["bg_gradient_bot"]
        steps = 60
        r1, g1, b1 = self.canvas.winfo_rgb(top)
        r2, g2, b2 = self.canvas.winfo_rgb(bot)
        for i in range(steps):
            t  = i / steps
            r  = int((r1 + (r2 - r1) * t) / 256)
            g  = int((g1 + (g2 - g1) * t) / 256)
            b  = int((b1 + (b2 - b1) * t) / 256)
            y0 = int(h * i / steps)
            y1 = int(h * (i + 1) / steps)
            clr = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_rectangle(0, y0, w, y1, fill=clr,
                                         outline="", tags="gradient")

    def _animate(self):
        if not self._running:
            return
        t = time.time()
        w = self.parent.winfo_width()  or 1100
        h = self.parent.winfo_height() or 700
        self.canvas.delete("leaf")
        for lf in self.leaves:
            lf["y"] += lf["speed"]
            lf["x"] += lf["drift"] + math.sin(t + lf["phase"]) * 0.3
            if lf["y"] > h + 60:
                lf["y"] = -50
                lf["x"] = random.uniform(0, w)
            # Fade by position
            fade = int(min(1.0, (lf["y"] + 60) / 80) *
                       min(1.0, (h + 60 - lf["y"]) / 80) * 80)
            self.canvas.create_text(
                lf["x"], lf["y"],
                text=lf["emoji"],
                font=("Segoe UI Emoji", lf["size"]),
                tags="leaf",
                fill=f"#{'%02x' % fade}{'%02x' % (fade + 20)}{'%02x' % fade}",
            )
        # Ensure gradient stays below leaves
        self.canvas.tag_lower("gradient")
        self.canvas.after(42, self._animate)   # ~24 fps

    def update_theme(self, theme):
        self.theme = theme
        self._draw_gradient()

    def stop(self):
        self._running = False

# ──────────────────────────────────────────────────────────────
#  ANIMATED BUTTON (hover colour transitions)
# ──────────────────────────────────────────────────────────────
class AnimatedButton(ctk.CTkButton):
    """CTkButton with a smooth background colour hover animation."""

    STEPS = 8

    def __init__(self, *args, hover_color=None, **kwargs):
        self._hover_col = hover_color or kwargs.get("fg_color", "#7BCFAB")
        super().__init__(*args, **kwargs)
        self._base_col   = kwargs.get("fg_color", "#7BCFAB")
        self._anim_id    = None
        self._step       = 0
        self._direction  = 0
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _=None):
        self._direction = 1
        self._animate()

    def _on_leave(self, _=None):
        self._direction = -1
        self._animate()

    def _animate(self):
        if self._anim_id:
            self.after_cancel(self._anim_id)
        self._step = max(0, min(self.STEPS, self._step + self._direction))
        t = self._step / self.STEPS
        col = self._lerp_color(self._base_col, self._hover_col, t)
        try:
            self.configure(fg_color=col)
        except Exception:
            pass
        if 0 < self._step < self.STEPS:
            self._anim_id = self.after(18, self._animate)

    @staticmethod
    def _lerp_color(c1: str, c2: str, t: float) -> str:
        """Linearly interpolate between two hex colours."""
        def parse(c):
            c = c.lstrip("#")
            return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
        r1, g1, b1 = parse(c1)
        r2, g2, b2 = parse(c2)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        return f"#{r:02x}{g:02x}{b:02x}"

    def update_colors(self, base, hover):
        self._base_col  = base
        self._hover_col = hover
        self._step = 0
        try:
            self.configure(fg_color=base, hover_color=hover)
        except Exception:
            pass


# ──────────────────────────────────────────────────────────────
#  TASK CARD  (individual to-do item)
# ──────────────────────────────────────────────────────────────
class TaskCard(ctk.CTkFrame):
    """A beautifully styled card for a single task."""

    def __init__(self, parent, task: dict, theme: dict,
                 on_toggle, on_delete, on_edit, **kwargs):
        super().__init__(
            parent,
            corner_radius=16,
            fg_color=theme["card_bg"],
            border_color=theme["card_border"],
            border_width=1,
            **kwargs,
        )
        self.task      = task
        self.theme     = theme
        self.on_toggle = on_toggle
        self.on_delete = on_delete
        self.on_edit   = on_edit
        self._hovered  = False
        self._build()
        self.bind("<Enter>", self._hover_in)
        self.bind("<Leave>", self._hover_out)

    # ── build UI ────────────────────────────────────────────
    def _build(self):
        done   = self.task.get("done", False)
        text   = self.task.get("text", "")
        cat    = self.task.get("category", "All")
        pri    = self.task.get("priority", "Low")
        due    = self.task.get("due", "")
        note   = self.task.get("note", "")

        pri_colors = {"High":   self.theme["priority_high"],
                      "Medium": self.theme["priority_med"],
                      "Low":    self.theme["priority_low"]}

        # Left accent bar (priority colour)
        accent = ctk.CTkFrame(self, width=5, corner_radius=4,
                               fg_color=pri_colors.get(pri, self.theme["accent_mint"]))
        accent.pack(side="left", fill="y", padx=(8, 0), pady=8)

        # Checkbox
        self._check_var = ctk.BooleanVar(value=done)
        cb = ctk.CTkCheckBox(
            self, variable=self._check_var, text="",
            width=24, height=24,
            fg_color=self.theme["accent_mint"],
            hover_color=self.theme["btn_primary_hover"],
            border_color=self.theme["card_border"],
            checkmark_color="#FFFFFF",
            command=self._toggle,
        )
        cb.pack(side="left", padx=(10, 4), pady=10)

        # Main body
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(side="left", fill="both", expand=True, padx=4, pady=6)

        # Task text
        strike = "overstrike" if done else ""
        fg     = self.theme["done_strike"] if done else self.theme["text_primary"]
        self._task_lbl = ctk.CTkLabel(
            body, text=text,
            font=ctk.CTkFont(family="Georgia", size=14, weight="normal"),
            text_color=fg, anchor="w", justify="left",
        )
        self._task_lbl.pack(anchor="w")

        # Meta row
        meta = ctk.CTkFrame(body, fg_color="transparent")
        meta.pack(anchor="w", pady=(2, 0))

        # Category tag
        ctk.CTkLabel(
            meta, text=cat,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=self.theme["text_secondary"],
            fg_color=self.theme["tag_bg"],
            corner_radius=8, padx=6, pady=1,
        ).pack(side="left", padx=(0, 4))

        # Priority tag
        ctk.CTkLabel(
            meta, text=f"● {pri}",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=pri_colors.get(pri, self.theme["accent_mint"]),
        ).pack(side="left", padx=(0, 8))

        # Due date
        if due:
            ctk.CTkLabel(
                meta, text=f"📅 {due}",
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color=self.theme["text_muted"],
            ).pack(side="left")

        # Note (if any)
        if note:
            ctk.CTkLabel(
                body, text=note,
                font=ctk.CTkFont(family="Segoe UI", size=11, slant="italic"),
                text_color=self.theme["text_muted"],
                anchor="w",
            ).pack(anchor="w", pady=(1, 0))

        # Action buttons on the right
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(side="right", padx=10, pady=10)

        AnimatedButton(
            btn_frame, text="✏️", width=32, height=32,
            corner_radius=10,
            fg_color=self.theme["accent_sage"],
            hover_color=self.theme["btn_primary_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=13),
            command=lambda: self.on_edit(self.task),
        ).pack(pady=(0, 4))

        AnimatedButton(
            btn_frame, text="🗑", width=32, height=32,
            corner_radius=10,
            fg_color=self.theme["btn_danger_bg"],
            hover_color=self.theme["btn_danger_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=13),
            command=lambda: self.on_delete(self.task),
        ).pack()

    def _toggle(self):
        self.task["done"] = self._check_var.get()
        self.on_toggle(self.task)

    def _hover_in(self, _=None):
        try:
            self.configure(fg_color=self.theme["card_hover"])
        except Exception:
            pass

    def _hover_out(self, _=None):
        try:
            self.configure(fg_color=self.theme["card_bg"])
        except Exception:
            pass


# ──────────────────────────────────────────────────────────────
#  ADD / EDIT TASK DIALOG
# ──────────────────────────────────────────────────────────────
class TaskDialog(ctk.CTkToplevel):
    """Modal dialog for adding or editing a task."""

    def __init__(self, parent, theme, on_save, task=None):
        super().__init__(parent)
        self.theme   = theme
        self.on_save = on_save
        self.task    = task or {}
        self.result  = None

        self.title("✏️  Task" if task else "🌱  New Task")
        self.geometry("480x460")
        self.resizable(False, False)
        self.configure(fg_color=theme["bg_gradient_top"])
        self.grab_set()
        self._center(parent)
        self._build()

    def _center(self, parent):
        self.update_idletasks()
        px = parent.winfo_rootx() + parent.winfo_width()  // 2 - 240
        py = parent.winfo_rooty() + parent.winfo_height() // 2 - 230
        self.geometry(f"+{px}+{py}")

    def _build(self):
        th = self.theme

        # Title
        ctk.CTkLabel(
            self,
            text="Edit Task 🌿" if self.task else "New Task 🌱",
            font=ctk.CTkFont(family="Georgia", size=20, weight="bold"),
            text_color=th["header_title"],
        ).pack(padx=24, pady=(20, 10))

        # Task text
        ctk.CTkLabel(self, text="Task description",
                     font=ctk.CTkFont(family="Segoe UI", size=12),
                     text_color=th["text_secondary"]).pack(anchor="w", padx=24)
        self._text_entry = ctk.CTkEntry(
            self, placeholder_text="What needs to be done? 🌿",
            height=40, corner_radius=12,
            fg_color=th["entry_bg"],
            border_color=th["entry_border"],
            text_color=th["text_primary"],
            font=ctk.CTkFont(family="Georgia", size=13),
        )
        self._text_entry.pack(fill="x", padx=24, pady=6)
        if self.task.get("text"):
            self._text_entry.insert(0, self.task["text"])

        # Note
        ctk.CTkLabel(self, text="Note (optional)",
                     font=ctk.CTkFont(family="Segoe UI", size=12),
                     text_color=th["text_secondary"]).pack(anchor="w", padx=24)
        self._note_entry = ctk.CTkEntry(
            self, placeholder_text="Add a note…",
            height=36, corner_radius=12,
            fg_color=th["entry_bg"],
            border_color=th["entry_border"],
            text_color=th["text_primary"],
        )
        self._note_entry.pack(fill="x", padx=24, pady=6)
        if self.task.get("note"):
            self._note_entry.insert(0, self.task["note"])

        # Category + Priority row
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=24, pady=6)

        # Category dropdown
        cat_col = ctk.CTkFrame(row, fg_color="transparent")
        cat_col.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkLabel(cat_col, text="Category",
                     font=ctk.CTkFont(family="Segoe UI", size=12),
                     text_color=th["text_secondary"]).pack(anchor="w")
        self._cat_var = ctk.StringVar(value=self.task.get("category", "🌿 Work"))
        ctk.CTkOptionMenu(
            cat_col, values=CATEGORIES[1:],
            variable=self._cat_var,
            corner_radius=10,
            fg_color=th["sidebar_bg"],
            button_color=th["accent_sage"],
            button_hover_color=th["btn_primary_hover"],
            text_color=th["text_primary"],
            dropdown_fg_color=th["sidebar_bg"],
            dropdown_text_color=th["text_primary"],
        ).pack(fill="x")

        # Priority dropdown
        pri_col = ctk.CTkFrame(row, fg_color="transparent")
        pri_col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(pri_col, text="Priority",
                     font=ctk.CTkFont(family="Segoe UI", size=12),
                     text_color=th["text_secondary"]).pack(anchor="w")
        self._pri_var = ctk.StringVar(value=self.task.get("priority", "Low"))
        ctk.CTkOptionMenu(
            pri_col, values=PRIORITIES,
            variable=self._pri_var,
            corner_radius=10,
            fg_color=th["sidebar_bg"],
            button_color=th["accent_sage"],
            button_hover_color=th["btn_primary_hover"],
            text_color=th["text_primary"],
            dropdown_fg_color=th["sidebar_bg"],
            dropdown_text_color=th["text_primary"],
        ).pack(fill="x")

        # Due date
        ctk.CTkLabel(self, text="Due date (optional — e.g. Jun 15)",
                     font=ctk.CTkFont(family="Segoe UI", size=12),
                     text_color=th["text_secondary"]).pack(anchor="w", padx=24)
        self._due_entry = ctk.CTkEntry(
            self, placeholder_text="e.g. Jun 15, 2026",
            height=36, corner_radius=12,
            fg_color=th["entry_bg"],
            border_color=th["entry_border"],
            text_color=th["text_primary"],
        )
        self._due_entry.pack(fill="x", padx=24, pady=6)
        if self.task.get("due"):
            self._due_entry.insert(0, self.task["due"])

        # Buttons
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=(12, 20))

        AnimatedButton(
            btn_row, text="Cancel", width=100, height=38,
            corner_radius=12,
            fg_color=th["sidebar_bg"],
            hover_color=th["sidebar_hover"],
            text_color=th["text_secondary"],
            command=self.destroy,
        ).pack(side="left")

        AnimatedButton(
            btn_row, text="Save Task 🌿", height=38,
            corner_radius=12,
            fg_color=th["btn_primary_bg"],
            hover_color=th["btn_primary_hover"],
            text_color=th["btn_primary_fg"],
            font=ctk.CTkFont(family="Georgia", size=13, weight="bold"),
            command=self._save,
        ).pack(side="right")

    def _save(self):
        txt = self._text_entry.get().strip()
        if not txt:
            self._text_entry.configure(border_color="#E07070")
            return
        self.task["text"]     = txt
        self.task["note"]     = self._note_entry.get().strip()
        self.task["category"] = self._cat_var.get()
        self.task["priority"] = self._pri_var.get()
        self.task["due"]      = self._due_entry.get().strip()
        if "done" not in self.task:
            self.task["done"] = False
        if "id" not in self.task:
            self.task["id"] = str(time.time())
        self.on_save(self.task)
        self.destroy()


# ──────────────────────────────────────────────────────────────
#  SIDEBAR
# ──────────────────────────────────────────────────────────────
class Sidebar(ctk.CTkFrame):
    """Left navigation sidebar with category filters and app branding."""

    def __init__(self, parent, theme, on_select, **kwargs):
        super().__init__(
            parent, width=200, corner_radius=0,
            fg_color=theme["sidebar_bg"], **kwargs,
        )
        self.theme     = theme
        self.on_select = on_select
        self._active   = "All"
        self._buttons  = {}
        self.pack_propagate(False)
        self._build()

    def _build(self):
        th = self.theme

        # ── Brand / Logo ──────────────────────────────────
        brand = ctk.CTkFrame(self, fg_color="transparent")
        brand.pack(fill="x", padx=16, pady=(28, 4))

        ctk.CTkLabel(
            brand, text="🌿",
            font=ctk.CTkFont(size=38),
        ).pack()
        ctk.CTkLabel(
            brand,
            text="Botanical",
            font=ctk.CTkFont(family="Georgia", size=22, weight="bold"),
            text_color=th["text_primary"],
        ).pack()
        ctk.CTkLabel(
            brand, text="To-Do",
            font=ctk.CTkFont(family="Georgia", size=14),
            text_color=th["text_secondary"],
        ).pack()

        # Divider
        ctk.CTkFrame(self, height=1, fg_color=th["card_border"]).pack(
            fill="x", padx=16, pady=16)

        # ── Category Buttons ─────────────────────────────
        ctk.CTkLabel(
            self, text="CATEGORIES",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=th["text_muted"],
        ).pack(anchor="w", padx=20, pady=(0, 8))

        for cat in CATEGORIES:
            self._make_cat_btn(cat)

        # Divider
        ctk.CTkFrame(self, height=1, fg_color=th["card_border"]).pack(
            fill="x", padx=16, pady=16)

        # ── Today's date ──────────────────────────────────
        now = datetime.now()
        ctk.CTkLabel(
            self,
            text=now.strftime("%A"),
            font=ctk.CTkFont(family="Georgia", size=13, weight="bold"),
            text_color=th["text_primary"],
        ).pack(anchor="w", padx=20)
        ctk.CTkLabel(
            self,
            text=now.strftime("%d %B %Y"),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=th["text_secondary"],
        ).pack(anchor="w", padx=20)

        # Spacer
        ctk.CTkFrame(self, fg_color="transparent").pack(fill="both", expand=True)

        # ── Decorative leaf strip ────────────────────────
        leaves_lbl = ctk.CTkLabel(
            self,
            text="🍃 🌿 🌱 🍀 🌾",
            font=ctk.CTkFont(size=14),
        )
        leaves_lbl.pack(pady=(0, 20))

    def _make_cat_btn(self, cat):
        th    = self.theme
        is_active = cat == self._active
        btn = ctk.CTkButton(
            self,
            text=f" {cat}",
            anchor="w",
            height=38,
            corner_radius=12,
            fg_color=th["sidebar_active"] if is_active else "transparent",
            hover_color=th["sidebar_hover"],
            text_color=th["text_primary"],
            font=ctk.CTkFont(family="Segoe UI", size=13),
            command=lambda c=cat: self._select(c),
        )
        btn.pack(fill="x", padx=12, pady=2)
        self._buttons[cat] = btn

    def _select(self, cat):
        th = self.theme
        if self._active in self._buttons:
            self._buttons[self._active].configure(fg_color="transparent")
        self._active = cat
        self._buttons[cat].configure(fg_color=th["sidebar_active"])
        self.on_select(cat)

    def update_theme(self, theme):
        self.theme = theme
        self.configure(fg_color=theme["sidebar_bg"])
        # Rebuild sidebar internals by destroying and rebuilding
        for w in self.winfo_children():
            w.destroy()
        self._buttons = {}
        self._build()
        # Restore active selection
        if self._active in self._buttons:
            self._buttons[self._active].configure(
                fg_color=theme["sidebar_active"])


# ──────────────────────────────────────────────────────────────
#  MAIN APPLICATION WINDOW
# ──────────────────────────────────────────────────────────────
class BotanicalTodo(ctk.CTk):
    """The top-level application window."""

    def __init__(self):
        super().__init__()

        # ── Window setup ──────────────────────────────────
        self.title("🌿 Botanical To-Do")
        self.geometry("1100x700")
        self.minsize(850, 560)

        # Start in light mode
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")
        self._dark = False
        self.theme = LIGHT

        # ── State ─────────────────────────────────────────
        self.tasks        = load_data()
        self._active_cat  = "All"
        self._search_term = ""

        # ── Build UI ──────────────────────────────────────
        self._build()
        self._refresh_tasks()

        # ── Handle close ──────────────────────────────────
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ─── Layout construction ──────────────────────────────
    def _build(self):
        th = self.theme

        # Root container (fills entire window)
        self._root_frame = ctk.CTkFrame(self, corner_radius=0,
                                         fg_color=th["bg_gradient_top"])
        self._root_frame.pack(fill="both", expand=True)

        # Floating leaf background
        self._leaves = FloatingLeaves(self._root_frame, th)

        # Main horizontal split
        self._main = ctk.CTkFrame(self._root_frame, fg_color="transparent")
        self._main.pack(fill="both", expand=True)

        # ── Sidebar ───────────────────────────────────────
        self._sidebar = Sidebar(
            self._main, th,
            on_select=self._on_cat_select,
        )
        self._sidebar.pack(side="left", fill="y")

        # ── Content area ──────────────────────────────────
        self._content = ctk.CTkFrame(self._main, fg_color="transparent")
        self._content.pack(side="left", fill="both", expand=True)

        self._build_header()
        self._build_input_bar()
        self._build_task_area()

    def _build_header(self):
        th  = self.theme
        hdr = ctk.CTkFrame(self._content, fg_color="transparent", height=70)
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        hdr.pack_propagate(False)

        # Left: Title
        title_col = ctk.CTkFrame(hdr, fg_color="transparent")
        title_col.pack(side="left", fill="y")

        ctk.CTkLabel(
            title_col,
            text="My Garden 🌱",
            font=ctk.CTkFont(family="Georgia", size=26, weight="bold"),
            text_color=th["header_title"],
        ).pack(anchor="w")
        self._subtitle_lbl = ctk.CTkLabel(
            title_col,
            text=self._subtitle_text(),
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=th["text_secondary"],
        )
        self._subtitle_lbl.pack(anchor="w")

        # Right: Dark mode toggle + stats
        right = ctk.CTkFrame(hdr, fg_color="transparent")
        right.pack(side="right", fill="y")

        # Stats badge
        self._stats_lbl = ctk.CTkLabel(
            right, text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=th["text_secondary"],
        )
        self._stats_lbl.pack(side="left", padx=(0, 16))

        # Dark mode label + switch
        ctk.CTkLabel(
            right, text="🌙",
            font=ctk.CTkFont(size=18),
        ).pack(side="left")

        self._dark_switch = ctk.CTkSwitch(
            right, text="",
            width=52, height=26,
            switch_width=52,
            switch_height=26,
            fg_color=th["sidebar_bg"],
            progress_color=th["accent_mint"],
            button_color=th["btn_primary_bg"],
            button_hover_color=th["btn_primary_hover"],
            command=self._toggle_dark,
        )
        self._dark_switch.pack(side="left", padx=(4, 0))

        self._hdr_frame = hdr  # save ref for theme updates

    def _build_input_bar(self):
        th    = self.theme
        bar   = ctk.CTkFrame(
            self._content,
            corner_radius=18,
            fg_color=self.theme["card_bg"],
            border_color=th["card_border"],
            border_width=1,
        )
        bar.pack(fill="x", padx=24, pady=16)

        # Search icon
        ctk.CTkLabel(bar, text="🔍", font=ctk.CTkFont(size=16)).pack(
            side="left", padx=(14, 4), pady=12)

        # Search / quick-add entry
        self._entry = ctk.CTkEntry(
            bar,
            placeholder_text="Search or quick-add a task… press Enter to add 🌱",
            height=42,
            border_width=0,
            fg_color="transparent",
            text_color=th["text_primary"],
            placeholder_text_color=th["text_muted"],
            font=ctk.CTkFont(family="Georgia", size=14),
        )
        self._entry.pack(side="left", fill="x", expand=True, padx=4)
        self._entry.bind("<Return>", self._quick_add)
        self._entry.bind("<KeyRelease>", self._on_search)

        # Add button
        self._add_btn = AnimatedButton(
            bar, text="+ Add Task",
            width=120, height=38,
            corner_radius=14,
            fg_color=th["btn_primary_bg"],
            hover_color=th["btn_primary_hover"],
            text_color=th["btn_primary_fg"],
            font=ctk.CTkFont(family="Georgia", size=13, weight="bold"),
            command=self._open_add_dialog,
        )
        self._add_btn.pack(side="right", padx=10, pady=6)

        self._bar_frame = bar

    def _build_task_area(self):
        th = self.theme

        # Filter bar (All / Pending / Done)
        fbar = ctk.CTkFrame(self._content, fg_color="transparent")
        fbar.pack(fill="x", padx=24, pady=(0, 8))

        self._filter_var = ctk.StringVar(value="All")
        for lbl in ("All", "Pending", "Done"):
            rb = ctk.CTkRadioButton(
                fbar, text=lbl, value=lbl,
                variable=self._filter_var,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=th["text_secondary"],
                fg_color=th["accent_mint"],
                hover_color=th["btn_primary_hover"],
                border_color=th["card_border"],
                command=self._refresh_tasks,
            )
            rb.pack(side="left", padx=(0, 16))

        # Scrollable task list
        self._task_scroll = ctk.CTkScrollableFrame(
            self._content,
            corner_radius=0,
            fg_color="transparent",
            scrollbar_button_color=th["scrollbar"],
            scrollbar_button_hover_color=th["accent_mint"],
        )
        self._task_scroll.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        self._task_inner = self._task_scroll

    # ─── Task rendering ───────────────────────────────────
    def _refresh_tasks(self):
        # Clear existing cards
        for w in self._task_inner.winfo_children():
            w.destroy()

        visible = self._filtered_tasks()
        total   = len(self.tasks)
        done_n  = sum(1 for t in self.tasks if t.get("done"))

        # Update stats label
        pending = total - done_n
        try:
            self._stats_lbl.configure(
                text=f"✅ {done_n}  ·  🌿 {pending} pending")
            self._subtitle_lbl.configure(text=self._subtitle_text())
        except Exception:
            pass

        if not visible:
            ctk.CTkLabel(
                self._task_inner,
                text="No tasks here yet.\nAdd one above 🌱",
                font=ctk.CTkFont(family="Georgia", size=15),
                text_color=self.theme["text_muted"],
                justify="center",
            ).pack(pady=60)
            return

        for task in visible:
            card = TaskCard(
                self._task_inner, task, self.theme,
                on_toggle=self._on_toggle,
                on_delete=self._on_delete,
                on_edit=self._on_edit,
            )
            card.pack(fill="x", pady=5, padx=2)

    def _filtered_tasks(self):
        flt   = self._filter_var.get()
        cat   = self._active_cat
        srch  = self._search_term.lower()
        out   = []
        for t in self.tasks:
            if cat != "All" and t.get("category") != cat:
                continue
            if flt == "Pending" and t.get("done"):
                continue
            if flt == "Done" and not t.get("done"):
                continue
            if srch and srch not in t.get("text", "").lower():
                continue
            out.append(t)
        # Sort: undone first, then by priority
        pri_order = {"High": 0, "Medium": 1, "Low": 2}
        out.sort(key=lambda t: (
            t.get("done", False),
            pri_order.get(t.get("priority", "Low"), 2),
        ))
        return out

    def _subtitle_text(self):
        now   = datetime.now()
        total = len(self.tasks)
        done  = sum(1 for t in self.tasks if t.get("done"))
        if total == 0:
            return f"{now.strftime('%A, %d %B')} · Start planting your tasks 🌱"
        pct = int(done / total * 100)
        return (f"{now.strftime('%A, %d %B')} · "
                f"{pct}% complete · {total - done} remaining")

    # ─── Event handlers ───────────────────────────────────
    def _on_cat_select(self, cat):
        self._active_cat = cat
        self._refresh_tasks()

    def _on_search(self, _=None):
        self._search_term = self._entry.get().strip()
        self._refresh_tasks()

    def _quick_add(self, _=None):
        txt = self._entry.get().strip()
        if not txt:
            return
        # If it's a search match, don't add
        if self._search_term:
            return
        task = {
            "id":       str(time.time()),
            "text":     txt,
            "done":     False,
            "category": self._active_cat if self._active_cat != "All"
                         else "🌿 Work",
            "priority": "Low",
            "due":      "",
            "note":     "",
        }
        self.tasks.append(task)
        save_data(self.tasks)
        self._entry.delete(0, "end")
        self._search_term = ""
        self._refresh_tasks()

    def _open_add_dialog(self):
        TaskDialog(self, self.theme,
                   on_save=self._save_task)

    def _on_toggle(self, task):
        save_data(self.tasks)
        self._refresh_tasks()

    def _on_delete(self, task):
        self.tasks = [t for t in self.tasks if t.get("id") != task.get("id")]
        save_data(self.tasks)
        self._refresh_tasks()

    def _on_edit(self, task):
        # Make a copy so edits don't corrupt until save
        TaskDialog(self, self.theme,
                   on_save=self._save_task, task=dict(task))

    def _save_task(self, task):
        # Update if exists, else append
        for i, t in enumerate(self.tasks):
            if t.get("id") == task.get("id"):
                self.tasks[i] = task
                break
        else:
            self.tasks.append(task)
        save_data(self.tasks)
        self._refresh_tasks()

    # ─── Dark mode toggle ─────────────────────────────────
    def _toggle_dark(self):
        self._dark = not self._dark
        if self._dark:
            ctk.set_appearance_mode("dark")
            self.theme = DARK
        else:
            ctk.set_appearance_mode("light")
            self.theme = LIGHT
        self._apply_theme()

    def _apply_theme(self):
        th = self.theme
        self._leaves.update_theme(th)
        self._sidebar.update_theme(th)

        # Rebuild content header + input bar style
        try:
            self._bar_frame.configure(
                fg_color=th["card_bg"],
                border_color=th["card_border"],
            )
            self._entry.configure(
                text_color=th["text_primary"],
                placeholder_text_color=th["text_muted"],
            )
            self._add_btn.update_colors(th["btn_primary_bg"],
                                        th["btn_primary_hover"])
            self._stats_lbl.configure(text_color=th["text_secondary"])
        except Exception:
            pass

        # Refresh all task cards
        self._refresh_tasks()

    # ─── Lifecycle ────────────────────────────────────────
    def _on_close(self):
        self._leaves.stop()
        save_data(self.tasks)
        self.destroy()


# ──────────────────────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = BotanicalTodo()
    app.mainloop()
