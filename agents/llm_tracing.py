# agents/llm_tracing.py

import streamlit as st
from google import genai
from google.genai import errors
from opik import track

# ----------------------------------------
# Gemini client (Streamlit-safe)
# ----------------------------------------
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=GEMINI_API_KEY)

# ----------------------------------------
# Prompt Versioning
# ----------------------------------------
PROMPT_VERSIONS = {
    "initial_v1": """
You are a seasoned academic planning assistant.

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
    "adaptive_v1": """
You are a seasoned academic planning assistant.

This is an adaptive evaluation of progress.
Use the same milestones and subtasks.
Focus on completed vs pending tasks.
Suggest next actions and adjustments based on current progress and constraints.

GOAL:
{goal}

CONSTRAINTS:
- Hours per day: {hours_per_day}
- Skill level: {skill_level}
- Deadline: {deadline}

MILESTONES:
{milestones}

PROGRESS:
{progress}

SUBTASKS:
{subtasks}

RESPONSE FORMAT:
- Concrete next actions for pending subtasks
- Warnings if behind schedule
- Adjustments based on time/skill/deadline
- Headings per milestone
"""
}

# ----------------------------------------
# Initial Plan Generation Trace
# ----------------------------------------
@track(
    name="llm_generate_detailed_plan",
    capture_input=True,
    capture_output=True,
)
def traced_generate_detailed_plan(goal, milestones, constraints, progress, subtasks, prompt_version="initial_v1"):
    """
    Traced Gemini 3 Flash Preview call for initial plan generation.
    """
    prompt_template = PROMPT_VERSIONS.get(prompt_version, PROMPT_VERSIONS["initial_v1"])
    prompt = prompt_template.format(
        goal=goal,
        milestones=milestones,
        progress=progress,
        subtasks=subtasks,
        hours_per_day=constraints.get("hours_per_day"),
        skill_level=constraints.get("skill_level"),
        deadline=constraints.get("deadline"),
    )
    
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
        )
        return {
            "plan_text": response.text,
            "model": "gemini-3-flash-preview",
            "prompt_version": prompt_version
        }

    except errors.ServerError:
        return {"plan_text": "⚠️ Gemini service temporarily unavailable.", "model": "gemini-3-flash-preview", "prompt_version": prompt_version}

    except errors.APIError:
        return {"plan_text": "❌ Unexpected error occurred.", "model": "gemini-3-flash-preview", "prompt_version": prompt_version}


# ----------------------------------------
# Adaptive Plan Trace
# ----------------------------------------
@track(
    name="llm_adapt_plan",
    capture_input=True,
    capture_output=True,
)
def traced_adapt_plan(goal, milestones, constraints, progress, subtasks, prompt_version="adaptive_v1"):
    """
    Traced Gemini 3 Flash Preview call for adaptive plan (progress re-evaluation).
    """
    prompt_template = PROMPT_VERSIONS.get(prompt_version, PROMPT_VERSIONS["adaptive_v1"])
    prompt = prompt_template.format(
        goal=goal,
        milestones=milestones,
        progress=progress,
        subtasks=subtasks,
        hours_per_day=constraints.get("hours_per_day"),
        skill_level=constraints.get("skill_level"),
        deadline=constraints.get("deadline"),
    )

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
        )
        return {
            "plan_text": response.text,
            "model": "gemini-3-flash-preview",
            "prompt_version": prompt_version
        }

    except errors.ServerError:
        return {"plan_text": "⚠️ Gemini service temporarily unavailable.", "model": "gemini-3-flash-preview", "prompt_version": prompt_version}

    except errors.APIError:
        return {"plan_text": "❌ Unexpected error occurred.", "model": "gemini-3-flash-preview", "prompt_version": prompt_version}
