# ACHIEVIT
**An LLM-Powered Academic Companion for Goal Achievement**

---

## Description
**ACHIEVIT** is an AI-driven, adaptive planning system designed to help **students and researchers structure, track, and achieve their resolution goals**.  
It supports academic tasks such as studying for exams, completing assignments, or writing dissertations/thesis while taking into account **real-world constraints** like time availability, skill level, and deadlines.  

By combining **heuristic milestone logic** with **LLM reasoning**, ACHIEVIT provides **adaptive, context-aware guidance** that evolves as users make progress on their goals. The system breaks goals into actionable milestones, tracks completion, and dynamically adjusts plans to maximize success.

<p align="center">
  <img src="assets/Achievit.jpg" alt="Achievit Logo" style="width:100%; max-width:800px;" />
</p>


## Architecture & Key Features

### Hybrid Intelligence Architecture
ACHIEVIT uses a layered, human-in-the-loop architecture:

<p align="center">
  <img src="assets/Achievitecture.png" alt="Achievitecture" style="width:100%; max-width:800px;" />
</p>

- **Heuristic Logic Layer**  
  - Generates deterministic milestones from high-level goals  
  - Handles constraints such as time, skill level, and deadlines  

- **LLM Reasoning Layer (Gemini)**  
  - Produces adaptive and context-aware plans  
  - Optimizes schedules based on progress  
  - Suggests strategies and relevant academic resources  

> This hybrid layering ensures plans are **structured, feasible, and intelligent**.

---

### Key Features and How it Works

#### 🎯 Goal-Oriented Planning
- Supports multiple academic goal types:  
  - **Exams**  
  - **Assignments**  
  - **Dissertations / Theses**  
- Accept high-level goals and transform them into **clear, actionable four milestones and 5 substacks**  taking into account:
	- Daily hours the user can commit to the goal
	- Skill level (Novice / Intermediate / Expert) of the user in completing the goal
	- Fixed deadlines  under which the goal is to be achieved
- Produces **realistic and achievable plans with guidance on what to do based on four milestones and five different sub-tasks per milestone**  
- Track and optimizes plans based on user progress on goal milestones and sub-tasks
- Produces adaptive and context-aware plans based on user progress on milestone and sub-tasks 
- Analyse behavioural risks and alerts users on implication on deadlines
- Suggests strategies and relevant academic resources to achieve the goal

#### 🧑‍🤝‍🧑 Human-in-the-Loop UI
- Built with **Streamlit** for interactive planning  
- Sidebar for goal input and constraints  
- Users remain in control of:  
  - Goal definition  
  - Progress updates  
  - Plan adaptation  
  
---

## Target Users
- Undergraduate and postgraduate students  
- Graduate researchers and PhD candidates  
- Self-directed learners with academic goals  
- Developers exploring **LLM agent systems with observability**

---

## Why ACHIEVIT?
- Combines **LLM reasoning + heuristic logic** for smarter planning  
- Supports **adaptive, milestone-driven execution**  
- Handles **real-world constraints** for feasible plans  
- Offers **downloadable plans (DOCX)** for offline use  
- Provides **progress tracking and adaptive updates** for ongoing goal achievement  

---
