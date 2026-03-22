import streamlit as st
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TASKS",
    page_icon="◈",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Session state ─────────────────────────────────────────────────────────────
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "completed" not in st.session_state:
    st.session_state.completed = []
if "input_key" not in st.session_state:
    st.session_state.input_key = 0

# ── Helpers ───────────────────────────────────────────────────────────────────
def add_task(text: str):
    if text.strip():
        st.session_state.tasks.append({"text": text.strip(), "added": datetime.now().strftime("%H:%M")})
        st.session_state.input_key += 1

def complete_task(idx: int):
    task = st.session_state.tasks.pop(idx)
    task["done"] = datetime.now().strftime("%H:%M")
    st.session_state.completed.insert(0, task)

def delete_task(idx: int):
    st.session_state.tasks.pop(idx)

def clear_history():
    st.session_state.completed = []

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@400;600;700;800&display=swap');

  /* ── Reset & Base ── */
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background: #080808 !important;
    color: #e8e8e0 !important;
    font-family: 'DM Mono', monospace !important;
  }

  /* Hide Streamlit chrome */
  #MainMenu, footer, header, [data-testid="stToolbar"],
  [data-testid="stDecoration"], [data-testid="stStatusWidget"] { display: none !important; }

  .block-container {
    max-width: 680px !important;
    padding: 3rem 1.5rem 6rem !important;
  }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 3px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: #2a2a2a; border-radius: 2px; }

  /* ── Header ── */
  .app-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    padding-bottom: 2rem;
    border-bottom: 1px solid #1a1a1a;
    margin-bottom: 2.5rem;
  }
  .app-title {
    font-family: 'Syne', sans-serif;
    font-size: 3.2rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 1;
    color: #f0f0e8;
  }
  .app-title span { color: #c8f564; }
  .app-meta {
    text-align: right;
    font-size: 0.68rem;
    letter-spacing: 0.12em;
    color: #3a3a3a;
    line-height: 1.8;
    text-transform: uppercase;
  }

  /* ── Stats bar ── */
  .stats-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1px;
    background: #1a1a1a;
    border: 1px solid #1a1a1a;
    border-radius: 4px;
    margin-bottom: 2.5rem;
    overflow: hidden;
  }
  .stat-cell {
    background: #0e0e0e;
    padding: 1rem 1.2rem;
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
  }
  .stat-num {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: #f0f0e8;
    line-height: 1;
  }
  .stat-num.accent { color: #c8f564; }
  .stat-label {
    font-size: 0.62rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #383838;
  }

  /* ── Progress bar ── */
  .prog-wrap {
    margin-bottom: 2.5rem;
  }
  .prog-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
    font-size: 0.62rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #383838;
  }
  .prog-track {
    height: 2px;
    background: #1a1a1a;
    border-radius: 2px;
    overflow: hidden;
  }
  .prog-fill {
    height: 100%;
    background: linear-gradient(90deg, #c8f564, #a8e040);
    border-radius: 2px;
    transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  }

  /* ── Input ── */
  .input-wrap {
    display: flex;
    gap: 0;
    margin-bottom: 2.5rem;
    border: 1px solid #1e1e1e;
    border-radius: 4px;
    overflow: hidden;
    transition: border-color 0.2s;
  }
  .input-wrap:focus-within { border-color: #2e2e2e; }

  [data-testid="stTextInput"] { flex: 1; }
  [data-testid="stTextInput"] > div { padding: 0 !important; }
  [data-testid="stTextInput"] input {
    background: #0e0e0e !important;
    border: none !important;
    border-radius: 0 !important;
    color: #e8e8e0 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.85rem !important;
    padding: 0.9rem 1.2rem !important;
    outline: none !important;
    box-shadow: none !important;
  }
  [data-testid="stTextInput"] input::placeholder { color: #2a2a2a !important; }
  [data-testid="stTextInput"] input:focus { box-shadow: none !important; }
  [data-testid="stTextInput"] label { display: none !important; }

  /* ── Buttons ── */
  [data-testid="stButton"] button {
    background: #c8f564 !important;
    color: #080808 !important;
    border: none !important;
    border-radius: 0 !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    padding: 0.9rem 1.4rem !important;
    cursor: pointer !important;
    transition: background 0.15s, transform 0.1s !important;
    white-space: nowrap !important;
    min-height: unset !important;
    height: auto !important;
  }
  [data-testid="stButton"] button:hover {
    background: #d8ff74 !important;
    transform: none !important;
    border: none !important;
  }
  [data-testid="stButton"] button:active { transform: scale(0.98) !important; }

  /* ── Section labels ── */
  .section-label {
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #2e2e2e;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.8rem;
  }
  .section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #1a1a1a;
  }

  /* ── Task items ── */
  .task-item {
    display: flex;
    align-items: center;
    gap: 0;
    border: 1px solid #141414;
    border-radius: 4px;
    margin-bottom: 6px;
    background: #0b0b0b;
    overflow: hidden;
    transition: border-color 0.2s, background 0.2s;
    animation: slideIn 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  }
  @keyframes slideIn {
    from { opacity: 0; transform: translateY(-8px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .task-item:hover { border-color: #222; background: #0e0e0e; }
  .task-index {
    padding: 0.85rem 1rem;
    font-size: 0.62rem;
    color: #282828;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    border-right: 1px solid #141414;
    min-width: 3rem;
    text-align: center;
    letter-spacing: 0.05em;
  }
  .task-text {
    flex: 1;
    padding: 0.85rem 1.1rem;
    font-size: 0.85rem;
    color: #c8c8c0;
    letter-spacing: 0.01em;
  }
  .task-added {
    padding: 0.85rem 0.8rem;
    font-size: 0.6rem;
    color: #252525;
    letter-spacing: 0.06em;
    border-right: 1px solid #141414;
  }

  /* Task action buttons – tiny ghost */
  .task-item [data-testid="stButton"] button {
    background: transparent !important;
    color: #282828 !important;
    font-size: 0.75rem !important;
    padding: 0.85rem 0.8rem !important;
    border-radius: 0 !important;
    font-family: 'DM Mono', monospace !important;
    font-weight: 400 !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
    border-left: 1px solid #141414 !important;
    width: 2.8rem;
  }
  .task-item [data-testid="stButton"] button:hover {
    background: #141414 !important;
    color: #c8f564 !important;
  }

  /* ── History items ── */
  .hist-item {
    display: flex;
    align-items: center;
    gap: 0;
    border: 1px solid #111;
    border-radius: 4px;
    margin-bottom: 5px;
    background: #090909;
    overflow: hidden;
    opacity: 0.5;
    transition: opacity 0.2s;
  }
  .hist-item:hover { opacity: 0.75; }
  .hist-done { color: #c8f564; font-size: 0.72rem; padding: 0.7rem 0.9rem; border-right: 1px solid #111; }
  .hist-text {
    flex: 1;
    padding: 0.7rem 1rem;
    font-size: 0.8rem;
    color: #383838;
    text-decoration: line-through;
    text-decoration-color: #222;
    letter-spacing: 0.01em;
  }
  .hist-time { padding: 0.7rem 0.9rem; font-size: 0.6rem; color: #202020; }

  /* ── Empty state ── */
  .empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: #1e1e1e;
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }
  .empty-icon { font-size: 1.8rem; display: block; margin-bottom: 0.8rem; opacity: 0.3; }

  /* ── Clock pulse ── */
  .clock-dot {
    display: inline-block;
    width: 5px; height: 5px;
    border-radius: 50%;
    background: #c8f564;
    margin-right: 6px;
    animation: pulse 2s ease-in-out infinite;
    vertical-align: middle;
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.2; }
  }

  /* ── Columns fix ── */
  [data-testid="column"] { padding: 0 !important; }
  div[data-testid="stHorizontalBlock"] { gap: 0 !important; }

  /* ── Form submit ── */
  [data-testid="stForm"] { border: none !important; padding: 0 !important; }

  /* ── Divider ── */
  hr { border-color: #111 !important; margin: 2rem 0 !important; }

  /* Remove red underlines from inputs */
  [data-testid="stTextInput"] [aria-invalid] { border: none !important; box-shadow: none !important; }
</style>
""", unsafe_allow_html=True)

# ── Computed values ────────────────────────────────────────────────────────────
total   = len(st.session_state.tasks)
done    = len(st.session_state.completed)
ratio   = done / (total + done) * 100 if (total + done) > 0 else 0
now     = datetime.now()
weekday = now.strftime("%A").upper()
date_s  = now.strftime("%d %b %Y").upper()
time_s  = now.strftime("%H:%M")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="app-header">
  <div class="app-title">TASK<span>S</span></div>
  <div class="app-meta">
    <span class="clock-dot"></span>{time_s}<br>
    {weekday}<br>
    {date_s}
  </div>
</div>
""", unsafe_allow_html=True)

# ── Stats ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="stats-row">
  <div class="stat-cell">
    <span class="stat-num">{total}</span>
    <span class="stat-label">Pending</span>
  </div>
  <div class="stat-cell">
    <span class="stat-num accent">{done}</span>
    <span class="stat-label">Completed</span>
  </div>
  <div class="stat-cell">
    <span class="stat-num">{int(ratio)}<span style="font-size:1rem;color:#282828">%</span></span>
    <span class="stat-label">Done rate</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Progress ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="prog-wrap">
  <div class="prog-header">
    <span>progress</span>
    <span>{int(ratio)}% complete</span>
  </div>
  <div class="prog-track">
    <div class="prog-fill" style="width:{ratio}%"></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="input-wrap">', unsafe_allow_html=True)
with st.form(key=f"add_form_{st.session_state.input_key}", clear_on_submit=True):
    cols = st.columns([5, 1])
    with cols[0]:
        task_input = st.text_input(
            "task",
            placeholder="what needs to be done?",
            label_visibility="collapsed",
            key=f"task_input_{st.session_state.input_key}"
        )
    with cols[1]:
        submitted = st.form_submit_button("ADD")
    if submitted and task_input.strip():
        add_task(task_input)
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ── Task list ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">active tasks</div>', unsafe_allow_html=True)

if not st.session_state.tasks:
    st.markdown("""
    <div class="empty-state">
      <span class="empty-icon">◈</span>
      no pending tasks
    </div>
    """, unsafe_allow_html=True)
else:
    for i, task in enumerate(st.session_state.tasks):
        st.markdown(f"""
        <div class="task-item">
          <span class="task-index">{str(i+1).zfill(2)}</span>
          <span class="task-text">{task['text']}</span>
          <span class="task-added">{task['added']}</span>
        </div>
        """, unsafe_allow_html=True)
        # Inline action buttons rendered outside the card HTML for Streamlit compat
        btn_cols = st.columns([7, 1, 1])
        with btn_cols[1]:
            if st.button("✓", key=f"done_{i}", help="Complete"):
                complete_task(i)
                st.rerun()
        with btn_cols[2]:
            if st.button("✕", key=f"del_{i}", help="Delete"):
                delete_task(i)
                st.rerun()

# ── History ───────────────────────────────────────────────────────────────────
if st.session_state.completed:
    st.markdown('<hr>', unsafe_allow_html=True)
    col_h, col_c = st.columns([4, 1])
    with col_h:
        st.markdown('<div class="section-label">completed</div>', unsafe_allow_html=True)
    with col_c:
        if st.button("CLEAR", key="clear_hist"):
            clear_history()
            st.rerun()

    for task in st.session_state.completed:
        st.markdown(f"""
        <div class="hist-item">
          <span class="hist-done">✓</span>
          <span class="hist-text">{task['text']}</span>
          <span class="hist-time">{task.get('done','')}</span>
        </div>
        """, unsafe_allow_html=True)
