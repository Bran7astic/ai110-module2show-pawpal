from datetime import datetime, timedelta

from pawpal_system import Owner, Pet, Task


def test_mark_complete_sets_task_status_true() -> None:
	task = Task(
		description="Give medication",
		due_by=datetime.now() + timedelta(hours=1),
		frequency="daily",
		duration_minutes=10,
		priority=4,
	)

	assert task.is_completed is False
	task.mark_complete()
	assert task.is_completed is True


def test_adding_task_to_pet_increases_task_count() -> None:
	owner = Owner(name="Alex", age=30, location="Seattle")
	pet = Pet(name="Milo", type="Dog", breed="Beagle", age=3)
	owner.register_pet(pet)

	task = Task(
		description="Evening walk",
		due_by=datetime.now() + timedelta(hours=2),
		frequency="daily",
		duration_minutes=25,
		priority=3,
	)

	before_count = len(pet.get_tasks())
	owner.add_task(pet, task)
	after_count = len(pet.get_tasks())

	assert after_count == before_count + 1
