# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
## Smarter Scheduling

The scheduler now includes several practical logic upgrades:

- **Time-aware sorting:** Tasks can be sorted by due time (with tie-breakers for priority and duration) so daily plans are ordered in a predictable way.
- **Task filtering:** Tasks can be filtered by pet name and/or completion status, including a convenience method to filter directly from an owner.
- **Recurring-task parsing:** Recurrence strings such as `daily`, `weekly`, `every 2 days`, and `every 2 weeks` are interpreted into concrete time intervals.
- **Auto-regeneration of recurring tasks:** When a **daily** or **weekly** task is marked complete, the completed task is preserved as history and a new task instance is automatically created for the next due occurrence.
- **Lightweight conflict detection:** The scheduler detects overlapping tasks and same-start-time collisions, then returns warning messages instead of raising exceptions.
- **Non-blocking warnings in CLI demo:** `main.py` now demonstrates same-time conflicts and prints user-friendly warnings while continuing to produce a schedule.

These improvements keep the app simple while making planning behavior more realistic and pet-owner friendly.

## Testing PawPal+

Run the automated tests with:

```bash
python -m pytest
```

Current test coverage focuses on core scheduler reliability:

- Task completion state updates
- Adding tasks to pets/owners
- Sorting correctness (earliest-first, descending order, tie-breakers)
- Filtering by pet name and completion status
- Recurrence behavior (daily/weekly next-instance creation and interval parsing)
- Conflict detection (overlap detection and same-time warning generation)

Confidence Level: ★★★★☆ (4/5)

Rationale: recent test runs are passing and cover key planning logic paths, but confidence is not perfect yet because broader integration and edge-case stress testing can still be expanded.


### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
