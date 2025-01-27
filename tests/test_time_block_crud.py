import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from src.models.task_manager import TimeBlockCRUD
from src.models.model import Database, Task, TimeBlock

@pytest_asyncio.fixture
async def setup_db():
    # Setup code to initialize the database and create a test task
    db = Database()
    async with db.get_session() as session:
        test_task = Task(
            title="Test Task",
            description="This is a test task.",
            priority=1,
            status="pending",
            due_date=datetime.utcnow().date() + timedelta(days=1),
            start_time=datetime.utcnow(),
            duration=timedelta(hours=1)
        )
        session.add(test_task)
        await session.commit()
        await session.refresh(test_task)
        yield test_task.id  # Provide the test task ID for use in tests
        await session.delete(test_task)  # Cleanup after tests

@pytest.mark.asyncio
async def test_start_time_block(setup_db):
    time_block_crud = TimeBlockCRUD()
    task_id = setup_db

    # Test starting a time block
    time_block = await time_block_crud.start_time_block(task_id)
    assert time_block.task_id == task_id
    assert time_block.start is not None

    # Test starting a time block with an invalid task ID
    with pytest.raises(ValueError):
        await time_block_crud.start_time_block(-1)

@pytest.mark.asyncio
async def test_end_time_block(setup_db):
    time_block_crud = TimeBlockCRUD()
    task_id = setup_db
    time_block = await time_block_crud.start_time_block(task_id)

    # Test ending a time block
    ended_time_block = await time_block_crud.end_time_block(time_block.id)
    assert ended_time_block.end is not None
    assert ended_time_block.actual_duration is not None

    # Test ending a time block with an invalid ID
    with pytest.raises(ValueError):
        await time_block_crud.end_time_block(-1)

@pytest.mark.asyncio
async def test_get_time_blocks(setup_db):
    time_block_crud = TimeBlockCRUD()
    task_id = setup_db
    await time_block_crud.start_time_block(task_id)

    # Test retrieving time blocks
    time_blocks = await time_block_crud.get_time_blocks(task_id)
    assert len(time_blocks) > 0

@pytest.mark.asyncio
async def test_adjust_time_block(setup_db):
    time_block_crud = TimeBlockCRUD()
    task_id = setup_db
    time_block = await time_block_crud.start_time_block(task_id)

    # Test adjusting the time block
    new_start = datetime.utcnow() + timedelta(hours=1)
    await time_block_crud.adjust_time_block(time_block.id, new_start=new_start)
    adjusted_time_block = await time_block_crud.get_time_blocks(task_id)
    assert adjusted_time_block[0].start == new_start

    # Test adjusting a time block with an invalid ID
    with pytest.raises(ValueError):
        await time_block_crud.adjust_time_block(-1)
