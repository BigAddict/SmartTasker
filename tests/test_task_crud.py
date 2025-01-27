import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from src.models.task_manager import TaskCRUD
from src.models.model import Database, Task

@pytest_asyncio.fixture
async def task_crud():
    db = Database()
    await db._create_tables()  # Ensure tables are created
    return TaskCRUD()

@pytest.mark.asyncio
async def test_create_task(task_crud):
    task = await task_crud.create_task(
        title="Test Task",
        description="This is a test task.",
        priority=1,
        status="pending",
        due_date=datetime.utcnow().date() + timedelta(days=1),
        start_time=datetime.utcnow(),
        duration=timedelta(hours=1)
    )
    assert task.title == "Test Task"
    assert task.description == "This is a test task."

@pytest.mark.asyncio
async def test_get_task_by_id(task_crud):
    task = await task_crud.create_task(
        title="Get Task",
        description="This task will be retrieved.",
        priority=1,
        status="pending",
        due_date=datetime.utcnow().date() + timedelta(days=1),
        start_time=datetime.utcnow(),
        duration=timedelta(hours=1)
    )
    retrieved_task = await task_crud.get_task_by_id(task.id)
    assert retrieved_task.id == task.id

@pytest.mark.asyncio
async def test_get_due_tasks(task_crud):
    await task_crud.create_task(
        title="Due Task",
        description="This task is due soon.",
        priority=1,
        status="pending",
        due_date=datetime.utcnow().date() + timedelta(days=1),
        start_time=datetime.utcnow(),
        duration=timedelta(hours=1)
    )
    due_tasks = await task_crud.get_due_tasks(due_within_days=1)
    assert len(due_tasks) > 0

@pytest.mark.asyncio
async def test_update_task_status(task_crud):
    task = await task_crud.create_task(
        title="Update Task",
        description="This task will have its status updated.",
        priority=1,
        status="pending",
        due_date=datetime.utcnow().date() + timedelta(days=1),
        start_time=datetime.utcnow(),
        duration=timedelta(hours=1)
    )
    updated_task = await task_crud.update_task_status(task.id, new_status="completed")
    assert updated_task.status == "completed"

@pytest.mark.asyncio
async def test_reschedule_task(task_crud):
    task = await task_crud.create_task(
        title="Reschedule Task",
        description="This task will be rescheduled.",
        priority=1,
        status="pending",
        due_date=datetime.utcnow().date() + timedelta(days=1),
        start_time=datetime.utcnow(),
        duration=timedelta(hours=1)
    )
    new_start_time = datetime.utcnow() + timedelta(days=2)
    rescheduled_task = await task_crud.reschedule_task(task.id, new_start_time=new_start_time)
    assert rescheduled_task.start_time == new_start_time

@pytest.mark.asyncio
async def test_delete_task(task_crud):
    task = await task_crud.create_task(
        title="Delete Task",
        description="This task will be deleted.",
        priority=1,
        status="pending",
        due_date=datetime.utcnow().date() + timedelta(days=1),
        start_time=datetime.utcnow(),
        duration=timedelta(hours=1)
    )
    deleted_task = await task_crud.delete_task(task.id, archive=True)
    assert deleted_task.status == "archived"

@pytest.mark.asyncio
async def test_add_task_dependency(task_crud):
    parent_task = await task_crud.create_task(
        title="Parent Task",
        description="This is a parent task.",
        priority=1,
        status="pending",
        due_date=datetime.utcnow().date() + timedelta(days=1),
        start_time=datetime.utcnow(),
        duration=timedelta(hours=1)
    )
    child_task = await task_crud.create_task(
        title="Child Task",
        description="This is a child task.",
        priority=1,
        status="pending",
        due_date=datetime.utcnow().date() + timedelta(days=1),
        start_time=datetime.utcnow(),
        duration=timedelta(hours=1)
    )
    updated_child_task = await task_crud.add_task_dependency(parent_task.id, child_task.id)
    assert updated_child_task.parent_id == parent_task.id
