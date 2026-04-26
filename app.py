import streamlit as st
import json
import os
from datetime import datetime, date, time
import uuid
import html as htmllib

st.set_page_config(
    page_title="TaskBoard · UET Taxila",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Data ──────────────────────────────────────────────────────────────────────
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

# ── State ─────────────────────────────────────────────────────────────────────
if "tasks"        not in st.session_state: st.session_state.tasks        = load_tasks()
if "courses"      not in st.session_state: st.session_state.courses      = load_courses()
if "show_form"    not in st.session_state: st.session_state.show_form    = False
if "edit_id"      not in st.session_state: st.session_state.edit_id      = None
if "show_courses" not in st.session_state: st.session_state.show_courses = False

CATEGORIES = [
    "Assignment Deadline", "Exam", "Scheduled Quiz", "Presentation",
    "Study Session", "Lab Report", "Project Milestone", "Other"
]
PRIORITY = ["High", "Medium", "Low"]

CAT_COLORS = {
    "Assignment Deadline": "#E05C5C", "Exam": "#E05C5C",
    "Scheduled Quiz": "#E09A3A",      "Presentation": "#9B7FE8",
    "Study Session": "#3A90D4",       "Lab Report": "#3EAD72",
    "Project Milestone": "#D4952A",   "Other": "#6B7280",
}
PRIORITY_COLORS = {"High": "#E05C5C", "Medium": "#E09A3A", "Low": "#3EAD72"}

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

*, html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

.stApp { background: #080A0F; color: #C9D1D9; }

/* hide streamlit chrome */
#MainMenu, footer { visibility: hidden; }
header { visibility: hidden; }
section[data-testid="stSidebar"] { display: none; }

.block-container {
    padding-top: 2.4rem !important;
    padding-bottom: 5rem !important;
    max-width: 1080px !important;
}

/* ── PAGE HEADER ── */
.page-header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    padding-bottom: 1.4rem;
    border-bottom: 1px solid #1A1F2E;
    margin-bottom: 1.8rem;
}
.page-title {
    font-size: 2rem;
    font-weight: 800;
    color: #F0F2F5;
    letter-spacing: -0.03em;
    line-height: 1;
    margin: 0 0 4px 0;
}
.page-sub {
    font-size: 0.78rem;
    font-weight: 500;
    color: #3D4451;
    margin: 0;
    letter-spacing: 0.01em;
}

/* ── STATS ROW ── */
.stats-row {
    display: flex;
    gap: 0.6rem;
    margin-bottom: 1.6rem;
    flex-wrap: wrap;
}
.stat-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: #0E1117;
    border: 1px solid #1A1F2E;
    border-radius: 8px;
    padding: 0.45rem 1rem;
    font-size: 0.78rem;
    font-weight: 600;
    color: #5B6475;
    letter-spacing: 0.02em;
}
.stat-chip .sn {
    font-size: 1.05rem;
    font-weight: 800;
    letter-spacing: -0.02em;
}

/* ── FILTER ROW ── */
.filter-row-wrap {
    background: #0C0F18;
    border: 1px solid #1A1F2E;
    border-radius: 10px;
    padding: 1rem 1.2rem 0.8rem 1.2rem;
    margin-bottom: 1.8rem;
}
.filter-label {
    font-size: 0.62rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #2E3441;
    margin-bottom: 0.6rem;
}

/* ── BUTTONS ── */
.stButton > button {
    background: #5B5FE8;
    color: #fff;
    border: none;
    border-radius: 8px;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600;
    font-size: 0.81rem;
    padding: 0.5rem 1.1rem;
    letter-spacing: 0.01em;
    transition: background 0.15s;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.stButton > button:hover { background: #4B4FC8; border: none; }
.stButton > button:focus { outline: none; border: none; box-shadow: none; }

.stButton > button[kind="secondary"] {
    background: #13161F !important;
    border: 1px solid #2A2F42 !important;
    color: #9CA3AF !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #1C2030 !important;
    color: #D1D5DB !important;
    border-color: #3D4451 !important;
}

/* Delete button — target by key prefix */
button[data-testid*="del_"] {
    color: #B45454 !important;
    border-color: #3B1010 !important;
}
button[data-testid*="del_"]:hover {
    background: #1A0808 !important;
    color: #E05C5C !important;
}

.btn-success > button {
    background: #14372A !important;
    border: 1px solid #1A4D38 !important;
    color: #3EAD72 !important;
}
.btn-success > button:hover {
    background: #1A4D38 !important;
}

/* ── FORM INPUTS ── */
div[data-baseweb="select"] > div,
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stDateInput > div > div > input {
    background: #0C0F18 !important;
    border: 1px solid #1A1F2E !important;
    border-radius: 8px !important;
    color: #C9D1D9 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.87rem !important;
}

div[data-baseweb="select"] > div:focus-within,
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #5B5FE8 !important;
    box-shadow: 0 0 0 2px rgba(91,95,232,0.15) !important;
}

label {
    font-size: 0.69rem !important;
    font-weight: 700 !important;
    color: #3D4451 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

/* ── FORM PANEL ── */
.form-panel {
    background: #0C0F18;
    border: 1px solid #1A1F2E;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.8rem;
}
.form-title {
    font-size: 0.85rem;
    font-weight: 700;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 1.2rem;
}

/* ── TASK CARD ── */
.tc {
    background: #0C0F18;
    border: 1px solid #1A1F2E;
    border-radius: 12px;
    padding: 14px 16px 14px 20px;
    margin-bottom: 8px;
    border-left: 3px solid var(--ac);
    transition: border-color 0.15s;
}
.tc:hover { border-color: #2A2F42; }
.tc.done-card { opacity: 0.3; }

.tc-badges { margin-bottom: 5px; }
.tc-badge {
    display: inline-block;
    font-size: 0.58rem;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-right: 5px;
}
.tc-title {
    font-size: 0.93rem;
    font-weight: 700;
    color: #E8ECF0;
    margin: 0 0 2px 0;
    line-height: 1.3;
}
.tc-title-done {
    font-size: 0.93rem;
    font-weight: 700;
    color: #3D4451;
    margin: 0 0 2px 0;
    text-decoration: line-through;
    line-height: 1.3;
}
.tc-course {
    font-size: 0.74rem;
    font-weight: 600;
    color: #5B5FE8;
    margin-bottom: 5px;
}
.tc-meta       { font-size: 0.73rem; color: #3D4451; font-weight: 500; }
.tc-meta-overdue { font-size: 0.73rem; font-weight: 700; color: #E05C5C; }
.tc-meta-soon  { font-size: 0.73rem; font-weight: 700; color: #E09A3A; }
.tc-desc {
    font-size: 0.75rem;
    color: #4B5563;
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid #1A1F2E;
    line-height: 1.55;
}

/* ── SECTION LABEL ── */
.section-lbl {
    font-size: 0.62rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #2E3441;
    margin: 1.8rem 0 0.6rem 0;
}

/* ── EMPTY STATE ── */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: #2E3441;
}
.empty-state h3 {
    font-size: 1rem;
    font-weight: 700;
    color: #3D4451;
    margin-bottom: 0.4rem;
}
.empty-state p {
    font-size: 0.82rem;
}

/* ── COURSES GRID ── */
.course-hint {
    font-size: 0.69rem;
    font-weight: 700;
    color: #2E3441;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 0.8rem 0 0.5rem;
}

/* ── TOGGLE ── */
div[data-testid="stToggle"] label {
    color: #6B7280 !important;
    text-transform: none !important;
    font-size: 0.81rem !important;
    font-weight: 600 !important;
    letter-spacing: 0 !important;
}

/* ── DIVIDER ── */
hr { border: none; border-top: 1px solid #1A1F2E; margin: 1rem 0; }

/* ── WARNING / INFO ── */
.stAlert { border-radius: 8px !important; font-size: 0.82rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def days_until(date_str):
    try:
        return (datetime.strptime(str(date_str), "%Y-%m-%d").date() - date.today()).days
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

def deadline_info(days):
    if days < 0:    return f"{abs(days)}d overdue", "tc-meta-overdue"
    if days == 0:   return "Due today",              "tc-meta-soon"
    if days == 1:   return "Due tomorrow",            "tc-meta-soon"
    if days <= 4:   return f"{days} days left",       "tc-meta-soon"
    return f"{days} days left", "tc-meta"

# ── Stats (computed once) ─────────────────────────────────────────────────────
tasks_all = st.session_state.tasks
total     = len(tasks_all)
done_cnt  = sum(1 for t in tasks_all if t.get("done"))
overdue   = sum(1 for t in tasks_all if not t.get("done") and days_until(t["due_date"]) < 0)
due_today = sum(1 for t in tasks_all if not t.get("done") and days_until(t["due_date"]) == 0)

# ── PAGE HEADER ───────────────────────────────────────────────────────────────
h_left, h_btn1, h_btn2 = st.columns([4, 1, 1], gap="small", vertical_alignment="bottom")

with h_left:
    st.markdown("""
    <h1 class="page-title">TaskBoard</h1>
    <p class="page-sub">UET Taxila &nbsp;&middot;&nbsp; Student Planner</p>
    """, unsafe_allow_html=True)

with h_btn1:
    if st.button("Add Task", use_container_width=True, key="btn_add_task"):
        st.session_state.show_form = True
        st.session_state.edit_id = None

with h_btn2:
    if st.button("Courses", use_container_width=True, key="btn_courses", type="secondary"):
        st.session_state.show_courses = not st.session_state.show_courses

st.markdown('<hr style="margin-top:1rem;margin-bottom:1.5rem">', unsafe_allow_html=True)

# ── STATS ROW ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="stats-row">
    <div class="stat-chip"><span class="sn" style="color:#5B5FE8">{total}</span> Total</div>
    <div class="stat-chip"><span class="sn" style="color:#3EAD72">{done_cnt}</span> Done</div>
    <div class="stat-chip"><span class="sn" style="color:#E05C5C">{overdue}</span> Overdue</div>
    <div class="stat-chip"><span class="sn" style="color:#E09A3A">{due_today}</span> Due Today</div>
</div>
""", unsafe_allow_html=True)

# ── FILTER ROW ────────────────────────────────────────────────────────────────
with st.container():
    f1, f2, f3, f4, f5 = st.columns([2.2, 2, 2, 2, 1.4], gap="small")
    with f1:
        sort_by = st.selectbox("Sort By", [
            "Deadline (soonest first)", "Deadline (latest first)",
            "Priority (high to low)", "Alphabetically (A to Z)",
            "Alphabetically (Z to A)", "Date Added (newest)", "Date Added (oldest)",
        ])
    with f2:
        filter_cat = st.multiselect("Category", CATEGORIES, placeholder="All categories")
    with f3:
        all_courses = sorted(set(
            [t.get("course", "") for t in st.session_state.tasks] +
            st.session_state.courses
        ))
        filter_course = st.multiselect("Course", all_courses, placeholder="All courses")
    with f4:
        filter_priority = st.multiselect("Priority", PRIORITY, placeholder="All priorities")
    with f5:
        st.markdown(
            '<p style="font-size:0.69rem;font-weight:700;color:#3D4451;'
            'text-transform:uppercase;letter-spacing:0.08em;margin:0 0 0.55rem 0">'
            'Show Done</p>',
            unsafe_allow_html=True
        )
        show_done = st.toggle("Show Done", value=True, label_visibility="collapsed")

st.markdown("<hr style='margin-top:0.2rem;margin-bottom:1.4rem'>", unsafe_allow_html=True)

# ── MANAGE COURSES ────────────────────────────────────────────────────────────
if st.session_state.show_courses:
    st.markdown('<div class="form-title">Manage Courses</div>', unsafe_allow_html=True)

    ci1, ci2, ci3 = st.columns([5, 1, 4], gap="small")
    with ci1:
        new_course = st.text_input(
            "Course name",
            placeholder="e.g. Compiler Construction",
            key="new_course_input",
            label_visibility="collapsed"
        )
    with ci2:
        if st.button("Add", use_container_width=True, key="btn_add_course"):
            nc = new_course.strip()
            if nc and nc not in st.session_state.courses:
                st.session_state.courses.append(nc)
                save_courses(st.session_state.courses)
                st.rerun()
            elif nc in st.session_state.courses:
                st.warning("Already exists.")

    if st.session_state.courses:
        st.markdown('<p class="course-hint">Click a course to remove it</p>', unsafe_allow_html=True)
        cols = st.columns(3, gap="small")
        for i, c in enumerate(sorted(st.session_state.courses)):
            with cols[i % 3]:
                if st.button(c, key=f"rm_{c}", use_container_width=True, type="secondary"):
                    st.session_state.courses.remove(c)
                    save_courses(st.session_state.courses)
                    st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

# ── TASK FORM ─────────────────────────────────────────────────────────────────
def task_form(edit_task=None):
    is_edit = edit_task is not None
    courses = sorted(st.session_state.courses)

    if not courses:
        st.warning("Add at least one course first using the Courses button.")
        return

    title_val    = edit_task.get("title", "")                              if is_edit else ""
    cat_val      = edit_task.get("category", CATEGORIES[0])               if is_edit else CATEGORIES[0]
    course_val   = edit_task.get("course", courses[0])                     if is_edit else courses[0]
    priority_val = edit_task.get("priority", "Medium")                     if is_edit else "Medium"
    desc_val     = edit_task.get("description", "")                        if is_edit else ""
    date_val     = datetime.strptime(str(edit_task.get("due_date", date.today())), "%Y-%m-%d").date() \
                   if is_edit else date.today()
    time_val_str = edit_task.get("due_time", "") if is_edit else ""
    try:
        tval = datetime.strptime(time_val_str, "%H:%M:%S").time() if time_val_str else time(23, 59)
    except:
        tval = time(23, 59)

    st.markdown(
        f'<div class="form-title">{"Edit Task" if is_edit else "New Task"}</div>',
        unsafe_allow_html=True
    )

    with st.form("task_form", border=False):
        # Row 1: Title (full width)
        title = st.text_input("Task Title", value=title_val, placeholder="e.g. Submit SDA Assignment")

        # Row 2: Category | Course
        r2a, r2b = st.columns(2, gap="medium")
        with r2a:
            category = st.selectbox(
                "Category", CATEGORIES,
                index=CATEGORIES.index(cat_val) if cat_val in CATEGORIES else 0
            )
        with r2b:
            course = st.selectbox(
                "Course", courses,
                index=courses.index(course_val) if course_val in courses else 0
            )

        # Row 3: Priority | Due Date | Due Time
        r3a, r3b, r3c = st.columns(3, gap="medium")
        with r3a:
            priority = st.selectbox(
                "Priority", PRIORITY,
                index=PRIORITY.index(priority_val) if priority_val in PRIORITY else 1
            )
        with r3b:
            due_date = st.date_input("Due Date", value=date_val, min_value=date(2020, 1, 1))
        with r3c:
            due_time_input = st.time_input("Due Time", value=tval)

        # Row 4: Description
        description = st.text_area(
            "Description (optional)",
            value=desc_val,
            placeholder="Notes, links, anything relevant.",
            height=90
        )

        # Row 5: Buttons
        rb1, rb2, _ = st.columns([1, 1, 5], gap="small")
        with rb1:
            submitted = st.form_submit_button("Save Task", use_container_width=True)
        with rb2:
            cancelled = st.form_submit_button("Cancel", use_container_width=True)

    if cancelled:
        st.session_state.show_form = False
        st.session_state.edit_id = None
        st.rerun()

    if submitted:
        if not title.strip():
            st.error("Task title is required.")
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

# ── FILTER & SORT ─────────────────────────────────────────────────────────────
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

# ── RENDER TASK ───────────────────────────────────────────────────────────────
def render_task(task):
    tid    = task["id"]
    done_  = task.get("done", False)
    cat    = task.get("category", "Other")
    color  = CAT_COLORS.get(cat, "#6B7280")
    pcolor = PRIORITY_COLORS.get(task.get("priority", ""), "#6B7280")
    days   = days_until(task["due_date"])
    dlabel, dcls = deadline_info(days)

    time_part    = fmt_time(task.get("due_time", ""))
    time_display = f"  {time_part}" if time_part else ""

    safe_title  = htmllib.escape(task.get("title", ""))
    safe_course = htmllib.escape(task.get("course", ""))
    safe_cat    = htmllib.escape(cat)
    safe_pri    = htmllib.escape(task.get("priority", ""))
    safe_desc   = htmllib.escape(task.get("description", ""))

    added_str = ""
    if task.get("added_at"):
        try:
            added_str = datetime.fromisoformat(task["added_at"]).strftime("%d %b")
        except:
            pass

    title_cls = "tc-title-done" if done_ else "tc-title"
    card_cls  = "tc done-card"  if done_ else "tc"
    desc_block  = f'<p class="tc-desc">{safe_desc}</p>'     if safe_desc  else ""
    added_block = f'<span class="tc-meta"> &nbsp; Added {added_str}</span>' if added_str else ""

    st.markdown(f"""
    <div class="{card_cls}" style="--ac:{color}">
        <div class="tc-badges">
            <span class="tc-badge" style="background:{color}1A;color:{color}">{safe_cat}</span>
            <span class="tc-badge" style="background:{pcolor}1A;color:{pcolor}">{safe_pri}</span>
        </div>
        <p class="{title_cls}">{safe_title}</p>
        <p class="tc-course">{safe_course}</p>
        <p>
            <span class="{dcls}">{dlabel}</span>
            <span class="tc-meta">&nbsp; {fmt_date(task["due_date"])}{time_display}</span>
            {added_block}
        </p>
        {desc_block}
    </div>""", unsafe_allow_html=True)

    ca, cb, cc = st.columns([3, 1, 1], gap="small")
    with ca:
        label = "Mark Pending" if done_ else "Mark Done"
        wrap  = "btn-success" if not done_ else "btn-ghost"
        st.markdown(f'<div class="{wrap}">', unsafe_allow_html=True)
        if st.button(label, key=f"done_{tid}", use_container_width=True):
            for t in st.session_state.tasks:
                if t["id"] == tid:
                    t["done"] = not t["done"]
                    break
            save_tasks(st.session_state.tasks)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with cb:
        if st.button("Edit", key=f"edit_{tid}", use_container_width=True, type="secondary"):
            st.session_state.edit_id   = tid
            st.session_state.show_form = False
            st.rerun()

    with cc:
        if st.button("Delete", key=f"del_{tid}", use_container_width=True, type="secondary"):
            st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != tid]
            save_tasks(st.session_state.tasks)
            st.rerun()

# ── TASK LIST ─────────────────────────────────────────────────────────────────
pending = [t for t in tasks if not t.get("done")]
done    = [t for t in tasks if t.get("done")]

if not tasks:
    st.markdown("""
    <div class="empty-state">
        <h3>No tasks here</h3>
        <p>Hit Add Task to get started.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    if pending:
        n = len(pending)
        st.markdown(
            f'<p class="section-lbl">Pending &nbsp; {n} task{"s" if n != 1 else ""}</p>',
            unsafe_allow_html=True
        )
        for t in pending:
            render_task(t)

    if done and show_done:
        n = len(done)
        st.markdown(
            f'<p class="section-lbl">Completed &nbsp; {n} task{"s" if n != 1 else ""}</p>',
            unsafe_allow_html=True
        )
        for t in done:
            render_task(t)
