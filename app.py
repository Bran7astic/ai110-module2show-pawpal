from datetime import datetime

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")
owner_age = st.number_input("Owner age", min_value=1, max_value=120, value=30)
owner_location = st.text_input("Owner location", value="San Diego")

# Keep one Owner object across reruns and recreate only when profile values change.
owner_obj = st.session_state.get("owner")
if (
    not isinstance(owner_obj, Owner)
    or owner_obj.name != owner_name
    or owner_obj.age != int(owner_age)
    or owner_obj.location != owner_location
):
    st.session_state.owner = Owner(
        name=owner_name,
        age=int(owner_age),
        location=owner_location,
    )

owner_obj = st.session_state.owner
st.caption(f"Active owner in session: {owner_obj.name} ({owner_obj.location})")

st.divider()

st.subheader("Add Pet")
pet_col1, pet_col2 = st.columns(2)
with pet_col1:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
with pet_col2:
    breed = st.text_input("Breed", value="Mixed")
    pet_age = st.number_input("Pet age", min_value=0, max_value=40, value=2)

if st.button("Register pet"):
    normalized_name = pet_name.strip()
    if not normalized_name:
        st.warning("Please enter a pet name.")
    elif any(p.name.lower() == normalized_name.lower() for p in owner_obj.pets):
        st.info(f"{normalized_name} is already registered.")
    else:
        new_pet = Pet(
            name=normalized_name,
            type=species,
            breed=breed.strip() or "Unknown",
            age=int(pet_age),
        )
        owner_obj.register_pet(new_pet)
        st.success(f"Registered pet: {new_pet.name}")

if owner_obj.pets:
    st.write("Registered pets:")
    st.table(
        [
            {"name": pet.name, "type": pet.type, "breed": pet.breed, "age": pet.age}
            for pet in owner_obj.pets
        ]
    )
else:
    st.info("No pets registered yet.")

st.divider()

st.subheader("Schedule Task")
if not owner_obj.pets:
    st.info("Register at least one pet before adding tasks.")
else:
    pet_lookup = {pet.name: pet for pet in owner_obj.pets}
    selected_pet_name = st.selectbox("Assign task to", options=list(pet_lookup.keys()))

    task_col1, task_col2 = st.columns(2)
    with task_col1:
        task_title = st.text_input("Task title", value="Morning walk")
        frequency = st.selectbox("Frequency", ["daily", "weekly", "every 2 days", "once"])
        due_date = st.date_input("Due date")
    with task_col2:
        due_time = st.time_input("Due time")
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    if st.button("Add task"):
        normalized_title = task_title.strip()
        if not normalized_title:
            st.warning("Please enter a task title.")
        else:
            due_by = datetime.combine(due_date, due_time)
            priority_value = {"low": 1, "medium": 2, "high": 3}[priority_label]
            task = Task(
                description=normalized_title,
                due_by=due_by,
                frequency=frequency,
                duration_minutes=int(duration),
                priority=priority_value,
            )
            owner_obj.add_task(pet_lookup[selected_pet_name], task)
            st.success(f"Added task '{task.description}' for {selected_pet_name}.")

scheduler_for_view = Scheduler()
all_tasks = owner_obj.get_all_tasks()

st.subheader("Current Tasks")
if all_tasks:
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        pet_filter_options = ["All pets"] + [pet.name for pet in owner_obj.pets]
        selected_pet_filter = st.selectbox("Filter by pet", options=pet_filter_options)
    with filter_col2:
        status_filter = st.selectbox("Filter by status", options=["All", "Pending", "Completed"])

    selected_pet_name = None if selected_pet_filter == "All pets" else selected_pet_filter
    selected_status = None
    if status_filter == "Pending":
        selected_status = False
    elif status_filter == "Completed":
        selected_status = True

    filtered_tasks = scheduler_for_view.filter_owner_tasks(
        owner_obj,
        pet_name=selected_pet_name,
        is_completed=selected_status,
    )
    sorted_filtered_tasks = scheduler_for_view.sort_tasks_by_time(filtered_tasks)

    st.success(f"Showing {len(sorted_filtered_tasks)} of {len(all_tasks)} tasks.")
    st.table(
        [
            {
                "description": task.description,
                "due_by": task.due_by.strftime("%Y-%m-%d %H:%M"),
                "frequency": task.frequency,
                "duration_minutes": task.duration_minutes,
                "priority": task.priority,
                "pets": ", ".join(p.name for p in task.participants),
                "completed": task.is_completed,
            }
            for task in sorted_filtered_tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.subheader("Task Status")
if all_tasks:
    tasks_for_status = scheduler_for_view.sort_tasks_by_time(all_tasks)
    task_display_lookup = {
        (
            f"{task.description} | {task.due_by.strftime('%Y-%m-%d %H:%M')} | "
            f"Pets: {', '.join(p.name for p in task.participants) or 'Unassigned'}"
        ): task
        for task in tasks_for_status
    }

    selected_task_label = st.selectbox(
        "Select task to update",
        options=list(task_display_lookup.keys()),
    )
    selected_task = task_display_lookup[selected_task_label]

    st.caption(
        f"Current status: {'Completed' if selected_task.is_completed else 'Pending'}"
    )

    status_col1, status_col2 = st.columns(2)
    with status_col1:
        if st.button("Mark Selected Task Complete"):
            next_task = scheduler_for_view.update_task_status(
                selected_task,
                True,
                owner=owner_obj,
            )
            st.success("Task marked as complete.")
            if next_task is not None:
                st.success(
                    "Recurring task detected. Created next instance due "
                    f"{next_task.due_by.strftime('%Y-%m-%d %H:%M')}."
                )

    with status_col2:
        if st.button("Mark Selected Task Incomplete"):
            scheduler_for_view.update_task_status(
                selected_task,
                False,
                owner=owner_obj,
            )
            st.success("Task marked as incomplete.")
else:
    st.info("Add tasks first to manage completion status.")

st.divider()

st.subheader("Build Schedule")
available_minutes = st.number_input(
    "Available minutes for today",
    min_value=1,
    max_value=1440,
    value=120,
)
prefer_earlier_due = st.checkbox("Prioritize earlier due times first", value=True)

if st.button("Generate schedule"):
    scheduler = Scheduler(
        available_minutes_per_day=int(available_minutes),
        prefer_earlier_due=prefer_earlier_due,
    )
    daily_plan = scheduler.generate_daily_plan(owner_obj)

    if not daily_plan:
        st.warning("No tasks fit the current schedule constraints.")
    else:
        sorted_plan = scheduler.sort_tasks_by_time(daily_plan)
        st.success("Today's schedule generated.")
        st.table(
            [
                {
                    "task": task.description,
                    "due_by": task.due_by.strftime("%Y-%m-%d %H:%M"),
                    "duration_minutes": task.duration_minutes,
                    "priority": task.priority,
                    "pets": ", ".join(p.name for p in task.participants),
                }
                for task in sorted_plan
            ]
        )

        overlap_conflicts = scheduler.detect_conflicts(sorted_plan)
        same_time_warnings = scheduler.detect_same_time_conflict_warnings(sorted_plan)
        if overlap_conflicts:
            st.warning(
                f"Detected {len(overlap_conflicts)} overlapping task conflict(s). "
                "Consider adjusting due times or durations."
            )
        for warning_message in same_time_warnings:
            st.warning(warning_message)
