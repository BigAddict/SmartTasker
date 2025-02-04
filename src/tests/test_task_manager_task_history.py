# Standard library imports
import sys
from pathlib import Path
from datetime import datetime, date

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# Third-party imports
import pytest
import pytest_asyncio
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import delete

# Local application imports
from src.models.model import Task, TaskHistory
from src.models.db_manager import TaskManager, TaskHistoryManager
from src.services.db_setup import create_db_and_tables, get_engine

@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Setup test database before each test."""
    await create_db_and_tables()
    
    # Clear all data from the task history table
    async with AsyncSession(get_engine()) as session:
        await session.exec(delete(TaskHistory))
        await session.commit()
    yield

@pytest_asyncio.fixture
async def task_history_manager():
    """Provide a TaskHistoryManager instance."""
    return TaskHistoryManager()

@pytest_asyncio.fixture
async def sample_task_history():
    """Provide a sample Goal instance."""
    task = Task(
        name="Sample Task",
        description="This is a sample task.",
        start_date=date(2022, 1, 1),
        end_date=date(2022, 1, 31),
    )
    await TaskManager().create_task(task)
    return TaskHistory(
        task=task,
        change_type="Update",
    )

class TestTaskHistory:
    """Test suite for TaskHistory"""

    @pytest.mark.asyncio
    async def test_create_task_history(self, task_history_manager: TaskHistoryManager, sample_task_history: TaskHistory):
        """Test creating a new TaskHistory instance."""
        #when
        created_task_history = await task_history_manager.create_task_history(sample_task_history)  

        #then
        assert created_task_history.id is not None
        assert created_task_history.change_type == "Update"

    @pytest.mark.asyncio
    async def test_get_task_history(self, task_history_manager: TaskHistoryManager, sample_task_history: TaskHistory):
        """Test retrieving a TaskHistory instance by its ID."""
        #given
        created_task_history = await task_history_manager.create_task_history(sample_task_history)

        #when 
        retrived_task_history = await task_history_manager.get_task_history(created_task_history.id)

        #then
        assert retrived_task_history.id is not None
        assert retrived_task_history.change_type == created_task_history.change_type

    @pytest.mark.asyncio
    async def test_get_non_existent_task_history(self, task_history_manager: TaskHistoryManager):
        """Test retrieving a non-existent TaskHistory instance by its ID."""
        #when
        retrived_task_history = await task_history_manager.get_task_history(9999)  # Assuming 9999 does not exist

        #then
        assert retrived_task_history is None

    @pytest.mark.asyncio
    async def test_create_task_history_with_invalid_data(self, task_history_manager: TaskHistoryManager):
        """Test creating a TaskHistory instance with invalid data."""
        #given
        invalid_task_history = TaskHistory(
            task=None,  # This should now raise an error since task is required
            change_type="Invalid Change Type",
        )

        #when
        with pytest.raises(ValueError):  # Change this line to expect ValueError
            await task_history_manager.create_task_history(invalid_task_history)

    @pytest.mark.asyncio
    async def test_delete_task_history(self, task_history_manager: TaskHistoryManager, sample_task_history: TaskHistory):
        """Test deleting a TaskHistory instance."""
        #given
        created_task_history = await task_history_manager.create_task_history(sample_task_history)

        #when
        await task_history_manager.delete_task_history(created_task_history.id)

        #then
        retrived_task_history = await task_history_manager.get_task_history(created_task_history.id)
        assert retrived_task_history is None
