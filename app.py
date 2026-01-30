# app.py

import streamlit as st
from datetime import date, datetime

from agents.heuristic import generate_plan, initialize_progress
from agents.llm_agent import generate_detailed_plan
from utils.validation import validate_goal_input
from utils import progress_manager
from utils.exporters import plan_to_docx
from utils.prompt_manager import AVAILABLE_VERSIONS, DEFAULT_VERSION

# ------------------------------
# Helpers
# ------------------------------
def compute_progress(progress_matrix):
    return {
        m: int(sum(s.values()) / len(s) * 100)
        for m, s in progress_matrix.items()
    }

def summarize_subtasks(progress_matrix):
    return {
        m: {
            "completed": [s for s, d in tasks.items() if d],
            "pending": [s for s, d in tasks.items() if not d],
        }
        for m, tasks in progress_matrix.items()
    }

# ------------------------------
# Session State
# ------------------------------
defaults = dict(
    plan_generated=False,
    goal="",
    constraints={},
    milestones=[],
    progress={},
    detailed_plan="",
    detailed_plan_original="",
    start_date=None,
    goal_id="",
    adapted=False,
    show_execution=False,
    prompt_version=DEFAULT_VERSION,
)

for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# ------------------------------
# UI Setup
# ------------------------------
st.set_page_config(page_title="ACHIEVIT", layout="centered")

st.title("A C H I E V I T")
st.caption("Hybrid AI academic planning agent system")

# Sidebar
st.sidebar.header("Control Panel")

st.sidebar.subheader("Prompt Version")
st.session_state.prompt_version = st.sidebar.radio(
    "Select Prompt Version",
    AVAILABLE_VERSIONS,
    index=AVAILABLE_VERSIONS.index(st.session_state.prompt_version),
)

goal_type = st.sidebar.selectbox("Goal Type", ["Exam", "Assignment", "Thesis"])
goal_input = st.sidebar.text_area("Describe your goal", height=150)

hours_per_day = st.sidebar.number_input("Hours per day", 1, 24, 2)
skill_level = st.sidebar.selectbox("Skill level", ["Novice", "Intermediate", "Expert"])
deadline = st.sidebar.date_input("Deadline", min_value=date.today())

# ------------------------------
# Generate Plan
# ------------------------------
if st.button("🚀 Get Roadmap", type="primary"):
    errors = validate_goal_input(goal_input, hours_per_day, deadline)
    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    with st.spinner("Generating roadmap..."):
        temp_goal = goal_input
        temp_goal_id = goal_input.lower().replace(" ", "_")
        temp_constraints = dict(hours_per_day=hours_per_day, skill_level=skill_level, deadline=str(deadline))
        temp_start_date = datetime.today().date()

        milestones = generate_plan(temp_goal, temp_constraints)
        progress = initialize_progress(milestones, temp_goal)

        result = generate_detailed_plan(
            goal=temp_goal,
            milestones=milestones,
            constraints=temp_constraints,
            progress=compute_progress(progress),
            subtasks=summarize_subtasks(progress),
            prompt_version=st.session_state.prompt_version,
        )

    st.session_state.update(
        plan_generated=True,
        goal=temp_goal,
        goal_id=temp_goal_id,
        constraints=temp_constraints,
        start_date=temp_start_date,
        milestones=milestones,
        progress=progress,
        detailed_plan_original=result["text"],
        detailed_plan=result["text"],
    )

    st.success(f"Plan generated using {result['version']}")

# ------------------------------
# Display Plan
# ------------------------------
if st.session_state.plan_generated:
    st.markdown("## 📘 Roadmap")
    st.write(st.session_state.detailed_plan_original)

    docx = plan_to_docx("ACHIEVIT Plan", st.session_state.goal, st.session_state.constraints, st.session_state.detailed_plan_original)
    st.download_button("Download DOCX", docx, file_name=f"{st.session_state.goal_id}.docx")

# ------------------------------
# Execution Layer
# ------------------------------
if st.session_state.plan_generated:
    if st.button("▶ Start Execution"):
        st.session_state.show_execution = True

if st.session_state.show_execution:
    st.markdown("## ✅ Execute Tasks")

    updated = {}
    for m, tasks in st.session_state.progress.items():
        st.subheader(m)
        updated[m] = {t: st.checkbox(t, v, key=f"{m}_{t}") for t, v in tasks.items()}

    if updated != st.session_state.progress:
        st.session_state.progress = updated
        progress_manager.save_progress(st.session_state.goal_id, updated, compute_progress(updated))

# ------------------------------
# Adapt Plan
# ------------------------------
if st.session_state.plan_generated and st.button("🔄 Get Advice on My Progress"):
    with st.spinner("Adapting plan..."):
        result = generate_detailed_plan(
            goal=st.session_state.goal,
            milestones=st.session_state.milestones,
            constraints=st.session_state.constraints,
            progress=compute_progress(st.session_state.progress),
            subtasks=summarize_subtasks(st.session_state.progress),
            prompt_version=st.session_state.prompt_version,
        )

    st.write(result["text"])
    st.success(f"Updated using {result['version']}")
