import streamlit as st
from datetime import datetime, date
import random

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TASKS",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE  (bootstrap once)
# ─────────────────────────────────────────────────────────────────────────────
QUOTES = [
    "Small actions compound into great outcomes.",
    "Progress, not perfection.",
    "Focus is the rarest and most valuable resource.",
    "Done is better than perfect.",
    "Discipline is choosing between what you want now and what you want most.",
    "One task at a time. That's the whole system.",
]
DEFAULTS: dict = {
    "tasks":           [],
    "completed":       [],
    "input_key":       0,
    "filter_priority": "All",
    "filter_category": "All",
    "search_query":    "",
    "sort_by":         "Date Added",
    "show_pomodoro":   False,
    "pomo_running":    False,
    "pomo_seconds":    1500,
    "pomo_start":      None,
    "streak":          0,
    "total_done":      0,
    "show_celebrate":  False,
    "daily_quote":     random.choice(QUOTES),
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
PRIORITIES = {
    "● Critical": "#f43f5e",
    "● High":     "#fb923c",
    "● Medium":   "#fbbf24",
    "● Low":      "#34d399",
}
CATEGORIES = ["Work", "Personal", "Health", "Finance", "Learning", "Creative", "Errands"]
CAT_ICONS  = {
    "Work": "◻", "Personal": "◇", "Health": "◈",
    "Finance": "◆", "Learning": "△", "Creative": "○",
    "Errands": "▷", "Uncategorized": "·",
}

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def add_task(text: str, priority: str, category: str, due_raw, notes: str) -> None:
    if not text.strip():
        return
    # Safely convert due date — avoid str(None) = "None"
    due_str = None
    if due_raw and due_raw != () and isinstance(due_raw, date):
        due_str = due_raw.isoformat()
    st.session_state.tasks.append({
        "id":       str(datetime.now().timestamp()),
        "text":     text.strip(),
        "priority": priority,
        "category": category,
        "due":      due_str,
        "notes":    notes.strip(),
        "added":    datetime.now().strftime("%d %b, %H:%M"),
        "pinned":   False,
    })
    st.session_state.input_key += 1

def complete_task(task_id: str) -> None:
    idx = _find_idx(task_id)
    if idx is None:
        return
    task = st.session_state.tasks.pop(idx)
    task["done_at"] = datetime.now().strftime("%H:%M · %d %b")
    st.session_state.completed.insert(0, task)
    st.session_state.total_done += 1
    st.session_state.streak    += 1
    if len(st.session_state.tasks) == 0:
        st.session_state.show_celebrate = True

def delete_task(task_id: str) -> None:
    idx = _find_idx(task_id)
    if idx is not None:
        st.session_state.tasks.pop(idx)

def toggle_pin(task_id: str) -> None:
    idx = _find_idx(task_id)
    if idx is not None:
        st.session_state.tasks[idx]["pinned"] = not st.session_state.tasks[idx]["pinned"]

def move_task(task_id: str, direction: int) -> None:
    idx = _find_idx(task_id)
    tasks = st.session_state.tasks
    if idx is None:
        return
    new_idx = idx + direction
    if 0 <= new_idx < len(tasks):
        tasks[idx], tasks[new_idx] = tasks[new_idx], tasks[idx]

def delete_completed(ci: int) -> None:
    if 0 <= ci < len(st.session_state.completed):
        st.session_state.completed.pop(ci)

def clear_history() -> None:
    st.session_state.completed = []

def _find_idx(task_id: str):
    for i, t in enumerate(st.session_state.tasks):
        if t["id"] == task_id:
            return i
    return None

def due_status(due_str):
    """Returns (label, css_class) or (None, None)."""
    if not due_str:
        return None, None
    try:
        d   = date.fromisoformat(due_str)
        diff = (d - date.today()).days
        if diff < 0:
            return f"OVERDUE {abs(diff)}d", "due-late"
        if diff == 0:
            return "DUE TODAY", "due-warn"
        if diff <= 3:
            return f"DUE IN {diff}d", "due-soon"
        return d.strftime("%d %b"), "due-ok"
    except Exception:
        return None, None

def get_filtered_tasks():
    tasks = list(st.session_state.tasks)  # shallow copy, keeps same dicts
    q = st.session_state.search_query.strip().lower()
    if q:
        tasks = [t for t in tasks if q in t["text"].lower() or q in t.get("notes", "").lower()]
    fp = st.session_state.filter_priority
    if fp != "All":
        tasks = [t for t in tasks if t.get("priority") == fp]
    fc = st.session_state.filter_category
    if fc != "All":
        tasks = [t for t in tasks if t.get("category") == fc]
    sort = st.session_state.sort_by
    prio_order = list(PRIORITIES.keys())
    if sort == "Priority":
        tasks.sort(key=lambda t: prio_order.index(t["priority"]) if t.get("priority") in prio_order else 99)
    elif sort == "Due Date":
        tasks.sort(key=lambda t: t.get("due") or "9999-12-31")
    # Pinned tasks always float to the top regardless of sort
    tasks.sort(key=lambda t: not t.get("pinned", False))
    return tasks

def export_text() -> str:
    lines = [
        "TASKS — EXPORT",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "=" * 48, "",
        "ACTIVE",
    ]
    for t in st.session_state.tasks:
        lines.append(f"  [ ] {t['text']}  ({t.get('priority','')}) — {t['added']}")
        if t.get("notes"):
            lines.append(f"       {t['notes']}")
    lines += ["", "COMPLETED"]
    for t in st.session_state.completed:
        lines.append(f"  [✓] {t['text']}  — {t.get('done_at','')}")
    return "\n".join(lines)

# ─────────────────────────────────────────────────────────────────────────────
# CSS  — NO div-wrapper anti-patterns, all native Streamlit selectors
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400;1,600&family=Poppins:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');

/* ── Variables ────────────────────────────────────────── */
:root {
  --bg:      #07070d;
  --bg2:     #0c0c18;
  --bg3:     #101020;
  --surface: #14142a;
  --s2:      #1c1c3a;
  --bd:      rgba(255,255,255,0.06);
  --bd2:     rgba(255,255,255,0.12);
  --t1:      #f0f0f8;
  --t2:      #8888aa;
  --t3:      #404060;
  --acc:     #6d6af6;
  --acc2:    #9d9bf9;
  --grn:     #22d3a0;
  --red:     #f43f5e;
  --org:     #fb923c;
  --yel:     #fbbf24;
}

/* ── Reset ───────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  color: var(--t1) !important;
  font-family: 'Poppins', sans-serif !important;
}

/* Ambient glow layers */
[data-testid="stAppViewContainer"]::after {
  content: '';
  position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background:
    radial-gradient(ellipse 70% 40% at 15% 5%,  rgba(109,106,246,.05) 0%, transparent 55%),
    radial-gradient(ellipse 50% 35% at 85% 90%, rgba(157,155,249,.04) 0%, transparent 55%);
}

/* Hide chrome */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

/* ── Layout ──────────────────────────────────────────── */
.block-container {
  max-width: 820px !important;
  padding: 2.5rem 1.5rem 6rem !important;
}
[data-testid="stSidebar"] {
  background: var(--bg2) !important;
  border-right: 1px solid var(--bd) !important;
}
[data-testid="stSidebar"] > div:first-child {
  padding: 2rem 1.2rem !important;
}

/* ── Scrollbar ───────────────────────────────────────── */
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--bd2); border-radius: 3px; }

/* ── Columns ─────────────────────────────────────────── */
[data-testid="column"] { padding: 0 0.15rem !important; }
div[data-testid="stHorizontalBlock"] { gap: 0.25rem !important; align-items: stretch !important; }

/* ── Form card ── target the stForm directly, no wrapper divs */
[data-testid="stForm"] {
  background: var(--bg3) !important;
  border: 1px solid var(--bd2) !important;
  border-radius: 16px !important;
  padding: 1.4rem 1.5rem !important;
  position: relative;
  overflow: hidden;
}
[data-testid="stForm"]::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, var(--acc), var(--acc2), var(--grn));
  opacity: 0.5;
}

/* ── Inputs ──────────────────────────────────────────── */
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stSelectbox"] label,
[data-testid="stDateInput"] label {
  font-family: 'Poppins', sans-serif !important;
  font-size: 0.6rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.14em !important;
  text-transform: uppercase !important;
  color: var(--t3) !important;
}
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
  background: var(--surface) !important;
  border: 1px solid var(--bd2) !important;
  border-radius: 10px !important;
  color: var(--t1) !important;
  font-family: 'Poppins', sans-serif !important;
  font-size: 0.85rem !important;
  font-weight: 400 !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder { color: var(--t3) !important; }
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
  border-color: var(--acc) !important;
  box-shadow: 0 0 0 3px rgba(109,106,246,.15) !important;
}
[data-testid="stSelectbox"] > div > div,
[data-testid="stDateInput"] input {
  background: var(--surface) !important;
  border: 1px solid var(--bd2) !important;
  border-radius: 10px !important;
  color: var(--t1) !important;
  font-family: 'Poppins', sans-serif !important;
  font-size: 0.82rem !important;
}
/* Dropdown list */
[data-testid="stSelectbox"] ul {
  background: var(--s2) !important;
  border: 1px solid var(--bd2) !important;
}
[data-testid="stSelectbox"] li {
  font-family: 'Poppins', sans-serif !important;
  font-size: 0.82rem !important;
  color: var(--t2) !important;
}
[data-testid="stSelectbox"] li:hover { background: var(--surface) !important; color: var(--t1) !important; }

/* ── Form SUBMIT button (Add Task) ───────────────────── */
[data-testid="stFormSubmitButton"] > button {
  background: linear-gradient(135deg, var(--acc) 0%, var(--acc2) 100%) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 10px !important;
  font-family: 'Poppins', sans-serif !important;
  font-weight: 600 !important;
  font-size: 0.8rem !important;
  letter-spacing: 0.06em !important;
  padding: 0.6rem 1.6rem !important;
  box-shadow: 0 4px 20px rgba(109,106,246,.35) !important;
  transition: all 0.2s !important;
}
[data-testid="stFormSubmitButton"] > button:hover {
  box-shadow: 0 6px 28px rgba(109,106,246,.5) !important;
  transform: translateY(-1px) !important;
}
[data-testid="stFormSubmitButton"] > button:active {
  transform: translateY(0) scale(0.98) !important;
}

/* ── Regular buttons (ghost style) ──────────────────── */
[data-testid="baseButton-secondary"],
[data-testid="stButton"] > button {
  background: transparent !important;
  color: var(--t3) !important;
  border: 1px solid var(--bd) !important;
  border-radius: 8px !important;
  font-family: 'Poppins', sans-serif !important;
  font-weight: 500 !important;
  font-size: 0.72rem !important;
  padding: 0.3rem 0.6rem !important;
  transition: all 0.18s !important;
  cursor: pointer !important;
}
[data-testid="baseButton-secondary"]:hover,
[data-testid="stButton"] > button:hover {
  background: var(--surface) !important;
  color: var(--t1) !important;
  border-color: var(--bd2) !important;
}

/* ── Sidebar buttons ─────────────────────────────────── */
[data-testid="stSidebar"] [data-testid="stButton"] > button {
  width: 100% !important;
  font-size: 0.74rem !important;
  padding: 0.45rem 0.8rem !important;
  border-radius: 8px !important;
  margin-bottom: 0.3rem !important;
}

/* ── Sidebar inputs ──────────────────────────────────── */
[data-testid="stSidebar"] [data-testid="stTextInput"] input,
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
  font-size: 0.78rem !important;
}
[data-testid="stSidebar"] label {
  font-family: 'Poppins', sans-serif !important;
  color: var(--t3) !important;
  font-size: 0.58rem !important;
}

/* ── Expander ────────────────────────────────────────── */
[data-testid="stExpander"] {
  background: var(--bg3) !important;
  border: 1px solid var(--bd) !important;
  border-radius: 12px !important;
}
[data-testid="stExpander"] summary {
  font-family: 'Poppins', sans-serif !important;
  font-size: 0.75rem !important;
  font-weight: 500 !important;
  color: var(--t2) !important;
}
[data-testid="stExpander"] summary:hover { color: var(--t1) !important; }

/* ── Download button ─────────────────────────────────── */
[data-testid="stDownloadButton"] > button {
  background: transparent !important;
  color: var(--t2) !important;
  border: 1px solid var(--bd) !important;
  border-radius: 8px !important;
  font-family: 'Poppins', sans-serif !important;
  font-size: 0.74rem !important;
  width: 100% !important;
  padding: 0.45rem 0.8rem !important;
}
[data-testid="stDownloadButton"] > button:hover {
  background: var(--surface) !important;
  color: var(--t1) !important;
  border-color: var(--bd2) !important;
}

/* ── HR ──────────────────────────────────────────────── */
hr { border: none !important; border-top: 1px solid var(--bd) !important; margin: 1.8rem 0 !important; }

/* ── Markdown text ───────────────────────────────────── */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span {
  font-family: 'Poppins', sans-serif !important;
}

/* ════════════════ CUSTOM HTML COMPONENTS ══════════════ */

/* ── App header ──────────────────────────────────────── */
.app-header {
  display: flex; justify-content: space-between; align-items: flex-end;
  padding-bottom: 2rem; margin-bottom: 2rem;
  border-bottom: 1px solid var(--bd);
}
.app-brand { line-height: 1; }
.app-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: 3.6rem; font-weight: 600; letter-spacing: -0.02em;
  color: var(--t1); line-height: 0.9;
}
.app-title em {
  font-style: italic; font-weight: 300;
  background: linear-gradient(135deg, var(--acc2), var(--grn));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
}
.app-tagline {
  font-family: 'Poppins', sans-serif;
  font-size: 0.58rem; font-weight: 500; letter-spacing: 0.22em;
  text-transform: uppercase; color: var(--t3); margin-top: 0.5rem;
}
.app-meta { text-align: right; }
.app-time {
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.8rem; font-weight: 300; letter-spacing: -0.02em;
  color: var(--t1); line-height: 1;
}
.app-date {
  font-size: 0.6rem; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--t3);
  margin-top: 0.25rem;
}
.app-quote {
  font-family: 'Cormorant Garamond', serif;
  font-style: italic; font-size: 0.78rem; font-weight: 300;
  color: var(--t3); margin-top: 0.3rem; max-width: 22ch; text-align: right;
}

/* ── Stats ───────────────────────────────────────────── */
.stats-row {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 1px; background: var(--bd);
  border: 1px solid var(--bd); border-radius: 14px;
  overflow: hidden; margin-bottom: 1.5rem;
}
.stat {
  background: var(--bg3); padding: 1rem 1.1rem;
  position: relative; overflow: hidden;
}
.stat::after {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1.5px;
  background: var(--stat-accent, transparent);
}
.stat:hover { background: var(--surface); }
.stat-n {
  font-family: 'Cormorant Garamond', serif;
  font-size: 2.4rem; font-weight: 600; letter-spacing: -0.03em;
  color: var(--stat-color, var(--t1)); line-height: 1;
}
.stat-l {
  font-family: 'Poppins', sans-serif;
  font-size: 0.55rem; font-weight: 600; letter-spacing: 0.16em;
  text-transform: uppercase; color: var(--t3); margin-top: 0.15rem;
}

/* ── Progress ────────────────────────────────────────── */
.prog {
  background: var(--bg3); border: 1px solid var(--bd);
  border-radius: 12px; padding: 1rem 1.2rem; margin-bottom: 1.5rem;
}
.prog-top {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 0.5rem;
}
.prog-lbl {
  font-family: 'Poppins', sans-serif;
  font-size: 0.58rem; font-weight: 600; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--t3);
}
.prog-pct {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem; font-weight: 400; color: var(--acc2);
}
.prog-track { height: 3px; background: var(--bd); border-radius: 3px; overflow: hidden; }
.prog-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--acc), var(--acc2) 50%, var(--grn));
  border-radius: 3px;
  transition: width 0.7s cubic-bezier(.4,0,.2,1);
  box-shadow: 0 0 6px var(--acc);
}

/* ── Section head ────────────────────────────────────── */
.sec {
  display: flex; align-items: center; gap: 0.7rem;
  margin-bottom: 0.9rem; margin-top: 0.3rem;
}
.sec-lbl {
  font-family: 'Poppins', sans-serif;
  font-size: 0.58rem; font-weight: 700; letter-spacing: 0.2em;
  text-transform: uppercase; color: var(--t3); white-space: nowrap;
}
.sec-ct {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem; color: var(--acc2);
  background: var(--surface); border: 1px solid var(--bd2);
  border-radius: 20px; padding: 0.05rem 0.45rem;
}
.sec-line { flex: 1; height: 1px; background: var(--bd); }

/* ── Task card ───────────────────────────────────────── */
.task-card {
  background: var(--bg3); border: 1px solid var(--bd);
  border-radius: 12px; padding: 0.85rem 1rem 0.8rem 1.1rem;
  position: relative; overflow: hidden;
  transition: border-color .2s, background .2s, transform .15s;
  animation: taskIn .28s cubic-bezier(.4,0,.2,1);
}
.task-card.is-pinned { border-color: rgba(251,191,36,.2) !important; }
.task-card:hover { border-color: var(--bd2); transform: translateY(-1px); }
.task-pbar {
  position: absolute; left: 0; top: 0; bottom: 0; width: 2.5px;
  border-radius: 12px 0 0 12px;
}
@keyframes taskIn {
  from { opacity: 0; transform: translateY(-8px) scale(.99); }
  to   { opacity: 1; transform: translateY(0)   scale(1); }
}
.task-name {
  font-family: 'Poppins', sans-serif;
  font-size: 0.9rem; font-weight: 500; color: var(--t1); line-height: 1.4;
  display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;
}
.task-name.overdue { color: var(--red); }
.task-pin-tag {
  font-size: 0.55rem; font-weight: 700; letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--yel);
  background: rgba(251,191,36,.12); border: 1px solid rgba(251,191,36,.25);
  border-radius: 4px; padding: 0.05rem 0.35rem;
}
.task-meta {
  display: flex; align-items: center; gap: 0.45rem;
  margin-top: 0.35rem; flex-wrap: wrap;
}
.badge {
  font-family: 'Poppins', sans-serif;
  font-size: 0.56rem; font-weight: 600; letter-spacing: 0.08em;
  text-transform: uppercase; border-radius: 5px; padding: 0.12rem 0.45rem;
}
.due-ok   { color: var(--grn); background: rgba(34,211,160,.1); border: 1px solid rgba(34,211,160,.2); }
.due-soon { color: var(--yel); background: rgba(251,191,36,.1); border: 1px solid rgba(251,191,36,.2); }
.due-warn { color: var(--org); background: rgba(251,146,60,.1); border: 1px solid rgba(251,146,60,.2); }
.due-late { color: var(--red); background: rgba(244,63,94,.12); border: 1px solid rgba(244,63,94,.25); }
.cat-badge { color: var(--t2); background: rgba(255,255,255,.04); border: 1px solid var(--bd2); }
.task-notes {
  font-family: 'Poppins', sans-serif;
  font-size: 0.72rem; font-weight: 300; font-style: italic;
  color: var(--t3); margin-top: 0.4rem;
  padding: 0.35rem 0.6rem;
  background: var(--bg2); border-left: 2px solid var(--bd2);
  border-radius: 0 5px 5px 0;
}
.task-added {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.56rem; color: var(--t3); letter-spacing: 0.04em;
}

/* ── Completed history ───────────────────────────────── */
.hist-card {
  display: flex; align-items: center; gap: 0.75rem;
  background: var(--bg2); border: 1px solid var(--bd);
  border-radius: 10px; padding: 0.7rem 1rem;
  margin-bottom: 5px; opacity: 0.5; transition: opacity .2s;
}
.hist-card:hover { opacity: 0.75; }
.hist-dot {
  width: 20px; height: 20px; border-radius: 50%; flex-shrink: 0;
  background: linear-gradient(135deg, var(--grn), #10b981);
  display: flex; align-items: center; justify-content: center;
  font-size: 0.6rem; color: #07070d; font-weight: 700;
  box-shadow: 0 0 8px rgba(34,211,160,.3);
}
.hist-text {
  flex: 1; font-family: 'Poppins', sans-serif;
  font-size: 0.8rem; font-weight: 400; color: var(--t3);
  text-decoration: line-through; text-decoration-color: rgba(255,255,255,.1);
}
.hist-time {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.58rem; color: var(--t3); white-space: nowrap;
}

/* ── Celebration banner ──────────────────────────────── */
.celebrate {
  text-align: center; padding: 1.8rem 1rem;
  background: linear-gradient(135deg, rgba(109,106,246,.08), rgba(34,211,160,.08));
  border: 1px solid rgba(34,211,160,.2); border-radius: 16px;
  margin-bottom: 1.5rem;
  animation: popIn .45s cubic-bezier(.4,0,.2,1);
}
@keyframes popIn {
  from { opacity: 0; transform: scale(.92); }
  60%  { transform: scale(1.02); }
  to   { opacity: 1; transform: scale(1); }
}
.celebrate-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.8rem; font-weight: 600; font-style: italic;
  background: linear-gradient(135deg, var(--grn), var(--acc2));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
}
.celebrate-sub {
  font-family: 'Poppins', sans-serif;
  font-size: 0.72rem; color: var(--t2); margin-top: 0.3rem;
}

/* ── Empty state ─────────────────────────────────────── */
.empty {
  text-align: center; padding: 3.5rem 1rem;
}
.empty-glyph {
  font-family: 'Cormorant Garamond', serif;
  font-size: 3rem; font-weight: 300; color: var(--t3);
  line-height: 1; display: block; margin-bottom: 0.8rem;
  opacity: 0.4;
}
.empty-lbl {
  font-family: 'Poppins', sans-serif;
  font-size: 0.72rem; font-weight: 600; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--t3);
}
.empty-sub {
  font-family: 'Poppins', sans-serif;
  font-size: 0.64rem; color: var(--t3); opacity: .6; margin-top: .25rem;
}

/* ── Pomodoro ─────────────────────────────────────────── */
.pomo {
  background: var(--bg3); border: 1px solid var(--bd2);
  border-radius: 16px; padding: 1.3rem 1.2rem 1rem;
  margin-bottom: 1.5rem; text-align: center; position: relative;
}
.pomo::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, var(--red), var(--org)); opacity: .6;
}
.pomo-time {
  font-family: 'JetBrains Mono', monospace;
  font-size: 3rem; font-weight: 300; letter-spacing: .04em;
  color: var(--t1); line-height: 1;
}
.pomo-state {
  font-family: 'Poppins', sans-serif;
  font-size: 0.58rem; font-weight: 600; letter-spacing: .18em;
  text-transform: uppercase; color: var(--t3); margin-top: .3rem;
}

/* ── Sidebar section label ───────────────────────────── */
.sb-lbl {
  font-family: 'Poppins', sans-serif;
  font-size: 0.56rem; font-weight: 700; letter-spacing: .18em;
  text-transform: uppercase; color: var(--t3);
  display: block; margin-bottom: .6rem;
}
.streak-box {
  background: linear-gradient(135deg, rgba(251,146,60,.08), rgba(251,191,36,.06));
  border: 1px solid rgba(251,146,60,.2); border-radius: 10px;
  padding: .8rem 1rem; display: flex; align-items: center; gap: .7rem;
  margin-bottom: 1rem;
}
.streak-n {
  font-family: 'Cormorant Garamond', serif;
  font-size: 2.2rem; font-weight: 600; color: var(--org); line-height: 1;
}
.streak-info {
  font-family: 'Poppins', sans-serif;
  font-size: 0.65rem; font-weight: 500; color: var(--t2);
}
.cat-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: .4rem 0; border-bottom: 1px solid var(--bd);
}
.cat-row:last-child { border-bottom: none; }
.cat-name { font-size: .72rem; color: var(--t2); font-family: 'Poppins', sans-serif; }
.cat-ct {
  font-family: 'JetBrains Mono', monospace; font-size: .6rem;
  color: var(--acc2); background: var(--surface);
  border: 1px solid var(--bd2); border-radius: 4px; padding: .05rem .35rem;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PRE-COMPUTE
# ─────────────────────────────────────────────────────────────────────────────
now      = datetime.now()
today    = date.today()
total    = len(st.session_state.tasks)
done_ct  = len(st.session_state.completed)
ratio    = done_ct / (total + done_ct) * 100 if (total + done_ct) > 0 else 0
overdue  = sum(
    1 for t in st.session_state.tasks
    if t.get("due") and _safe_date(t["due"]) and _safe_date(t["due"]) < today
)

def _safe_date(s):
    try: return date.fromisoformat(s)
    except: return None

# Re-compute overdue with safe helper
overdue  = sum(1 for t in st.session_state.tasks if t.get("due") and _safe_date(t["due"]) and _safe_date(t["due"]) < today)
critical = sum(1 for t in st.session_state.tasks if "Critical" in t.get("priority",""))

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<span class="sb-lbl">◈  Tasks</span>', unsafe_allow_html=True)

    # Streak
    st.markdown(f"""
    <div class="streak-box">
      <div class="streak-n">🔥{st.session_state.streak}</div>
      <div>
        <div class="streak-info">task streak</div>
        <div class="streak-info" style="color:var(--t3);font-size:0.58rem;">{st.session_state.total_done} all-time completed</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<span class="sb-lbl">Search & Filter</span>', unsafe_allow_html=True)
    st.session_state.search_query    = st.text_input("Search", value=st.session_state.search_query, placeholder="search tasks…", label_visibility="collapsed")
    st.session_state.filter_priority = st.selectbox("Priority", ["All"] + list(PRIORITIES.keys()), index=(["All"]+list(PRIORITIES.keys())).index(st.session_state.filter_priority) if st.session_state.filter_priority in ["All"]+list(PRIORITIES.keys()) else 0)
    st.session_state.filter_category = st.selectbox("Category", ["All"] + CATEGORIES, index=(["All"]+CATEGORIES).index(st.session_state.filter_category) if st.session_state.filter_category in ["All"]+CATEGORIES else 0)
    st.session_state.sort_by         = st.selectbox("Sort", ["Date Added","Priority","Due Date"], index=["Date Added","Priority","Due Date"].index(st.session_state.sort_by) if st.session_state.sort_by in ["Date Added","Priority","Due Date"] else 0)

    st.markdown("---")
    st.markdown('<span class="sb-lbl">By Category</span>', unsafe_allow_html=True)
    cat_counts: dict = {}
    for t in st.session_state.tasks:
        c = t.get("category","Uncategorized")
        cat_counts[c] = cat_counts.get(c,0) + 1
    if cat_counts:
        rows = "".join(f'<div class="cat-row"><span class="cat-name">{CAT_ICONS.get(c,"·")} {c}</span><span class="cat-ct">{n}</span></div>' for c,n in sorted(cat_counts.items(), key=lambda x:-x[1]))
        st.markdown(rows, unsafe_allow_html=True)
    else:
        st.markdown('<span style="font-size:.65rem;color:var(--t3);">No tasks yet.</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<span class="sb-lbl">Pomodoro Timer</span>', unsafe_allow_html=True)
    if st.button("🍅  Toggle Timer", use_container_width=True):
        st.session_state.show_pomodoro = not st.session_state.show_pomodoro
        st.rerun()

    st.markdown("---")
    st.markdown('<span class="sb-lbl">Export & Clear</span>', unsafe_allow_html=True)
    st.download_button("⬇  Export Tasks", data=export_text(), file_name=f"tasks_{now.strftime('%Y%m%d')}.txt", mime="text/plain", use_container_width=True)
    if st.button("🗑  Clear History", use_container_width=True):
        clear_history(); st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# MAIN — HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="app-header">
  <div class="app-brand">
    <div class="app-title">Task<em>s</em></div>
    <div class="app-tagline">your command center</div>
  </div>
  <div class="app-meta">
    <div class="app-time">{now.strftime('%H:%M')}</div>
    <div class="app-date">{now.strftime('%A · %d %B %Y')}</div>
    <div class="app-quote">{st.session_state.daily_quote}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CELEBRATION BANNER
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.show_celebrate:
    st.markdown("""
    <div class="celebrate">
      <div class="celebrate-title">All tasks complete.</div>
      <div class="celebrate-sub">Exceptional. Zero pending. You are the system.</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("✕  Dismiss", key="dismiss_celebrate"):
        st.session_state.show_celebrate = False; st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# STATS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="stats-row">
  <div class="stat" style="--stat-accent:var(--acc);">
    <div class="stat-n">{total}</div>
    <div class="stat-l">Active</div>
  </div>
  <div class="stat" style="--stat-accent:var(--grn); --stat-color:var(--grn);">
    <div class="stat-n" style="color:var(--grn);">{done_ct}</div>
    <div class="stat-l">Completed</div>
  </div>
  <div class="stat" style="--stat-accent:var(--red);">
    <div class="stat-n" style="color:{'var(--red)' if overdue>0 else 'var(--t3)'};">{overdue}</div>
    <div class="stat-l">Overdue</div>
  </div>
  <div class="stat" style="--stat-accent:var(--org);">
    <div class="stat-n" style="color:{'var(--org)' if critical>0 else 'var(--t3)'};">{critical}</div>
    <div class="stat-l">Critical</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PROGRESS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="prog">
  <div class="prog-top">
    <span class="prog-lbl">Overall Progress</span>
    <span class="prog-pct">{int(ratio)}%</span>
  </div>
  <div class="prog-track">
    <div class="prog-fill" style="width:{ratio:.1f}%"></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# POMODORO  (toggled from sidebar)
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.show_pomodoro:
    if st.session_state.pomo_running and st.session_state.pomo_start:
        elapsed   = int((datetime.now() - st.session_state.pomo_start).total_seconds())
        remaining = max(0, st.session_state.pomo_seconds - elapsed)
    else:
        remaining = st.session_state.pomo_seconds
    m, s    = divmod(remaining, 60)
    p_state = "RUNNING" if st.session_state.pomo_running else "PAUSED"

    st.markdown(f"""
    <div class="pomo">
      <div class="pomo-time">{m:02d}:{s:02d}</div>
      <div class="pomo-state">🍅 Pomodoro · {p_state}</div>
    </div>
    """, unsafe_allow_html=True)

    pc1, pc2, pc3 = st.columns(3)
    with pc1:
        lbl = "⏸  Pause" if st.session_state.pomo_running else "▶  Start"
        if st.button(lbl, key="pomo_toggle", use_container_width=True):
            if not st.session_state.pomo_running:
                st.session_state.pomo_running = True
                st.session_state.pomo_start   = datetime.now()
            else:
                st.session_state.pomo_running = False
                st.session_state.pomo_seconds = remaining
                st.session_state.pomo_start   = None
            st.rerun()
    with pc2:
        if st.button("↺  Reset", key="pomo_reset", use_container_width=True):
            st.session_state.pomo_running = False
            st.session_state.pomo_seconds = 1500
            st.session_state.pomo_start   = None
            st.rerun()
    with pc3:
        dur = st.selectbox("Duration", ["25 min","15 min","10 min","5 min"], key="pomo_dur", label_visibility="collapsed")
        dur_map = {"25 min":1500,"15 min":900,"10 min":600,"5 min":300}
        if not st.session_state.pomo_running:
            st.session_state.pomo_seconds = dur_map.get(dur, 1500)

# ─────────────────────────────────────────────────────────────────────────────
# ADD TASK FORM  — styled via [data-testid="stForm"], NO wrapper divs
# ─────────────────────────────────────────────────────────────────────────────
# Section label ABOVE the form (pure HTML, no widget inside)
st.markdown(f"""
<div class="sec" style="margin-bottom:.7rem;">
  <span class="sec-lbl">New Task</span>
  <span class="sec-line"></span>
</div>
""", unsafe_allow_html=True)

with st.form(key=f"task_form_{st.session_state.input_key}", clear_on_submit=True):
    fc1, fc2 = st.columns([3, 1])
    with fc1:
        task_input = st.text_input("Task", placeholder="What needs to be done?")
    with fc2:
        prio_input = st.selectbox("Priority", list(PRIORITIES.keys()), index=2)

    fc3, fc4, fc5 = st.columns([2, 1, 1])
    with fc3:
        notes_input = st.text_input("Notes", placeholder="Optional context or details…")
    with fc4:
        cat_input = st.selectbox("Category", CATEGORIES)
    with fc5:
        # BUG FIX: value=None properly handled; added try/except in add_task
        due_input = st.date_input("Due date", value=None, min_value=today, format="YYYY-MM-DD")

    submitted = st.form_submit_button("＋  Add Task")
    if submitted:
        if task_input.strip():
            add_task(task_input, prio_input, cat_input, due_input, notes_input)
            st.session_state.show_celebrate = False
            st.rerun()
        else:
            st.warning("Please enter a task name.", icon="⚠️")

# ─────────────────────────────────────────────────────────────────────────────
# TASK LIST
# ─────────────────────────────────────────────────────────────────────────────
filtered   = get_filtered_tasks()
filt_count = len(filtered)

st.markdown(f"""
<div class="sec">
  <span class="sec-lbl">Active Tasks</span>
  <span class="sec-ct">{filt_count}</span>
  <span class="sec-line"></span>
</div>
""", unsafe_allow_html=True)

if total == 0:
    st.markdown("""
    <div class="empty">
      <span class="empty-glyph">◈</span>
      <div class="empty-lbl">All clear</div>
      <div class="empty-sub">Add a task above to begin</div>
    </div>
    """, unsafe_allow_html=True)
elif filt_count == 0:
    st.markdown("""
    <div class="empty">
      <span class="empty-glyph">○</span>
      <div class="empty-lbl">No matches</div>
      <div class="empty-sub">Adjust your search or filters</div>
    </div>
    """, unsafe_allow_html=True)
else:
    for task in filtered:
        task_id    = task["id"]
        prio_color = PRIORITIES.get(task.get("priority",""), "#404060")
        cat        = task.get("category","Uncategorized")
        pinned     = task.get("pinned", False)
        due_lbl, due_cls = due_status(task.get("due"))

        # Build badge HTML fragments
        prio_colors = {
            "● Critical": "color:var(--red);background:rgba(244,63,94,.1);border:1px solid rgba(244,63,94,.25);",
            "● High":     "color:var(--org);background:rgba(251,146,60,.1);border:1px solid rgba(251,146,60,.25);",
            "● Medium":   "color:var(--yel);background:rgba(251,191,36,.1);border:1px solid rgba(251,191,36,.25);",
            "● Low":      "color:var(--grn);background:rgba(34,211,160,.1);border:1px solid rgba(34,211,160,.25);",
        }
        prio_style  = prio_colors.get(task.get("priority",""), "color:var(--t3);background:var(--bd);border:1px solid var(--bd2);")
        pin_tag     = '<span class="task-pin-tag">pinned</span>' if pinned else ""
        notes_frag  = f'<div class="task-notes">{task["notes"]}</div>' if task.get("notes") else ""
        due_frag    = f'<span class="badge {due_cls}">{due_lbl}</span>' if due_lbl else ""
        prio_frag   = f'<span class="badge" style="{prio_style}">{task.get("priority","")}</span>'
        cat_frag    = f'<span class="badge cat-badge">{CAT_ICONS.get(cat,"·")} {cat}</span>'
        added_frag  = f'<span class="task-added">{task.get("added","")}</span>'
        name_cls    = "task-name overdue" if due_lbl and "OVERDUE" in due_lbl else "task-name"
        pin_cls     = "task-card is-pinned" if pinned else "task-card"

        # ── Task card HTML (pure display, no Streamlit widgets inside) ────────
        # ── Action buttons in same horizontal block, in their own columns ─────
        # Using [task_html_col | ✓ | ✕ | 📌 | ↑ | ↓]
        col_info, col_done, col_del, col_pin, col_up, col_dn = st.columns([7, 1, 1, 1, 1, 1])

        with col_info:
            st.markdown(f"""
            <div class="{pin_cls}">
              <div class="task-pbar" style="background:{prio_color};"></div>
              <div class="{name_cls}">{task['text']}{pin_tag}</div>
              <div class="task-meta">{prio_frag}{cat_frag}{due_frag}{added_frag}</div>
              {notes_frag}
            </div>
            """, unsafe_allow_html=True)

        with col_done:
            if st.button("✓", key=f"done_{task_id}", help="Mark complete"):
                complete_task(task_id); st.rerun()
        with col_del:
            if st.button("✕", key=f"del_{task_id}", help="Delete task"):
                delete_task(task_id); st.rerun()
        with col_pin:
            if st.button("📌", key=f"pin_{task_id}", help="Pin/unpin"):
                toggle_pin(task_id); st.rerun()
        with col_up:
            if st.button("↑", key=f"up_{task_id}", help="Move up"):
                move_task(task_id, -1); st.rerun()
        with col_dn:
            if st.button("↓", key=f"dn_{task_id}", help="Move down"):
                move_task(task_id, +1); st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# COMPLETED HISTORY
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.completed:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="sec">
      <span class="sec-lbl">Completed</span>
      <span class="sec-ct">{done_ct}</span>
      <span class="sec-line"></span>
    </div>
    """, unsafe_allow_html=True)

    with st.expander(f"Show {done_ct} completed task{'s' if done_ct != 1 else ''}", expanded=False):
        for ci, ct in enumerate(st.session_state.completed):
            st.markdown(f"""
            <div class="hist-card">
              <div class="hist-dot">✓</div>
              <div class="hist-text">{ct['text']}</div>
              <div class="hist-time">{ct.get('done_at','')}</div>
            </div>
            """, unsafe_allow_html=True)
            # Remove individual completed item — no div wrapper
            if st.button("remove", key=f"rm_{ci}_{ct.get('id',ci)}", help="Remove"):
                delete_completed(ci); st.rerun()

        st.markdown("---")
        if st.button("🗑  Clear All Completed", key="clear_all_hist", use_container_width=True):
            clear_history(); st.rerun()
