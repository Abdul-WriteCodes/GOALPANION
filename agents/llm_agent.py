# agents/llm_agent.py

import streamlit as st
from google import genai

# Pull API key from Streamlit secrets
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

def generate_detailed_plan(goal, milestones, constraints, progress=None):
    """
    Generate detailed adaptive steps for milestones using Gemini LLM.
    progress: dict mapping milestone -> status ("Not started", "In progress", "Completed")
    """
    if progress is None:
        progress = {m: "Not started" for m in milestones}

    prompt = f"""
    You are an academic assistant helping a student achieve their goal.

    Goal: {goal}
    Constraints: {constraints}
    Milestones: {milestones}
    Progress so far: {progress}

    Based on the milestones completed or in progress, suggest:
    1. Updated steps for remaining milestones
    2. Adaptive tips to optimize time
    3. Recommended resources for each remaining milestone
    4. Adjust schedule if needed to meet the deadline

    Return the response in a clear, structured format, milestone by milestone.
    """

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )
    return response.text
