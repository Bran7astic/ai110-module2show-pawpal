from datetime import datetime, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def next_occurrence(hour: int, minute: int = 0) -> datetime:
	now = datetime.now()
	target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
	if target <= now:
		target += timedelta(days=1)
	return target


def build_sample_data() -> tuple[Owner, Scheduler]:
	owner = Owner(name="Jordan", age=31, location="San Diego")

	pet_one = Pet(name="Milo", type="Dog", breed="Labrador", age=4)
	pet_two = Pet(name="Luna", type="Cat", breed="Siamese", age=2)

	owner.register_pet(pet_one)
	owner.register_pet(pet_two)

	walk_task = Task(
		description="Morning walk",
		due_by=next_occurrence(7, 0),
		frequency="daily",
		duration_minutes=30,
		priority=3,
	)

	feed_task = Task(
		description="Feed dinner",
		due_by=next_occurrence(18, 0),
		frequency="daily",
		duration_minutes=15,
		priority=5,
	)

	groom_task = Task(
		description="Brush fur",
		due_by=next_occurrence(12, 30),
		frequency="every 2 days",
		duration_minutes=20,
		priority=2,
	)

	owner.add_task(pet_one, walk_task)
	owner.add_task(pet_one, feed_task)
	owner.add_task(pet_two, groom_task)

	scheduler = Scheduler(available_minutes_per_day=90, prefer_earlier_due=True)
	return owner, scheduler


def print_schedule(owner: Owner, scheduler: Scheduler) -> None:
	plan = scheduler.generate_daily_plan(owner)

	print("Today's Schedule")
	print("-" * 40)

	if not plan:
		print("No tasks scheduled for today.")
		return

	for index, task in enumerate(plan, start=1):
		pet_names = ", ".join(pet.name for pet in task.participants) or "Unassigned"
		due_text = task.due_by.strftime("%Y-%m-%d %H:%M")
		print(
			f"{index}. {task.description} | Due: {due_text} | "
			f"Duration: {task.duration_minutes} min | Priority: {task.priority} | Pets: {pet_names}"
		)


if __name__ == "__main__":
	owner_obj, scheduler_obj = build_sample_data()
	print_schedule(owner_obj, scheduler_obj)
