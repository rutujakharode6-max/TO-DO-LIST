# 🌿 TO-DO LIST — Botanical Productivity App

A **Pinterest-worthy** To-Do List app built in **two flavours**:

| Flavour | Tech | File |
|---------|------|------|
| 🖥️ Desktop GUI | Python · CustomTkinter | `botanical_todo.py` |
| 🌐 Web App | HTML · CSS · JavaScript | `botanical_web/index.html` |
| 🗒️ Advanced Pro | Python · Tkinter · OOP | `todo_pro.py` |

---

## ✨ Features

### 🌿 Botanical To-Do (Desktop + Web)
- Soft **pastel mint · sage · cream · peach** colour palette
- 🍃 **Animated floating leaf** emojis as decorative elements
- **Gradient background** (light & dark mode)
- **Sidebar** with categories: Work · Personal · Study · Health
- **Smooth hover animations** on all cards and buttons
- **Rounded corners** on every UI element
- Google Fonts — **Playfair Display + Poppins**
- **Dark mode toggle** with smooth transition
- **Search** tasks live + **quick-add** by pressing Enter
- **Priority colour coding** — 🔴 High · 🟡 Medium · 🟢 Low
- Due dates with overdue detection ⚠️
- **Auto-save** to localStorage (web) / JSON file (desktop)

### 🗒️ To-Do Pro (Advanced Desktop)
- Full **OOP architecture** with 6 classes
- `tkcalendar` date picker
- **Statistics dashboard** — Total · Done · Pending · %
- **Filter** by status · priority · category
- **Sort** by date · priority · title · creation
- **Export** to CSV or TXT
- **Undo** last action (up to 20 levels)
- Auto-save to `~/todo_pro_data.json`

---

## 🚀 Quick Start

### Web App (browser)
```bash
# Python 3 — no extra installs needed
python -m http.server 8080 --directory botanical_web
# Open http://localhost:8080
```

### Desktop App (CustomTkinter)
```bash
pip install customtkinter pillow
python botanical_todo.py
```

### Advanced Pro App
```bash
pip install tkcalendar
python todo_pro.py
```

---

## 📁 Project Structure

```
TO-DO-LIST/
├── botanical_web/
│   └── index.html          # Standalone web app (HTML + CSS + JS)
├── botanical_todo.py       # Desktop GUI — CustomTkinter
├── todo_pro.py             # Advanced OOP desktop app — Tkinter
├── requirements.txt        # Python dependencies
└── README.md
```

---

## 🎨 Design

| Element | Value |
|---------|-------|
| Primary font | Playfair Display (serif) |
| UI font | Poppins / Segoe UI |
| Mint accent | `#7BCFAB` |
| Sage accent | `#8DB8A0` |
| Peach accent | `#F4A96A` |
| Background | Gradient `#E8F5F0 → #FFF5ED` |

---

## 🛠️ Tech Stack

- **Python 3.10+**
- [`customtkinter`](https://github.com/TomSchimansky/CustomTkinter) ≥ 5.2
- [`tkcalendar`](https://pypi.org/project/tkcalendar/) ≥ 1.6
- **Vanilla HTML + CSS + JavaScript** (zero dependencies for web)

---

## 📸 Screenshots

> Light mode · Botanical pastel theme · Floating leaf animations

---

## 📄 License

MIT © 2026 rutujakharode6-max
