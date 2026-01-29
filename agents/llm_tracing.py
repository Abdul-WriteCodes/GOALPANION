# agents/llm_tracing.py

import streamlit as st
from google import genai
from google.genai import errors
from opik import track, set_metadata

# ----------------------------------------
# Gemini Client
# ----------------------------------------
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=GEMINI_API_KEY)

# ----------------------------------------
# Prompt Versions
# ----------------------------------------
PROMPT_VERSIONS = {
    "initial_v1": """You are a seasoned academic planning assistant.
GOAL:
{goal}
CONSTRAINTS:
- Hours per day: {hours_per_day}
- Skill level: {skill_level}
- Deadline: {deadline}
MILESTONES (FIXED):
{milestones}
EXECUTION STATUS:
Progress percentages per milestone:
{progress}
Completed and pending subtasks per milestone:
{subtasks}
TASK:
1. Explain each milestone briefly
2. Acknowledge completed subtasks
3. Focus on pending subtasks: what to do next and why
4. Adjust workload based on time/skill/deadline
5. Warn if progress is low and deadline is near
6. Suggest resources ONLY if directly useful
RESPONSE FORMAT:
- Concrete, execution-focused
- Headings per milestone
""",
    "initial_v2": """You are a highly experienced academic advisor.
GOAL:
{goal}
CONSTRAINTS:
- Hours/day: {hours_per_day}
- Skill: {skill_level}
- Deadline: {deadline}
MILESTONES:
{milestones}
PROGRESS STATUS:
{progress}
SUBTASKS:
{subtasks}
TASK:
- Explain each milestone concisely
- Highlight completed subtasks
- Prioritize pending subtasks with rationale
- Adjust actions to time, skill, and deadline
- Issue warnings for low progress if deadline is close
RESPONSE:
- Use clear headings
- Execution-focused
- Avoid generic advice
""",
    "adaptive_v1": """You are a seasoned academic planning assistant.
Adaptive evaluation using current progress:
GOAL: {goal}
CONSTRAINTS:
- Hours per day: {hours_per_day}
- Skill level: {skill_level}
- Deadline: {deadline}
MILESTONES: {milestones}
PROGRESS: {progress}
SUBTASKS: {subtasks}
RESPONSE FORMAT:
- Next actions for pending subtasks
- Warnings if behind schedule
- Adjustments for time/skill/deadline
- Headings per milestone
""",
    "adaptive_v2": """Generate an adaptive, milestone-based academic plan.
GOAL: {goal}
CONSTRAINTS:
- Hours/day: {hours_per_day}
- Skill: {skill_level}
- Deadline: {deadline}
MILESTONES: {milestones}
PROGRESS: {progress}
SUBTASKS: {subtasks}
TASK:
- Focus on pending subtasks
- Explain what to do next and why
- Adjust based on time/skill/deadline
- Warn if progress is low and deadline is near
RESPONSE:
- Concrete, actionable steps
- Headings per milestone
- Execution-focused, avoid generic study advice
"""
}

# ----------------------------------------
# Utility: build prompt
# ----------------------------------------
def build_prompt(version, goal, milestones, constraints, progress, subtasks):
    template = PROMPT_VERSIONS.get(version)
    return template.format(
        goal=goal,
        milestones=milestones,
        progress=progress,
        subtasks=subtasks,
        hours_per_day=constraints.get("hours_per_day"),
        skill_level=constraints.get("skill_level"),
        deadline=constraints.get("deadline"),
    )

# ----------------------------------------
# Generic LLM Call Wrapper
# ----------------------------------------
def call_gemini(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        return response.text
    except errors.ServerError:
        return "⚠️ Gemini service temporarily unavailable."
    except errors.APIError:
        return "❌ Unexpected error occurred."

# ----------------------------------------
# Initial Plan Trace
# ----------------------------------------
@track(name="llm_generate_detailed_plan", capture_input=True, capture_output=True)
def traced_generate_detailed_plan(goal, milestones, constraints, progress, subtasks, prompt_version="initial_v1"):
    prompt = build_prompt(prompt_version, goal, milestones, constraints, progress, subtasks)
    
    # Metadata for OPIK
    set_metadata({
        "agent": "achievit-llm",
        "call_type": "initial_plan",
        "milestone_count": len(milestones),
        "prompt_version": prompt_version
    })

    plan_text = call_gemini(prompt)
    return {
        "plan_text": plan_text,
        "model": "gemini-3-flash-preview",
        "prompt_version": prompt_version
    }

# ----------------------------------------
# Adaptive Plan Trace
# ----------------------------------------
@track(name="llm_adapt_plan", capture_input=True, capture_output=True)
def traced_adapt_plan(goal, milestones, constraints, progress, subtasks, prompt_version="adaptive_v1"):
    prompt = build_prompt(prompt_version, goal, milestones, constraints, progress, subtasks)
    
    # Metadata for OPIK
    set_metadata({
        "agent": "achievit-llm",
        "call_type": "adaptive_plan",
        "milestone_count": len(milestones),
        "avg_progress": sum(progress.values()) / len(progress) if progress else 0,
        "low_progress_flag": (sum(progress.values()) / len(progress) if progress else 0) < 40,
        "prompt_version": prompt_version
    })

    plan_text = call_gemini(prompt)
    return {
        "plan_text": plan_text,
        "model": "gemini-3-flash-preview",
        "prompt_version": prompt_version
    }


