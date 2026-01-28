# agents/llm_agent.py

import streamlit as st
from google import genai
from google.genai import errors

from opik import track
from opik.integrations.genai import track_genai


# ------------------------------
# Gemini Client (wrapped by OPIK)
# ------------------------------
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

_base_client = genai.Client(api_key=GEMINI_API_KEY)
client = track_genai(_base_client)   # ✅ THIS enables tracing


# ------------------------------
# LLM Plan Generator (TRACED)
# ------------------------------
@track(task_name="llm_generate_detailed_plan")
def generate_detailed_plan(
    goal: str,
    milestones: list[str],
    constraints: dict,
    progress: dict,
    subtasks: dict,
):
    """
    Generate an adaptive, milestone-based academic plan.

    progress: dict mapping milestone -> completion percentage (0–100)
    subtasks: dict mapping milestone -> {
        "completed": [subtasks],
        "pending": [subtasks]
    }
    """

    prompt = f"""
You are a seasoned academic planning assistant.

This system uses a FIXED heuristic structure.
You MUST respect the given milestones and subtasks.
Do NOT invent new milestones or new subtasks.

====================
GOAL
====================
{goal}

====================
CONSTRAINTS
====================
- Hours per day: {constraints.get("hours_per_day")}
- Skill level: {constraints.get("skill_level")}
- Deadline: {constraints.get("deadline")}

====================
MILESTONES (FIXED)
====================
{milestones}

====================
EXECUTION STATUS
====================
Progress percentages per milestone:
{progress}

Completed and pending subtasks per milestone:
{subtasks}

====================
YOUR TASK
====================
For EACH milestone:

1. Comprehensively explain what this milestone is and why it matters.
2. Acknowledge completed subtasks succinctly.
3. Focus on pending subtasks:
   - What should be done next
   - Why it matters now
4. Adjust workload based on time, skill, and deadline.
5. If progress is low and deadline is near, warn clearly.
6. Recommend resources ONLY if directly helpful.

====================
RESPONSE FORMAT
====================
- Clear headings per milestone
- Execution-focused
- No generic advice
"""

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
        )
        return response.text

    except errors.ServerError:
        st.warning(
            "⚠️ Gemini API limit may be exceeded or the server is overloaded.\n"
            "Please wait a few minutes and try again."
        )
        return (
            "⚠️ Unable to generate a plan right now due to temporary AI limits."
        )

    except errors.APIError:
        st.error("❌ An unexpected error occurred while contacting the AI service.")
        return (
            "❌ An unexpected error occurred while generating your plan."
        )
