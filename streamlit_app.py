import streamlit as st
from datetime import datetime, date
import json
import random

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NEXUS TASKS",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state bootstrap ───────────────────────────────────────────────────
DEFAULTS = {
    "tasks": [],
    "completed": [],
    "input_key": 0,
    "filter_priority": "All",
    "filter_category": "All",
    "filter_status": "Active",
    "search_query": "",
    "sort_by": "Date Added",
    "edit_idx": None,
    "show_pomodoro": False,
    "pomo_running": False,
    "pomo_seconds": 1500,
    "pomo_start": None,
    "theme": "dark",
    "streak": 0,
    "total_ever_done": 0,
    "show_confetti": False,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Constants ─────────────────────────────────────────────────────────────────
PRIORITIES = {"🔴 Critical": "#ff4757", "🟠 High": "#ff6b35", "🟡 Medium": "#ffd32a", "🟢 Low": "#2ed573"}
CATEGORIES  = ["Work", "Personal", "Health", "Finance", "Learning", "Creative", "Errands"]
CAT_ICONS   = {"Work": "💼", "Personal": "🌿", "Health": "❤️", "Finance": "💰", "Learning": "📚", "Creative": "✦", "Errands": "🛒", "Uncategorized": "◈"}
QUOTES = [
    "Every task completed is a step toward your best self.",
    "Progress, not perfection.",
    "Small actions. Big outcomes.",
    "Focus is your superpower.",
    "Done is better than perfect.",
    "You are what you consistently do.",
]

# ── Helpers ───────────────────────────────────────────────────────────────────
def add_task(text, priority, category, due_date, notes):
    if text.strip():
        st.session_state.tasks.append({
            "id": datetime.now().timestamp(),
            "text": text.strip(),
            "priority": priority,
            "category": category,
            "due": str(due_date) if due_date else None,
            "notes": notes.strip() if notes else "",
            "added": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "pinned": False,
        })
        st.session_state.input_key += 1

def complete_task(idx):
    task = st.session_state.tasks.pop(idx)
    task["done"] = datetime.now().strftime("%H:%M · %d %b")
    st.session_state.completed.insert(0, task)
    st.session_state.total_ever_done += 1
    st.session_state.streak += 1
    if not st.session_state.tasks:
        st.session_state.show_confetti = True

def delete_task(idx):
    st.session_state.tasks.pop(idx)

def delete_completed(idx):
    st.session_state.completed.pop(idx)

def toggle_pin(idx):
    st.session_state.tasks[idx]["pinned"] = not st.session_state.tasks[idx]["pinned"]

def clear_history():
    st.session_state.completed = []

def move_up(idx):
    if idx > 0:
        tasks = st.session_state.tasks
        tasks[idx], tasks[idx-1] = tasks[idx-1], tasks[idx]

def move_down(idx):
    tasks = st.session_state.tasks
    if idx < len(tasks) - 1:
        tasks[idx], tasks[idx+1] = tasks[idx+1], tasks[idx]

def export_tasks():
    lines = ["NEXUS TASKS — EXPORT", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", "="*50, ""]
    lines.append("▸ ACTIVE TASKS")
    for t in st.session_state.tasks:
        p = t.get("priority","?")
        lines.append(f"  [{p}] {t['text']}  (Added: {t['added']})")
        if t.get("notes"): lines.append(f"      Notes: {t['notes']}")
    lines += ["", "▸ COMPLETED TASKS"]
    for t in st.session_state.completed:
        lines.append(f"  [✓] {t['text']}  (Done: {t.get('done','')})")
    return "\n".join(lines)

def get_filtered_tasks():
    tasks = st.session_state.tasks.copy()
    q = st.session_state.search_query.lower()
    if q:
        tasks = [t for t in tasks if q in t["text"].lower() or q in t.get("notes","").lower()]
    if st.session_state.filter_priority != "All":
        tasks = [t for t in tasks if t.get("priority") == st.session_state.filter_priority]
    if st.session_state.filter_category != "All":
        tasks = [t for t in tasks if t.get("category") == st.session_state.filter_category]
    sort = st.session_state.sort_by
    prio_order = list(PRIORITIES.keys())
    if sort == "Priority":
        tasks.sort(key=lambda t: prio_order.index(t.get("priority", prio_order[-1])) if t.get("priority") in prio_order else 99)
    elif sort == "Due Date":
        tasks.sort(key=lambda t: t.get("due") or "9999")
    elif sort == "Pinned First":
        tasks.sort(key=lambda t: not t.get("pinned", False))
    # pinned always on top if not sorting by pinned
    if sort != "Pinned First":
        tasks.sort(key=lambda t: not t.get("pinned", False))
    return tasks

# ── MEGA CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&family=Fira+Code:wght@300;400;500&display=swap');

:root {
  --bg:        #0a0a0f;
  --bg2:       #0f0f18;
  --bg3:       #141420;
  --surface:   #1a1a2e;
  --surface2:  #16213e;
  --border:    #ffffff0d;
  --border2:   #ffffff18;
  --text:      #e8e8f0;
  --text2:     #9090b0;
  --text3:     #404060;
  --accent:    #7c6af7;
  --accent2:   #a78bfa;
  --green:     #34d399;
  --red:       #ff4757;
  --orange:    #ff6b35;
  --yellow:    #ffd32a;
  --glow:      0 0 40px #7c6af720;
  --glow2:     0 0 80px #7c6af710;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Poppins', sans-serif !important;
}

/* ── Animated background ── */
[data-testid="stAppViewContainer"]::before {
  content: '';
  position: fixed;
  inset: 0;
  background:
    radial-gradient(ellipse 80% 50% at 20% 10%, #7c6af708 0%, transparent 60%),
    radial-gradient(ellipse 60% 40% at 80% 80%, #a78bfa06 0%, transparent 60%),
    radial-gradient(ellipse 40% 40% at 50% 50%, #34d39904 0%, transparent 60%);
  pointer-events: none;
  z-index: 0;
}

#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

/* ── Layout ── */
.block-container {
  max-width: 860px !important;
  padding: 2rem 1.5rem 5rem !important;
}
[data-testid="stSidebar"] {
  background: var(--bg2) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div { padding: 1.5rem 1rem !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #ffffff15; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #ffffff25; }

/* ══════════════ HEADER ══════════════ */
.nx-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border);
}
.nx-logo {
  display: flex;
  align-items: center;
  gap: 0.7rem;
}
.nx-logo-icon {
  width: 42px; height: 42px;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.2rem;
  box-shadow: 0 0 20px #7c6af740;
}
.nx-title {
  font-size: 1.6rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  background: linear-gradient(135deg, #e8e8f0 30%, var(--accent2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.1;
}
.nx-subtitle {
  font-size: 0.65rem;
  color: var(--text3);
  letter-spacing: 0.15em;
  text-transform: uppercase;
  font-weight: 500;
}
.nx-date-block {
  text-align: right;
}
.nx-time {
  font-family: 'Fira Code', monospace;
  font-size: 1.6rem;
  font-weight: 500;
  color: var(--text);
  letter-spacing: -0.02em;
  line-height: 1;
}
.nx-date {
  font-size: 0.65rem;
  color: var(--text3);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-top: 0.2rem;
}
.nx-quote {
  font-size: 0.7rem;
  color: var(--text3);
  font-style: italic;
  font-weight: 300;
  margin-top: 0.3rem;
}

/* ══════════════ STATS ══════════════ */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1px;
  background: var(--border);
  border: 1px solid var(--border);
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 1.5rem;
}
.stat-card {
  background: var(--bg3);
  padding: 1.1rem 1.2rem;
  position: relative;
  overflow: hidden;
  transition: background 0.2s;
}
.stat-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: var(--accent-color, transparent);
  opacity: 0.6;
}
.stat-card:hover { background: var(--surface); }
.stat-icon {
  font-size: 1rem;
  margin-bottom: 0.4rem;
  display: block;
}
.stat-num {
  font-size: 2.2rem;
  font-weight: 800;
  letter-spacing: -0.04em;
  line-height: 1;
  color: var(--stat-color, var(--text));
  font-family: 'Poppins', sans-serif;
}
.stat-label {
  font-size: 0.58rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--text3);
  font-weight: 600;
  margin-top: 0.2rem;
}

/* ══════════════ PROGRESS ══════════════ */
.prog-block {
  margin-bottom: 1.5rem;
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1rem 1.2rem;
}
.prog-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.6rem;
}
.prog-label {
  font-size: 0.65rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text3);
  font-weight: 600;
}
.prog-pct {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--accent2);
  font-family: 'Fira Code', monospace;
}
.prog-track {
  height: 4px;
  background: var(--border);
  border-radius: 4px;
  overflow: hidden;
}
.prog-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), var(--accent2), var(--green));
  border-radius: 4px;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 0 8px var(--accent);
}
.prog-milestones {
  display: flex;
  justify-content: space-between;
  margin-top: 0.4rem;
}
.milestone {
  font-size: 0.52rem;
  color: var(--text3);
  letter-spacing: 0.05em;
}

/* ══════════════ SEARCH BAR ══════════════ */
.search-wrap { margin-bottom: 1rem; }

/* ══════════════ FORM / INPUT ══════════════ */
.form-card {
  background: var(--bg3);
  border: 1px solid var(--border2);
  border-radius: 16px;
  padding: 1.2rem 1.4rem;
  margin-bottom: 1.5rem;
  position: relative;
  overflow: hidden;
}
.form-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--accent), var(--accent2), var(--green));
  opacity: 0.7;
}
.form-title {
  font-size: 0.62rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--text3);
  font-weight: 600;
  margin-bottom: 1rem;
}

/* ── All inputs ── */
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stSelectbox"] label,
[data-testid="stDateInput"] label { 
  font-size: 0.62rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
  color: var(--text3) !important;
  font-family: 'Poppins', sans-serif !important;
}

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
  background: var(--surface) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
  font-family: 'Poppins', sans-serif !important;
  font-size: 0.85rem !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 2px #7c6af720 !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder { color: var(--text3) !important; }

[data-testid="stSelectbox"] > div > div {
  background: var(--surface) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
}
[data-testid="stDateInput"] input {
  background: var(--surface) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
  font-family: 'Poppins', sans-serif !important;
}

/* ── Buttons ── */
[data-testid="stButton"] button {
  font-family: 'Poppins', sans-serif !important;
  font-weight: 600 !important;
  border-radius: 10px !important;
  transition: all 0.2s !important;
  cursor: pointer !important;
}
[data-testid="stButton"] button:hover { transform: translateY(-1px) !important; }
[data-testid="stButton"] button:active { transform: translateY(0) scale(0.98) !important; }

/* Primary add button */
.btn-add [data-testid="stButton"] button {
  background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
  color: white !important;
  border: none !important;
  font-size: 0.8rem !important;
  letter-spacing: 0.05em !important;
  padding: 0.65rem 1.5rem !important;
  box-shadow: 0 4px 15px #7c6af730 !important;
}
.btn-add [data-testid="stButton"] button:hover {
  box-shadow: 0 6px 20px #7c6af750 !important;
}

/* ══════════════ SECTION HEADERS ══════════════ */
.section-head {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  margin-bottom: 0.8rem;
  margin-top: 0.5rem;
}
.section-head-label {
  font-size: 0.6rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--text3);
  font-weight: 700;
}
.section-count {
  background: var(--surface);
  border: 1px solid var(--border2);
  border-radius: 20px;
  padding: 0.1rem 0.5rem;
  font-size: 0.6rem;
  font-weight: 700;
  color: var(--accent2);
  font-family: 'Fira Code', monospace;
}
.section-line {
  flex: 1;
  height: 1px;
  background: var(--border);
}

/* ══════════════ TASK CARDS ══════════════ */
.task-card {
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 0.9rem 1.1rem;
  margin-bottom: 8px;
  position: relative;
  overflow: hidden;
  transition: border-color 0.2s, background 0.2s, transform 0.15s;
  animation: taskEnter 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
@keyframes taskEnter {
  from { opacity: 0; transform: translateY(-10px) scale(0.98); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}
.task-card:hover {
  border-color: var(--border2);
  background: var(--surface);
  transform: translateY(-1px);
}
.task-card.pinned {
  border-color: #ffd32a40 !important;
  background: #ffd32a05 !important;
}
.task-priority-bar {
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 3px;
  border-radius: 14px 0 0 14px;
}
.task-header {
  display: flex;
  align-items: flex-start;
  gap: 0.7rem;
  margin-left: 0.4rem;
}
.task-main { flex: 1; min-width: 0; }
.task-text-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.task-text {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text);
  line-height: 1.4;
}
.task-text.overdue { color: var(--red); }
.task-pin-badge {
  font-size: 0.65rem;
  background: #ffd32a20;
  color: #ffd32a;
  border: 1px solid #ffd32a30;
  border-radius: 4px;
  padding: 0.05rem 0.4rem;
  font-weight: 600;
  letter-spacing: 0.05em;
}
.task-meta {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-top: 0.4rem;
  flex-wrap: wrap;
}
.task-badge {
  font-size: 0.58rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  border-radius: 6px;
  padding: 0.15rem 0.5rem;
  text-transform: uppercase;
}
.task-notes {
  font-size: 0.72rem;
  color: var(--text3);
  font-style: italic;
  margin-top: 0.4rem;
  padding: 0.4rem 0.6rem;
  background: var(--bg2);
  border-radius: 6px;
  border-left: 2px solid var(--border2);
  line-height: 1.5;
  margin-left: 0.4rem;
}
.task-due-ok   { color: var(--green); background: #34d39915; border: 1px solid #34d39930; }
.task-due-warn { color: var(--yellow); background: #ffd32a15; border: 1px solid #ffd32a30; }
.task-due-late { color: var(--red); background: #ff475715; border: 1px solid #ff475730; }
.task-cat-badge { background: #ffffff08; border: 1px solid var(--border2); color: var(--text2); }
.task-prio-badge { font-size: 0.58rem; font-weight: 700; letter-spacing: 0.06em; border-radius: 6px; padding: 0.15rem 0.5rem; }

/* ══════════════ HISTORY CARDS ══════════════ */
.hist-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 0.75rem 1rem;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 0.8rem;
  opacity: 0.55;
  transition: opacity 0.2s;
}
.hist-card:hover { opacity: 0.8; }
.hist-check {
  width: 22px; height: 22px;
  background: linear-gradient(135deg, var(--green), #10b981);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.65rem;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 0 8px #34d39940;
}
.hist-text {
  flex: 1;
  font-size: 0.8rem;
  color: var(--text3);
  text-decoration: line-through;
  text-decoration-color: #ffffff15;
}
.hist-done-time {
  font-size: 0.58rem;
  color: var(--text3);
  font-family: 'Fira Code', monospace;
  white-space: nowrap;
}

/* ══════════════ EMPTY STATE ══════════════ */
.empty-state {
  text-align: center;
  padding: 3.5rem 1rem;
}
.empty-icon-wrap {
  width: 60px; height: 60px;
  background: var(--surface);
  border: 1px solid var(--border2);
  border-radius: 16px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.5rem;
  margin: 0 auto 1rem;
  opacity: 0.5;
}
.empty-label {
  font-size: 0.75rem;
  color: var(--text3);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  font-weight: 600;
}
.empty-sub {
  font-size: 0.65rem;
  color: var(--text3);
  opacity: 0.6;
  margin-top: 0.3rem;
}

/* ══════════════ POMODORO ══════════════ */
.pomo-card {
  background: var(--bg3);
  border: 1px solid var(--border2);
  border-radius: 16px;
  padding: 1.2rem;
  margin-bottom: 1.5rem;
  text-align: center;
  position: relative;
  overflow: hidden;
}
.pomo-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, var(--red), var(--orange));
  opacity: 0.7;
}
.pomo-time {
  font-family: 'Fira Code', monospace;
  font-size: 2.8rem;
  font-weight: 500;
  letter-spacing: 0.05em;
  color: var(--text);
  line-height: 1;
}
.pomo-label {
  font-size: 0.6rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--text3);
  margin-top: 0.3rem;
  font-weight: 600;
}

/* ══════════════ CONFETTI ══════════════ */
.confetti-msg {
  text-align: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, #7c6af710, #34d39910);
  border: 1px solid #34d39930;
  border-radius: 16px;
  margin-bottom: 1.5rem;
  animation: celebPop 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
@keyframes celebPop {
  0%   { transform: scale(0.9); opacity: 0; }
  60%  { transform: scale(1.02); }
  100% { transform: scale(1); opacity: 1; }
}
.confetti-title {
  font-size: 1.2rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--green), var(--accent2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.confetti-sub {
  font-size: 0.72rem;
  color: var(--text2);
  margin-top: 0.3rem;
}

/* ══════════════ SIDEBAR ══════════════ */
.sidebar-section {
  margin-bottom: 1.5rem;
}
.sidebar-label {
  font-size: 0.58rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--text3);
  font-weight: 700;
  margin-bottom: 0.6rem;
  display: block;
}
.streak-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #ff6b3520, #ffd32a15);
  border: 1px solid #ff6b3530;
  border-radius: 10px;
  padding: 0.7rem 0.9rem;
  margin-bottom: 0.8rem;
}
.streak-num {
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--orange);
  line-height: 1;
  font-family: 'Poppins', sans-serif;
}
.streak-info { font-size: 0.65rem; color: var(--text2); font-weight: 500; }

.cat-stat {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.45rem 0;
  border-bottom: 1px solid var(--border);
}
.cat-stat:last-child { border-bottom: none; }
.cat-stat-name { font-size: 0.72rem; color: var(--text2); }
.cat-stat-num { 
  font-size: 0.65rem;
  font-family: 'Fira Code', monospace;
  background: var(--surface);
  border: 1px solid var(--border2);
  border-radius: 4px;
  padding: 0.1rem 0.4rem;
  color: var(--accent2);
}

/* ── Misc ── */
[data-testid="stForm"] { border: none !important; padding: 0 !important; background: transparent !important; }
[data-testid="column"] { padding: 0 0.2rem !important; }
div[data-testid="stHorizontalBlock"] { gap: 0.3rem !important; align-items: flex-end !important; }
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }
[data-testid="stMarkdownContainer"] p { font-family: 'Poppins', sans-serif !important; }

/* Sidebar selects / radios */
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div,
[data-testid="stSidebar"] [data-testid="stTextInput"] input {
  background: var(--surface) !important;
  border: 1px solid var(--border2) !important;
  color: var(--text) !important;
}
[data-testid="stSidebar"] label {
  color: var(--text2) !important;
  font-size: 0.75rem !important;
  font-family: 'Poppins', sans-serif !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] button {
  background: var(--surface) !important;
  color: var(--text2) !important;
  border: 1px solid var(--border2) !important;
  font-size: 0.75rem !important;
  padding: 0.5rem 1rem !important;
  width: 100%;
}
[data-testid="stSidebar"] [data-testid="stButton"] button:hover {
  background: var(--surface2) !important;
  color: var(--text) !important;
  border-color: var(--accent) !important;
}
.danger-btn [data-testid="stButton"] button {
  background: #ff475710 !important;
  color: var(--red) !important;
  border: 1px solid #ff475730 !important;
}
.danger-btn [data-testid="stButton"] button:hover {
  background: #ff475720 !important;
  border-color: var(--red) !important;
}

/* Task action mini buttons */
.task-actions [data-testid="stButton"] button {
  background: transparent !important;
  color: var(--text3) !important;
  border: 1px solid var(--border) !important;
  font-size: 0.7rem !important;
  padding: 0.3rem 0.55rem !important;
  border-radius: 7px !important;
  min-height: unset !important;
}
.task-actions [data-testid="stButton"] button:hover {
  background: var(--surface) !important;
  color: var(--text) !important;
  border-color: var(--border2) !important;
}
.task-done-btn [data-testid="stButton"] button {
  background: #34d39915 !important;
  color: var(--green) !important;
  border: 1px solid #34d39930 !important;
}
.task-done-btn [data-testid="stButton"] button:hover {
  background: #34d39925 !important;
}
.task-del-btn [data-testid="stButton"] button {
  background: #ff475710 !important;
  color: var(--red) !important;
  border: 1px solid #ff475725 !important;
}
.task-del-btn [data-testid="stButton"] button:hover {
  background: #ff475725 !important;
}
.pin-active [data-testid="stButton"] button {
  color: #ffd32a !important;
  border-color: #ffd32a40 !important;
  background: #ffd32a10 !important;
}

/* Expander */
[data-testid="stExpander"] {
  background: var(--bg3) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
}
[data-testid="stExpander"] summary {
  font-size: 0.75rem !important;
  font-weight: 600 !important;
  color: var(--text2) !important;
  font-family: 'Poppins', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# ── Compute ───────────────────────────────────────────────────────────────────
now     = datetime.now()
total   = len(st.session_state.tasks)
done_ct = len(st.session_state.completed)
ratio   = done_ct / (total + done_ct) * 100 if (total + done_ct) > 0 else 0
today   = date.today()

def due_status(due_str):
    if not due_str: return None, None
    try:
        d = date.fromisoformat(due_str)
        diff = (d - today).days
        if diff < 0:  return "OVERDUE", "task-due-late"
        if diff == 0: return "TODAY",   "task-due-warn"
        if diff <= 2: return f"IN {diff}D", "task-due-warn"
        return due_str, "task-due-ok"
    except: return None, None

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<span class="sidebar-label">⬡  Nexus Tasks</span>', unsafe_allow_html=True)

    # Streak
    st.markdown(f"""
    <div class="streak-badge">
      <div>
        <div class="streak-num">🔥 {st.session_state.streak}</div>
        <div class="streak-info">task streak · {st.session_state.total_ever_done} total done</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<span class="sidebar-label">🔍  Search & Filter</span>', unsafe_allow_html=True)

    st.session_state.search_query = st.text_input("Search tasks", value=st.session_state.search_query, placeholder="Search by name or notes…", label_visibility="collapsed")

    st.session_state.filter_priority = st.selectbox(
        "Priority filter",
        ["All"] + list(PRIORITIES.keys()),
        index=(["All"] + list(PRIORITIES.keys())).index(st.session_state.filter_priority),
    )
    st.session_state.filter_category = st.selectbox(
        "Category filter",
        ["All"] + CATEGORIES,
        index=(["All"] + CATEGORIES).index(st.session_state.filter_category) if st.session_state.filter_category in ["All"] + CATEGORIES else 0,
    )
    st.session_state.sort_by = st.selectbox(
        "Sort by",
        ["Date Added", "Priority", "Due Date", "Pinned First"],
        index=["Date Added", "Priority", "Due Date", "Pinned First"].index(st.session_state.sort_by),
    )

    st.markdown("---")
    st.markdown('<span class="sidebar-label">📊  By Category</span>', unsafe_allow_html=True)
    cat_counts = {}
    for t in st.session_state.tasks:
        c = t.get("category", "Uncategorized")
        cat_counts[c] = cat_counts.get(c, 0) + 1
    if cat_counts:
        cats_html = ""
        for c, n in sorted(cat_counts.items(), key=lambda x: -x[1]):
            cats_html += f'<div class="cat-stat"><span class="cat-stat-name">{CAT_ICONS.get(c,"◈")} {c}</span><span class="cat-stat-num">{n}</span></div>'
        st.markdown(cats_html, unsafe_allow_html=True)
    else:
        st.markdown('<span style="font-size:0.65rem;color:#404060;">No tasks yet.</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<span class="sidebar-label">⏱  Pomodoro Timer</span>', unsafe_allow_html=True)
    if st.button("🍅  Toggle Pomodoro"):
        st.session_state.show_pomodoro = not st.session_state.show_pomodoro
        st.rerun()

    st.markdown("---")
    st.markdown('<span class="sidebar-label">⬇  Export / Clear</span>', unsafe_allow_html=True)
    export_txt = export_tasks()
    st.download_button("⬇  Export Tasks (.txt)", data=export_txt, file_name=f"nexus_tasks_{now.strftime('%Y%m%d')}.txt", mime="text/plain", use_container_width=True)
    st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
    if st.button("🗑  Clear All Completed", use_container_width=True):
        clear_history()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════ MAIN CONTENT ══════════════════════════════════════════════

# ── Header ────────────────────────────────────────────────────────────────────
quote = random.choice(QUOTES)
st.markdown(f"""
<div class="nx-header">
  <div class="nx-logo">
    <div class="nx-logo-icon">⬡</div>
    <div>
      <div class="nx-title">Nexus Tasks</div>
      <div class="nx-subtitle">Your command center</div>
    </div>
  </div>
  <div class="nx-date-block">
    <div class="nx-time">{now.strftime('%H:%M')}</div>
    <div class="nx-date">{now.strftime('%A · %d %B %Y')}</div>
    <div class="nx-quote">"{quote}"</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Confetti ──────────────────────────────────────────────────────────────────
if st.session_state.show_confetti:
    st.markdown("""
    <div class="confetti-msg">
      <div class="confetti-title">🎉  All Tasks Cleared!</div>
      <div class="confetti-sub">Incredible. Zero pending tasks. You're in the zone.</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("✕  Dismiss"):
        st.session_state.show_confetti = False
        st.rerun()

# ── Stats ─────────────────────────────────────────────────────────────────────
overdue_ct = sum(1 for t in st.session_state.tasks if t.get("due") and date.fromisoformat(t["due"]) < today)
critical_ct = sum(1 for t in st.session_state.tasks if "Critical" in t.get("priority",""))
st.markdown(f"""
<div class="stats-grid">
  <div class="stat-card" style="--accent-color:#7c6af7;">
    <span class="stat-icon">📋</span>
    <div class="stat-num" style="--stat-color:#e8e8f0;">{total}</div>
    <div class="stat-label">Active</div>
  </div>
  <div class="stat-card" style="--accent-color:#34d399;">
    <span class="stat-icon">✓</span>
    <div class="stat-num" style="color:#34d399;">{done_ct}</div>
    <div class="stat-label">Completed</div>
  </div>
  <div class="stat-card" style="--accent-color:#ff4757;">
    <span class="stat-icon">⚠</span>
    <div class="stat-num" style="color:{'#ff4757' if overdue_ct>0 else '#404060'};">{overdue_ct}</div>
    <div class="stat-label">Overdue</div>
  </div>
  <div class="stat-card" style="--accent-color:#ff6b35;">
    <span class="stat-icon">🔴</span>
    <div class="stat-num" style="color:{'#ff6b35' if critical_ct>0 else '#404060'};">{critical_ct}</div>
    <div class="stat-label">Critical</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Progress ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="prog-block">
  <div class="prog-top">
    <span class="prog-label">Overall Progress</span>
    <span class="prog-pct">{int(ratio)}% complete</span>
  </div>
  <div class="prog-track">
    <div class="prog-fill" style="width:{ratio}%"></div>
  </div>
  <div class="prog-milestones">
    <span class="milestone">0%</span>
    <span class="milestone">25%</span>
    <span class="milestone">50%</span>
    <span class="milestone">75%</span>
    <span class="milestone">100%</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Pomodoro ──────────────────────────────────────────────────────────────────
if st.session_state.show_pomodoro:
    if st.session_state.pomo_running and st.session_state.pomo_start:
        elapsed = int((datetime.now() - st.session_state.pomo_start).total_seconds())
        remaining = max(0, st.session_state.pomo_seconds - elapsed)
    else:
        remaining = st.session_state.pomo_seconds

    mins, secs = divmod(remaining, 60)
    pomo_display = f"{mins:02d}:{secs:02d}"
    state_label = "RUNNING" if st.session_state.pomo_running else "PAUSED"

    st.markdown(f"""
    <div class="pomo-card">
      <div class="pomo-time">{pomo_display}</div>
      <div class="pomo-label">🍅 Pomodoro · {state_label}</div>
    </div>
    """, unsafe_allow_html=True)

    pc1, pc2, pc3 = st.columns(3)
    with pc1:
        if st.button("▶  Start" if not st.session_state.pomo_running else "⏸  Pause"):
            if not st.session_state.pomo_running:
                st.session_state.pomo_running = True
                st.session_state.pomo_start = datetime.now()
            else:
                st.session_state.pomo_running = False
                st.session_state.pomo_seconds = remaining
                st.session_state.pomo_start = None
            st.rerun()
    with pc2:
        if st.button("↺  Reset"):
            st.session_state.pomo_running = False
            st.session_state.pomo_seconds = 1500
            st.session_state.pomo_start = None
            st.rerun()
    with pc3:
        pomo_select = st.selectbox("Duration", ["25 min", "10 min", "5 min"], label_visibility="collapsed")
        if pomo_select == "10 min": st.session_state.pomo_seconds = 600
        elif pomo_select == "5 min": st.session_state.pomo_seconds = 300
        else: st.session_state.pomo_seconds = 1500

# ── Add Task Form ─────────────────────────────────────────────────────────────
st.markdown('<div class="form-card"><div class="form-title">+ New Task</div>', unsafe_allow_html=True)
with st.form(key=f"form_{st.session_state.input_key}", clear_on_submit=True):
    r1c1, r1c2 = st.columns([3, 1])
    with r1c1:
        task_input = st.text_input("Task name", placeholder="What needs to be done?", label_visibility="visible")
    with r1c2:
        priority_input = st.selectbox("Priority", list(PRIORITIES.keys()), index=2)

    r2c1, r2c2, r2c3 = st.columns([2, 1, 1])
    with r2c1:
        notes_input = st.text_input("Notes (optional)", placeholder="Add context or details…", label_visibility="visible")
    with r2c2:
        cat_input = st.selectbox("Category", CATEGORIES)
    with r2c3:
        due_input = st.date_input("Due date", value=None, min_value=today, format="YYYY-MM-DD", label_visibility="visible")

    st.markdown('<div class="btn-add">', unsafe_allow_html=True)
    submitted = st.form_submit_button("⬡  Add Task", use_container_width=False)
    st.markdown('</div>', unsafe_allow_html=True)

    if submitted and task_input.strip():
        add_task(task_input, priority_input, cat_input, due_input, notes_input)
        st.session_state.show_confetti = False
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ── Task List ─────────────────────────────────────────────────────────────────
filtered = get_filtered_tasks()
task_count = len(filtered)

st.markdown(f"""
<div class="section-head">
  <span class="section-head-label">Active Tasks</span>
  <span class="section-count">{task_count}</span>
  <span class="section-line"></span>
</div>
""", unsafe_allow_html=True)

if not st.session_state.tasks:
    st.markdown("""
    <div class="empty-state">
      <div class="empty-icon-wrap">⬡</div>
      <div class="empty-label">All clear</div>
      <div class="empty-sub">Add a task above to get started</div>
    </div>
    """, unsafe_allow_html=True)
elif task_count == 0:
    st.markdown("""
    <div class="empty-state">
      <div class="empty-icon-wrap">🔍</div>
      <div class="empty-label">No matches</div>
      <div class="empty-sub">Try adjusting your filters or search query</div>
    </div>
    """, unsafe_allow_html=True)
else:
    for display_task in filtered:
        # Find true index in session state for mutations
        true_idx = next((i for i, t in enumerate(st.session_state.tasks) if t["id"] == display_task["id"]), None)
        if true_idx is None: continue

        task = display_task
        prio_color = PRIORITIES.get(task.get("priority",""), "#404060")
        cat = task.get("category", "Uncategorized")
        cat_icon = CAT_ICONS.get(cat, "◈")
        due_label, due_cls = due_status(task.get("due"))
        pinned = task.get("pinned", False)

        # Priority badge colors
        prio_map = {
            "🔴 Critical": "background:#ff475720;color:#ff4757;border:1px solid #ff475740;",
            "🟠 High":     "background:#ff6b3520;color:#ff6b35;border:1px solid #ff6b3540;",
            "🟡 Medium":   "background:#ffd32a20;color:#ffd32a;border:1px solid #ffd32a40;",
            "🟢 Low":      "background:#34d39920;color:#34d399;border:1px solid #34d39940;",
        }
        prio_style = prio_map.get(task.get("priority",""), "")

        pin_badge = '<span class="task-pin-badge">📌 PINNED</span>' if pinned else ""
        notes_html = f'<div class="task-notes">📎 {task["notes"]}</div>' if task.get("notes") else ""
        due_html   = f'<span class="task-badge {due_cls}">{due_label}</span>' if due_label else ""
        prio_html  = f'<span class="task-badge task-prio-badge" style="{prio_style}">{task.get("priority","")}</span>'
        cat_html   = f'<span class="task-badge task-cat-badge">{cat_icon} {cat}</span>'
        added_html = f'<span style="font-size:0.55rem;color:#303050;font-family:\'Fira Code\',monospace;">{task["added"]}</span>'
        overdue_cls = " overdue" if due_label == "OVERDUE" else ""

        st.markdown(f"""
        <div class="task-card {'pinned' if pinned else ''}">
          <div class="task-priority-bar" style="background:{prio_color};"></div>
          <div class="task-header">
            <div class="task-main">
              <div class="task-text-row">
                <span class="task-text{overdue_cls}">{task['text']}</span>
                {pin_badge}
              </div>
              <div class="task-meta">
                {prio_html}
                {cat_html}
                {due_html}
                {added_html}
              </div>
              {notes_html}
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Action buttons
        st.markdown('<div class="task-actions">', unsafe_allow_html=True)
        ac1, ac2, ac3, ac4, ac5, ac6 = st.columns([1, 1, 1, 1, 1, 8])
        with ac1:
            st.markdown('<div class="task-done-btn">', unsafe_allow_html=True)
            if st.button("✓", key=f"done_{task['id']}", help="Mark complete"):
                complete_task(true_idx)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with ac2:
            st.markdown('<div class="task-del-btn">', unsafe_allow_html=True)
            if st.button("✕", key=f"del_{task['id']}", help="Delete"):
                delete_task(true_idx)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with ac3:
            st.markdown(f'<div class="{"pin-active" if pinned else ""}">', unsafe_allow_html=True)
            if st.button("📌", key=f"pin_{task['id']}", help="Pin task"):
                toggle_pin(true_idx)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with ac4:
            if st.button("↑", key=f"up_{task['id']}", help="Move up"):
                move_up(true_idx)
                st.rerun()
        with ac5:
            if st.button("↓", key=f"dn_{task['id']}", help="Move down"):
                move_down(true_idx)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ── Completed History ─────────────────────────────────────────────────────────
if st.session_state.completed:
    st.markdown("<hr>", unsafe_allow_html=True)
    hcol1, hcol2 = st.columns([4, 1])
    with hcol1:
        st.markdown(f"""
        <div class="section-head">
          <span class="section-head-label">Completed</span>
          <span class="section-count">{done_ct}</span>
          <span class="section-line"></span>
        </div>
        """, unsafe_allow_html=True)

    with st.expander(f"Show {done_ct} completed task{'s' if done_ct!=1 else ''}", expanded=False):
        for ci, ctask in enumerate(st.session_state.completed):
            cat_i = CAT_ICONS.get(ctask.get("category","Uncategorized"), "◈")
            st.markdown(f"""
            <div class="hist-card">
              <div class="hist-check">✓</div>
              <div class="hist-text">{ctask['text']}</div>
              <div style="font-size:0.6rem;color:#303050;margin-right:0.3rem;">{cat_i}</div>
              <div class="hist-done-time">{ctask.get('done','')}</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('<div class="task-actions">', unsafe_allow_html=True)
            if st.button("✕ Remove", key=f"cdel_{ci}_{ctask.get('id',ci)}", help="Remove from history"):
                delete_completed(ci)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
        if st.button("🗑  Clear All History", use_container_width=True, key="clear_all_hist_main"):
            clear_history()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
