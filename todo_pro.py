"""
╔══════════════════════════════════════════════════════════════════╗
║           🗒️  TO-DO PRO  ·  Professional Task Manager           ║
║  OOP · Pastel Theme · Calendar · Stats · Export · Undo · Search  ║
╚══════════════════════════════════════════════════════════════════╝

Features:
  1.  Add / Edit / Delete / Toggle-complete tasks
  2.  Priority levels  (High 🔴 · Medium 🟡 · Low 🟢)  with colour rows
  3.  Calendar date picker  (tkcalendar, with plain-entry fallback)
  4.  Categories / tags
  5.  Live search  +  filter by status · priority · category
  6.  Sort by creation, due date, priority, or title
  7.  Statistics dashboard  (total · done · pending · %)
  8.  Auto-save to JSON with timestamp
  9.  Export to CSV or TXT
  10. Undo last action  (up to 20 levels)

Requires: tkcalendar  (pip install tkcalendar)
Run     : python todo_pro.py
"""

# ── Standard library ──────────────────────────────────────────────────────────
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv
import os
import uuid
from datetime import datetime, date
from dataclasses import dataclass, asdict, field
from typing import List, Optional
from copy import deepcopy
from enum import Enum

# ── Optional dependency ───────────────────────────────────────────────────────
try:
    from tkcalendar import DateEntry          # calendar widget
    HAS_CALENDAR = True
except ImportError:
    HAS_CALENDAR = False                      # graceful fallback to plain Entry

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 1 — CONSTANTS & THEME
# ══════════════════════════════════════════════════════════════════════════════

APP_NAME   = "To-Do Pro"
VERSION    = "2.0"
DATA_FILE  = os.path.join(os.path.expanduser("~"), "todo_pro_data.json")


class C:
    """Centralised colour palette (soft pastel + professional accents)."""
    # ── Backgrounds ──────────────────────────────────────────────────
    BG           = "#F2F0FF"   # main window — soft lavender
    BG2          = "#ECEAFF"   # subtle variant
    SIDEBAR      = "#DDD9FF"   # left stats panel
    HEADER       = "#6C63FF"   # purple header bar
    HEADER_FG    = "#FFFFFF"
    WHITE        = "#FFFFFF"
    CARD         = "#FFFFFF"

    # ── Toolbar buttons ──────────────────────────────────────────────
    BTN_ADD      = "#6C63FF"   # purple
    BTN_ADD_H    = "#5A54D4"
    BTN_EDIT     = "#3ABDC8"   # teal
    BTN_EDIT_H   = "#2E9CA8"
    BTN_DEL      = "#FF6B6B"   # coral
    BTN_DEL_H    = "#E55A5A"
    BTN_UNDO     = "#F4A261"   # peach
    BTN_UNDO_H   = "#DA8F52"
    BTN_EXP      = "#52B788"   # mint
    BTN_EXP_H    = "#3F9A6E"
    BTN_FG       = "#FFFFFF"

    # ── Priority rows ────────────────────────────────────────────────
    HIGH_ROW     = "#FFE8E8"
    HIGH_FG      = "#C0392B"
    HIGH_TAG     = "#E74C3C"

    MED_ROW      = "#FFF5E0"
    MED_FG       = "#935300"
    MED_TAG      = "#F39C12"

    LOW_ROW      = "#E8F8F0"
    LOW_FG       = "#1A6B3C"
    LOW_TAG      = "#27AE60"

    DONE_ROW     = "#F0F0F0"
    DONE_FG      = "#7F8C8D"
    OVER_ROW     = "#FFF0F0"   # overdue (but not done)

    ODD_ROW      = "#F9F8FF"
    EVEN_ROW     = "#EEEEFF"
    SEL_ROW      = "#C9C4FF"
    HOVER_ROW    = "#E4E2FF"

    # ── Text ─────────────────────────────────────────────────────────
    TXT          = "#2C3E50"
    TXT2         = "#5D6D7E"
    TXT3         = "#ABB2B9"
    LINK         = "#6C63FF"

    # ── Stats cards ──────────────────────────────────────────────────
    S_TOTAL      = "#6C63FF"
    S_DONE       = "#52B788"
    S_PEND       = "#F4A261"
    S_OVER       = "#FF6B6B"
    S_HIGH       = "#E74C3C"

    # ── Misc ─────────────────────────────────────────────────────────
    BORDER       = "#D0CCFF"
    STATUS_BG    = "#2C3E50"
    STATUS_FG    = "#ECF0F1"
    ENTRY_BG     = "#FAFAFF"
    ENTRY_BD     = "#B0AAFF"
    FOCUS_BD     = "#6C63FF"


class F:
    """Font definitions."""
    TITLE     = ("Segoe UI", 16, "bold")
    SUBTITLE  = ("Segoe UI", 9)
    SECTION   = ("Segoe UI", 11, "bold")
    BODY      = ("Segoe UI", 10)
    BODY_B    = ("Segoe UI", 10, "bold")
    SMALL     = ("Segoe UI", 9)
    MICRO     = ("Segoe UI", 8)
    STAT_N    = ("Segoe UI", 22, "bold")
    STAT_L    = ("Segoe UI", 8)
    BTN       = ("Segoe UI", 9, "bold")
    STATUS    = ("Segoe UI", 9)
    MONO      = ("Consolas", 9)
    TREE      = ("Segoe UI", 10)
    TREE_H    = ("Segoe UI", 10, "bold")


# ── Priority enum ─────────────────────────────────────────────────────────────
class Priority(Enum):
    HIGH   = "High"
    MEDIUM = "Medium"
    LOW    = "Low"


PRI_ICON  = {Priority.HIGH: "🔴", Priority.MEDIUM: "🟡", Priority.LOW: "🟢"}
PRI_ORDER = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
PRI_VALUES = [p.value for p in Priority]

DEFAULT_CATS = ["Work", "Personal", "Study", "Health",
                "Shopping", "Finance", "Other"]


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 2 — DATA MODEL
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class Task:
    """
    Immutable-ish task record.  All dates are stored as ISO strings.
    The `id` field is a UUID hex so it survives serialisation round-trips.
    """
    id:         str
    title:      str
    notes:      str  = ""
    category:   str  = "Personal"
    priority:   str  = Priority.LOW.value
    due_date:   str  = ""          # YYYY-MM-DD  or  ""
    done:       bool = False
    created:    str  = field(default_factory=lambda: datetime.now().isoformat())
    completed:  str  = ""          # ISO timestamp set when done=True

    # ── Derived helpers ──────────────────────────────────────────────────────
    def priority_enum(self) -> Priority:
        for p in Priority:
            if p.value == self.priority:
                return p
        return Priority.LOW

    def due_display(self) -> str:
        """Human-readable due date (e.g. '15 Jun 2026')."""
        if not self.due_date:
            return ""
        try:
            return date.fromisoformat(self.due_date).strftime("%d %b %Y")
        except ValueError:
            return self.due_date

    def is_overdue(self) -> bool:
        if not self.due_date or self.done:
            return False
        try:
            return date.fromisoformat(self.due_date) < date.today()
        except ValueError:
            return False

    def created_display(self) -> str:
        try:
            return datetime.fromisoformat(self.created).strftime("%d %b %Y")
        except Exception:
            return ""

    # ── Serialisation ────────────────────────────────────────────────────────
    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Task":
        valid = {k: v for k, v in d.items() if k in cls.__dataclass_fields__}
        return cls(**valid)

    @classmethod
    def new(cls, title: str, **kwargs) -> "Task":
        return cls(id=uuid.uuid4().hex, title=title, **kwargs)


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 3 — TASK MANAGER  (business logic)
# ══════════════════════════════════════════════════════════════════════════════

class TaskManager:
    """
    Manages the task list, persistence, filtering/sorting,
    undo stack, and export.  No UI dependencies.
    """
    MAX_UNDO = 20

    def __init__(self, data_file: str = DATA_FILE):
        self.data_file = data_file
        self._tasks: List[Task] = []
        self._undo_stack: List[tuple] = []   # (label, deep-copy snapshot)
        self.load()

    # ── Undo ─────────────────────────────────────────────────────────────────
    def _push_undo(self, label: str):
        """Snapshot current state before a mutating operation."""
        self._undo_stack.append((label, deepcopy(self._tasks)))
        if len(self._undo_stack) > self.MAX_UNDO:
            self._undo_stack.pop(0)

    def undo(self) -> Optional[str]:
        """Restore the last snapshotted state. Returns action label or None."""
        if not self._undo_stack:
            return None
        label, snapshot = self._undo_stack.pop()
        self._tasks = snapshot
        self.save()
        return label

    @property
    def can_undo(self) -> bool:
        return bool(self._undo_stack)

    @property
    def undo_label(self) -> str:
        return self._undo_stack[-1][0] if self._undo_stack else ""

    # ── CRUD ─────────────────────────────────────────────────────────────────
    def add(self, task: Task) -> Task:
        self._push_undo(f"Add '{task.title}'")
        self._tasks.append(task)
        self.save()
        return task

    def update(self, task: Task) -> bool:
        """Replace the task with the same id."""
        self._push_undo(f"Edit '{task.title}'")
        for i, t in enumerate(self._tasks):
            if t.id == task.id:
                self._tasks[i] = task
                self.save()
                return True
        return False

    def delete(self, task_id: str) -> bool:
        t = self.get(task_id)
        if not t:
            return False
        self._push_undo(f"Delete '{t.title}'")
        self._tasks = [x for x in self._tasks if x.id != task_id]
        self.save()
        return True

    def toggle_done(self, task_id: str) -> Optional[Task]:
        t = self.get(task_id)
        if not t:
            return None
        self._push_undo("Toggle done")
        t.done = not t.done
        t.completed = datetime.now().isoformat() if t.done else ""
        self.save()
        return t

    def get(self, task_id: str) -> Optional[Task]:
        for t in self._tasks:
            if t.id == task_id:
                return t
        return None

    @property
    def tasks(self) -> List[Task]:
        return list(self._tasks)

    # ── Filter + Sort ─────────────────────────────────────────────────────────
    def filter_tasks(
        self,
        search:   str = "",
        status:   str = "All",      # All | Pending | Completed | Overdue
        priority: str = "All",      # All | High | Medium | Low
        category: str = "All",
        sort_by:  str = "Created",  # Created | Due Date | Priority | Title
        ascending: bool = True,
    ) -> List[Task]:

        results = list(self._tasks)

        # ── Text search ───────────────────────────────────────────────
        if search.strip():
            q = search.strip().lower()
            results = [t for t in results
                       if q in t.title.lower()
                       or q in t.notes.lower()
                       or q in t.category.lower()]

        # ── Status filter ─────────────────────────────────────────────
        if status == "Pending":
            results = [t for t in results if not t.done]
        elif status == "Completed":
            results = [t for t in results if t.done]
        elif status == "Overdue":
            results = [t for t in results if t.is_overdue()]

        # ── Priority filter ───────────────────────────────────────────
        if priority != "All":
            results = [t for t in results if t.priority == priority]

        # ── Category filter ───────────────────────────────────────────
        if category != "All":
            results = [t for t in results if t.category == category]

        # ── Sort ──────────────────────────────────────────────────────
        def key(t: Task):
            if sort_by == "Due Date":
                return t.due_date or "9999-99-99"
            if sort_by == "Priority":
                return PRI_ORDER.get(t.priority_enum(), 9)
            if sort_by == "Title":
                return t.title.lower()
            return t.created  # default: Created

        results.sort(key=key, reverse=not ascending)
        return results

    # ── Statistics ────────────────────────────────────────────────────────────
    def stats(self) -> dict:
        ts    = self._tasks
        total = len(ts)
        done  = sum(1 for t in ts if t.done)
        over  = sum(1 for t in ts if t.is_overdue())
        return {
            "total":   total,
            "done":    done,
            "pending": total - done,
            "overdue": over,
            "pct":     round(done / total * 100) if total else 0,
            "high":    sum(1 for t in ts if t.priority == Priority.HIGH.value),
            "medium":  sum(1 for t in ts if t.priority == Priority.MEDIUM.value),
            "low":     sum(1 for t in ts if t.priority == Priority.LOW.value),
        }

    # ── Categories ────────────────────────────────────────────────────────────
    def all_categories(self) -> List[str]:
        used = {t.category for t in self._tasks}
        return sorted(used | set(DEFAULT_CATS))

    # ── Persistence ───────────────────────────────────────────────────────────
    def save(self):
        try:
            payload = {
                "app":      APP_NAME,
                "version":  VERSION,
                "saved_at": datetime.now().isoformat(),
                "tasks":    [t.to_dict() for t in self._tasks],
            }
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except OSError as e:
            print(f"[TaskManager] Save failed: {e}")

    def load(self):
        if not os.path.exists(self.data_file):
            return
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                payload = json.load(f)
            self._tasks = [Task.from_dict(d) for d in payload.get("tasks", [])]
        except Exception as e:
            print(f"[TaskManager] Load failed: {e}")
            self._tasks = []

    # ── Export ────────────────────────────────────────────────────────────────
    def export_csv(self, path: str) -> int:
        tasks = self._tasks
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["ID", "Title", "Notes", "Category", "Priority",
                         "Due Date", "Done", "Created", "Completed"])
            for t in tasks:
                w.writerow([t.id, t.title, t.notes, t.category, t.priority,
                             t.due_date, "Yes" if t.done else "No",
                             t.created, t.completed])
        return len(tasks)

    def export_txt(self, path: str) -> int:
        tasks = self._tasks
        s = self.stats()
        sep = "═" * 62
        lines = [
            sep,
            f"  {APP_NAME}  ·  Task Export",
            f"  Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"  Total: {s['total']}  ·  Done: {s['done']}  ·  Pending: {s['pending']}  ·  {s['pct']}%",
            sep, "",
        ]
        for i, t in enumerate(tasks, 1):
            tick  = "✓" if t.done else "○"
            icon  = PRI_ICON.get(t.priority_enum(), "")
            lines.append(f"  [{i}] {tick}  {t.title}  {icon}")
            lines.append(f"       Category : {t.category}  |  Priority : {t.priority}")
            if t.due_date:
                over = "  ⚠ OVERDUE" if t.is_overdue() else ""
                lines.append(f"       Due      : {t.due_display()}{over}")
            if t.notes:
                lines.append(f"       Notes    : {t.notes}")
            lines.append(f"       Created  : {t.created_display()}")
            lines.append("")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return len(tasks)


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 4 — STYLE SETUP
# ══════════════════════════════════════════════════════════════════════════════

def apply_styles(root: tk.Tk):
    """Configure all ttk widget styles once at startup."""
    s = ttk.Style(root)
    s.theme_use("clam")

    # ── Generic ──────────────────────────────────────────────────────────────
    s.configure("TFrame",       background=C.BG)
    s.configure("TLabel",       background=C.BG, foreground=C.TXT,
                                font=F.BODY)
    s.configure("TEntry",       fieldbackground=C.ENTRY_BG,
                                foreground=C.TXT, borderwidth=1,
                                relief="flat")

    # ── Sidebar frame ─────────────────────────────────────────────────────────
    s.configure("Sidebar.TFrame",  background=C.SIDEBAR)
    s.configure("Sidebar.TLabel",  background=C.SIDEBAR, foreground=C.TXT,
                                   font=F.BODY)

    # ── Treeview ─────────────────────────────────────────────────────────────
    s.configure("Treeview",
                background=C.ODD_ROW,
                fieldbackground=C.ODD_ROW,
                foreground=C.TXT,
                rowheight=28,
                font=F.TREE,
                borderwidth=0,
                relief="flat")
    s.configure("Treeview.Heading",
                background=C.BG2,
                foreground=C.TXT,
                font=F.TREE_H,
                relief="flat",
                padding=(6, 4))
    s.map("Treeview",
          background=[("selected", C.SEL_ROW)],
          foreground=[("selected", C.TXT)])
    s.map("Treeview.Heading",
          background=[("active", C.BORDER)])

    # ── Combobox ─────────────────────────────────────────────────────────────
    s.configure("TCombobox",
                fieldbackground=C.ENTRY_BG,
                background=C.BG,
                foreground=C.TXT,
                selectbackground=C.SEL_ROW,
                font=F.BODY)
    s.map("TCombobox",
          fieldbackground=[("readonly", C.ENTRY_BG)],
          selectbackground=[("readonly", C.SEL_ROW)],
          selectforeground=[("readonly", C.TXT)])

    # ── Scrollbar ─────────────────────────────────────────────────────────────
    s.configure("Vertical.TScrollbar",
                background=C.BG2, troughcolor=C.BG,
                arrowcolor=C.TXT3, borderwidth=0, relief="flat")
    s.configure("Horizontal.TScrollbar",
                background=C.BG2, troughcolor=C.BG,
                arrowcolor=C.TXT3, borderwidth=0, relief="flat")

    # ── Separator ─────────────────────────────────────────────────────────────
    s.configure("TSeparator", background=C.BORDER)

    # ── Radio buttons ─────────────────────────────────────────────────────────
    s.configure("TRadiobutton", background=C.BG, foreground=C.TXT,
                                font=F.SMALL)
    s.map("TRadiobutton", background=[("active", C.BG)])

    # ── Checkbutton ───────────────────────────────────────────────────────────
    s.configure("TCheckbutton", background=C.BG, foreground=C.TXT,
                                font=F.BODY)
    s.map("TCheckbutton", background=[("active", C.BG)])


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 5 — REUSABLE UI HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def make_button(parent, text, bg, hover_bg, cmd, width=None, icon=""):
    """Creates a styled flat tk.Button with hover animation."""
    label = f"{icon}  {text}" if icon else text
    kw = dict(
        text=label,
        bg=bg, fg=C.BTN_FG,
        activebackground=hover_bg,
        activeforeground=C.BTN_FG,
        font=F.BTN, relief="flat",
        bd=0, cursor="hand2",
        padx=12, pady=6,
        command=cmd,
    )
    if width:
        kw["width"] = width
    btn = tk.Button(parent, **kw)
    btn.bind("<Enter>", lambda _: btn.config(bg=hover_bg))
    btn.bind("<Leave>", lambda _: btn.config(bg=bg))
    return btn


def make_label(parent, text, font=None, fg=None, bg=None, **kw):
    return tk.Label(
        parent, text=text,
        font=font or F.BODY,
        fg=fg or C.TXT,
        bg=bg or C.BG,
        **kw,
    )


def labeled_entry(parent, label_text, bg=C.BG, entry_width=30):
    """Returns (frame, entry_var, entry_widget)."""
    var  = tk.StringVar()
    frm  = tk.Frame(parent, bg=bg)
    make_label(frm, label_text, font=F.SMALL, fg=C.TXT2, bg=bg).pack(anchor="w")
    ent  = tk.Entry(
        frm, textvariable=var, width=entry_width,
        bg=C.ENTRY_BG, fg=C.TXT, relief="solid",
        bd=1, font=F.BODY, highlightthickness=1,
        highlightbackground=C.ENTRY_BD,
        highlightcolor=C.FOCUS_BD,
        insertbackground=C.TXT,
    )
    ent.pack(fill="x")
    return frm, var, ent


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 6 — STATS PANEL  (left sidebar)
# ══════════════════════════════════════════════════════════════════════════════

class StatsPanel(tk.Frame):
    """
    Left-side dashboard showing:
      • 4 stat cards (Total, Done, Pending, %)
      • Priority breakdown
      • Overdue count
    Auto-refreshes when `refresh(stats_dict)` is called.
    """

    def __init__(self, parent, **kw):
        super().__init__(parent, bg=C.SIDEBAR, width=190, **kw)
        self.pack_propagate(False)
        self._vars: dict = {}
        self._build()

    # ── Construction ─────────────────────────────────────────────────────────
    def _build(self):
        # ── App branding ─────────────────────────────────────────────────────
        tk.Label(
            self, text="🗒️", font=("Segoe UI Emoji", 32),
            bg=C.SIDEBAR,
        ).pack(pady=(20, 0))
        tk.Label(
            self, text=APP_NAME, font=F.TITLE,
            bg=C.SIDEBAR, fg=C.TXT,
        ).pack()
        tk.Label(
            self, text=f"v{VERSION}", font=F.MICRO,
            bg=C.SIDEBAR, fg=C.TXT3,
        ).pack(pady=(0, 14))

        tk.Frame(self, bg=C.BORDER, height=1).pack(fill="x", padx=16)

        # ── Stat cards ────────────────────────────────────────────────────────
        cards = [
            ("total",   "Total",     C.S_TOTAL),
            ("done",    "Completed", C.S_DONE),
            ("pending", "Pending",   C.S_PEND),
            ("pct",     "Done %",    C.BTN_EDIT),
        ]
        tk.Label(self, text="OVERVIEW", font=F.MICRO,
                 bg=C.SIDEBAR, fg=C.TXT3).pack(anchor="w", padx=16, pady=(12, 4))

        for key, lbl, colour in cards:
            self._stat_card(key, lbl, colour)

        tk.Frame(self, bg=C.BORDER, height=1).pack(fill="x", padx=16, pady=10)

        # ── Priority breakdown ────────────────────────────────────────────────
        tk.Label(self, text="PRIORITY BREAKDOWN", font=F.MICRO,
                 bg=C.SIDEBAR, fg=C.TXT3).pack(anchor="w", padx=16, pady=(0, 6))

        for key, lbl, dot in [
            ("high",   "High",   C.HIGH_TAG),
            ("medium", "Medium", C.MED_TAG),
            ("low",    "Low",    C.LOW_TAG),
        ]:
            self._pri_row(key, lbl, dot)

        tk.Frame(self, bg=C.BORDER, height=1).pack(fill="x", padx=16, pady=10)

        # ── Overdue ───────────────────────────────────────────────────────────
        self._pri_row("overdue", "Overdue ⚠", C.BTN_DEL)

        # ── Spacer ────────────────────────────────────────────────────────────
        tk.Frame(self, bg=C.SIDEBAR).pack(fill="both", expand=True)

        # ── Save path note ────────────────────────────────────────────────────
        tk.Frame(self, bg=C.BORDER, height=1).pack(fill="x", padx=16)
        tk.Label(
            self,
            text="Auto-saved to:\ntodo_pro_data.json",
            font=F.MICRO, bg=C.SIDEBAR, fg=C.TXT3,
            justify="center",
        ).pack(pady=10)

    def _stat_card(self, key: str, label: str, colour: str):
        """A coloured number + label mini-card."""
        frm = tk.Frame(self, bg=C.WHITE, bd=0)
        frm.pack(fill="x", padx=14, pady=3, ipady=4)

        left = tk.Frame(frm, bg=colour, width=5)
        left.pack(side="left", fill="y")

        inner = tk.Frame(frm, bg=C.WHITE)
        inner.pack(side="left", fill="both", expand=True, padx=8, pady=2)

        num_var = tk.StringVar(value="0")
        self._vars[key] = num_var

        tk.Label(inner, textvariable=num_var, font=F.STAT_N,
                 bg=C.WHITE, fg=colour, anchor="w").pack(anchor="w")
        tk.Label(inner, text=label, font=F.STAT_L,
                 bg=C.WHITE, fg=C.TXT2, anchor="w").pack(anchor="w")

    def _pri_row(self, key: str, label: str, dot_colour: str):
        frm = tk.Frame(self, bg=C.SIDEBAR)
        frm.pack(fill="x", padx=16, pady=2)

        tk.Label(frm, text="●", font=F.BODY, bg=C.SIDEBAR,
                 fg=dot_colour).pack(side="left")

        tk.Label(frm, text=f" {label}", font=F.SMALL,
                 bg=C.SIDEBAR, fg=C.TXT2).pack(side="left")

        num_var = tk.StringVar(value="0")
        self._vars[key] = num_var
        tk.Label(frm, textvariable=num_var, font=F.BODY_B,
                 bg=C.SIDEBAR, fg=C.TXT, anchor="e").pack(side="right")

    # ── Public API ───────────────────────────────────────────────────────────
    def refresh(self, s: dict):
        """Update all stat variables from a stats dict."""
        for key, var in self._vars.items():
            val = s.get(key, 0)
            var.set(f"{val}%" if key == "pct" else str(val))


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 7 — FILTER / SEARCH BAR
# ══════════════════════════════════════════════════════════════════════════════

class FilterBar(tk.Frame):
    """
    A horizontal control strip with:
      search entry · status combo · priority combo · category combo ·
      sort combo · asc/desc toggle · Clear button
    Calls `on_change()` whenever any control changes.
    """

    def __init__(self, parent, on_change, categories: List[str], **kw):
        super().__init__(parent, bg=C.BG2, **kw)
        self._on_change  = on_change
        self._categories = categories
        self._build()

    # ── Construction ─────────────────────────────────────────────────────────
    def _build(self):
        pad = dict(padx=4, pady=6)

        # ── Search ────────────────────────────────────────────────────────────
        tk.Label(self, text="🔍", font=("Segoe UI Emoji", 13),
                 bg=C.BG2).pack(side="left", padx=(10, 2), pady=6)

        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._on_change())
        search_ent = tk.Entry(
            self, textvariable=self._search_var, width=22,
            bg=C.ENTRY_BG, fg=C.TXT, relief="solid", bd=1,
            font=F.BODY, highlightthickness=1,
            highlightbackground=C.ENTRY_BD, highlightcolor=C.FOCUS_BD,
            insertbackground=C.TXT,
        )
        search_ent.pack(side="left", **pad)

        self._sep("Status")

        # ── Status ────────────────────────────────────────────────────────────
        self._status_var = tk.StringVar(value="All")
        self._status_var.trace_add("write", lambda *_: self._on_change())
        ttk.Combobox(
            self, textvariable=self._status_var, state="readonly",
            values=["All", "Pending", "Completed", "Overdue"],
            width=10, font=F.SMALL,
        ).pack(side="left", **pad)

        self._sep("Priority")

        # ── Priority ─────────────────────────────────────────────────────────
        self._pri_var = tk.StringVar(value="All")
        self._pri_var.trace_add("write", lambda *_: self._on_change())
        ttk.Combobox(
            self, textvariable=self._pri_var, state="readonly",
            values=["All"] + PRI_VALUES,
            width=9, font=F.SMALL,
        ).pack(side="left", **pad)

        self._sep("Category")

        # ── Category ─────────────────────────────────────────────────────────
        self._cat_var = tk.StringVar(value="All")
        self._cat_var.trace_add("write", lambda *_: self._on_change())
        self._cat_combo = ttk.Combobox(
            self, textvariable=self._cat_var, state="readonly",
            values=["All"] + self._categories,
            width=10, font=F.SMALL,
        )
        self._cat_combo.pack(side="left", **pad)

        self._sep("Sort")

        # ── Sort ─────────────────────────────────────────────────────────────
        self._sort_var = tk.StringVar(value="Created")
        self._sort_var.trace_add("write", lambda *_: self._on_change())
        ttk.Combobox(
            self, textvariable=self._sort_var, state="readonly",
            values=["Created", "Due Date", "Priority", "Title"],
            width=10, font=F.SMALL,
        ).pack(side="left", **pad)

        # ── Asc / Desc toggle ─────────────────────────────────────────────────
        self._asc_var = tk.BooleanVar(value=True)
        self._asc_btn = tk.Button(
            self, text="↑ Asc", font=F.SMALL,
            bg=C.BTN_ADD, fg=C.BTN_FG, relief="flat", bd=0,
            padx=8, pady=4, cursor="hand2",
            command=self._toggle_asc,
        )
        self._asc_btn.pack(side="left", padx=4)

        # ── Clear button ──────────────────────────────────────────────────────
        make_button(self, "Clear", C.TXT3, C.TXT2, self.clear, icon="✕").pack(
            side="left", padx=(8, 4))

    def _sep(self, label: str):
        tk.Label(self, text=label, font=F.MICRO,
                 bg=C.BG2, fg=C.TXT3).pack(side="left", padx=(8, 2))

    def _toggle_asc(self):
        self._asc_var.set(not self._asc_var.get())
        self._asc_btn.config(
            text="↑ Asc" if self._asc_var.get() else "↓ Desc",
            bg=C.BTN_ADD if self._asc_var.get() else C.BTN_EDIT,
        )
        self._on_change()

    # ── Public API ───────────────────────────────────────────────────────────
    def get_params(self) -> dict:
        return {
            "search":    self._search_var.get(),
            "status":    self._status_var.get(),
            "priority":  self._pri_var.get(),
            "category":  self._cat_var.get(),
            "sort_by":   self._sort_var.get(),
            "ascending": self._asc_var.get(),
        }

    def clear(self):
        self._search_var.set("")
        self._status_var.set("All")
        self._pri_var.set("All")
        self._cat_var.set("All")
        self._sort_var.set("Created")
        self._asc_var.set(True)
        self._asc_btn.config(text="↑ Asc", bg=C.BTN_ADD)
        self._on_change()

    def update_categories(self, cats: List[str]):
        self._cat_combo.configure(values=["All"] + cats)


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 8 — TASK TABLE  (ttk.Treeview with colour-coded rows)
# ══════════════════════════════════════════════════════════════════════════════

COLUMNS = [
    ("done",      "✓",          35),
    ("priority",  "Priority",   80),
    ("title",     "Title",      240),
    ("category",  "Category",   100),
    ("due",       "Due Date",   100),
    ("created",   "Created",    100),
    ("notes",     "Notes",      180),
]


class TaskTable(tk.Frame):
    """
    Scrollable ttk.Treeview that displays filtered/sorted tasks.
    Row colours reflect priority & done state.
    Double-click or Enter triggers `on_edit`.
    """

    def __init__(self, parent, on_select, on_edit, **kw):
        super().__init__(parent, bg=C.BG, **kw)
        self._on_select = on_select
        self._on_edit   = on_edit
        self._row_ids: List[str] = []   # task IDs in display order
        self._build()

    # ── Construction ─────────────────────────────────────────────────────────
    def _build(self):
        cols = [c[0] for c in COLUMNS]
        self._tree = ttk.Treeview(
            self, columns=cols, show="headings",
            selectmode="browse",
        )

        # ── Column headers & widths ───────────────────────────────────────────
        for col_id, heading, width in COLUMNS:
            self._tree.heading(col_id, text=heading,
                               command=lambda c=col_id: self._sort_col(c))
            self._tree.column(col_id, width=width, minwidth=30,
                               anchor="center" if col_id in ("done", "priority") else "w")

        # ── Row colour tags ───────────────────────────────────────────────────
        self._tree.tag_configure("high",    background=C.HIGH_ROW, foreground=C.HIGH_FG)
        self._tree.tag_configure("medium",  background=C.MED_ROW,  foreground=C.MED_FG)
        self._tree.tag_configure("low",     background=C.LOW_ROW,  foreground=C.LOW_FG)
        self._tree.tag_configure("done",    background=C.DONE_ROW, foreground=C.DONE_FG)
        self._tree.tag_configure("overdue", background=C.OVER_ROW, foreground=C.HIGH_FG)
        self._tree.tag_configure("odd",     background=C.ODD_ROW)
        self._tree.tag_configure("even",    background=C.EVEN_ROW)

        # ── Scrollbars ────────────────────────────────────────────────────────
        vsb = ttk.Scrollbar(self, orient="vertical",   command=self._tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self._tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # ── Bindings ─────────────────────────────────────────────────────────
        self._tree.bind("<<TreeviewSelect>>", self._on_sel)
        self._tree.bind("<Double-1>",         self._on_dbl)
        self._tree.bind("<Return>",           self._on_dbl)

        # ── Empty-state label ─────────────────────────────────────────────────
        self._empty_lbl = tk.Label(
            self, text="No tasks yet — click '+ Add' to get started 🌱",
            font=F.BODY, bg=C.BG, fg=C.TXT3,
        )

    # ── Populate ─────────────────────────────────────────────────────────────
    def populate(self, tasks: List[Task]):
        """Clear and repopulate the tree from `tasks`."""
        for item in self._tree.get_children():
            self._tree.delete(item)
        self._row_ids = []

        if not tasks:
            self._empty_lbl.place(relx=0.5, rely=0.5, anchor="center")
            return
        self._empty_lbl.place_forget()

        for i, t in enumerate(tasks):
            tag = self._row_tag(t, i)
            pri = f"{PRI_ICON.get(t.priority_enum(), '')} {t.priority}"
            done_mark = "✓" if t.done else ""
            due_disp  = t.due_display()
            if t.is_overdue():
                due_disp = f"⚠ {due_disp}"

            self._tree.insert(
                "", "end", iid=t.id,
                values=(done_mark, pri, t.title, t.category,
                        due_disp, t.created_display(), t.notes),
                tags=(tag,),
            )
            self._row_ids.append(t.id)

    def _row_tag(self, t: Task, idx: int) -> str:
        if t.done:
            return "done"
        if t.is_overdue():
            return "overdue"
        p = t.priority_enum()
        if p == Priority.HIGH:
            return "high"
        if p == Priority.MEDIUM:
            return "medium"
        return "low"

    # ── Selection / events ────────────────────────────────────────────────────
    def _on_sel(self, _=None):
        sel = self._tree.selection()
        self._on_select(sel[0] if sel else None)

    def _on_dbl(self, _=None):
        sel = self._tree.selection()
        if sel:
            self._on_edit(sel[0])

    def _sort_col(self, col_id: str):
        """Clicking a column header re-sorts (stub — real sort is in FilterBar)."""
        pass  # Sorting is handled by the filter/sort controls

    def selected_id(self) -> Optional[str]:
        sel = self._tree.selection()
        return sel[0] if sel else None

    def select_id(self, task_id: str):
        try:
            self._tree.selection_set(task_id)
            self._tree.see(task_id)
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 9 — TASK DIALOG  (Add / Edit modal)
# ══════════════════════════════════════════════════════════════════════════════

class TaskDialog(tk.Toplevel):
    """
    Modal dialog for creating or editing a task.
    Returns the saved Task via `self.result` after the window closes.
    Uses tkcalendar.DateEntry if available, otherwise a plain Entry.
    """

    def __init__(self, parent, manager: TaskManager,
                 task: Optional[Task] = None):
        super().__init__(parent)
        self.manager  = manager
        self.task     = task          # None  →  Add mode
        self.result: Optional[Task] = None
        self._editing = task is not None

        self.title("Edit Task" if self._editing else "Add New Task")
        self.configure(bg=C.BG)
        self.resizable(False, False)
        self.grab_set()
        self._build()
        self._center(parent)
        # Pre-fill if editing
        if self._editing:
            self._prefill()
        self.wait_window()

    # ── Build UI ─────────────────────────────────────────────────────────────
    def _build(self):
        # ── Header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=C.HEADER)
        hdr.pack(fill="x")
        icon = "✏️" if self._editing else "➕"
        tk.Label(
            hdr,
            text=f"  {icon}  {'Edit Task' if self._editing else 'New Task'}",
            font=F.SECTION, bg=C.HEADER, fg=C.HEADER_FG,
        ).pack(side="left", pady=12, padx=10)

        # ── Body ──────────────────────────────────────────────────────────────
        body = tk.Frame(self, bg=C.BG, padx=20, pady=12)
        body.pack(fill="both", expand=True)

        # Title
        frm, self._title_var, title_ent = labeled_entry(body, "Task Title *", entry_width=42)
        frm.pack(fill="x", pady=(0, 8))
        title_ent.focus_set()

        # Notes
        make_label(body, "Notes", font=F.SMALL, fg=C.TXT2).pack(anchor="w")
        self._notes_text = tk.Text(
            body, height=3, width=44,
            bg=C.ENTRY_BG, fg=C.TXT, relief="solid", bd=1,
            font=F.BODY, wrap="word",
            highlightthickness=1, highlightbackground=C.ENTRY_BD,
            highlightcolor=C.FOCUS_BD, insertbackground=C.TXT,
        )
        self._notes_text.pack(fill="x", pady=(0, 8))

        # Row: Priority + Category
        row1 = tk.Frame(body, bg=C.BG)
        row1.pack(fill="x", pady=(0, 8))

        # Priority
        pri_frm = tk.Frame(row1, bg=C.BG)
        pri_frm.pack(side="left", padx=(0, 12))
        make_label(pri_frm, "Priority", font=F.SMALL, fg=C.TXT2).pack(anchor="w")
        self._pri_var = tk.StringVar(value=Priority.LOW.value)
        ttk.Combobox(
            pri_frm, textvariable=self._pri_var,
            values=PRI_VALUES, state="readonly", width=12, font=F.BODY,
        ).pack()

        # Category
        cat_frm = tk.Frame(row1, bg=C.BG)
        cat_frm.pack(side="left")
        make_label(cat_frm, "Category", font=F.SMALL, fg=C.TXT2).pack(anchor="w")
        cats = manager_cats = self.manager.all_categories()
        self._cat_var = tk.StringVar(value="Personal")
        self._cat_combo = ttk.Combobox(
            cat_frm, textvariable=self._cat_var,
            values=cats, width=16, font=F.BODY,
        )
        self._cat_combo.pack()

        # Due date
        make_label(body, "Due Date (optional)", font=F.SMALL, fg=C.TXT2).pack(anchor="w")
        due_frm = tk.Frame(body, bg=C.BG)
        due_frm.pack(anchor="w", pady=(0, 8))

        if HAS_CALENDAR:
            self._due_entry = DateEntry(
                due_frm, width=18, background=C.HEADER,
                foreground=C.HEADER_FG, borderwidth=2,
                font=F.BODY, date_pattern="yyyy-mm-dd",
                showweeknumbers=False,
            )
            self._due_entry.pack(side="left")
            self._use_date = tk.BooleanVar(value=False)
            chk = ttk.Checkbutton(
                due_frm, text="Set due date",
                variable=self._use_date,
                command=self._toggle_date,
            )
            chk.pack(side="left", padx=8)
            self._due_entry.configure(state="disabled")
        else:
            # Fallback: plain entry
            self._due_var = tk.StringVar()
            tk.Entry(
                due_frm, textvariable=self._due_var, width=16,
                bg=C.ENTRY_BG, fg=C.TXT, relief="solid", bd=1,
                font=F.BODY, highlightthickness=1,
                highlightbackground=C.ENTRY_BD, highlightcolor=C.FOCUS_BD,
                insertbackground=C.TXT,
            ).pack(side="left")
            make_label(due_frm, "  YYYY-MM-DD", font=F.MICRO, fg=C.TXT3).pack(side="left")
            self._use_date = tk.BooleanVar(value=False)

        # ── Validation message ─────────────────────────────────────────────────
        self._err_var = tk.StringVar()
        tk.Label(body, textvariable=self._err_var, font=F.SMALL,
                 fg=C.BTN_DEL, bg=C.BG).pack(anchor="w")

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_row = tk.Frame(body, bg=C.BG)
        btn_row.pack(fill="x", pady=(4, 0))

        make_button(btn_row, "Cancel", C.TXT3, C.TXT2,
                    self.destroy).pack(side="left")
        lbl = "Save Changes" if self._editing else "Add Task"
        make_button(btn_row, lbl, C.BTN_ADD, C.BTN_ADD_H,
                    self._save, icon="💾").pack(side="right")

        # Keyboard shortcut
        self.bind("<Return>", lambda _: self._save())
        self.bind("<Escape>", lambda _: self.destroy())

    def _toggle_date(self):
        if HAS_CALENDAR:
            state = "normal" if self._use_date.get() else "disabled"
            self._due_entry.configure(state=state)

    # ── Pre-fill for editing ──────────────────────────────────────────────────
    def _prefill(self):
        t = self.task
        self._title_var.set(t.title)
        self._notes_text.insert("1.0", t.notes)
        self._pri_var.set(t.priority)
        self._cat_var.set(t.category)
        if t.due_date:
            self._use_date.set(True)
            if HAS_CALENDAR:
                try:
                    self._due_entry.set_date(date.fromisoformat(t.due_date))
                    self._due_entry.configure(state="normal")
                except Exception:
                    pass
            else:
                self._due_var.set(t.due_date)

    # ── Save ─────────────────────────────────────────────────────────────────
    def _save(self):
        title = self._title_var.get().strip()
        if not title:
            self._err_var.set("⚠  Task title is required.")
            return

        notes = self._notes_text.get("1.0", "end-1c").strip()
        cat   = self._cat_var.get().strip() or "Personal"
        pri   = self._pri_var.get()

        # Due date
        due = ""
        if self._use_date.get():
            if HAS_CALENDAR:
                try:
                    due = self._due_entry.get_date().isoformat()
                except Exception:
                    pass
            else:
                raw = self._due_var.get().strip()
                if raw:
                    try:
                        date.fromisoformat(raw)
                        due = raw
                    except ValueError:
                        self._err_var.set("⚠  Date must be YYYY-MM-DD.")
                        return

        if self._editing:
            self.task.title    = title
            self.task.notes    = notes
            self.task.category = cat
            self.task.priority = pri
            self.task.due_date = due
            self.result = self.task
        else:
            self.result = Task.new(
                title=title, notes=notes, category=cat,
                priority=pri, due_date=due,
            )
        self.destroy()

    # ── Center on parent ─────────────────────────────────────────────────────
    def _center(self, parent: tk.Tk):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        px   = parent.winfo_rootx() + parent.winfo_width()  // 2 - w // 2
        py   = parent.winfo_rooty() + parent.winfo_height() // 2 - h // 2
        self.geometry(f"+{max(0, px)}+{max(0, py)}")


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 10 — STATUS BAR
# ══════════════════════════════════════════════════════════════════════════════

class StatusBar(tk.Frame):
    """One-line status strip at the bottom of the window."""

    def __init__(self, parent, **kw):
        super().__init__(parent, bg=C.STATUS_BG, height=24, **kw)
        self._var = tk.StringVar()
        tk.Label(
            self, textvariable=self._var,
            font=F.STATUS, bg=C.STATUS_BG, fg=C.STATUS_FG,
            anchor="w", padx=10,
        ).pack(side="left", fill="both", expand=True)

        # Right: calendar indicator
        tk.Label(
            self,
            text=f"  {APP_NAME} v{VERSION}  ·  "
                 f"{'Calendar ✓' if HAS_CALENDAR else 'No calendar (pip install tkcalendar)'}",
            font=F.STATUS, bg=C.STATUS_BG, fg=C.STATUS_FG,
            anchor="e", padx=10,
        ).pack(side="right")

    def set(self, msg: str, colour: str = C.STATUS_FG):
        self._var.set(f"  {msg}")


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 11 — MAIN APP WINDOW
# ══════════════════════════════════════════════════════════════════════════════

class App(tk.Tk):
    """
    Root application window.  Coordinates all panels:
      StatsPanel  |  FilterBar
                  |  TaskTable
                  |  StatusBar
    """

    def __init__(self):
        super().__init__()
        self.title(f"🗒️  {APP_NAME}")
        self.geometry("1180x680")
        self.minsize(920, 520)
        self.configure(bg=C.BG)

        apply_styles(self)

        self.manager = TaskManager()

        self._build_ui()
        self.refresh()
        self.status.set(f"Loaded {len(self.manager.tasks)} task(s) from disk.")

    # ── UI construction ───────────────────────────────────────────────────────
    def _build_ui(self):
        self._build_header()

        # ── Horizontal split: sidebar | main ─────────────────────────────────
        body = tk.Frame(self, bg=C.BG)
        body.pack(fill="both", expand=True)

        self.stats_panel = StatsPanel(body)
        self.stats_panel.pack(side="left", fill="y")

        # Thin divider
        tk.Frame(body, bg=C.BORDER, width=1).pack(side="left", fill="y")

        main = tk.Frame(body, bg=C.BG)
        main.pack(side="left", fill="both", expand=True)

        # ── Filter bar ────────────────────────────────────────────────────────
        self.filter_bar = FilterBar(
            main,
            on_change=self.refresh,
            categories=self.manager.all_categories(),
        )
        self.filter_bar.pack(fill="x")

        tk.Frame(main, bg=C.BORDER, height=1).pack(fill="x")

        # ── Task table ────────────────────────────────────────────────────────
        self.table = TaskTable(
            main,
            on_select=self._on_select,
            on_edit=self._cmd_edit,
        )
        self.table.pack(fill="both", expand=True, padx=0, pady=0)

        # ── Status bar ────────────────────────────────────────────────────────
        self.status = StatusBar(self)
        self.status.pack(fill="x", side="bottom")

        # ── Keyboard shortcuts ────────────────────────────────────────────────
        self.bind("<Control-n>", lambda _: self._cmd_add())
        self.bind("<Control-e>", lambda _: self._cmd_edit())
        self.bind("<Delete>",    lambda _: self._cmd_delete())
        self.bind("<space>",     lambda _: self._cmd_toggle())
        self.bind("<Control-z>", lambda _: self._cmd_undo())
        self.bind("<F5>",        lambda _: self.refresh())

    def _build_header(self):
        hdr = tk.Frame(self, bg=C.HEADER)
        hdr.pack(fill="x")

        # ── Left: title ───────────────────────────────────────────────────────
        tk.Label(
            hdr, text=f"  🗒️  {APP_NAME}",
            font=F.TITLE, bg=C.HEADER, fg=C.HEADER_FG,
        ).pack(side="left", pady=10)

        # ── Right: toolbar ────────────────────────────────────────────────────
        toolbar = tk.Frame(hdr, bg=C.HEADER)
        toolbar.pack(side="right", padx=10, pady=8)

        # Helper — makes a toolbar button and packs it immediately
        def tb(text, bg, hover, cmd, icon=""):
            btn = make_button(toolbar, text, bg, hover, cmd, icon=icon)
            btn.pack(side="left", padx=3)
            return btn

        tb("Add",    C.BTN_ADD,  C.BTN_ADD_H,  self._cmd_add,    "➕")
        tb("Edit",   C.BTN_EDIT, C.BTN_EDIT_H, self._cmd_edit,   "✏️")
        tb("Delete", C.BTN_DEL,  C.BTN_DEL_H,  self._cmd_delete, "🗑")
        tk.Frame(toolbar, bg=C.HEADER, width=12).pack(side="left")
        tb("Toggle ✓", C.BTN_UNDO, C.BTN_UNDO_H, self._cmd_toggle, "✓")
        tk.Frame(toolbar, bg=C.HEADER, width=12).pack(side="left")

        self._undo_btn = tb("Undo", C.BTN_UNDO, C.BTN_UNDO_H, self._cmd_undo, "↩")
        tk.Frame(toolbar, bg=C.HEADER, width=12).pack(side="left")
        tb("Export ▾", C.BTN_EXP, C.BTN_EXP_H, self._cmd_export, "📤")

        # Keyboard hint
        tk.Label(
            hdr, text="  Ctrl+N Add  ·  Ctrl+E Edit  ·  Del Delete  ·  Space Toggle  ·  Ctrl+Z Undo",
            font=F.MICRO, bg=C.HEADER, fg="#C4C0FF",
        ).pack(side="left", padx=10)

    # ── Internal state ────────────────────────────────────────────────────────
    def _on_select(self, task_id: Optional[str]):
        self._selected_id = task_id

    @property
    def _selected_id(self):
        return getattr(self, "__selected", None)

    @_selected_id.setter
    def _selected_id(self, v):
        self.__selected = v

    # ── Refresh (re-read filter → re-populate table → update stats) ───────────
    def refresh(self):
        params  = self.filter_bar.get_params()
        tasks   = self.manager.filter_tasks(**params)
        self.table.populate(tasks)

        stats = self.manager.stats()
        self.stats_panel.refresh(stats)
        self.filter_bar.update_categories(self.manager.all_categories())

        # Update undo button tooltip / state
        if self.manager.can_undo:
            self._undo_btn.config(
                bg=C.BTN_UNDO,
                text=f"↩  Undo ({self.manager.undo_label})",
            )
        else:
            self._undo_btn.config(bg=C.TXT3, text="↩  Undo")

    # ── Commands ──────────────────────────────────────────────────────────────
    def _cmd_add(self):
        dlg = TaskDialog(self, self.manager)
        if dlg.result:
            self.manager.add(dlg.result)
            self.refresh()
            self.table.select_id(dlg.result.id)
            self.status.set(f"Added: '{dlg.result.title}'")

    def _cmd_edit(self, task_id: Optional[str] = None):
        tid = task_id or self._selected_id or self.table.selected_id()
        if not tid:
            self.status.set("Select a task to edit.")
            return
        task = self.manager.get(tid)
        if not task:
            return
        dlg = TaskDialog(self, self.manager, task=task)
        if dlg.result:
            self.manager.update(dlg.result)
            self.refresh()
            self.table.select_id(dlg.result.id)
            self.status.set(f"Updated: '{dlg.result.title}'")

    def _cmd_delete(self):
        tid = self._selected_id or self.table.selected_id()
        if not tid:
            self.status.set("Select a task to delete.")
            return
        task = self.manager.get(tid)
        if not task:
            return
        if messagebox.askyesno(
            "Delete Task",
            f"Permanently delete:\n\n  '{task.title}' ?\n\nThis can be undone with Ctrl+Z.",
            parent=self,
        ):
            self.manager.delete(tid)
            self.refresh()
            self.status.set(f"Deleted: '{task.title}' (Ctrl+Z to undo)")

    def _cmd_toggle(self):
        tid = self._selected_id or self.table.selected_id()
        if not tid:
            self.status.set("Select a task to toggle.")
            return
        t = self.manager.toggle_done(tid)
        if t:
            word = "Completed ✓" if t.done else "Re-opened"
            self.refresh()
            self.table.select_id(tid)
            self.status.set(f"{word}: '{t.title}'")

    def _cmd_undo(self):
        if not self.manager.can_undo:
            self.status.set("Nothing to undo.")
            return
        label = self.manager.undo()
        self.refresh()
        self.status.set(f"Undid: {label}")

    def _cmd_export(self):
        """Show a small popup to choose CSV or TXT."""
        popup = tk.Toplevel(self)
        popup.title("Export Tasks")
        popup.configure(bg=C.BG)
        popup.resizable(False, False)
        popup.grab_set()

        # Center on parent
        popup.update_idletasks()
        px = self.winfo_rootx() + self.winfo_width()  // 2 - 160
        py = self.winfo_rooty() + self.winfo_height() // 2 - 80
        popup.geometry(f"320x170+{px}+{py}")

        tk.Frame(popup, bg=C.HEADER).pack(fill="x")
        tk.Label(popup, text="  📤  Export Tasks", font=F.SECTION,
                 bg=C.HEADER, fg=C.HEADER_FG).pack(
            fill="x", pady=10, padx=10, in_=tk.Frame(popup, bg=C.HEADER))

        frm = tk.Frame(popup, bg=C.HEADER)
        frm.pack(fill="x")
        tk.Label(frm, text="  📤  Export Tasks", font=F.SECTION,
                 bg=C.HEADER, fg=C.HEADER_FG).pack(pady=10, padx=10, anchor="w")

        body = tk.Frame(popup, bg=C.BG)
        body.pack(fill="both", expand=True, padx=20, pady=12)
        make_label(body, "Choose export format:", font=F.BODY).pack(anchor="w", pady=(0, 10))

        btn_row = tk.Frame(body, bg=C.BG)
        btn_row.pack()

        def do_csv():
            popup.destroy()
            path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export as CSV",
                initialfile="tasks_export.csv",
            )
            if path:
                try:
                    n = self.manager.export_csv(path)
                    self.status.set(f"Exported {n} tasks → {os.path.basename(path)}")
                    messagebox.showinfo("Export Complete",
                                        f"Exported {n} tasks to:\n{path}", parent=self)
                except Exception as e:
                    messagebox.showerror("Export Failed", str(e), parent=self)

        def do_txt():
            popup.destroy()
            path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Export as TXT",
                initialfile="tasks_export.txt",
            )
            if path:
                try:
                    n = self.manager.export_txt(path)
                    self.status.set(f"Exported {n} tasks → {os.path.basename(path)}")
                    messagebox.showinfo("Export Complete",
                                        f"Exported {n} tasks to:\n{path}", parent=self)
                except Exception as e:
                    messagebox.showerror("Export Failed", str(e), parent=self)

        make_button(btn_row, "Export CSV", C.BTN_EXP, C.BTN_EXP_H,
                    do_csv, icon="📊").pack(side="left", padx=(0, 10))
        make_button(btn_row, "Export TXT", C.BTN_EDIT, C.BTN_EDIT_H,
                    do_txt, icon="📄").pack(side="left")

        make_button(body, "Cancel", C.TXT3, C.TXT2,
                    popup.destroy).pack(pady=(12, 0))


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = App()
    app.mainloop()
