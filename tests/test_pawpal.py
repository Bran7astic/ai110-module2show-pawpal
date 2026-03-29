from datetime import datetime, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


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


def test_sort_tasks_by_time_orders_earliest_first() -> None:
	"""
	Tests that Scheduler.sort_tasks_by_time correctly orders tasks from
	earliest to latest based on their due times.
	"""
	scheduler = Scheduler()
	base = datetime.now().replace(second=0, microsecond=0)

	later_task = Task(
		description="Later",
		due_by=base + timedelta(hours=3),
		frequency="once",
		duration_minutes=10,
		priority=1,
	)
	earlier_task = Task(
		description="Earlier",
		due_by=base + timedelta(hours=1),
		frequency="once",
		duration_minutes=10,
		priority=1,
	)

	sorted_tasks = scheduler.sort_tasks_by_time([later_task, earlier_task])
	assert [task.description for task in sorted_tasks] == ["Earlier", "Later"]


def test_filter_tasks_by_pet_and_status() -> None:
	owner = Owner(name="Sam", age=28, location="Austin")
	dog = Pet(name="Milo", type="Dog", breed="Mixed", age=4)
	cat = Pet(name="Luna", type="Cat", breed="Siamese", age=2)
	owner.register_pet(dog)
	owner.register_pet(cat)

	dog_task = Task(
		description="Walk",
		due_by=datetime.now() + timedelta(hours=1),
		frequency="daily",
		duration_minutes=20,
		priority=3,
	)
	cat_task = Task(
		description="Brush",
		due_by=datetime.now() + timedelta(hours=2),
		frequency="once",
		duration_minutes=15,
		priority=2,
	)

	owner.add_task(dog, dog_task)
	owner.add_task(cat, cat_task)
	dog_task.mark_complete()

	scheduler = Scheduler()
	tasks = scheduler.retrieve_tasks(owner)

	filtered_for_milo = scheduler.filter_tasks(tasks, pet_name="milo")
	assert [task.description for task in filtered_for_milo] == ["Walk"]

	completed_tasks = scheduler.filter_tasks(tasks, is_completed=True)
	assert [task.description for task in completed_tasks] == ["Walk"]


def test_filter_owner_tasks_by_pet_and_status() -> None:
	owner = Owner(name="Jamie", age=35, location="Denver")
	dog = Pet(name="Milo", type="Dog", breed="Terrier", age=5)
	cat = Pet(name="Nori", type="Cat", breed="Tabby", age=3)
	owner.register_pet(dog)
	owner.register_pet(cat)

	walk = Task(
		description="Walk",
		due_by=datetime.now() + timedelta(hours=1),
		frequency="daily",
		duration_minutes=30,
		priority=3,
	)
	feed = Task(
		description="Feed",
		due_by=datetime.now() + timedelta(hours=2),
		frequency="daily",
		duration_minutes=10,
		priority=4,
	)

	owner.add_task(dog, walk)
	owner.add_task(cat, feed)
	feed.mark_complete()

	scheduler = Scheduler()

	filtered_pet = scheduler.filter_owner_tasks(owner, pet_name="milo")
	assert [task.description for task in filtered_pet] == ["Walk"]

	filtered_completed = scheduler.filter_owner_tasks(owner, is_completed=True)
	assert [task.description for task in filtered_completed] == ["Feed"]


def test_update_task_status_creates_new_instance_for_daily_task() -> None:
	base = datetime.now().replace(second=0, microsecond=0)
	owner = Owner(name="Dana", age=33, location="Boston")
	pet = Pet(name="Milo", type="Dog", breed="Mixed", age=4)
	owner.register_pet(pet)

	recurring_task = Task(
		description="Feed",
		due_by=base - timedelta(days=1),
		frequency="daily",
		duration_minutes=10,
		priority=3,
	)
	owner.add_task(pet, recurring_task)

	scheduler = Scheduler()
	next_task = scheduler.update_task_status(recurring_task, True, owner=owner)

	assert recurring_task.is_completed is True
	assert next_task is not None
	assert next_task is not recurring_task
	assert next_task.description == recurring_task.description
	assert next_task.frequency == "daily"
	assert next_task.is_completed is False
	assert next_task.due_by > datetime.now()
	assert next_task in pet.get_tasks()


def test_update_task_status_creates_new_instance_for_weekly_task() -> None:
	base = datetime.now().replace(second=0, microsecond=0)
	owner = Owner(name="Casey", age=29, location="Portland")
	pet = Pet(name="Luna", type="Cat", breed="Siamese", age=2)
	owner.register_pet(pet)

	weekly_task = Task(
		description="Litter deep clean",
		due_by=base - timedelta(days=8),
		frequency="weekly",
		duration_minutes=20,
		priority=2,
	)
	owner.add_task(pet, weekly_task)

	scheduler = Scheduler()
	next_task = scheduler.update_task_status(weekly_task, True, owner=owner)

	assert weekly_task.is_completed is True
	assert next_task is not None
	assert next_task.frequency == "weekly"
	assert next_task.due_by > datetime.now()
	assert next_task in pet.get_tasks()


def test_update_task_status_does_not_create_new_instance_for_once_task() -> None:
	task = Task(
		description="Vet visit",
		due_by=datetime.now() + timedelta(days=1),
		frequency="once",
		duration_minutes=45,
		priority=5,
	)

	scheduler = Scheduler()
	next_task = scheduler.update_task_status(task, True)

	assert task.is_completed is True
	assert next_task is None


def test_detect_conflicts_finds_overlapping_tasks() -> None:
	base = datetime.now().replace(second=0, microsecond=0)

	task_one = Task(
		description="Morning walk",
		due_by=base,
		frequency="once",
		duration_minutes=30,
		priority=3,
	)
	task_two = Task(
		description="Medication",
		due_by=base + timedelta(minutes=15),
		frequency="once",
		duration_minutes=10,
		priority=5,
	)
	task_three = Task(
		description="Playtime",
		due_by=base + timedelta(minutes=45),
		frequency="once",
		duration_minutes=10,
		priority=1,
	)

	scheduler = Scheduler()
	conflicts = scheduler.detect_conflicts([task_one, task_two, task_three])

	assert len(conflicts) == 1
	assert conflicts[0][0].description == "Morning walk"
	assert conflicts[0][1].description == "Medication"


def test_detect_same_time_conflict_warnings_returns_warning_messages() -> None:
	base = datetime.now().replace(second=0, microsecond=0)

	pet_one = Pet(name="Milo", type="Dog", breed="Mixed", age=3)
	pet_two = Pet(name="Luna", type="Cat", breed="Mixed", age=2)

	task_one = Task(
		description="Feed",
		due_by=base,
		frequency="daily",
		duration_minutes=10,
		priority=3,
	)
	task_two = Task(
		description="Medication",
		due_by=base,
		frequency="daily",
		duration_minutes=10,
		priority=4,
	)

	task_one.add_participant(pet_one)
	task_two.add_participant(pet_two)

	scheduler = Scheduler()
	warnings = scheduler.detect_same_time_conflict_warnings([task_one, task_two])

	assert len(warnings) == 1
	assert "Warning:" in warnings[0]
	assert "simultaneous tasks" in warnings[0]
