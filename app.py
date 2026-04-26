import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date, time
import uuid

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TaskBoard · Student Planner",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Persistence helpers ───────────────────────────────────────────────────────
DATA_FILE = "tasks.json"

def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=2, default=str)

# ── Session state ─────────────────────────────────────────────────────────────
if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks()
if "show_form" not in st.session_state:
    st.session_state.show_form = False
if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

# ── Constants ─────────────────────────────────────────────────────────────────
CATEGORIES = [
    "📝  Assignment Deadline",
    "📚  Exam",
    "🧪  Scheduled Quiz",
    "🎤  Presentation",
    "📖  Study Session",
    "🔬  Lab Report",
    "💻  Project Milestone",
    "📌  Other",
]

COURSES = [
    "Data Structures & Algorithms",
    "Object Oriented Programming",
    "Database Systems",
    "Operating Systems",
    "Computer Networks",
    "Software Engineering",
    "Discrete Mathematics",
    "Linear Algebra",
    "Probability & Statistics",
    "Web Engineering",
    "Artificial Intelligence",
    "Computer Architecture",
    "Custom (type below)…",
]

PRIORITY = ["🔴  High", "🟡  Medium", "🟢  Low"]

CAT_COLORS = {
    "📝  Assignment Deadline": "#FF6B6B",
    "📚  Exam":               "#FF4D4D",
    "🧪  Scheduled Quiz":     "#FFA94D",
    "🎤  Presentation":       "#A78BFA",
    "📖  Study Session":      "#4DABF7",
    "🔬  Lab Report":         "#69DB7C",
    "💻  Project Milestone":  "#F59F00",
    "📌  Other":              "#ADB5BD",
}

PRIORITY_COLORS = {
    "🔴  High":   "#FF4D4D",
    "🟡  Medium": "#FFA94D",
    "🟢  Low":    "#69DB7C",
}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Background */
.stApp {
    background: #0D0F14;
    color: #E8EAF0;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #12151C !important;
    border-right: 1px solid #1E2330;
}

/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }

/* Header */
.tb-header {
    padding: 2rem 0 1.5rem 0;
    margin-bottom: 1rem;
}
.tb-header h1 {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2.6rem;
    letter-spacing: -1px;
    color: #FFFFFF;
    margin: 0;
}
.tb-header h1 span {
    color: #6C63FF;
}
.tb-header p {
    color: #6B7280;
    margin: 4px 0 0 0;
    font-size: 0.95rem;
}

/* Stats row */
.stat-card {
    background: #12151C;
    border: 1px solid #1E2330;
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    text-align: center;
}
.stat-card .num {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #6C63FF;
    line-height: 1;
}
.stat-card .lbl {
    font-size: 0.75rem;
    color: #6B7280;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Task card */
.task-card {
    background: #12151C;
    border: 1px solid #1E2330;
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.9rem;
    transition: border-color 0.2s;
    position: relative;
    overflow: hidden;
}
.task-card:hover { border-color: #6C63FF; }
.task-card.done {
    opacity: 0.45;
    border-color: #1E2330 !important;
}
.task-card .accent-bar {
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 4px;
    border-radius: 4px 0 0 4px;
}
.task-card .cat-badge {
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.task-card .task-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: #FFFFFF;
    margin: 0 0 4px 0;
}
.task-card.done .task-title {
    text-decoration: line-through;
    color: #6B7280;
}
.task-card .course-name {
    font-size: 0.82rem;
    color: #6B7280;
    margin-bottom: 0.5rem;
}
.task-card .meta-row {
    display: flex;
    gap: 1rem;
    font-size: 0.8rem;
    color: #6B7280;
    margin-top: 0.5rem;
    flex-wrap: wrap;
}
.task-card .meta-row span {
    display: flex;
    align-items: center;
    gap: 4px;
}
.task-card .overdue {
    color: #FF4D4D !important;
    font-weight: 600;
}
.task-card .due-soon {
    color: #FFA94D !important;
    font-weight: 600;
}
.task-card .desc {
    font-size: 0.85rem;
    color: #9CA3AF;
    margin-top: 0.5rem;
    border-top: 1px solid #1E2330;
    padding-top: 0.5rem;
}

/* Section title */
.section-title {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 1.5rem 0 0.8rem 0;
}

/* Add button */
.stButton > button {
    background: #6C63FF;
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.9rem;
    padding: 0.55rem 1.4rem;
    transition: background 0.2s, transform 0.1s;
}
.stButton > button:hover {
    background: #5A52E8;
    transform: translateY(-1px);
}
.stButton > button:active { transform: translateY(0); }

/* Form styling */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div,
.stDateInput > div > div > input {
    background: #1A1D27 !important;
    border: 1px solid #2A2D3E !important;
    border-radius: 10px !important;
    color: #E8EAF0 !important;
}

/* Streamlit selectbox dropdown */
div[data-baseweb="select"] > div {
    background: #1A1D27 !important;
    border-color: #2A2D3E !important;
    border-radius: 10px !important;
}

/* Expander */
details {
    background: #12151C;
    border: 1px solid #1E2330 !important;
    border-radius: 12px;
    padding: 0.3rem 0.8rem;
}

/* Empty state */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: #6B7280;
}
.empty-state .icon { font-size: 3rem; margin-bottom: 1rem; }
.empty-state h3 {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    color: #9CA3AF;
    margin-bottom: 0.5rem;
}

/* Checkbox styling */
.stCheckbox > label { color: #9CA3AF; font-size: 0.85rem; }

/* Filter row */
.filter-label {
    font-size: 0.75rem;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
    margin-bottom: 0.3rem;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def days_until(date_str):
    try:
        d = datetime.strptime(str(date_str), "%Y-%m-%d").date()
        return (d - date.today()).days
    except:
        return 9999

def format_date(date_str):
    try:
        d = datetime.strptime(str(date_str), "%Y-%m-%d")
        return d.strftime("%d %b %Y")
    except:
        return str(date_str)

def format_time(time_str):
    try:
        return datetime.strptime(str(time_str), "%H:%M:%S").strftime("%I:%M %p")
    except:
        try:
            return datetime.strptime(str(time_str), "%H:%M").strftime("%I:%M %p")
        except:
            return str(time_str)

def date_label(days):
    if days < 0:    return f"⚠ {abs(days)}d overdue", "overdue"
    if days == 0:   return "⚡ Due today", "due-soon"
    if days == 1:   return "⏰ Due tomorrow", "due-soon"
    if days <= 3:   return f"⏳ {days} days left", "due-soon"
    return f"📅 {days} days left", ""

def get_unique_courses():
    courses = set()
    for t in st.session_state.tasks:
        courses.add(t.get("course", ""))
    return sorted(courses)


# ── Add / Edit form ───────────────────────────────────────────────────────────
def task_form(edit_task=None):
    is_edit = edit_task is not None
    title_val     = edit_task.get("title", "")          if is_edit else ""
    cat_val       = edit_task.get("category", CATEGORIES[0]) if is_edit else CATEGORIES[0]
    course_val    = edit_task.get("course", COURSES[0]) if is_edit else COURSES[0]
    custom_course = edit_task.get("custom_course", "")  if is_edit else ""
    priority_val  = edit_task.get("priority", PRIORITY[1]) if is_edit else PRIORITY[1]
    desc_val      = edit_task.get("description", "")    if is_edit else ""
    date_val      = datetime.strptime(str(edit_task.get("due_date", date.today())), "%Y-%m-%d").date() if is_edit else date.today()
    time_val_str  = edit_task.get("due_time", "")       if is_edit else ""

    with st.form("task_form", clear_on_submit=True):
        st.markdown(f"### {'✏️ Edit Task' if is_edit else '➕ Add New Task'}")
        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Task Title *", value=title_val, placeholder="e.g. Submit DSA Assignment")
        with col2:
            category = st.selectbox("Category *", CATEGORIES,
                                    index=CATEGORIES.index(cat_val) if cat_val in CATEGORIES else 0)

        col3, col4 = st.columns(2)
        with col3:
            course_choice = st.selectbox("Course *", COURSES,
                                         index=COURSES.index(course_val) if course_val in COURSES else 0)
        with col4:
            priority = st.selectbox("Priority", PRIORITY,
                                    index=PRIORITY.index(priority_val) if priority_val in PRIORITY else 1)

        if course_choice == "Custom (type below)…":
            custom_course = st.text_input("Custom Course Name", value=custom_course,
                                          placeholder="Enter your course name")
        else:
            custom_course = ""

        col5, col6 = st.columns(2)
        with col5:
            due_date = st.date_input("Due Date *", value=date_val, min_value=date(2020, 1, 1))
        with col6:
            due_time_input = st.time_input("Due Time (optional)",
                                           value=datetime.strptime(time_val_str, "%H:%M:%S").time()
                                           if time_val_str else time(23, 59))

        description = st.text_area("Description (optional)", value=desc_val,
                                   placeholder="Add any notes, links, or details…", height=100)

        col_sub, col_cancel = st.columns([1, 3])
        with col_sub:
            submitted = st.form_submit_button("💾 Save Task" if is_edit else "✅ Add Task",
                                              use_container_width=True)
        with col_cancel:
            cancelled = st.form_submit_button("Cancel", use_container_width=False)

        if cancelled:
            st.session_state.show_form = False
            st.session_state.edit_id = None
            st.rerun()

        if submitted:
            if not title.strip():
                st.error("Task title is required.")
                return
            final_course = custom_course.strip() if course_choice == "Custom (type below)…" else course_choice
            if not final_course:
                st.error("Please enter a course name.")
                return

            task = {
                "id":           edit_task["id"] if is_edit else str(uuid.uuid4()),
                "title":        title.strip(),
                "category":     category,
                "course":       final_course,
                "priority":     priority,
                "due_date":     str(due_date),
                "due_time":     str(due_time_input),
                "description":  description.strip(),
                "done":         edit_task.get("done", False) if is_edit else False,
                "added_at":     edit_task.get("added_at", datetime.now().isoformat()) if is_edit else datetime.now().isoformat(),
            }

            if is_edit:
                st.session_state.tasks = [t if t["id"] != task["id"] else task
                                          for t in st.session_state.tasks]
            else:
                st.session_state.tasks.append(task)

            save_tasks(st.session_state.tasks)
            st.session_state.show_form = False
            st.session_state.edit_id = None
            st.success("Task saved!" if is_edit else "Task added!")
            st.rerun()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1.2rem 0 0.5rem 0;">
        <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800;color:#fff;">
            Task<span style="color:#6C63FF;">Board</span>
        </div>
        <div style="font-size:0.78rem;color:#6B7280;margin-top:2px;">Student Planner</div>
    </div>
    <hr style="border-color:#1E2330;margin:0.8rem 0;">
    """, unsafe_allow_html=True)

    if st.button("＋  Add New Task", use_container_width=True):
        st.session_state.show_form = True
        st.session_state.edit_id = None

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # Filters
    st.markdown("**🔍 Filter & Sort**")

    sort_by = st.selectbox("Sort by", [
        "Deadline (soonest first)",
        "Deadline (latest first)",
        "Priority (high → low)",
        "Alphabetically (A–Z)",
        "Alphabetically (Z–A)",
        "Date Added (newest)",
        "Date Added (oldest)",
    ])

    filter_cat = st.multiselect("Category", [c.split("  ")[1] for c in CATEGORIES],
                                placeholder="All categories")

    all_courses = get_unique_courses()
    filter_course = st.multiselect("Course", all_courses, placeholder="All courses")

    filter_priority = st.multiselect("Priority", ["High", "Medium", "Low"],
                                     placeholder="All priorities")

    show_done = st.toggle("Show completed tasks", value=True)

    st.markdown("<hr style='border-color:#1E2330;margin:1rem 0'>", unsafe_allow_html=True)

    # Quick stats in sidebar
    tasks = st.session_state.tasks
    total     = len(tasks)
    done_cnt  = sum(1 for t in tasks if t.get("done"))
    overdue   = sum(1 for t in tasks if not t.get("done") and days_until(t["due_date"]) < 0)
    due_today = sum(1 for t in tasks if not t.get("done") and days_until(t["due_date"]) == 0)

    st.markdown(f"""
    <div style='font-size:0.75rem;color:#6B7280;text-transform:uppercase;letter-spacing:0.05em;font-weight:600;margin-bottom:0.6rem'>Overview</div>
    <div style='display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;'>
        <div style='background:#1A1D27;border-radius:10px;padding:0.7rem;text-align:center;'>
            <div style='font-family:Syne,sans-serif;font-size:1.5rem;font-weight:800;color:#6C63FF'>{total}</div>
            <div style='font-size:0.7rem;color:#6B7280'>Total</div>
        </div>
        <div style='background:#1A1D27;border-radius:10px;padding:0.7rem;text-align:center;'>
            <div style='font-family:Syne,sans-serif;font-size:1.5rem;font-weight:800;color:#69DB7C'>{done_cnt}</div>
            <div style='font-size:0.7rem;color:#6B7280'>Done</div>
        </div>
        <div style='background:#1A1D27;border-radius:10px;padding:0.7rem;text-align:center;'>
            <div style='font-family:Syne,sans-serif;font-size:1.5rem;font-weight:800;color:#FF4D4D'>{overdue}</div>
            <div style='font-size:0.7rem;color:#6B7280'>Overdue</div>
        </div>
        <div style='background:#1A1D27;border-radius:10px;padding:0.7rem;text-align:center;'>
            <div style='font-family:Syne,sans-serif;font-size:1.5rem;font-weight:800;color:#FFA94D'>{due_today}</div>
            <div style='font-size:0.7rem;color:#6B7280'>Due Today</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Main area ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="tb-header">
    <h1>Task<span>Board</span></h1>
    <p>Your academic planner — stay on top of every deadline.</p>
</div>
""", unsafe_allow_html=True)

# Show form if needed
edit_task_data = None
if st.session_state.edit_id:
    for t in st.session_state.tasks:
        if t["id"] == st.session_state.edit_id:
            edit_task_data = t
            break

if st.session_state.show_form or st.session_state.edit_id:
    task_form(edit_task=edit_task_data)
    st.markdown("---")

# ── Filter & sort tasks ───────────────────────────────────────────────────────
tasks = st.session_state.tasks[:]

# Filter
if not show_done:
    tasks = [t for t in tasks if not t.get("done")]

if filter_cat:
    tasks = [t for t in tasks if any(fc in t.get("category", "") for fc in filter_cat)]

if filter_course:
    tasks = [t for t in tasks if t.get("course", "") in filter_course]

if filter_priority:
    tasks = [t for t in tasks if any(fp in t.get("priority", "") for fp in filter_priority)]

# Sort
if sort_by == "Deadline (soonest first)":
    tasks.sort(key=lambda t: (t.get("done", False), days_until(t["due_date"])))
elif sort_by == "Deadline (latest first)":
    tasks.sort(key=lambda t: (t.get("done", False), -days_until(t["due_date"])))
elif sort_by == "Priority (high → low)":
    pmap = {"🔴  High": 0, "🟡  Medium": 1, "🟢  Low": 2}
    tasks.sort(key=lambda t: (t.get("done", False), pmap.get(t.get("priority", ""), 1)))
elif sort_by == "Alphabetically (A–Z)":
    tasks.sort(key=lambda t: (t.get("done", False), t.get("title", "").lower()))
elif sort_by == "Alphabetically (Z–A)":
    tasks.sort(key=lambda t: (t.get("done", False), t.get("title", "").lower()), reverse=True)
elif sort_by == "Date Added (newest)":
    tasks.sort(key=lambda t: (t.get("done", False), t.get("added_at", "")), reverse=True)
elif sort_by == "Date Added (oldest)":
    tasks.sort(key=lambda t: (t.get("done", False), t.get("added_at", "")))

# ── Render tasks ──────────────────────────────────────────────────────────────
pending = [t for t in tasks if not t.get("done")]
done    = [t for t in tasks if t.get("done")]

def render_task(task):
    tid   = task["id"]
    done_ = task.get("done", False)
    cat   = task.get("category", "📌  Other")
    color = CAT_COLORS.get(cat, "#ADB5BD")
    pcolor = PRIORITY_COLORS.get(task.get("priority", ""), "#ADB5BD")
    days  = days_until(task["due_date"])
    dlabel, dcls = date_label(days)
    card_cls = "task-card done" if done_ else "task-card"

    cat_label = cat.split("  ")[-1] if "  " in cat else cat

    time_str = f" · {format_time(task['due_time'])}" if task.get("due_time") else ""
    desc_html = f'<div class="desc">{task["description"]}</div>' if task.get("description") else ""
    pri_label = task.get("priority", "").split("  ")[-1] if "  " in task.get("priority","") else task.get("priority","")

    st.markdown(f"""
    <div class="{card_cls}">
        <div class="accent-bar" style="background:{color}"></div>
        <div style="padding-left:0.5rem">
            <div>
                <span class="cat-badge" style="background:{color}22;color:{color}">{cat_label}</span>
                <span class="cat-badge" style="background:{pcolor}22;color:{pcolor};margin-left:6px">{pri_label}</span>
            </div>
            <div class="task-title">{"✅ " if done_ else ""}{task["title"]}</div>
            <div class="course-name">📚 {task["course"]}</div>
            <div class="meta-row">
                <span class="{dcls}">{dlabel}</span>
                <span>🗓 {format_date(task["due_date"])}{time_str}</span>
                <span>🕐 Added {datetime.fromisoformat(task["added_at"]).strftime("%d %b") if task.get("added_at") else "—"}</span>
            </div>
            {desc_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        btn_label = "↩️ Mark Pending" if done_ else "✅ Mark Done"
        if st.button(btn_label, key=f"done_{tid}", use_container_width=True):
            for t in st.session_state.tasks:
                if t["id"] == tid:
                    t["done"] = not t["done"]
                    break
            save_tasks(st.session_state.tasks)
            st.rerun()
    with col2:
        if st.button("✏️ Edit", key=f"edit_{tid}", use_container_width=True):
            st.session_state.edit_id = tid
            st.session_state.show_form = False
            st.rerun()
    with col3:
        if st.button("🗑 Delete", key=f"del_{tid}", use_container_width=True):
            st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != tid]
            save_tasks(st.session_state.tasks)
            st.rerun()

    st.markdown("<div style='margin-bottom:0.2rem'></div>", unsafe_allow_html=True)


if not tasks:
    st.markdown("""
    <div class="empty-state">
        <div class="icon">📭</div>
        <h3>No tasks here</h3>
        <p>Hit "Add New Task" to get started.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    if pending:
        st.markdown(f'<div class="section-title">📌 Pending — {len(pending)} task{"s" if len(pending)!=1 else ""}</div>',
                    unsafe_allow_html=True)
        for t in pending:
            render_task(t)

    if done and show_done:
        st.markdown(f'<div class="section-title">✅ Completed — {len(done)} task{"s" if len(done)!=1 else ""}</div>',
                    unsafe_allow_html=True)
        for t in done:
            render_task(t)
