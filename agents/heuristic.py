# agents/heuristic.py

"""
Heuristic planning layer for ACHIEVIT.

Responsibilities:
- Detect goal type
- Generate stable, deterministic milestones
- Generate structured subtasks per milestone
"""

# ------------------------------
# Goal Type Detection
# ------------------------------
def detect_goal_type(goal: str) -> str:
    goal = goal.lower()

    if "exam" in goal or "test" in goal:
        return "exam"

    if "assignment" in goal or "homework" in goal:
        return "assignment"

    if "dissertation" in goal or "thesis" in goal or "research paper" in goal:
        return "dissertation"

    return "generic"


# ------------------------------
# Milestone Generator (UNCHANGED CORE LOGIC)
# ------------------------------
def generate_plan(goal: str, constraints: dict) -> list[str]:
    goal_type = detect_goal_type(goal)

    if goal_type == "exam":
        return [
            "Understand exam syllabus and requirements",
            "Study core topics and concepts",
            "Practice past questions and mock exams",
            "Final revision and exam readiness"
        ]

    if goal_type == "assignment":
        return [
            "Understand assignment requirements",
            "Research and gather relevant materials",
            "Draft and refine the assignment",
            "Final review and submission"
        ]

    if goal_type == "dissertation":
        return [
            "Draft Proposal and Chapter One: Define research scope and purpose",
            "Draft Chapter Two: Conduct literature review and methodology planning",
            "Draft Chapter Three: Execute research and write core chapters",
            "Draft Chapter Four and Five: Analyse results, review, edit, and submit"
        ]

    return [
        "Clarify and scope the goal",
        "Plan and execute core tasks",
        "Review progress and refine work",
        "Finalize and complete the goal"
    ]


# ------------------------------
# Subtask Generator (NEW LAYER)
# ------------------------------
def generate_subtasks(milestone: str, goal_type: str) -> list[str]:
    """
    Returns 5 deterministic execution subtasks per milestone.
    These are stable and auditable, suitable for checkbox tracking.
    """

    if goal_type == "exam":
        return [
            "Break down syllabus topics for this stage",
            "Study required materials and notes",
            "Practice relevant exam questions",
            "Identify weak areas and revise",
            "Confirm readiness for this section"
        ]

    if goal_type == "assignment":
        return [
            "Analyse task instructions and grading rubric",
            "Gather academic sources and references",
            "Write initial draft for this section",
            "Edit and improve clarity and arguments",
            "Format and validate submission requirements"
        ]

    if goal_type == "dissertation":
        return [
            "Clarify chapter objectives and expected outcomes",
            "Collect and review relevant literature or data",
            "Write draft content for this chapter",
            "Revise structure, coherence, and academic tone",
            "Finalize chapter and prepare for review"
        ]

    return [
        "Clarify scope of this milestone",
        "Prepare required resources and tools",
        "Execute core task",
        "Review quality and completeness",
        "Finalize and mark milestone as complete"
    ]


# ------------------------------
# Progress Initializer (UTILITY)
# ------------------------------
def initialize_progress(milestones: list[str], goal: str) -> dict:
    """
    Creates a milestone × subtask progress matrix.
    """
    goal_type = detect_goal_type(goal)

    return {
        milestone: {
            subtask: False
            for subtask in generate_subtasks(milestone, goal_type)
        }
        for milestone in milestones
    }
