from datetime import datetime, timedelta
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from src.models.model import Database, Task, TaskHistory, TimeBlock  # Import models and database class
import asyncio

class TaskCRUD:
    def __init__(self):
        self.db = Database()

    async def create_task(self, title, description, priority, status, due_date, start_time, duration, **kwargs):
        """
        Create a new task with required fields and optional additional fields.
        """
        if not all([title, description, priority, status, due_date, start_time, duration]):
            raise ValueError("All required fields (title, description, priority, status, due_date, start_time, duration) must be provided.")

        async with self.db.get_session() as session:
            new_task = Task(
                title=title,
                description=description,
                priority=priority,
                status=status,
                due_date=due_date,
                start_time=start_time,
                duration=duration,
                **kwargs  # Handle additional fields
            )
            session.add(new_task)
            await session.commit()
            await session.refresh(new_task)
            return new_task

    async def get_task_by_id(self, task_id):
        """
        Retrieve a single task with its full hierarchy (parent and children).
        """
        async with self.db.get_session() as session:
            result = await session.execute(
                select(Task)
                .options(selectinload(Task.parent), selectinload(Task.children))
                .where(Task.id == task_id)
            )
            task = result.scalars().first()
            if not task:
                raise ValueError(f"Task with ID {task_id} not found.")
            return task

    async def get_due_tasks(self, due_within_days=1):
        """
        Get tasks due today or soon, sorted by priority.
        """
        today = datetime.utcnow().date()
        due_date_limit = today + timedelta(days=due_within_days)

        async with self.db.get_session() as session:
            result = await session.execute(
                select(Task)
                .where(and_(Task.due_date >= today, Task.due_date <= due_date_limit))
                .order_by(Task.priority)
            )
            tasks = result.scalars().all()
            return tasks

    async def update_task_status(self, task_id, new_status):
        """
        Update the status of a task (e.g., 'completed', 'in_progress').
        If the task has children, they must be completed first.
        If the task is marked as completed, it is moved to task history.
        """
        async with self.db.get_session() as session:
            result = await session.execute(
                select(Task)
                .options(selectinload(Task.children))
                .where(Task.id == task_id)
            )
            task = result.scalars().first()
            if not task:
                raise ValueError(f"Task with ID {task_id} not found.")

            # Check if task has incomplete children
            if new_status == "completed" and task.children:
                incomplete_children = [child for child in task.children if child.status != "completed"]
                if incomplete_children:
                    raise ValueError("Cannot complete task: Some child tasks are incomplete.")

            # Update task status
            task.status = new_status
            task.updated_at = datetime.utcnow()

            # If task is completed, move it to task history
            if new_status == "completed":
                history_entry = TaskHistory(
                    task_id=task.id,
                    change_type="status_change",
                    previous_state={"status": task.status},
                    new_state={"status": new_status}
                )
                session.add(history_entry)

            await session.commit()
            await session.refresh(task)
            return task

    async def reschedule_task(self, task_id, new_start_time=None, new_duration=None):
        """
        Reschedule a task by modifying its start_time and/or duration.
        Tracks changes in the task history.
        """
        async with self.db.get_session() as session:
            result = await session.execute(select(Task).where(Task.id == task_id))
            task = result.scalars().first()
            if not task:
                raise ValueError(f"Task with ID {task_id} not found.")

            # Track previous state
            previous_state = {
                "start_time": task.start_time,
                "duration": task.duration
            }

            # Update task
            if new_start_time:
                task.start_time = new_start_time
            if new_duration:
                task.duration = new_duration
            task.updated_at = datetime.utcnow()

            # Log change in task history
            history_entry = TaskHistory(
                task_id=task_id,
                change_type="reschedule",
                previous_state=previous_state,
                new_state={
                    "start_time": task.start_time,
                    "duration": task.duration
                }
            )
            session.add(history_entry)
            await session.commit()
            await session.refresh(task)
            return task

    async def delete_task(self, task_id, archive=True):
        """
        Soft delete a task with an option to archive it.
        """
        async with self.db.get_session() as session:
            result = await session.execute(select(Task).where(Task.id == task_id))
            task = result.scalars().first()
            if not task:
                raise ValueError(f"Task with ID {task_id} not found.")

            if archive:
                task.status = "archived"  # Soft delete by marking as archived
            else:
                await session.delete(task)  # Hard delete
            await session.commit()
            return task

    async def add_task_dependency(self, parent_task_id, child_task_id):
        """
        Link a parent task to a child task (add dependency).
        """
        async with self.db.get_session() as session:
            result = await session.execute(select(Task).where(Task.id == child_task_id))
            child_task = result.scalars().first()
            if not child_task:
                raise ValueError(f"Child task with ID {child_task_id} not found.")

            result = await session.execute(select(Task).where(Task.id == parent_task_id))
            parent_task = result.scalars().first()
            if not parent_task:
                raise ValueError(f"Parent task with ID {parent_task_id} not found.")

            child_task.parent_id = parent_task_id
            await session.commit()
            await session.refresh(child_task)
            return child_task

class TimeBlockCRUD:
    def __init__(self):
        self.db = Database()

    async def start_time_block(self, task_id):
        if task_id <= 0:
            raise ValueError("Invalid task ID provided.")
        
        async with self.db.get_session() as session:
            result = await session.execute(select(Task).where(Task.id == task_id))
            task = result.scalars().first()
            if not task:
                raise ValueError(f"Task with ID {task_id} not found.")

        """
        Begin tracking a work session and link it to the specified task.
        """
        async with self.db.get_session() as session:
            time_block = TimeBlock(
                task_id=task_id,
                start=datetime.utcnow()
            )
            session.add(time_block)
            await session.commit()
            await session.refresh(time_block)
            return time_block

    async def end_time_block(self, time_block_id):
        """
        Finalize the duration of the work session and calculate the productivity score.
        """
        async with self.db.get_session() as session:
            result = await session.execute(select(TimeBlock).where(TimeBlock.id == time_block_id))
            time_block = result.scalars().first()
            if not time_block:
                raise ValueError(f"TimeBlock with ID {time_block_id} not found.")

            time_block.end = datetime.utcnow()
            time_block.actual_duration = time_block.end - time_block.start
            # Example productivity score calculation (this can be adjusted)
            time_block.productivity_score = (time_block.actual_duration.total_seconds() / 3600)  # Example calculation

            await session.commit()
            await session.refresh(time_block)
            return time_block

    async def get_time_blocks(self, task_id):
        """
        Retrieve all work sessions associated with a specific task.
        """
        async with self.db.get_session() as session:
            result = await session.execute(select(TimeBlock).where(TimeBlock.task_id == task_id))
            time_blocks = result.scalars().all()
            return time_blocks

    async def adjust_time_block(self, time_block_id, new_start=None, new_end=None):
        """
        Manually correct the start or end time of a tracked session.
        """
        async with self.db.get_session() as session:
            result = await session.execute(select(TimeBlock).where(TimeBlock.id == time_block_id))
            time_block = result.scalars().first()
            if not time_block:
                raise ValueError(f"TimeBlock with ID {time_block_id} not found.")

            if new_start:
                time_block.start = new_start
            if new_end:
                time_block.end = new_end
                time_block.actual_duration = time_block.end - time_block.start
                # Update productivity score if end time is adjusted
                time_block.productivity_score = (time_block.actual_duration.total_seconds() / 3600)  # Example calculation

            await session.commit()
            await session.refresh(time_block)
            return time_block
            

if __name__ == "__main__":
    async def main():
        task_crud = TaskCRUD()

        # Create a new task
        task = await task_crud.create_task(
            title="Learn Async SQLAlchemy",
            description="Study async database operations",
            priority=2,
            status="pending",
            due_date=datetime.utcnow().date() + timedelta(days=1),
            start_time=datetime.utcnow(),
            duration=timedelta(hours=2)
        )
        print(f"Created Task: {task.title} (ID: {task.id})")

        # Retrieve a task by ID
        retrieved_task = await task_crud.get_task_by_id(task.id)
        print(f"Retrieved Task: {retrieved_task.title}")

        # Get tasks due today or soon
        due_tasks = await task_crud.get_due_tasks(due_within_days=1)
        print(f"Due Tasks: {[t.title for t in due_tasks]}")

        # Update task status
        try:
            updated_task = await task_crud.update_task_status(task.id, new_status="completed")
            print(f"Updated Task Status: {updated_task.status}")
        except ValueError as e:
            print(f"Error: {e}")

        # Reschedule a task
        new_start_time = datetime.utcnow() + timedelta(days=1)
        rescheduled_task = await task_crud.reschedule_task(task.id, new_start_time=new_start_time)
        print(f"Rescheduled Task Start Time: {rescheduled_task.start_time}")

        # Add a task dependency
        child_task = await task_crud.create_task(
            title="Practice SQLAlchemy",
            description="Write some async queries",
            priority=2,
            status="pending",
            due_date=datetime.utcnow().date() + timedelta(days=1),
            start_time=datetime.utcnow(),
            duration=timedelta(hours=1)
        )
        await task_crud.add_task_dependency(parent_task_id=task.id, child_task_id=child_task.id)
        print(f"Added Dependency: {child_task.title} is a child of {task.title}")

        # Soft delete a task
        deleted_task = await task_crud.delete_task(task.id, archive=True)
        print(f"Deleted Task Status: {deleted_task.status}")

    asyncio.run(main())
