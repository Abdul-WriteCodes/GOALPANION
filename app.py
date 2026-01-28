import streamlit as st
from datetime import date, datetime

from agents.heuristic import (
    generate_plan,
    initialize_progress,
)
from agents.llm_tracing import traced_generate_detailed_plan, traced_adapt_plan
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
    "initial_prompt_version": "initial_v1",
    "adaptive_prompt_version": "adaptive_v1",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ------------------------------
# Page Setup
# ------------------------------
st.set_page_config(page_title="ACHIEVIT", layout="centered")

# ---------------- HEADER ----------------
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
# Prompt Version Selection
# ------------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("Prompt Versions (for testing)")

initial_prompt_version = st.sidebar.selectbox(
    "Initial Plan Prompt Version",
    ["initial_v1", "initial_v2"],
    index=["initial_v1", "initial_v2"].index(st.session_state.initial_prompt_version)
)

adaptive_prompt_version = st.sidebar.selectbox(
    "Adaptive Plan Prompt Version",
    ["adaptive_v1", "adaptive_v2"],
    index=["adaptive_v1", "adaptive_v2"].index(st.session_state.adaptive_prompt_version)
)

st.session_state.initial_prompt_version = initial_prompt_version
st.session_state.adaptive_prompt_version = adaptive_prompt_version

# ------------------------------
# Main Panel
# ------------------------------
st.markdown("### Hello 👋!")
st.markdown(
    """
    <p style='font-size:14px; color:#2ECC71; line-height:1.5;'>
    Achievit is an AI-powered intelligent system that will accompany you in finishing whatever goal you start.<br><br>
    Use the Sidebar to get started:<br>
    🎯 <strong>Select a goal type</strong><br>
    📝 <strong>Describe your goal</strong><br>
    ⏱️ <strong>State your constraints</strong><br>
    👇 Click <strong>'Get Roadmap'</strong><br>
    🕹️ Take control from there!
    </p>
    """,
    unsafe_allow_html=True
)

# ------------------------------
# Generate Plan
# ------------------------------
if st.button("🚀 Get Roadmap", type="primary"):
    errors = validate_goal_input(goal_input, hours_per_day, deadline)

    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    with st.spinner("🧠 Thinking through your goal and constraints..."):
        try:
            temp_goal = goal_input
            temp_goal_id = goal_input.lower().replace(" ", "_")

            temp_constraints = {
                "hours_per_day": hours_per_day,
                "skill_level": skill_level,
                "deadline": str(deadline),
            }

            temp_start_date = datetime.today().date()

            temp_milestones = generate_plan(temp_goal, temp_constraints)
            temp_progress = initialize_progress(temp_milestones, temp_goal)

            if len(temp_milestones) != 4 or any(len(v) != 5 for v in temp_progress.values()):
                st.error("❌ Internal planning error. Please try again.")
                st.stop()

            # ---- Use Traced LLM wrapper with selected prompt version ----
            result = traced_generate_detailed_plan(
                goal=temp_goal,
                milestones=temp_milestones,
                constraints=temp_constraints,
                progress=compute_progress(temp_progress),
                subtasks=summarize_subtasks(temp_progress),
                prompt_version=st.session_state.initial_prompt_version,
            )
            plan_text = result["plan_text"]

        except Exception:
            st.error("❌ AI service unavailable. Please try again.")
            st.stop()

    st.session_state.update({
        "plan_generated": True,
        "adapted": False,
        "goal": temp_goal,
        "goal_id": temp_goal_id,
        "constraints": temp_constraints,
        "start_date": temp_start_date,
        "milestones": temp_milestones,
        "progress": temp_progress,
        "detailed_plan_original": plan_text,
        "detailed_plan": plan_text,
        "show_execution": False,
    })

    st.success("✅ Analysis completed successfully!")

# ------------------------------
# Adaptive Plan (Get Advice)
# ------------------------------
if st.session_state.plan_generated and st.button("🔄 Get Advice on My Progress"):
    with st.spinner("🧠 Re-evaluating your progress..."):
        result = traced_adapt_plan(
            goal=st.session_state.goal,
            milestones=st.session_state.milestones,
            constraints=st.session_state.constraints,
            progress=compute_progress(st.session_state.progress),
            subtasks=summarize_subtasks(st.session_state.progress),
            prompt_version=st.session_state.adaptive_prompt_version,
        )
        adapted_plan = result["plan_text"]

    st.session_state.detailed_plan = adapted_plan
    st.session_state.adapted = True

    st.success("Evaluation successful.")
    st.subheader("🔁 Here is what your progress means....")
    st.write(st.session_state.detailed_plan)

# ------------------------------
# (Rest of app remains same: Execution, Progress, Download, New Goal)
# ------------------------------
