# agents/heuristic.py

def generate_plan(goal, constraints):
    goal_lower = goal.lower()
    milestones = []

    if "exam" in goal_lower or "test" in goal_lower:
        milestones = [
            "Review syllabus & topics",
            "Create study schedule",
            "Practice questions",
            "Mock exams",
            "Revision & final prep"
        ]
    elif "assignment" in goal_lower or "homework" in goal_lower:
        milestones = [
            "Understand assignment requirements",
            "Research & gather resources",
            "Draft assignment",
            "Review & edit",
            "Submit assignment"
        ]
    elif "dissertation" in goal_lower or "thesis" in goal_lower or "research paper" in goal_lower:
        milestones = [
            "Submit proposal",
            "Literature review",
            "Methodology planning",
            "Data collection / Experiments",
            "Writing chapters",
            "Review & submit"
        ]
    else:
        milestones = [
            "Break down goal into tasks",
            "Set deadlines for each task",
            "Monitor progress",
            "Review & complete"
        ]

    # Adjust based on time constraint
    hours_per_day = constraints.get("hours_per_day", 2)
    if hours_per_day < 2:
        milestones = milestones[:max(1, len(milestones)//2)]

    return milestones
