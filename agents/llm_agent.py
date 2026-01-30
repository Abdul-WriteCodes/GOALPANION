# agents/llm_agent.py

import streamlit as st
from google import genai
from google.genai import errors

from opik import track
from opik.integrations.genai import track_genai
from utils.prompt_manager import get_prompt

# Gemini client
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
_base_client = genai.Client(api_key=GEMINI_API_KEY)
client = track_genai(_base_client)

# ------------------------------
# LLM Planner
# ------------------------------
@track
def generate_detailed_plan(
    goal,
    milestones,
    constraints,
    progress,
    subtasks,
    prompt_version="v1.0",
):
    prompt_template = get_prompt(prompt_version)

    prompt = prompt_template.format(
        goal=goal,
        constraints=constraints,
        milestones=milestones,
        progress=progress,
        subtasks=subtasks,
    )

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
        )

        return {
            "text": response.text,
            "version": prompt_version,
        }

    except errors.ServerError:
        return {"text": "⚠️ Gemini temporarily unavailable.", "version": prompt_version}

    except Exception as e:
        return {"text": f"❌ LLM error: {str(e)}", "version": prompt_version}
