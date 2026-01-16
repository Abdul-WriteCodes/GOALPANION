# utils/validation.py

from datetime import date

def validate_goal_input(goal, hours_per_day, deadline):
    errors = []
    if not goal or goal.strip() == "":
        errors.append("Goal cannot be empty.")
    if hours_per_day <= 0:
        errors.append("Hours per day must be greater than 0.")
    if deadline < date.today():
        errors.append("Deadline cannot be in the past.")
    return errors
