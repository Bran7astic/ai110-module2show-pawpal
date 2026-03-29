from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import re
from uuid import uuid4


@dataclass
class Task:
	"""
	Represents a task with a description, due date, frequency, duration,
	priority, unique ID, completion status, and associated participants.
	Provides methods to mark completion, check if due, and manage
	participants.
	"""
	description: str
	due_by: datetime
	frequency: str
	duration_minutes: int
	priority: int
	task_id: str = field(default_factory=lambda: str(uuid4()))
	is_completed: bool = False
	participants: list[Pet] = field(default_factory=list, repr=False, compare=False)

	def mark_complete(self) -> None:
		self.is_completed = True

	def mark_incomplete(self) -> None:
		self.is_completed = False

	def is_due(self, current_time: datetime) -> bool:
		return (not self.is_completed) and current_time >= self.due_by

	def add_participant(self, pet: Pet) -> None:
		if pet not in self.participants:
			self.participants.append(pet)

	def remove_participant(self, pet: Pet) -> None:
		if pet in self.participants:
			self.participants.remove(pet)

	def is_recurring(self) -> bool:
		normalized_frequency = self.frequency.strip().lower()
		return normalized_frequency not in {"", "once", "one time", "one-time"}

	def recurrence_interval(self) -> timedelta | None:
		normalized_frequency = self.frequency.strip().lower()
		if normalized_frequency in {"daily", "every day"}:
			return timedelta(days=1)
		if normalized_frequency in {"weekly", "every week"}:
			return timedelta(weeks=1)

		every_n_days_match = re.fullmatch(r"every\s+(\d+)\s+days?", normalized_frequency)
		if every_n_days_match:
			return timedelta(days=int(every_n_days_match.group(1)))

		every_n_weeks_match = re.fullmatch(r"every\s+(\d+)\s+weeks?", normalized_frequency)
		if every_n_weeks_match:
			return timedelta(weeks=int(every_n_weeks_match.group(1)))

		return None

	def advance_due_date(self, reference_time: datetime | None = None) -> bool:
		interval = self.recurrence_interval()
		if interval is None:
			return False

		reference = reference_time or datetime.now()
		while self.due_by <= reference:
			self.due_by += interval

		self.mark_incomplete()
		return True


@dataclass
class Pet:
	"""
	Represents a pet with attributes name, type, breed, and age, and manages
	a list of associated Task objects. Provides methods to add, remove, and
	retrieve tasks.
	"""
	name: str
	type: str
	breed: str
	age: int
	tasks: list[Task] = field(default_factory=list, compare=False)

	def _add_task(self, task: Task) -> None:
		if task not in self.tasks:
			self.tasks.append(task)

	def _remove_task(self, task: Task) -> None:
		if task in self.tasks:
			self.tasks.remove(task)

	def get_tasks(self) -> list[Task]:
		return list(self.tasks)


class Owner:
	"""
	Represents an owner with a name, age, and location, who can register
	pets, assign or remove tasks for their pets, and retrieve all unique
	tasks associated with their pets.
	"""
	def __init__(self, name: str, age: int, location: str) -> None:
		self.name = name
		self.age = age
		self.location = location
		self.pets: list[Pet] = []

	def register_pet(self, pet: Pet) -> None:
		if pet not in self.pets:
			self.pets.append(pet)

	def add_task(self, pet: Pet, task: Task) -> None:
		if pet not in self.pets:
			raise ValueError("Pet must be registered to this owner before assigning tasks.")

		pet._add_task(task)
		task.add_participant(pet)

	def remove_task(self, pet: Pet, task: Task) -> None:
		if pet not in self.pets:
			raise ValueError("Pet must be registered to this owner before removing tasks.")

		pet._remove_task(task)
		task.remove_participant(pet)

	def get_all_tasks(self) -> list[Task]:
		unique_tasks: dict[str, Task] = {}
		for pet in self.pets:
			for task in pet.tasks:
				unique_tasks[task.task_id] = task

		return list(unique_tasks.values())


class Scheduler:
	"""
	Schedules and prioritizes tasks for an owner, allowing configuration of
	available minutes per day and due date preference. Provides methods to
	retrieve, organize, and plan tasks, as well as update their completion
	status.
	"""
	def __init__(
		self,
		available_minutes_per_day: int | None = None,
		prefer_earlier_due: bool = True,
	) -> None:
		self.available_minutes_per_day = available_minutes_per_day
		self.prefer_earlier_due = prefer_earlier_due

	def retrieve_tasks(self, owner: Owner) -> list[Task]:
		return owner.get_all_tasks()

	def sort_tasks_by_time(self, tasks: list[Task], descending: bool = False) -> list[Task]:
		return sorted(
			tasks,
			key=lambda task: (task.due_by, -task.priority, task.duration_minutes, task.task_id),
			reverse=descending,
		)

	def filter_tasks(
		self,
		tasks: list[Task],
		pet_name: str | None = None,
		is_completed: bool | None = None,
	) -> list[Task]:
		filtered = tasks

		if pet_name is not None:
			normalized_pet_name = pet_name.strip().lower()
			filtered = [
				task
				for task in filtered
				if any(pet.name.lower() == normalized_pet_name for pet in task.participants)
			]

		if is_completed is not None:
			filtered = [task for task in filtered if task.is_completed is is_completed]

		return filtered

	def filter_owner_tasks(
		self,
		owner: Owner,
		pet_name: str | None = None,
		is_completed: bool | None = None,
	) -> list[Task]:
		owner_tasks = self.retrieve_tasks(owner)
		return self.filter_tasks(owner_tasks, pet_name=pet_name, is_completed=is_completed)

	def detect_conflicts(self, tasks: list[Task]) -> list[tuple[Task, Task]]:
		if len(tasks) < 2:
			return []

		time_sorted_tasks = self.sort_tasks_by_time(tasks)
		conflicts: list[tuple[Task, Task]] = []

		for current_task, next_task in zip(time_sorted_tasks, time_sorted_tasks[1:]):
			current_end = current_task.due_by + timedelta(minutes=current_task.duration_minutes)
			if next_task.due_by < current_end:
				conflicts.append((current_task, next_task))

		return conflicts

	def detect_same_time_conflict_warnings(self, tasks: list[Task]) -> list[str]:
		warnings: list[str] = []
		tasks_by_due_time: dict[datetime, list[Task]] = {}

		for task in tasks:
			tasks_by_due_time.setdefault(task.due_by, []).append(task)

		for due_time in sorted(tasks_by_due_time.keys()):
			same_time_tasks = tasks_by_due_time[due_time]
			if len(same_time_tasks) < 2:
				continue

			for index, left_task in enumerate(same_time_tasks):
				for right_task in same_time_tasks[index + 1:]:
					left_pets = {pet.name for pet in left_task.participants}
					right_pets = {pet.name for pet in right_task.participants}
					shared_pets = sorted(left_pets.intersection(right_pets))

					if shared_pets:
						warnings.append(
							"Warning: conflict at "
							f"{due_time.strftime('%Y-%m-%d %H:%M')} between "
							f"'{left_task.description}' and '{right_task.description}' "
							f"for pet(s): {', '.join(shared_pets)}."
						)
					else:
						warnings.append(
							"Warning: simultaneous tasks at "
							f"{due_time.strftime('%Y-%m-%d %H:%M')} -> "
							f"'{left_task.description}' ({', '.join(sorted(left_pets)) or 'Unassigned'}) and "
							f"'{right_task.description}' ({', '.join(sorted(right_pets)) or 'Unassigned'})."
						)

		return warnings

	def organize_tasks(self, tasks: list[Task]) -> list[Task]:
		if self.prefer_earlier_due:
			return sorted(
				tasks,
				key=lambda task: (
					task.due_by,
					-task.priority,
					task.duration_minutes,
					task.task_id,
				),
			)

		return sorted(
			tasks,
			key=lambda task: (
				-task.priority,
				task.due_by,
				task.duration_minutes,
				task.task_id,
			),
		)

	def generate_daily_plan(self, owner: Owner) -> list[Task]:
		pending_tasks = [task for task in self.retrieve_tasks(owner) if not task.is_completed]
		organized_tasks = self.organize_tasks(pending_tasks)

		if self.available_minutes_per_day is None:
			return organized_tasks

		plan: list[Task] = []
		minutes_used = 0
		for task in organized_tasks:
			if minutes_used + task.duration_minutes <= self.available_minutes_per_day:
				plan.append(task)
				minutes_used += task.duration_minutes

		return plan

	def _build_next_recurring_task(self, task: Task, reference_time: datetime | None = None) -> Task | None:
		normalized_frequency = task.frequency.strip().lower()
		if normalized_frequency not in {"daily", "every day", "weekly", "every week"}:
			return None

		interval = task.recurrence_interval()
		if interval is None:
			return None

		reference = reference_time or datetime.now()
		next_due_by = task.due_by + interval
		while next_due_by <= reference:
			next_due_by += interval

		return Task(
			description=task.description,
			due_by=next_due_by,
			frequency=task.frequency,
			duration_minutes=task.duration_minutes,
			priority=task.priority,
		)

	def update_task_status(self, task: Task, status: bool, owner: Owner | None = None) -> Task | None:
		if status:
			task.mark_complete()
			next_task = self._build_next_recurring_task(task)
			if next_task is None:
				return None

			for pet in list(task.participants):
				next_task.add_participant(pet)
				if owner is not None and pet in owner.pets:
					pet._add_task(next_task)

			return next_task
		else:
			task.mark_incomplete()
			return None
