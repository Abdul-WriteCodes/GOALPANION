# agents/heuristic.py

def generate_plan(goal, constraints):
    goal_lower = goal.lower()

    if "exam" in goal_lower or "test" in goal_lower:
        milestones = [
            "Understand exam syllabus and requirements",
            "Study core topics and concepts",
            "Practice past questions and mock exams",
            "Final revision and exam readiness"
        ]

    elif "assignment" in goal_lower or "homework" in goal_lower:
        milestones = [
            "Understand assignment requirements",
            "Research and gather relevant materials",
            "Draft and refine the assignment",
            "Final review and submission"
        ]

    elif (
        "dissertation" in goal_lower
        or "thesis" in goal_lower
        or "research paper" in goal_lower
    ):
        milestones = [
            "Define research scope and proposal",
            "Conduct literature review and methodology planning",
            "Execute research and write core chapters",
            "Final review, editing, and submission"
        ]

    else:
        milestones = [
            "Clarify and scope the goal",
            "Plan and execute core tasks",
            "Review progress and refine work",
            "Finalize and complete the goal"
        ]

    return milestones
