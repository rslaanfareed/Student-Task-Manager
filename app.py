import streamlit as st
import json
import os
from datetime import datetime, date, time
import uuid
import html

st.set_page_config(
    page_title="TaskBoard",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = "tasks.json"
COURSES_FILE = "courses.json"

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
        "Data Structures and Algorithms",
        "Object Oriented Programming",
        "Database Systems",
        "Operating Systems",
        "Computer Networks",
        "Software Engineering",
        "Discrete Mathematics",
        "Linear Algebra",
        "Probability and Statistics",
        "Web Engineering",
        "Artificial Intelligence",
        "Computer Architecture",
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

if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks()
if "courses" not in st.session_state:
    st.session_state.courses = load_courses()
if "show_form" not in st.session_state:
    st.session_state.show_form = False
if "edit_id" not in st.session_state:
    st.session_state.edit_id = None
if "show_add_course" not in st.session_state:
    st.session_state.show_add_course = False

CATEGORIES = [
    "Assignment Deadline",
    "Exam",
    "Scheduled Quiz",
    "Presentation",
    "Study Session",
    "Lab Report",
    "Project Milestone",
    "Other",
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

PRIORITY_COLORS = {
    "High":   "#E05C5C",
    "Medium": "#E09A3A",
    "Low":    "#3EAD72",
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Manrope', sans-serif !important;
}

.stApp {
    background: #0A0C10;
    color: #D1D5DB;
}

section[data-testid="stSidebar"] {
    background: #0E1117 !important;
    border-right: 1px solid #1C2030;
}

#MainMenu, footer, header { visibility: hidden; }

.tb-logo {
    font-size: 1.3rem;
    font-weight: 800;
    color: #fff;
    letter-spacing: -0.5px;
    padding: 1.4rem 0 0.2rem 0;
}
.tb-logo span { color: #6366F1; }
.tb-sub {
    font-size: 0.72rem;
    color: #4B5563;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 1.2rem;
}

.page-title {
    font-size: 2rem;
    font-weight: 800;
    color: #F9FAFB;
    letter-spacing: -0.8px;
    margin: 1.8rem 0 0.2rem 0;
}
.page-sub {
    font-size: 0.88rem;
    color: #4B5563;
    margin-bottom: 1.6rem;
    font-weight: 400;
}

.stat-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}
.stat-box {
    background: #13161F;
    border: 1px solid #1C2030;
    border-radius: 10px;
    padding: 0.8rem 0.6rem;
    text-align: center;
}
.stat-box .n {
    font-size: 1.6rem;
    font-weight: 800;
    line-height: 1;
    color: #6366F1;
}
.stat-box .n.red { color: #E05C5C; }
.stat-box .n.amber { color: #E09A3A; }
.stat-box .n.green { color: #3EAD72; }
.stat-box .l {
    font-size: 0.65rem;
    color: #4B5563;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-top: 3px;
    font-weight: 600;
}

.section-label {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #374151;
    margin: 1.4rem 0 0.6rem 0;
}

.task-card {
    background: #0E1117;
    border: 1px solid #1C2030;
    border-radius: 12px;
    padding: 1.1rem 1.2rem 1.1rem 1.5rem;
    margin-bottom: 0.7rem;
    position: relative;
    transition: border-color 0.15s;
}
.task-card:hover { border-color: #6366F1; }
.task-card.done { opacity: 0.38; }

.task-card .bar {
    position: absolute;
    left: 0; top: 12px; bottom: 12px;
    width: 3px;
    border-radius: 3px;
}

.badge {
    display: inline-block;
    font-size: 0.62rem;
    font-weight: 700;
    padding: 2px 9px;
    border-radius: 4px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-right: 5px;
    margin-bottom: 0.55rem;
}

.task-title {
    font-size: 0.98rem;
    font-weight: 700;
    color: #F3F4F6;
    margin: 0 0 2px 0;
    letter-spacing: -0.2px;
}
.task-card.done .task-title {
    text-decoration: line-through;
    color: #4B5563;
}

.task-course {
    font-size: 0.78rem;
    color: #6366F1;
    font-weight: 600;
    margin-bottom: 0.45rem;
}

.task-meta {
    display: flex;
    gap: 1.2rem;
    font-size: 0.75rem;
    color: #4B5563;
    flex-wrap: wrap;
    font-weight: 500;
}
.task-meta .overdue { color: #E05C5C; font-weight: 700; }
.task-meta .soon    { color: #E09A3A; font-weight: 700; }
.task-meta .ok      { color: #4B5563; }

.task-desc {
    font-size: 0.78rem;
    color: #6B7280;
    margin-top: 0.6rem;
    padding-top: 0.6rem;
    border-top: 1px solid #1C2030;
    font-weight: 400;
    line-height: 1.5;
}

.stButton > button {
    background: #6366F1;
    color: #fff;
    border: none;
    border-radius: 8px;
    font-family: 'Manrope', sans-serif !important;
    font-weight: 700;
    font-size: 0.82rem;
    padding: 0.45rem 1rem;
    letter-spacing: 0.01em;
}
.stButton > button:hover { background: #4F52D3; }

div[data-baseweb="select"] > div,
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stDateInput > div > div > input,
.stTimeInput > div > div > input {
    background: #13161F !important;
    border: 1px solid #1C2030 !important;
    border-radius: 8px !important;
    color: #D1D5DB !important;
    font-family: 'Manrope', sans-serif !important;
}

label, .stSelectbox label, .stTextInput label,
.stTextArea label, .stDateInput label {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    color: #6B7280 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}

.empty-msg {
    text-align: center;
    padding: 5rem 0;
    color: #374151;
}
.empty-msg h3 {
    font-size: 1.1rem;
    font-weight: 700;
    color: #4B5563;
    margin-bottom: 0.3rem;
}
.empty-msg p { font-size: 0.85rem; }

hr { border-color: #1C2030 !important; }

.form-box {
    background: #0E1117;
    border: 1px solid #1C2030;
    border-radius: 14px;
    padding: 1.6rem;
    margin-bottom: 1.5rem;
}
.form-title {
    font-size: 1rem;
    font-weight: 800;
    color: #F3F4F6;
    margin-bottom: 1.2rem;
    letter-spacing: -0.3px;
}
</style>
""", unsafe_allow_html=True)


def days_until(date_str):
    try:
        d = datetime.strptime(str(date_str), "%Y-%m-%d").date()
        return (d - date.today()).days
    except:
        return 9999

def fmt_date(date_str):
    try:
        return datetime.strptime(str(date_str), "%Y-%m-%d").strftime("%d %b %Y")
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

def deadline_label(days):
    if days < 0:   return f"{abs(days)}d overdue", "overdue"
    if days == 0:  return "Due today", "soon"
    if days == 1:  return "Due tomorrow", "soon"
    if days <= 4:  return f"{days} days left", "soon"
    return f"{days} days left", "ok"


# ---------- sidebar ----------

with st.sidebar:
    st.markdown('<div class="tb-logo">Task<span>Board</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="tb-sub">Student Planner</div>', unsafe_allow_html=True)

    if st.button("Add New Task", use_container_width=True):
        st.session_state.show_form = True
        st.session_state.edit_id = None

    st.markdown('<div class="section-label">Filter and Sort</div>', unsafe_allow_html=True)

    sort_by = st.selectbox("Sort by", [
        "Deadline (soonest first)",
        "Deadline (latest first)",
        "Priority (high to low)",
        "Alphabetically (A to Z)",
        "Alphabetically (Z to A)",
        "Date Added (newest)",
        "Date Added (oldest)",
    ], label_visibility="collapsed")

    filter_cat = st.multiselect("Category", CATEGORIES, placeholder="All categories")

    all_courses = sorted(set(
        [t.get("course", "") for t in st.session_state.tasks] + st.session_state.courses
    ))
    filter_course = st.multiselect("Course", all_courses, placeholder="All courses")

    filter_priority = st.multiselect("Priority", PRIORITY, placeholder="All priorities")

    show_done = st.toggle("Show completed", value=True)

    st.markdown('<div class="section-label">Overview</div>', unsafe_allow_html=True)

    tasks_all = st.session_state.tasks
    total     = len(tasks_all)
    done_cnt  = sum(1 for t in tasks_all if t.get("done"))
    overdue   = sum(1 for t in tasks_all if not t.get("done") and days_until(t["due_date"]) < 0)
    due_today = sum(1 for t in tasks_all if not t.get("done") and days_until(t["due_date"]) == 0)

    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-box"><div class="n">{total}</div><div class="l">Total</div></div>
        <div class="stat-box"><div class="n green">{done_cnt}</div><div class="l">Done</div></div>
        <div class="stat-box"><div class="n red">{overdue}</div><div class="l">Overdue</div></div>
        <div class="stat-box"><div class="n amber">{due_today}</div><div class="l">Today</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Courses</div>', unsafe_allow_html=True)
    if st.button("Manage Courses", use_container_width=True):
        st.session_state.show_add_course = not st.session_state.show_add_course


# ---------- main area ----------

st.markdown('<div class="page-title">TaskBoard</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Stay on top of every deadline.</div>', unsafe_allow_html=True)


# ---------- manage courses panel ----------

if st.session_state.show_add_course:
    with st.container(border=True):
        st.markdown('<div class="form-title">Manage Courses</div>', unsafe_allow_html=True)
        new_course = st.text_input("Add a new course", placeholder="e.g. Compiler Construction")
        c1, c2 = st.columns([1, 3])
        with c1:
            if st.button("Add Course", use_container_width=True):
                nc = new_course.strip()
                if nc and nc not in st.session_state.courses:
                    st.session_state.courses.append(nc)
                    save_courses(st.session_state.courses)
                    st.success(f'"{nc}" added.')
                    st.rerun()
                elif nc in st.session_state.courses:
                    st.warning("Already exists.")
        if st.session_state.courses:
            st.markdown("**Current courses** (click to remove):")
            cols = st.columns(3)
            for i, c in enumerate(sorted(st.session_state.courses)):
                with cols[i % 3]:
                    if st.button(f"x  {c}", key=f"rm_{c}", use_container_width=True):
                        st.session_state.courses.remove(c)
                        save_courses(st.session_state.courses)
                        st.rerun()


# ---------- add/edit form ----------

def task_form(edit_task=None):
    is_edit = edit_task is not None
    courses = sorted(st.session_state.courses)

    title_val    = edit_task.get("title", "")              if is_edit else ""
    cat_val      = edit_task.get("category", CATEGORIES[0]) if is_edit else CATEGORIES[0]
    course_val   = edit_task.get("course", courses[0] if courses else "") if is_edit else (courses[0] if courses else "")
    priority_val = edit_task.get("priority", "Medium")     if is_edit else "Medium"
    desc_val     = edit_task.get("description", "")        if is_edit else ""
    date_val     = datetime.strptime(str(edit_task.get("due_date", date.today())), "%Y-%m-%d").date() if is_edit else date.today()
    time_val_str = edit_task.get("due_time", "")           if is_edit else ""

    st.markdown(f'<div class="form-title">{"Edit Task" if is_edit else "New Task"}</div>', unsafe_allow_html=True)
    with st.form("task_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Task Title", value=title_val, placeholder="e.g. Submit DSA Assignment")
        with col2:
            cat_idx = CATEGORIES.index(cat_val) if cat_val in CATEGORIES else 0
            category = st.selectbox("Category", CATEGORIES, index=cat_idx)

        col3, col4 = st.columns(2)
        with col3:
            course_idx = courses.index(course_val) if course_val in courses else 0
            course = st.selectbox("Course", courses if courses else ["No courses added yet"], index=course_idx)
        with col4:
            pri_idx = PRIORITY.index(priority_val) if priority_val in PRIORITY else 1
            priority = st.selectbox("Priority", PRIORITY, index=pri_idx)

        col5, col6 = st.columns(2)
        with col5:
            due_date = st.date_input("Due Date", value=date_val, min_value=date(2020, 1, 1))
        with col6:
            try:
                tval = datetime.strptime(time_val_str, "%H:%M:%S").time() if time_val_str else time(23, 59)
            except:
                tval = time(23, 59)
            due_time_input = st.time_input("Due Time", value=tval)

        description = st.text_area("Description (optional)", value=desc_val,
                                   placeholder="Notes, links, anything relevant.", height=90)

        col_s, col_c = st.columns([1, 4])
        with col_s:
            submitted = st.form_submit_button("Save Task", use_container_width=True)
        with col_c:
            cancelled = st.form_submit_button("Cancel")

        if cancelled:
            st.session_state.show_form = False
            st.session_state.edit_id = None
            st.rerun()

        if submitted:
            if not title.strip():
                st.error("Title is required.")
                return
            if not courses:
                st.error("Add at least one course first.")
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


# ---------- filter and sort ----------

tasks = st.session_state.tasks[:]

if not show_done:
    tasks = [t for t in tasks if not t.get("done")]

if filter_cat:
    tasks = [t for t in tasks if t.get("category", "") in filter_cat]

if filter_course:
    tasks = [t for t in tasks if t.get("course", "") in filter_course]

if filter_priority:
    tasks = [t for t in tasks if t.get("priority", "") in filter_priority]

pmap = {"High": 0, "Medium": 1, "Low": 2}

if sort_by == "Deadline (soonest first)":
    tasks.sort(key=lambda t: (t.get("done", False), days_until(t["due_date"])))
elif sort_by == "Deadline (latest first)":
    tasks.sort(key=lambda t: (t.get("done", False), -days_until(t["due_date"])))
elif sort_by == "Priority (high to low)":
    tasks.sort(key=lambda t: (t.get("done", False), pmap.get(t.get("priority", ""), 1)))
elif sort_by == "Alphabetically (A to Z)":
    tasks.sort(key=lambda t: (t.get("done", False), t.get("title", "").lower()))
elif sort_by == "Alphabetically (Z to A)":
    tasks.sort(key=lambda t: (t.get("done", False), t.get("title", "").lower()), reverse=True)
elif sort_by == "Date Added (newest)":
    tasks.sort(key=lambda t: (t.get("done", False), t.get("added_at", "")), reverse=True)
elif sort_by == "Date Added (oldest)":
    tasks.sort(key=lambda t: (t.get("done", False), t.get("added_at", "")))


# ---------- render ----------

def render_task(task):
    tid    = task["id"]
    done_  = task.get("done", False)
    cat    = task.get("category", "Other")
    color  = CAT_COLORS.get(cat, "#6B7280")
    pcolor = PRIORITY_COLORS.get(task.get("priority", ""), "#6B7280")
    days   = days_until(task["due_date"])
    dlabel, dcls = deadline_label(days)
    card_cls = "task-card done" if done_ else "task-card"

    time_part = fmt_time(task.get("due_time", ""))
    time_display = f"  {time_part}" if time_part else ""

    # Safe-escape description to prevent any HTML rendering
    raw_desc = task.get("description", "")
    desc_html = ""
    if raw_desc:
        safe_desc = html.escape(raw_desc)
        desc_html = f'<div class="task-desc">{safe_desc}</div>'

    added_str = ""
    if task.get("added_at"):
        try:
            added_str = datetime.fromisoformat(task["added_at"]).strftime("%d %b")
        except:
            pass

    safe_title = html.escape(task.get("title", ""))
    safe_course = html.escape(task.get("course", ""))

    st.markdown(f"""
    <div class="{card_cls}">
        <div class="bar" style="background:{color}"></div>
        <div style="margin-left:0.6rem">
            <div>
                <span class="badge" style="background:{color}1A;color:{color}">{html.escape(cat)}</span>
                <span class="badge" style="background:{pcolor}1A;color:{pcolor}">{html.escape(task.get("priority",""))}</span>
            </div>
            <div class="task-title">{safe_title}</div>
            <div class="task-course">{safe_course}</div>
            <div class="task-meta">
                <span class="{dcls}">{dlabel}</span>
                <span>{fmt_date(task["due_date"])}{time_display}</span>
                {"<span>Added " + added_str + "</span>" if added_str else ""}
            </div>
            {desc_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

    ca, cb, cc = st.columns([2, 1, 1])
    with ca:
        btn_lbl = "Mark Pending" if done_ else "Mark Done"
        if st.button(btn_lbl, key=f"done_{tid}", use_container_width=True):
            for t in st.session_state.tasks:
                if t["id"] == tid:
                    t["done"] = not t["done"]
                    break
            save_tasks(st.session_state.tasks)
            st.rerun()
    with cb:
        if st.button("Edit", key=f"edit_{tid}", use_container_width=True):
            st.session_state.edit_id = tid
            st.session_state.show_form = False
            st.rerun()
    with cc:
        if st.button("Delete", key=f"del_{tid}", use_container_width=True):
            st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != tid]
            save_tasks(st.session_state.tasks)
            st.rerun()


pending = [t for t in tasks if not t.get("done")]
done    = [t for t in tasks if t.get("done")]

if not tasks:
    st.markdown("""
    <div class="empty-msg">
        <h3>No tasks</h3>
        <p>Hit "Add New Task" in the sidebar to get started.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    if pending:
        n = len(pending)
        st.markdown(f'<div class="section-label">Pending &nbsp; {n} task{"s" if n != 1 else ""}</div>',
                    unsafe_allow_html=True)
        for t in pending:
            render_task(t)

    if done and show_done:
        n = len(done)
        st.markdown(f'<div class="section-label">Completed &nbsp; {n} task{"s" if n != 1 else ""}</div>',
                    unsafe_allow_html=True)
        for t in done:
            render_task(t)
