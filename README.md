<div align="center">

# TaskBoard
### Student Task Manager built with Streamlit

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org/)

A dark-themed academic task manager for tracking assignments, exams, quizzes, presentations and everything in between.

</div>

---

## Features

- **Task categories** - Assignment, Exam, Quiz, Presentation, Study Session, Lab Report, Project Milestone
- **Course selection** - pick from a preset list or enter a custom course name
- **Priority levels** - High, Medium, Low with color-coded badges
- **Due date and time** - full datetime support with overdue detection
- **Optional description** - notes, links, reminders
- **Filter and sort** - by deadline, priority, alphabetically, date added, category, or course
- **Mark done or pending** - toggle completion with one click
- **Edit and delete** - full CRUD on every task
- **Persistent storage** - tasks saved locally to tasks.json
- **Dark UI** - eye-friendly dark theme with color-coded categories

---

## Run Locally

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>

pip install -r requirements.txt

streamlit run app.py
```

App runs at http://localhost:8501

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

## Author

**Arslan Fareed** - Software Engineering, UET Taxila  
[github.com/rslaanfareed](https://github.com/rslaanfareed)
