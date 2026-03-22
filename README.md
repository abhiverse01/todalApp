# todalApp ◈


> A minimal, focused task manager built with Streamlit.

![Python](https://img.shields.io/badge/Python-3.9+-1a1a1a?style=flat-square&labelColor=0e0e0e&color=c8f564)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-1a1a1a?style=flat-square&labelColor=0e0e0e&color=c8f564)
![License](https://img.shields.io/badge/License-MIT-1a1a1a?style=flat-square&labelColor=0e0e0e&color=c8f564)

---

## Preview

```
TASKS                          14:32
                                MONDAY
                          23 JAN 2025

  ┌──────────┬──────────┬──────────┐
  │    3     │    5     │   62%    │
  │ Pending  │Completed │ Done rate│
  └──────────┴──────────┴──────────┘

  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░  62% complete

  [ what needs to be done?        ADD ]

  active tasks ────────────────────────
  01  Design landing page       14:10  ✓  ✕
  02  Review pull requests      14:28  ✓  ✕
  03  Write weekly report       14:31  ✓  ✕
```

---

## Features

- **Add & complete tasks** — instant feedback, no page reload
- **Live stats** — pending count, completion count, done-rate percentage
- **Animated progress bar** — reflects completion ratio in real time
- **Task history** — completed tasks logged with timestamps, clearable on demand
- **Live clock** — pulsing timestamp in the header, updates on interaction
- **Zero-clutter UI** — all Streamlit chrome hidden, pure focused layout

---

## Stack

| Layer | Choice |
|---|---|
| Framework | [Streamlit](https://streamlit.io) |
| Fonts | Syne (display) · DM Mono (body) |
| State | `st.session_state` |
| Styling | Custom CSS injected via `st.markdown` |

---

## Getting Started

**1. Clone the repo**
```bash
git clone https://github.com/your-username/tasks-app.git
cd tasks-app
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run**
```bash
streamlit run todo_app.py
```

App opens at `http://localhost:8501`

---

## Project Structure

```
tasks-app/
├── todo_app.py        # Main application
├── requirements.txt   # Dependencies
└── README.md
```

---

## Deploy

**Streamlit Community Cloud** — free, one-click:

1. Push repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repo → set `todo_app.py` as entrypoint → **Deploy**

---

<div align="center">
  <sub>Built with <a href="https://streamlit.io">Streamlit</a> · Designed to stay out of your way.</sub>
</div>
