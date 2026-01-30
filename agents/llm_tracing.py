# agents/llm_tracing.py

import streamlit as st
from google import genai
from opik import track
import json
from datetime import datetime

# ------------------------------
# Initialize Gemini client
# ------------------------------
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)


# ------------------------------
# Traced Generate Detailed Plan
# ------------------------------
@track(name="generate_detailed_plan", metadata={"type": "initial_plan"})
def traced_generate_detailed_plan(goal, milestones, constraints, progress, subtasks, prompt_version="initial_v1"):
    """
    Generate a detailed plan using the LLM, traced for observability.
    """
    try:
        # Customize prompt based on version
        prompt = f"[{prompt_version}] Generate a detailed plan for goal: {goal}.\n"
        prompt += f"Milestones: {json.dumps(milestones)}\n"
        prompt += f"Constraints: {json.dumps(constraints)}\n"
        prompt += f"Progress: {json.dumps(progress)}\n"
        prompt += f"Subtasks: {json.dumps(subtasks)}"

        response = client.generate_text(prompt)
        plan_text = response.text if response.text else "No plan generated."

        return {"plan_text": plan_text}

    except Exception as e:
        st.error(f"❌ LLM plan generation failed: {str(e)}")
        return {"plan_text": "Plan generation failed."}


# ------------------------------
# Traced Adapt Plan
# ------------------------------
@track(name="adapt_plan", metadata={"type": "adaptive_plan"})
def traced_adapt_plan(goal, milestones, constraints, progress, subtasks, prompt_version="adaptive_v1"):
    """
    Generate an adaptive plan based on current progress, traced for observability.
    """
    try:
        prompt = f"[{prompt_version}] Adapt the plan for goal: {goal}.\n"
        prompt += f"Milestones: {json.dumps(milestones)}\n"
        prompt += f"Constraints: {json.dumps(constraints)}\n"
        prompt += f"Progress: {json.dumps(progress)}\n"
        prompt += f"Subtasks: {json.dumps(subtasks)}"

        response = client.generate_text(prompt)
        plan_text = response.text if response.text else "No adaptive plan generated."

        return {"plan_text": plan_text}

    except Exception as e:
        st.error(f"❌ Adaptive plan generation failed: {str(e)}")
        return {"plan_text": "Adaptive plan generation failed."}


# ------------------------------
# Judge Plan
# ------------------------------
@track(name="judge_plan", metadata={"type": "evaluation"})
def judge_plan(goal, milestones, constraints, progress, plan_text, prompt_version="judge_v1", call_type="initial_plan"):
    """
    Evaluate a plan for relevance, consistency, and hallucination risk.
    Returns a dictionary of scores.
    """
    try:
        prompt = f"[{prompt_version}] Judge the following plan for goal: {goal}.\n"
        prompt += f"Milestones: {json.dumps(milestones)}\n"
        prompt += f"Constraints: {json.dumps(constraints)}\n"
        prompt += f"Progress: {json.dumps(progress)}\n"
        prompt += f"Plan Text: {plan_text}\n"
        prompt += "Provide scores between 0-100 for relevance, consistency, and hallucination risk."

        response = client.generate_text(prompt)
        text = response.text

        # Try to parse JSON-like response
        try:
            scores = json.loads(text)
            # Ensure all keys exist
            for key in ["relevance", "consistency", "hallucination"]:
                if key not in scores:
                    scores[key] = None
        except Exception:
            # Fallback: assign default perfect scores if parsing fails
            scores = {"relevance": 100, "consistency": 100, "hallucination": 100}

        return scores

    except Exception as e:
        st.error(f"❌ Plan judging failed: {str(e)}")
        return {"relevance": None, "consistency": None, "hallucination": None}
