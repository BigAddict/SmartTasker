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
from src.models.model import Task
from src.models.db_manager import TaskManager
from src.services.db_setup import create_db_and_tables, get_engine

@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Setup test database before each test."""
    await create_db_and_tables()
    
    # Clear all data from the Tasks table
    async with AsyncSession(get_engine()) as session:
        await session.exec(delete(Task))
        await session.commit()
    yield

@pytest_asyncio.fixture
async def task_manager():
    """Provide a TaskManager instance."""
    return TaskManager()

@pytest_asyncio.fixture
async def sample_task():
    """Provide a sample Task instance."""
    return Task(
        name="Sample Task",
        description="This is a sample task.",
        due_date=date(2024, 3, 16),
        completed=False,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        status="In Progress"
    )

class TestTaskManager:
    """Test suite for TaskManager."""
    
    @pytest.mark.asyncio
    async def test_create_task(self, task_manager: TaskManager, sample_task: Task):
        """Test task creation."""
        # When
        created_task = await task_manager.create_task(sample_task)
        
        # Then
        assert created_task.id is not None
        assert created_task.name == "Sample Task"
        assert created_task.description == "This is a sample task."
        assert created_task.status == "In Progress"
        assert created_task.created_at is not None

    @pytest.mark.asyncio
    async def test_get_task(self, task_manager: TaskManager, sample_task: Task):
        """Test task retrieval."""
        # Given
        created_task = await task_manager.create_task(sample_task)
        
        # When
        retrieved_task = await task_manager.get_task(created_task.id)
        
        # Then
        assert retrieved_task is not None
        assert retrieved_task.id == created_task.id
        assert retrieved_task.name == created_task.name
        assert retrieved_task.description == created_task.description

    @pytest.mark.asyncio
    async def test_get_all_tasks(self, task_manager: TaskManager, sample_task: Task):
        """Test retrieving all tasks."""
        # Given
        created_task = await task_manager.create_task(sample_task)
        second_task = await task_manager.create_task(
            Task(
                name="Second Task",
                description="Another task",
                status="Not Started"
            )
        )
        
        # When
        all_tasks = await task_manager.get_all_tasks()
        
        # Then
        assert len(all_tasks) == 2
        assert any(t.id == created_task.id for t in all_tasks)
        assert any(t.id == second_task.id for t in all_tasks)

    @pytest.mark.asyncio
    async def test_update_task(self, task_manager: TaskManager, sample_task: Task):
        """Test task update."""
        # Given
        created_task = await task_manager.create_task(sample_task)
        
        # When
        updated_task = await task_manager.update_task(
            created_task.id,
            name="Updated Task",
            description="Updated Description"
        )
        
        # Then
        assert updated_task is not None
        assert updated_task.name == "Updated Task"
        assert updated_task.description == "Updated Description"
        
        # Verify update
        verified_task = await task_manager.get_task(created_task.id)
        assert verified_task.name == "Updated Task"
        assert verified_task.description == "Updated Description"

    @pytest.mark.asyncio
    async def test_delete_task(self, task_manager: TaskManager, sample_task: Task):
        """Test task deletion."""
        # Given
        created_task = await task_manager.create_task(sample_task)
        
        # When
        delete_success = await task_manager.delete_task(created_task.id)
        
        # Then
        assert delete_success is True
        deleted_task = await task_manager.get_task(created_task.id)
        assert deleted_task is None

    @pytest.mark.asyncio
    async def test_get_non_existent_task(self, task_manager: TaskManager):
        """Test retrieving a non-existent task."""
        # When
        non_existent = await task_manager.get_task(999)
        
        # Then
        assert non_existent is None

    @pytest.mark.asyncio
    async def test_update_non_existent_task(self, task_manager: TaskManager):
        """Test updating a non-existent task."""
        # When
        updated_task = await task_manager.update_task(
            999,
            name="Updated Task",
            description="Updated Description"
        )
        
        # Then
        assert updated_task is None

    @pytest.mark.asyncio
    async def test_delete_non_existent_task(self, task_manager: TaskManager):
        """Test deleting a non-existent task."""
        # When
        delete_success = await task_manager.delete_task(999)
        
        # Then
        assert delete_success is False
