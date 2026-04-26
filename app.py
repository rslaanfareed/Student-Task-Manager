import streamlit as st
import json
import os
from datetime import datetime, date, time
import uuid
import html as htmllib

st.set_page_config(
    page_title="TaskBoard",
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

if "tasks"           not in st.session_state: st.session_state.tasks           = load_tasks()
if "courses"         not in st.session_state: st.session_state.courses         = load_courses()
if "show_form"       not in st.session_state: st.session_state.show_form       = False
if "edit_id"         not in st.session_state: st.session_state.edit_id         = None
if "show_courses"    not in st.session_state: st.session_state.show_courses    = False

CATEGORIES = ["Assignment Deadline","Exam","Scheduled Quiz","Presentation",
               "Study Session","Lab Report","Project Milestone","Other"]
PRIORITY   = ["High","Medium","Low"]

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
PRIORITY_COLORS = {"High":"#E05C5C","Medium":"#E09A3A","Low":"#3EAD72"}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

*, html, body, [class*="css"] { font-family: 'Manrope', sans-serif !important; }
.stApp { background:#0A0C10; color:#D1D5DB; }
section[data-testid="stSidebar"] { background:#0E1117 !important; border-right:1px solid #1C2030; }
#MainMenu, footer, header { visibility:hidden; }

.stButton > button {
    background:#6366F1; color:#fff; border:none; border-radius:8px;
    font-family:'Manrope',sans-serif !important; font-weight:700;
    font-size:0.82rem; padding:0.45rem 1rem;
}
.stButton > button:hover { background:#4F52D3; border:none; }
.stButton > button:focus { outline:none; border:none; box-shadow:none; }

div[data-baseweb="select"] > div,
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stDateInput > div > div > input {
    background:#13161F !important; border:1px solid #1C2030 !important;
    border-radius:8px !important; color:#D1D5DB !important;
    font-family:'Manrope',sans-serif !important;
}
label {
    font-size:0.75rem !important; font-weight:600 !important;
    color:#6B7280 !important; text-transform:uppercase !important;
    letter-spacing:0.06em !important;
}

.tc {
    background:#0E1117;
    border:1px solid #1C2030;
    border-radius:12px;
    padding:14px 16px 14px 20px;
    margin-bottom:10px;
    border-left:3px solid var(--ac);
}
.tc.done-card { opacity:0.35; }
.tc-badges { margin-bottom:6px; }
.tc-badge {
    display:inline-block; font-size:0.6rem; font-weight:700;
    padding:2px 8px; border-radius:4px; text-transform:uppercase;
    letter-spacing:0.06em; margin-right:5px;
}
.tc-title { font-size:0.97rem; font-weight:700; color:#F3F4F6; margin:0 0 2px 0; }
.tc-title-done { font-size:0.97rem; font-weight:700; color:#4B5563; margin:0 0 2px 0; text-decoration:line-through; }
.tc-course { font-size:0.77rem; font-weight:600; color:#6366F1; margin-bottom:5px; }
.tc-meta { font-size:0.75rem; color:#4B5563; font-weight:500; }
.tc-meta-overdue { font-size:0.75rem; font-weight:700; color:#E05C5C; }
.tc-meta-soon    { font-size:0.75rem; font-weight:700; color:#E09A3A; }
.tc-desc { font-size:0.77rem; color:#6B7280; margin-top:8px; padding-top:8px; border-top:1px solid #1C2030; line-height:1.5; }
.section-lbl {
    font-size:0.66rem; font-weight:700; text-transform:uppercase;
    letter-spacing:0.1em; color:#374151; margin:1.4rem 0 0.6rem 0;
}
.stat-grid { display:grid; grid-template-columns:1fr 1fr; gap:0.5rem; margin-bottom:0.5rem; }
.stat-box { background:#13161F; border:1px solid #1C2030; border-radius:10px; padding:0.8rem 0.6rem; text-align:center; }
.stat-n { font-size:1.6rem; font-weight:800; line-height:1; }
.stat-l { font-size:0.63rem; color:#4B5563; text-transform:uppercase; letter-spacing:0.06em; margin-top:3px; font-weight:600; }
</style>
""", unsafe_allow_html=True)


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
    if days < 0:  return f"{abs(days)}d overdue", "tc-meta-overdue"
    if days == 0: return "Due today",     "tc-meta-soon"
    if days == 1: return "Due tomorrow",  "tc-meta-soon"
    if days <= 4: return f"{days} days left", "tc-meta-soon"
    return f"{days} days left", "tc-meta"


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## TaskBoard")
    st.caption("Student Planner")
    st.divider()

    if st.button("Add New Task", use_container_width=True):
        st.session_state.show_form = True
        st.session_state.edit_id   = None

    if st.button("Manage Courses", use_container_width=True):
        st.session_state.show_courses = not st.session_state.show_courses

    st.divider()
    st.caption("FILTER AND SORT")

    sort_by = st.selectbox("Sort by", [
        "Deadline (soonest first)", "Deadline (latest first)",
        "Priority (high to low)", "Alphabetically (A to Z)",
        "Alphabetically (Z to A)", "Date Added (newest)", "Date Added (oldest)",
    ])

    filter_cat      = st.multiselect("Category", CATEGORIES, placeholder="All categories")
    all_courses     = sorted(set([t.get("course","") for t in st.session_state.tasks] + st.session_state.courses))
    filter_course   = st.multiselect("Course", all_courses, placeholder="All courses")
    filter_priority = st.multiselect("Priority", PRIORITY, placeholder="All priorities")
    show_done       = st.toggle("Show completed", value=True)

    st.divider()
    tasks_all = st.session_state.tasks
    total     = len(tasks_all)
    done_cnt  = sum(1 for t in tasks_all if t.get("done"))
    overdue   = sum(1 for t in tasks_all if not t.get("done") and days_until(t["due_date"]) < 0)
    due_today = sum(1 for t in tasks_all if not t.get("done") and days_until(t["due_date"]) == 0)

    st.markdown(f"""
<div class="stat-grid">
<div class="stat-box"><div class="stat-n" style="color:#6366F1">{total}</div><div class="stat-l">Total</div></div>
<div class="stat-box"><div class="stat-n" style="color:#3EAD72">{done_cnt}</div><div class="stat-l">Done</div></div>
<div class="stat-box"><div class="stat-n" style="color:#E05C5C">{overdue}</div><div class="stat-l">Overdue</div></div>
<div class="stat-box"><div class="stat-n" style="color:#E09A3A">{due_today}</div><div class="stat-l">Today</div></div>
</div>
""", unsafe_allow_html=True)


# ── Main ──────────────────────────────────────────────────────────────────────
st.markdown("## TaskBoard")
st.caption("Stay on top of every deadline.")

# ── Manage Courses ────────────────────────────────────────────────────────────
if st.session_state.show_courses:
    with st.expander("Manage Courses", expanded=True):
        new_course = st.text_input("New course name", placeholder="e.g. Compiler Construction", key="new_course_input")
        if st.button("Add Course"):
            nc = new_course.strip()
            if nc and nc not in st.session_state.courses:
                st.session_state.courses.append(nc)
                save_courses(st.session_state.courses)
                st.rerun()
            elif nc in st.session_state.courses:
                st.warning("Already exists.")

        if st.session_state.courses:
            st.caption("Click a course to remove it")
            cols = st.columns(3)
            for i, c in enumerate(sorted(st.session_state.courses)):
                with cols[i % 3]:
                    if st.button(c, key=f"rm_{c}", use_container_width=True):
                        st.session_state.courses.remove(c)
                        save_courses(st.session_state.courses)
                        st.rerun()


# ── Task Form ─────────────────────────────────────────────────────────────────
def task_form(edit_task=None):
    is_edit  = edit_task is not None
    courses  = sorted(st.session_state.courses)
    if not courses:
        st.warning("Add at least one course first using Manage Courses.")
        return

    title_val    = edit_task.get("title", "")               if is_edit else ""
    cat_val      = edit_task.get("category", CATEGORIES[0]) if is_edit else CATEGORIES[0]
    course_val   = edit_task.get("course", courses[0])      if is_edit else courses[0]
    priority_val = edit_task.get("priority", "Medium")      if is_edit else "Medium"
    desc_val     = edit_task.get("description", "")         if is_edit else ""
    date_val     = datetime.strptime(str(edit_task.get("due_date", date.today())), "%Y-%m-%d").date() if is_edit else date.today()
    time_val_str = edit_task.get("due_time", "")            if is_edit else ""
    try:
        tval = datetime.strptime(time_val_str, "%H:%M:%S").time() if time_val_str else time(23, 59)
    except:
        tval = time(23, 59)

    with st.expander("Edit Task" if is_edit else "New Task", expanded=True):
        with st.form("task_form"):
            c1, c2 = st.columns(2)
            with c1: title    = st.text_input("Task Title", value=title_val, placeholder="e.g. Submit DSA Assignment")
            with c2: category = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index(cat_val) if cat_val in CATEGORIES else 0)

            c3, c4 = st.columns(2)
            with c3: course   = st.selectbox("Course", courses, index=courses.index(course_val) if course_val in courses else 0)
            with c4: priority = st.selectbox("Priority", PRIORITY, index=PRIORITY.index(priority_val) if priority_val in PRIORITY else 1)

            c5, c6 = st.columns(2)
            with c5: due_date       = st.date_input("Due Date", value=date_val, min_value=date(2020,1,1))
            with c6: due_time_input = st.time_input("Due Time", value=tval)

            description = st.text_area("Description (optional)", value=desc_val, placeholder="Notes, links, anything relevant.", height=90)

            cs, cc = st.columns([1, 4])
            with cs: submitted = st.form_submit_button("Save Task", use_container_width=True)
            with cc: cancelled = st.form_submit_button("Cancel")

            if cancelled:
                st.session_state.show_form = False
                st.session_state.edit_id   = None
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
                st.session_state.edit_id   = None
                st.rerun()


edit_task_data = None
if st.session_state.edit_id:
    for t in st.session_state.tasks:
        if t["id"] == st.session_state.edit_id:
            edit_task_data = t
            break

if st.session_state.show_form or st.session_state.edit_id:
    task_form(edit_task=edit_task_data)


# ── Filter & Sort ─────────────────────────────────────────────────────────────
tasks = st.session_state.tasks[:]
if not show_done:      tasks = [t for t in tasks if not t.get("done")]
if filter_cat:         tasks = [t for t in tasks if t.get("category","") in filter_cat]
if filter_course:      tasks = [t for t in tasks if t.get("course","") in filter_course]
if filter_priority:    tasks = [t for t in tasks if t.get("priority","") in filter_priority]

pmap = {"High":0,"Medium":1,"Low":2}
if   sort_by == "Deadline (soonest first)":  tasks.sort(key=lambda t:(t.get("done",False), days_until(t["due_date"])))
elif sort_by == "Deadline (latest first)":   tasks.sort(key=lambda t:(t.get("done",False),-days_until(t["due_date"])))
elif sort_by == "Priority (high to low)":    tasks.sort(key=lambda t:(t.get("done",False), pmap.get(t.get("priority",""),1)))
elif sort_by == "Alphabetically (A to Z)":   tasks.sort(key=lambda t:(t.get("done",False), t.get("title","").lower()))
elif sort_by == "Alphabetically (Z to A)":   tasks.sort(key=lambda t:(t.get("done",False), t.get("title","").lower()),reverse=True)
elif sort_by == "Date Added (newest)":       tasks.sort(key=lambda t:(t.get("done",False), t.get("added_at","")),reverse=True)
elif sort_by == "Date Added (oldest)":       tasks.sort(key=lambda t:(t.get("done",False), t.get("added_at","")))


# ── Render Tasks ──────────────────────────────────────────────────────────────
def render_task(task):
    tid    = task["id"]
    done_  = task.get("done", False)
    cat    = task.get("category", "Other")
    color  = CAT_COLORS.get(cat, "#6B7280")
    pcolor = PRIORITY_COLORS.get(task.get("priority",""), "#6B7280")
    days   = days_until(task["due_date"])
    dlabel, dcls = deadline_info(days)

    time_part    = fmt_time(task.get("due_time",""))
    time_display = f"  {time_part}" if time_part else ""

    safe_title  = htmllib.escape(task.get("title",""))
    safe_course = htmllib.escape(task.get("course",""))
    safe_cat    = htmllib.escape(cat)
    safe_pri    = htmllib.escape(task.get("priority",""))
    safe_desc   = htmllib.escape(task.get("description",""))

    added_str = ""
    if task.get("added_at"):
        try: added_str = datetime.fromisoformat(task["added_at"]).strftime("%d %b")
        except: pass

    title_cls = "tc-title-done" if done_ else "tc-title"
    card_cls  = "tc done-card"  if done_ else "tc"

    desc_block = f'<p class="tc-desc">{safe_desc}</p>' if safe_desc else ""
    added_block = f' &nbsp; Added {added_str}' if added_str else ""

    # Single flat HTML block — no nested divs beyond 1 level
    st.markdown(f"""<div class="{card_cls}" style="--ac:{color}">
<div class="tc-badges">
<span class="tc-badge" style="background:{color}1A;color:{color}">{safe_cat}</span>
<span class="tc-badge" style="background:{pcolor}1A;color:{pcolor}">{safe_pri}</span>
</div>
<p class="{title_cls}">{safe_title}</p>
<p class="tc-course">{safe_course}</p>
<p><span class="{dcls}">{dlabel}</span> <span class="tc-meta">&nbsp; {fmt_date(task["due_date"])}{time_display}{added_block}</span></p>
{desc_block}
</div>""", unsafe_allow_html=True)

    ca, cb, cc = st.columns([2,1,1])
    with ca:
        if st.button("Mark Pending" if done_ else "Mark Done", key=f"done_{tid}", use_container_width=True):
            for t in st.session_state.tasks:
                if t["id"] == tid: t["done"] = not t["done"]; break
            save_tasks(st.session_state.tasks); st.rerun()
    with cb:
        if st.button("Edit", key=f"edit_{tid}", use_container_width=True):
            st.session_state.edit_id = tid; st.session_state.show_form = False; st.rerun()
    with cc:
        if st.button("Delete", key=f"del_{tid}", use_container_width=True):
            st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != tid]
            save_tasks(st.session_state.tasks); st.rerun()


pending = [t for t in tasks if not t.get("done")]
done    = [t for t in tasks if t.get("done")]

if not tasks:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.info("No tasks yet. Hit Add New Task in the sidebar.")
else:
    if pending:
        n = len(pending)
        st.markdown(f'<p class="section-lbl">Pending &nbsp; {n} task{"s" if n!=1 else ""}</p>', unsafe_allow_html=True)
        for t in pending: render_task(t)
    if done and show_done:
        n = len(done)
        st.markdown(f'<p class="section-lbl">Completed &nbsp; {n} task{"s" if n!=1 else ""}</p>', unsafe_allow_html=True)
        for t in done: render_task(t)
