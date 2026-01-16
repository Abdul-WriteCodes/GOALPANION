import streamlit as st
from datetime import date
from agents.heuristic import generate_plan
from agents.llm_agent import generate_detailed_plan
from utils.validation import validate_goal_input
from utils import progress_manager

st.title("Companion: Academic Goal Assistant")

# --- Sidebar: Goal Input & Constraints ---
st.sidebar.header("Goal Control Panel")

goal_type = st.sidebar.selectbox(
    "Select your academic goal type:",
    ["Exam", "Assignment", "Dissertation / Thesis"]
)

goal = st.sidebar.text_input(f"Enter your {goal_type} goal:")
hours_per_day = st.sidebar.number_input(
    "Hours you can dedicate daily:", min_value=1, max_value=24, value=2
)
skill_level = st.sidebar.selectbox(
    "Your skill level:", ["Novice", "Intermediate", "Expert"]
)
deadline = st.sidebar.date_input(
    "Goal deadline:", min_value=date.today()
)

submit = st.sidebar.button("Generate Plan")

# --- Main Panel ---
if submit:
    errors = validate_goal_input(goal, hours_per_day, deadline)

    if errors:
        for e in errors:
            st.error(e)

    else:
        constraints = {
            "hours_per_day": hours_per_day,
            "skill_level": skill_level,
            "deadline": str(deadline)
        }

        # --- Internal structure (NOT shown yet) ---
        milestones = generate_plan(goal, constraints)

        goal_id = goal.lower().replace(" ", "_")
        progress = progress_manager.load_progress(goal_id) or {
            m: 0 for m in milestones
        }

        # --- LLM FIRST ---
        with st.spinner("Thinking through your goal and constraints..."):
            detailed_plan = generate_detailed_plan(
                goal=goal,
                milestones=milestones,
                constraints=constraints,
                progress=progress
            )

        st.subheader("Your Adaptive Study Plan")
        st.write(detailed_plan)

        # --- (Optional) Save progress silently ---
        progress_manager.save_progress(goal_id, progress)
