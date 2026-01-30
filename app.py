# app.py

import streamlit as st
from datetime import date, datetime

from agents.heuristic import generate_plan, initialize_progress
from agents.llm_tracing import traced_generate_detailed_plan, traced_adapt_plan, judge_plan
from utils.validation import validate_goal_input
from utils import progress_manager
from utils.exporters import plan_to_docx

# ------------------ Helper Functions ------------------
def compute_progress(progress_matrix):
    return {m: int(sum(s.values())/len(s)*100) for m,s in progress_matrix.items()}

def summarize_subtasks(progress_matrix):
    return {m: {"completed":[s for s,done in sub.items() if done],
                "pending":[s for s,done in sub.items() if not done]} 
            for m, sub in progress_matrix.items()}

# ------------------ Session Defaults ------------------
defaults = {
    "plan_generated": False,
    "goal": "",
    "constraints": {},
    "milestones": [],
    "progress": {},
    "detailed_plan_original": "",
    "detailed_plan": "",
    "start_date": None,
    "goal_id": "",
    "adapted": False,
    "show_execution": False,
    "initial_prompt_version": "initial_v1",
    "adaptive_prompt_version": "adaptive_v1",
    "initial_judge_scores": {},
    "adaptive_judge_scores": {},
}

for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ------------------ Page Setup ------------------
st.set_page_config(page_title="ACHIEVIT", layout="centered")

st.markdown("""
<div style='text-align:center;'>
    <h1>A C H I E V I T</h1>
    <p style='font-size:16px; color:gray; font-weight:600'>
        A hybrid intelligent agent system for students and researchers in achieving their goals/resolutions
    </p>
    <p style='font-size:14px; color:#2ECC71; font-weight:600'>
        🎯 Set Goals • 📝 Create Plans • 🔄 Execute & Adapt • ✅ Complete
    </p>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# ------------------ Sidebar Inputs ------------------
st.sidebar.header("Goal Control Panel")
goal_type = st.sidebar.selectbox("Select Goal Type", ["Exam", "Assignment", "Dissertation / Thesis"])
goal_input = st.sidebar.text_area(f"Clearly explain your {goal_type} goal, give context and important details:", height=160)

st.sidebar.markdown("---")
st.sidebar.caption("Consider these constraints and indicate how they fit into your plan")
with st.sidebar.expander("Constraints", expanded=True):
    hours_per_day = st.number_input("Hours per day you can dedicate to this", min_value=1, max_value=24, value=2)
    skill_level = st.selectbox("Skill level", ["Novice", "Intermediate", "Expert"])
    deadline = st.date_input("What is your deadline or time frame for this", min_value=date.today())

# ------------------ Prompt Version Selection ------------------
st.sidebar.markdown("---")
st.sidebar.subheader("Prompt Versions (for testing)")
initial_prompt_version = st.sidebar.selectbox(
    "Initial Plan Prompt Version", ["initial_v1", "initial_v2"],
    index=["initial_v1","initial_v2"].index(st.session_state.initial_prompt_version)
)
adaptive_prompt_version = st.sidebar.selectbox(
    "Adaptive Plan Prompt Version", ["adaptive_v1", "adaptive_v2"],
    index=["adaptive_v1","adaptive_v2"].index(st.session_state.adaptive_prompt_version)
)
st.session_state.initial_prompt_version = initial_prompt_version
st.session_state.adaptive_prompt_version = adaptive_prompt_version

# ------------------ Main Panel ------------------
st.markdown("### Hello 👋!")
st.markdown("""
<p style='font-size:14px; color:#2ECC71; line-height:1.5;'>
Achievit is an AI-powered intelligent system that will accompany you in finishing whatever goal you start.<br><br>
Use the Sidebar to get started:<br>
🎯 <strong>Select a goal type</strong><br>
📝 <strong>Describe your goal</strong><br>
⏱️ <strong>State your constraints</strong><br>
👇 Click <strong>'Get Roadmap'</strong><br>
🕹️ Take control from there!
</p>
""", unsafe_allow_html=True)

# ------------------ Generate Initial Plan ------------------
if st.button("🚀 Get Roadmap", type="primary"):
    st.session_state.goal = goal_input
    errors = validate_goal_input(goal_input, hours_per_day, deadline)
    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    with st.spinner("🧠 Thinking through your goal and constraints..."):
        temp_constraints = {"hours_per_day": hours_per_day, "skill_level": skill_level, "deadline": str(deadline)}
        temp_start_date = datetime.today().date()
        temp_milestones = generate_plan(goal_input, temp_constraints)
        temp_progress = initialize_progress(temp_milestones, goal_input)

        # Generate Initial Plan (Traced)
        result = traced_generate_detailed_plan(
            goal=goal_input,
            milestones=temp_milestones,
            constraints=temp_constraints,
            progress=compute_progress(temp_progress),
            subtasks=summarize_subtasks(temp_progress),
            prompt_version=st.session_state.initial_prompt_version
        )
        plan_text = result["plan_text"]

        # Judge the Initial Plan
        judge_scores = judge_plan(
            goal=goal_input,
            milestones=temp_milestones,
            constraints=temp_constraints,
            progress=compute_progress(temp_progress),
            plan_text=plan_text,
            prompt_version=st.session_state.initial_prompt_version,
            call_type="initial_plan"
        )

    st.session_state.update({
        "plan_generated": True,
        "adapted": False,
        "goal_id": goal_input.lower().replace(" ","_"),
        "constraints": temp_constraints,
        "start_date": temp_start_date,
        "milestones": temp_milestones,
        "progress": temp_progress,
        "detailed_plan_original": plan_text,
        "detailed_plan": plan_text,
        "initial_judge_scores": judge_scores,
        "show_execution": False
    })

    st.success("✅ Initial Plan generated successfully!")
    st.subheader("📝 Detailed Plan (Initial)")
    st.write(st.session_state.detailed_plan_original)
    st.markdown(f"**Judge Scores:** {st.session_state.initial_judge_scores}")

    # Download DOCX
    docx_file = plan_to_docx(
        title="ACHIEVIT – Roadmap Plan",
        goal=st.session_state.goal,
        constraints=st.session_state.constraints,
        plan_text=st.session_state.detailed_plan_original
    )
    st.download_button(
        "⬇️ Download Initial Plan (DOCX)",
        data=docx_file,
        file_name=f"{st.session_state.goal_id}_initial_plan.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

# ------------------ Adaptive Plan ------------------
if st.session_state.plan_generated and st.button("🔄 Get Advice on My Progress"):
    with st.spinner("🧠 Re-evaluating your progress..."):
        result = traced_adapt_plan(
            goal=st.session_state.goal,
            milestones=st.session_state.milestones,
            constraints=st.session_state.constraints,
            progress=compute_progress(st.session_state.progress),
            subtasks=summarize_subtasks(st.session_state.progress),
            prompt_version=st.session_state.adaptive_prompt_version
        )
        adapted_plan = result["plan_text"]

        # Judge the Adaptive Plan
        judge_scores_adapt = judge_plan(
            goal=st.session_state.goal,
            milestones=st.session_state.milestones,
            constraints=st.session_state.constraints,
            progress=compute_progress(st.session_state.progress),
            plan_text=adapted_plan,
            prompt_version=st.session_state.adaptive_prompt_version,
            call_type="adaptive_plan"
        )

    st.session_state.detailed_plan = adapted_plan
    st.session_state.adaptive_judge_scores = judge_scores_adapt
    st.session_state.adapted = True

    st.success("✅ Adaptive Plan generated successfully!")
    st.subheader("🔁 Adaptive Plan (Advice on Progress)")
    st.write(st.session_state.detailed_plan)
    st.markdown(f"**Judge Scores:** {st.session_state.adaptive_judge_scores}")

# ------------------ Reveal Execution Subtasks ------------------
if st.session_state.plan_generated and not st.session_state.show_execution:
    st.markdown("---")
    st.subheader("🧠 Ready to Execute Your Plan?")
    st.caption("Reveal actionable subtasks and begin execution.")
    if st.button("▶️ Generate Planned Tasks and Activities"):
        st.session_state.show_execution = True
        st.rerun()

# ------------------ Execution Layer ------------------
if st.session_state.plan_generated and st.session_state.show_execution:
    st.markdown("---")
    st.subheader(f"✅ Execute Your Plan: Tasks for {goal_type}")

    updated_progress = {}
    for milestone, subtasks in st.session_state.progress.items():
        st.markdown(f"### 🎯 {milestone}")
        updated_progress[milestone] = {}
        for subtask, done in subtasks.items():
            updated_progress[milestone][subtask] = st.checkbox(subtask, value=done, key=f"{milestone}_{subtask}")

    if updated_progress != st.session_state.progress:
        st.session_state.progress = updated_progress
        progress_manager.save_progress(
            st.session_state.goal_id,
            execution_matrix=updated_progress,
            computed_progress=compute_progress(updated_progress)
        )
        st.success("Progress updated.")

# ------------------ Deadline Risk Check ------------------
if st.session_state.plan_generated and st.session_state.show_execution:
    computed = compute_progress(st.session_state.progress)
    total = sum(computed.values()) / len(computed)
    today = datetime.today().date()
    days_total = (deadline - st.session_state.start_date).days
    days_elapsed = (today - st.session_state.start_date).days
    expected = (days_elapsed/days_total)*100 if days_total>0 else 100
    if total < expected:
        st.warning(f"⚠️ Behind schedule — {total:.1f}% done vs {expected:.1f}% expected")

# ------------------ Progress Overview ------------------
if st.session_state.plan_generated and st.session_state.show_execution:
    st.markdown("---")
    st.subheader("📊 Progress Overview")
    st.table(compute_progress(st.session_state.progress))

# ------------------ Start New Goal ------------------
if st.session_state.plan_generated:
    st.markdown("---")
    if st.button("🆕 Start New Goal"):
        for k,v in defaults.items():
            st.session_state[k] = v
        st.rerun()



# ------------------ Footer ------------------
st.markdown("""
<div style="text-align: center; font-size: 0.85em; color: gray;">
    <strong>ACHIEVIT</strong> — 2026 Encode Commit To Change Hackathon<br>
    🔬 <a href="https://abdul-writecodes.github.io/portfolio/" target="_blank">Developer Portfolio</a><br>
    <strong>Disclaimer:</strong> No personal data collected.<br>
    © 2025 Abdul Write & Codes.
</div>
""", unsafe_allow_html=True)
