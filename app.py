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
hours_per_day = st.sidebar.number_input("Hours you can dedicate daily:", min_value=0, max_value=24, value=2)
skill_level = st.sidebar.selectbox("Your skill level:", ["Novice", "Intermediate", "Expert"])
deadline = st.sidebar.date_input("Goal deadline:", min_value=date.today())

submit = st.sidebar.button("Generate Plan")

# --- Main Panel ---
if submit:
    # Validate input
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

        # --- Generate heuristic milestones ---
        milestones = generate_plan(goal, constraints)

        st.subheader("Milestones")
        
        # Load existing progress if any
        goal_id = goal.lower().replace(" ", "_")
        saved_progress = progress_manager.load_progress(goal_id)

        progress = {}
        for i, m in enumerate(milestones):
            status = saved_progress.get(m, "Not started")
            progress[m] = st.selectbox(
                f"Milestone: {m}",
                ["Not started", "In progress", "Completed"],
                index=["Not started", "In progress", "Completed"].index(status),
                key=f"{goal_id}_{i}"
            )

        # Save updated progress
        progress_manager.save_progress(goal_id, progress)

        # --- Generate adaptive detailed plan using LLM ---
        with st.spinner("Generating adaptive detailed plan with LLM..."):
            detailed_plan = generate_detailed_plan(goal, milestones, constraints, progress)
        st.subheader("Adaptive Detailed Plan")
        st.write(detailed_plan)

        # --- Optional: Progress bar ---
        completed_count = sum(1 for status in progress.values() if status == "Completed")
        total = len(progress)
        st.progress(completed_count / total if total > 0 else 0)
        st.write(f"{completed_count}/{total} milestones completed")
