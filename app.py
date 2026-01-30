# ------------------------------  
# Step 1: OPIK Bootstrap  
# ------------------------------
import opik

# Configure OPIK project BEFORE anything else
opik.configure(
    project_name="ACHIEVIT",
    tags=["dev"],   
)

# ------------------------------  
# Imports  
# ------------------------------
import streamlit as st
from datetime import date, datetime

from agents.heuristic import (
    generate_plan,
    initialize_progress,
)
from agents.llm_agent import generate_detailed_plan
from utils.validation import validate_goal_input
from utils import progress_manager
from utils.exporters import plan_to_docx

# ------------------------------  
# Helper Functions  
# ------------------------------
def compute_progress(progress_matrix):
    computed = {}
    for milestone, subtasks in progress_matrix.items():
        total = len(subtasks)
        done = sum(subtasks.values())
        computed[milestone] = int((done / total) * 100)
    return computed


def summarize_subtasks(progress_matrix):
    summary = {}
    for milestone, subtasks in progress_matrix.items():
        summary[milestone] = {
            "completed": [s for s, done in subtasks.items() if done],
            "pending": [s for s, done in subtasks.items() if not done],
        }
    return summary

# ------------------------------  
# Sanity Check Trace  
# ------------------------------
from opik import track

@track(name="sanity_check")
def opik_sanity():
    return "OPIK is configured correctly"

# Run the sanity check once
opik_sanity()

# ------------------------------  
# Initialize Session State  
# ------------------------------
defaults = {
    "plan_generated": False,
    "goal": "",
    "constraints": {},
    "milestones": [],
    "progress": {},
    "detailed_plan": "",
    "detailed_plan_original": "",
    "start_date": None,
    "goal_id": "",
    "adapted": False,
    "show_execution": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ------------------------------  
# Page Setup  
# ------------------------------
st.set_page_config(page_title="ACHIEVIT", layout="centered")

st.markdown(
    """
    <div style='text-align:center;'>
        <h1>A C H I E V I T</h1>
        <p style='font-size:16px; color:gray; font-weight:600'>
            A hybrid intelligent agent system for students and researchers in achieving their goals/resolutions
        </p>
        <p style='font-size:14px; color:#2ECC71; text-align:center; font-weight:600'>
            🎯 Set Goals • 📝 Create Plans • 🔄 Execute & Adapt • ✅ Complete
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

# ------------------------------  
# Sidebar Inputs  
# ------------------------------
st.sidebar.header("Goal Control Panel")

goal_type = st.sidebar.selectbox(
    "Select Goal Type",
    ["Exam", "Assignment", "Dissertation / Thesis"],
)

goal_input = st.sidebar.text_area(
    f"Clearly explain your {goal_type} goal, give context and important details:",
    height=160,
)

st.sidebar.markdown("---")
st.sidebar.caption("Consider these constraints and indicate how they fit into your plan")

with st.sidebar.expander("Constraints", expanded=True):
    hours_per_day = st.number_input(
        "Hours per day you can dedicate to this",
        min_value=1,
        max_value=24,
        value=2,
    )
    skill_level = st.selectbox(
        "Skill level",
        ["Novice", "Intermediate", "Expert"],
    )
    deadline = st.date_input(
        "What is your deadline or time frame for this",
        min_value=date.today(),
    )

# ------------------------------  
# Minimal Main Panel  
# ------------------------------
st.markdown("### Hello 👋! ACHIEVIT is ready.")

st.info("Step 1: OPIK bootstrap complete. A sanity trace has been sent to the ACHIEVIT project. Check your OPIK dashboard.")
