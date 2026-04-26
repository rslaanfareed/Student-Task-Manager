import streamlit as st
import json
import os
from datetime import datetime, date, time
import uuid
import html as htmllib

st.set_page_config(
    page_title="TaskBoard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DATA_FILE = "tasks.json"
COURSES_FILE = "courses.json"

# ── Data helpers ───────────────────────────────────────────────────────────────
def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=2, default=str)

def load_courses():
    default = [
        "Data Structures and Algorithms", "Object Oriented Programming",
        "Database Systems", "Operating Systems", "Computer Networks",
        "Software Engineering", "Discrete Mathematics", "Linear Algebra",
        "Probability and Statistics", "Web Engineering",
        "Artificial Intelligence", "Computer Architecture",
    ]
    if os.path.exists(COURSES_FILE):
        with open(COURSES_FILE, "r") as f:
            saved = json.load(f)
        for c in default:
            if c not in saved:
                saved.append(c)
        return saved
    return default

def save_courses(courses):
    with open(COURSES_FILE, "w") as f:
        json.dump(courses, f, indent=2)

# ── Session state ──────────────────────────────────────────────────────────────
if "tasks" not in st.session_state:          st.session_state.tasks = load_tasks()
if "courses" not in st.session_state:        st.session_state.courses = load_courses()
if "show_form" not in st.session_state:      st.session_state.show_form = False
if "edit_id" not in st.session_state:        st.session_state.edit_id = None
if "show_courses" not in st.session_state:   st.session_state.show_courses = False
if "confirm_delete_id" not in st.session_state: st.session_state.confirm_delete_id = None

CATEGORIES = [
    "Assignment Deadline", "Exam", "Scheduled Quiz", "Presentation",
    "Study Session", "Lab Report", "Project Milestone", "Other",
]
PRIORITY = ["High", "Medium", "Low"]

CAT_COLORS = {
    "Assignment Deadline": "#E05C5C",
    "Exam":                "#E05C5C",
    "Scheduled Quiz":      "#E09A3A",
    "Presentation":        "#9B7FE8",
    "Study Session":       "#3A90D4",
    "Lab Report":          "#3EAD72",
    "Project Milestone":   "#D4952A",
    "Other":               "#6B7280",
}
PRIORITY_COLORS = {"High": "#E05C5C", "Medium": "#E09A3A", "Low": "#3EAD72"}

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

*, html, body, [class*="css"] { font-family: 'Manrope', sans-serif !important; }
.stApp { background: #080A0F; color: #C9D1D9; }

/* ── hide sidebar completely ── */
[data-testid="collapsedControl"]  { display: none !important; }
section[data-testid="stSidebar"]  { display: none !important; }
#MainMenu, footer, header         { visibility: hidden; }

/* ── global button reset ── */
.stButton > button {
    background: #161B26;
    color: #9CA3AF;
    border: 1px solid #21293D;
    border-radius: 7px;
    font-family: 'Manrope', sans-serif !important;
    font-weight: 600;
    font-size: 0.78rem;
    padding: 0.35rem 0.85rem;
    transition: background 0.15s, border-color 0.15s, color 0.15s;
    white-space: nowrap;
}
.stButton > button:hover  { background: #1E2637; border-color: #3A4560; color: #E5E7EB; }
.stButton > button:focus  { outline: none !important; box-shadow: none !important; border-color: #4F6BFF; }

/* ── coloured button variants via wrapper classes ──
   We inject a <span class="v-*"> right before the button's parent col,
   then use the adjacent + stButton selector.  */
.v-primary + div > .stButton > button,
.v-primary ~ div .stButton > button   { background:#4F6BFF !important; color:#fff !important; border-color:#4F6BFF !important; }
.v-primary + div > .stButton > button:hover { background:#3B55E6 !important; border-color:#3B55E6 !important; }

.v-success + div > .stButton > button  { background:#0D2419 !important; color:#3EAD72 !important; border-color:#1A3D2A !important; }
.v-success + div > .stButton > button:hover { background:#112D20 !important; border-color:#3EAD72 !important; }

.v-danger + div > .stButton > button   { background:#1E0D0D !important; color:#E05C5C !important; border-color:#3A1515 !important; }
.v-danger + div > .stButton > button:hover  { background:#2A1212 !important; border-color:#E05C5C !important; }

.v-warn + div > .stButton > button     { background:#1E180D !important; color:#E09A3A !important; border-color:#3A2D15 !important; }
.v-warn + div > .stButton > button:hover { background:#231D10 !important; border-color:#E09A3A !important; }

/* ── form inputs ── */
div[data-baseweb="select"] > div,
.stTextInput  > div > div > input,
.stTextArea   > div > div > textarea,
.stDateInput  > div > div > input {
    background: #0E1117 !important;
    border: 1px solid #1C2538 !important;
    border-radius: 8px !important;
    color: #D1D5DB !important;
    font-family: 'Manrope', sans-serif !important;
    font-size: 0.85rem !important;
}
label {
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    color: #4B5563 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

/* ── divider ── */
.h-rule { border: none; border-top: 1px solid #141A26; margin: 0.6rem 0; }

/* ── stats strip ── */
.stats-strip { display: flex; gap: 0.6rem; margin: 0.75rem 0 0.9rem; }
.stat-pill {
    background: #0E1117;
    border: 1px solid #1C2538;
    border-radius: 9px;
    padding: 0.5rem 1rem;
    display: flex; align-items: center; gap: 0.55rem;
}
.stat-n { font-size: 1.25rem; font-weight: 800; line-height: 1; }
.stat-l { font-size: 0.6rem; color: #374151; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700; }

/* ── filter bar ── */
.filter-bar { 
    background: #0B0E16;
    border: 1px solid #141A26;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    margin-bottom: 1.1rem;
}

/* ── section label ── */
.sec-lbl {
    font-size: 0.6rem; font-weight: 800; text-transform: uppercase;
    letter-spacing: 0.12em; color: #252D3D;
    margin: 1rem 0 0.4rem;
    display: flex; align-items: center; gap: 8px;
}
.sec-lbl::after { content:''; flex:1; height:1px; background:#141A26; }

/* ── task card ── */
.tc {
    background: #0B0E16;
    border: 1px solid #141A26;
    border-radius: 9px;
    padding: 8px 12px 6px 14px;
    margin-bottom: 5px;
    border-left: 3px solid var(--ac);
}
.tc.done-card { opacity: 0.38; }
.tc-r1 { display: flex; align-items: center; gap: 7px; flex-wrap: nowrap; overflow: hidden; }
.tc-badge {
    display: inline-block;
    font-size: 0.56rem; font-weight: 800;
    padding: 2px 6px; border-radius: 4px;
    text-transform: uppercase; letter-spacing: 0.06em;
    white-space: nowrap; flex-shrink: 0;
}
.tc-title {
    font-size: 0.88rem; font-weight: 700; color: #E5E7EB;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex: 1;
}
.tc-title-done {
    font-size: 0.88rem; font-weight: 700; color: #2D3748;
    text-decoration: line-through;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex: 1;
}
.tc-r2 { display: flex; align-items: center; gap: 10px; margin-top: 3px; flex-wrap: wrap; }
.tc-course { font-size: 0.68rem; font-weight: 700; color: #4F6BFF; }
.tc-meta   { font-size: 0.68rem; color: #2D3748; font-weight: 500; }
.tc-overdue { font-size: 0.68rem; font-weight: 800; color: #E05C5C; }
.tc-soon    { font-size: 0.68rem; font-weight: 800; color: #E09A3A; }
.tc-desc    { font-size: 0.7rem; color: #374151; margin-top: 5px; padding-top: 5px; border-top: 1px solid #141A26; line-height: 1.5; }

/* ── confirm strip ── */
.confirm-strip {
    background: #12080A;
    border: 1px solid #3A1515;
    border-radius: 8px;
    padding: 7px 12px;
    margin-bottom: 5px;
    margin-top: -3px;
    display: flex; align-items: center; gap: 10px;
}
.confirm-txt { font-size: 0.78rem; color: #E05C5C; font-weight: 600; flex: 1; }

/* ── top brand ── */
.brand { font-size: 1.25rem; font-weight: 800; color: #E5E7EB; letter-spacing: -0.02em; }
.brand-sub { font-size: 0.7rem; color: #374151; font-weight: 500; margin-top: 1px; }

/* ── empty state ── */
.empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: #252D3D;
}
.empty-state .e-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
.empty-state .e-title { font-size: 1rem; font-weight: 700; margin-bottom: 0.25rem; color: #2D3748; }
.empty-state .e-sub   { font-size: 0.78rem; }
</style>
""", unsafe_allow_html=True)

# ── Utilities ─────────────────────────────────────────────────────────────────
def days_until(date_str):
    try:
        return (datetime.strptime(str(date_str), "%Y-%m-%d").date() - date.today()).days
    except:
        return 9999

def fmt_date(date_str):
    try:
        return datetime.strptime(str(date_str), "%Y-%m-%d").strftime("%d %b")
    except:
        return str(date_str)

def fmt_time(time_str):
    if not time_str:
        return ""
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(str(time_str), fmt).strftime("%I:%M %p")
        except:
            pass
    return ""

def deadline_info(days):
    if days < 0:  return f"{abs(days)}d overdue", "tc-overdue"
    if days == 0: return "Due today",              "tc-soon"
    if days == 1: return "Due tomorrow",           "tc-soon"
    if days <= 4: return f"{days}d left",          "tc-soon"
    return f"{days}d left", "tc-meta"

# ── Top bar ───────────────────────────────────────────────────────────────────
tasks_all = st.session_state.tasks
total     = len(tasks_all)
done_cnt  = sum(1 for t in tasks_all if t.get("done"))
overdue   = sum(1 for t in tasks_all if not t.get("done") and days_until(t["due_date"]) < 0)
due_today = sum(1 for t in tasks_all if not t.get("done") and days_until(t["due_date"]) == 0)

col_brand, col_gap, col_add, col_courses = st.columns([4, 2, 1, 1])
with col_brand:
    st.markdown('<div class="brand">📋 TaskBoard</div><div class="brand-sub">Student planner · UET Taxila</div>', unsafe_allow_html=True)
with col_add:
    st.markdown('<span class="v-primary"></span>', unsafe_allow_html=True)
    if st.button("＋ Add Task", use_container_width=True, key="top_add"):
        st.session_state.show_form = True
        st.session_state.edit_id = None
with col_courses:
    if st.button("⚙ Courses", use_container_width=True, key="top_courses"):
        st.session_state.show_courses = not st.session_state.show_courses

# Stats strip
st.markdown(f"""
<div class="stats-strip">
  <div class="stat-pill"><div class="stat-n" style="color:#4F6BFF">{total}</div><div class="stat-l">Total</div></div>
  <div class="stat-pill"><div class="stat-n" style="color:#3EAD72">{done_cnt}</div><div class="stat-l">Done</div></div>
  <div class="stat-pill"><div class="stat-n" style="color:#E05C5C">{overdue}</div><div class="stat-l">Overdue</div></div>
  <div class="stat-pill"><div class="stat-n" style="color:#E09A3A">{due_today}</div><div class="stat-l">Today</div></div>
</div>
""", unsafe_allow_html=True)

# ── Filter bar ────────────────────────────────────────────────────────────────
with st.container():
    fc1, fc2, fc3, fc4, fc5 = st.columns([2, 2, 2, 2, 1])
    with fc1:
        sort_by = st.selectbox("Sort by", [
            "Deadline ↑ (soonest)", "Deadline ↓ (latest)",
            "Priority (high → low)", "A → Z", "Z → A",
            "Newest added", "Oldest added",
        ])
    with fc2:
        filter_cat = st.multiselect("Category", CATEGORIES, placeholder="All categories")
    with fc3:
        all_courses = sorted(set(
            [t.get("course", "") for t in st.session_state.tasks] + st.session_state.courses
        ))
        filter_course = st.multiselect("Course", all_courses, placeholder="All courses")
    with fc4:
        filter_priority = st.multiselect("Priority", PRIORITY, placeholder="All priorities")
    with fc5:
        show_done = st.toggle("Show done", value=True)

st.markdown('<hr class="h-rule">', unsafe_allow_html=True)

# ── Manage Courses ─────────────────────────────────────────────────────────────
if st.session_state.show_courses:
    with st.expander("⚙ Manage Courses", expanded=True):
        ni1, ni2 = st.columns([4, 1])
        with ni1:
            new_course = st.text_input("Course name", placeholder="e.g. Compiler Construction", label_visibility="collapsed", key="new_course_input")
        with ni2:
            st.markdown('<span class="v-primary"></span>', unsafe_allow_html=True)
            if st.button("Add", use_container_width=True, key="add_course_btn"):
                nc = new_course.strip()
                if nc and nc not in st.session_state.courses:
                    st.session_state.courses.append(nc)
                    save_courses(st.session_state.courses)
                    st.rerun()
                elif nc in st.session_state.courses:
                    st.warning("Already exists.")
        if st.session_state.courses:
            st.caption("Click a course to remove it")
            cols = st.columns(4)
            for i, c in enumerate(sorted(st.session_state.courses)):
                with cols[i % 4]:
                    if st.button(c, key=f"rm_{c}", use_container_width=True):
                        st.session_state.courses.remove(c)
                        save_courses(st.session_state.courses)
                        st.rerun()

# ── Task form ──────────────────────────────────────────────────────────────────
def task_form(edit_task=None):
    is_edit = edit_task is not None
    courses = sorted(st.session_state.courses)
    if not courses:
        st.warning("Add at least one course first via ⚙ Courses.")
        return

    title_val    = edit_task.get("title", "")            if is_edit else ""
    cat_val      = edit_task.get("category", CATEGORIES[0]) if is_edit else CATEGORIES[0]
    course_val   = edit_task.get("course", courses[0])   if is_edit else courses[0]
    priority_val = edit_task.get("priority", "Medium")   if is_edit else "Medium"
    desc_val     = edit_task.get("description", "")      if is_edit else ""
    date_val     = datetime.strptime(str(edit_task.get("due_date", date.today())), "%Y-%m-%d").date() if is_edit else date.today()
    time_val_str = edit_task.get("due_time", "")         if is_edit else ""
    try:
        tval = datetime.strptime(time_val_str, "%H:%M:%S").time() if time_val_str else time(23, 59)
    except:
        tval = time(23, 59)

    header = "✏️ Edit Task" if is_edit else "＋ New Task"
    with st.expander(header, expanded=True):
        with st.form("task_form"):
            r1c1, r1c2, r1c3, r1c4 = st.columns([3, 2, 2, 1])
            with r1c1: title    = st.text_input("Task title *", value=title_val, placeholder="e.g. Submit DSA Assignment")
            with r1c2: category = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index(cat_val) if cat_val in CATEGORIES else 0)
            with r1c3: course   = st.selectbox("Course",   courses,    index=courses.index(course_val) if course_val in courses else 0)
            with r1c4: priority = st.selectbox("Priority", PRIORITY,   index=PRIORITY.index(priority_val) if priority_val in PRIORITY else 1)

            r2c1, r2c2, r2c3 = st.columns([1, 1, 3])
            with r2c1: due_date       = st.date_input("Due date", value=date_val, min_value=date(2020, 1, 1))
            with r2c2: due_time_input = st.time_input("Due time", value=tval)
            with r2c3: description    = st.text_area("Description (optional)", value=desc_val, placeholder="Notes, links, references…", height=68)

            ba, bb = st.columns([1, 5])
            with ba: submitted = st.form_submit_button("Save Task", use_container_width=True)
            with bb: cancelled = st.form_submit_button("Cancel")

            if cancelled:
                st.session_state.show_form = False
                st.session_state.edit_id = None
                st.rerun()

            if submitted:
                if not title.strip():
                    st.error("Title is required.")
                    return
                task = {
                    "id":          edit_task["id"] if is_edit else str(uuid.uuid4()),
                    "title":       title.strip(),
                    "category":    category,
                    "course":      course,
                    "priority":    priority,
                    "due_date":    str(due_date),
                    "due_time":    str(due_time_input),
                    "description": description.strip(),
                    "done":        edit_task.get("done", False) if is_edit else False,
                    "added_at":    edit_task.get("added_at", datetime.now().isoformat()) if is_edit else datetime.now().isoformat(),
                }
                if is_edit:
                    st.session_state.tasks = [t if t["id"] != task["id"] else task for t in st.session_state.tasks]
                else:
                    st.session_state.tasks.append(task)
                save_tasks(st.session_state.tasks)
                st.session_state.show_form = False
                st.session_state.edit_id = None
                st.rerun()

edit_task_data = None
if st.session_state.edit_id:
    for t in st.session_state.tasks:
        if t["id"] == st.session_state.edit_id:
            edit_task_data = t
            break

if st.session_state.show_form or st.session_state.edit_id:
    task_form(edit_task=edit_task_data)

# ── Filter & sort ──────────────────────────────────────────────────────────────
tasks = st.session_state.tasks[:]
if not show_done:     tasks = [t for t in tasks if not t.get("done")]
if filter_cat:        tasks = [t for t in tasks if t.get("category", "") in filter_cat]
if filter_course:     tasks = [t for t in tasks if t.get("course", "")   in filter_course]
if filter_priority:   tasks = [t for t in tasks if t.get("priority", "") in filter_priority]

pmap = {"High": 0, "Medium": 1, "Low": 2}
if   sort_by == "Deadline ↑ (soonest)":   tasks.sort(key=lambda t: (t.get("done", False),  days_until(t["due_date"])))
elif sort_by == "Deadline ↓ (latest)":    tasks.sort(key=lambda t: (t.get("done", False), -days_until(t["due_date"])))
elif sort_by == "Priority (high → low)":  tasks.sort(key=lambda t: (t.get("done", False),  pmap.get(t.get("priority", ""), 1)))
elif sort_by == "A → Z":                  tasks.sort(key=lambda t: (t.get("done", False),  t.get("title", "").lower()))
elif sort_by == "Z → A":                  tasks.sort(key=lambda t: (t.get("done", False),  t.get("title", "").lower()), reverse=True)
elif sort_by == "Newest added":           tasks.sort(key=lambda t: (t.get("done", False),  t.get("added_at", "")), reverse=True)
elif sort_by == "Oldest added":           tasks.sort(key=lambda t: (t.get("done", False),  t.get("added_at", "")))

# ── Render a single task card ──────────────────────────────────────────────────
def render_task(task):
    tid   = task["id"]
    done_ = task.get("done", False)
    cat   = task.get("category", "Other")
    color = CAT_COLORS.get(cat, "#6B7280")
    pclr  = PRIORITY_COLORS.get(task.get("priority", ""), "#6B7280")
    days  = days_until(task["due_date"])
    dlabel, dcls = deadline_info(days)
    tp    = fmt_time(task.get("due_time", ""))
    tdisp = f" · {tp}" if tp else ""

    st_title  = htmllib.escape(task.get("title", ""))
    st_course = htmllib.escape(task.get("course", ""))
    st_cat    = htmllib.escape(cat)
    st_pri    = htmllib.escape(task.get("priority", ""))
    st_desc   = htmllib.escape(task.get("description", ""))

    title_cls = "tc-title-done" if done_ else "tc-title"
    card_cls  = "tc done-card"  if done_ else "tc"
    desc_html = f'<div class="tc-desc">{st_desc}</div>' if st_desc else ""

    st.markdown(f"""
<div class="{card_cls}" style="--ac:{color}">
  <div class="tc-r1">
    <span class="tc-badge" style="background:{color}1A;color:{color}">{st_cat}</span>
    <span class="tc-badge" style="background:{pclr}1A;color:{pclr}">{st_pri}</span>
    <span class="{title_cls}">{st_title}</span>
  </div>
  <div class="tc-r2">
    <span class="tc-course">{st_course}</span>
    <span class="{dcls}">{dlabel}</span>
    <span class="tc-meta">{fmt_date(task['due_date'])}{tdisp}</span>
  </div>
  {desc_html}
</div>""", unsafe_allow_html=True)

    # ── Delete confirmation inline ─────────────────────────────────────────────
    if st.session_state.confirm_delete_id == tid:
        st.markdown(f"""
<div class="confirm-strip">
  <span class="confirm-txt">⚠️ Delete <b>"{st_title}"</b>? This cannot be undone.</span>
</div>""", unsafe_allow_html=True)
        cdy, cdn, _ = st.columns([1, 1, 4])
        with cdy:
            if st.button("✕ Yes, delete", key=f"cyes_{tid}", use_container_width=True):
                st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != tid]
                save_tasks(st.session_state.tasks)
                st.session_state.confirm_delete_id = None
                st.rerun()
        with cdn:
            if st.button("Keep it", key=f"cno_{tid}", use_container_width=True):
                st.session_state.confirm_delete_id = None
                st.rerun()
        return  # skip normal action buttons while confirming

    # ── Action buttons ────────────────────────────────────────────────────────
    ba, bb, bc = st.columns([2, 1, 1])
    with ba:
        label = "↩ Mark Pending" if done_ else "✓ Mark Done"
        if st.button(label, key=f"done_{tid}", use_container_width=True):
            for t in st.session_state.tasks:
                if t["id"] == tid:
                    t["done"] = not t["done"]
                    break
            save_tasks(st.session_state.tasks)
            st.rerun()
    with bb:
        if st.button("✏ Edit", key=f"edit_{tid}", use_container_width=True):
            st.session_state.edit_id   = tid
            st.session_state.show_form = False
            st.rerun()
    with bc:
        if st.button("🗑 Delete", key=f"del_{tid}", use_container_width=True):
            st.session_state.confirm_delete_id = tid
            st.rerun()

# ── Task list ──────────────────────────────────────────────────────────────────
pending_tasks   = [t for t in tasks if not t.get("done")]
completed_tasks = [t for t in tasks if t.get("done")]

if not tasks:
    st.markdown("""
<div class="empty-state">
  <div class="e-icon">📭</div>
  <div class="e-title">No tasks here</div>
  <div class="e-sub">Hit <b>＋ Add Task</b> to get started</div>
</div>""", unsafe_allow_html=True)
else:
    if pending_tasks:
        n = len(pending_tasks)
        st.markdown(f'<div class="sec-lbl">Pending &nbsp; {n} task{"s" if n != 1 else ""}</div>', unsafe_allow_html=True)
        for t in pending_tasks:
            render_task(t)

    if completed_tasks and show_done:
        n = len(completed_tasks)
        st.markdown(f'<div class="sec-lbl">Completed &nbsp; {n}</div>', unsafe_allow_html=True)
        for t in completed_tasks:
            render_task(t)
