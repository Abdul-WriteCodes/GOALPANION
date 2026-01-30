# agents/llm_agent.py

import streamlit as st
from google import genai
from google.genai import errors

from opik import track
from opik.integrations.genai import track_genai
from utils.prompt_manager import get_prompt

# ------------------------------
# Gemini Client (wrapped by OPIK)
# ------------------------------
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

_base_client = genai.Client(api_key=GEMINI_API_KEY)
client = track_genai(_base_client)   # ✅ enables tracing

# ------------------------------
# LLM Plan Generator (TRACED)
# ------------------------------
@track  # OPIK decorator
def generate_detailed_plan(
    goal: str,
    milestones: list[str],
    constraints: dict,
    progress: dict,
    subtasks: dict,
    prompt_version: str = None,
):
    """
    Generate milestone-based academic plan using selected prompt version.
    Returns a dict with "text" and "version".
    """
    prompt_text, used_version = get_prompt(prompt_version)

    # Fill prompt placeholders
    prompt_filled = prompt_text.format(
        goal=goal,
        milestones=milestones,
        progress=progress,
        subtasks=subtasks,
        hours_per_day=constraints.get("hours_per_day"),
        skill_level=constraints.get("skill_level"),
        deadline=constraints.get("deadline"),
        constraints=constraints,  # for v1.1 style prompts
    )

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt_filled,
        )
        return {"text": response.text, "version": used_version}

    except errors.ServerError:
        st.warning("⚠️ Gemini API limit exceeded or server overloaded. Try again in a few minutes.")
        return {"text": "⚠️ Unable to generate plan due to temporary AI limits.", "version": used_version}

    except errors.APIError:
        st.error("❌ Unexpected error contacting the AI service.")
        return {"text": "❌ Unexpected AI service error.", "version": used_version}
