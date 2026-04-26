<div align="center">

# TaskBoard
### Student Task Manager · Built with Streamlit

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org/)
[![Deploy](https://img.shields.io/badge/Deploy-Streamlit%20Cloud-FF4B4B?style=flat-square)](https://share.streamlit.io/)

A clean, dark-themed task manager built for students — track assignments, exams, quizzes, presentations and more from one place.

</div>

---

## Features

- **Task categories** — Assignment, Exam, Quiz, Presentation, Study Session, Lab Report, Project Milestone
- **Course selection** — pick from a list or add your own custom course name
- **Priority levels** — High, Medium, Low with color-coded badges
- **Due date & time** — full datetime support with overdue detection
- **Optional description** — notes, links, reminders
- **Filter & sort** — by deadline, priority, alphabetically, date added, category, or course
- **Mark done / pending** — toggle completion with one click
- **Edit & delete** — full CRUD on every task
- **Persistent storage** — tasks saved to `tasks.json` locally; use Streamlit secrets or cloud storage for deployment
- **Dark UI** — eye-friendly dark theme with color-coded categories

---

## Run Locally

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>

pip install -r requirements.txt

streamlit run app.py
```

App opens at `http://localhost:8501`

---

## Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io/) → **New app**
3. Select your repo, branch `main`, and set **Main file path** to `app.py`
4. Click **Deploy**

> **Note:** Streamlit Cloud's filesystem is ephemeral — tasks won't persist between sessions unless you integrate a database (e.g. Supabase, Firebase, or Streamlit's built-in secrets with an external store). For a persistent free option, use [Supabase](https://supabase.com/) with a simple REST call.

---

## Project Structure

```
taskboard/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .gitignore
└── README.md
```

---

## Built by

**Arslan Fareed** — Software Engineering, UET Taxila  
[github.com/rslaanfareed](https://github.com/rslaanfareed)
