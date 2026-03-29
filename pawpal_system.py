from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
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

	def update_task_status(self, task: Task, status: bool) -> None:
		if status:
			task.mark_complete()
		else:
			task.mark_incomplete()
