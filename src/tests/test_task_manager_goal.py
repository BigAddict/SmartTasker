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
from src.models.model import Goal
from src.models.db_manager import GoalManager
from src.services.db_setup import create_db_and_tables, get_engine

@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Setup test database before each test."""
    await create_db_and_tables()
    
    # Clear all data from the goals table
    async with AsyncSession(get_engine()) as session:
        await session.exec(delete(Goal))
        await session.commit()
    yield

@pytest_asyncio.fixture
async def goal_manager():
    """Provide a GoalManager instance."""
    return GoalManager()

@pytest_asyncio.fixture
async def sample_goal():
    """Provide a sample Goal instance."""
    return Goal(
        name="Test Goal",
        description="Test Goal Description",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        status="In Progress"
    )

class TestGoalManager:
    """Test suite for GoalManager."""
    
    @pytest.mark.asyncio
    async def test_create_goal(self, goal_manager: GoalManager, sample_goal: Goal):
        """Test goal creation."""
        # When
        created_goal = await goal_manager.create_goal(sample_goal)
        
        # Then
        assert created_goal.id is not None
        assert created_goal.name == "Test Goal"
        assert created_goal.description == "Test Goal Description"
        assert created_goal.status == "In Progress"
        assert created_goal.created_at is not None

    @pytest.mark.asyncio
    async def test_get_goal(self, goal_manager: GoalManager, sample_goal: Goal):
        """Test goal retrieval."""
        # Given
        created_goal = await goal_manager.create_goal(sample_goal)
        
        # When
        retrieved_goal = await goal_manager.get_goal(created_goal.id)
        
        # Then
        assert retrieved_goal is not None
        assert retrieved_goal.id == created_goal.id
        assert retrieved_goal.name == created_goal.name
        assert retrieved_goal.description == created_goal.description

    @pytest.mark.asyncio
    async def test_get_all_goals(self, goal_manager: GoalManager, sample_goal: Goal):
        """Test retrieving all goals."""
        # Given
        created_goal = await goal_manager.create_goal(sample_goal)
        second_goal = await goal_manager.create_goal(
            Goal(
                name="Second Goal",
                description="Another goal",
                status="Not Started"
            )
        )
        
        # When
        all_goals = await goal_manager.get_all_goals()
        
        # Then
        assert len(all_goals) == 2
        assert any(g.id == created_goal.id for g in all_goals)
        assert any(g.id == second_goal.id for g in all_goals)

    @pytest.mark.asyncio
    async def test_update_goal(self, goal_manager: GoalManager, sample_goal: Goal):
        """Test goal update."""
        # Given
        created_goal = await goal_manager.create_goal(sample_goal)
        
        # When
        updated_goal = await goal_manager.update_goal(
            created_goal.id,
            name="Updated Goal",
            description="Updated Description"
        )
        
        # Then
        assert updated_goal is not None
        assert updated_goal.name == "Updated Goal"
        assert updated_goal.description == "Updated Description"
        
        # Verify update
        verified_goal = await goal_manager.get_goal(created_goal.id)
        assert verified_goal.name == "Updated Goal"
        assert verified_goal.description == "Updated Description"

    @pytest.mark.asyncio
    async def test_delete_goal(self, goal_manager: GoalManager, sample_goal: Goal):
        """Test goal deletion."""
        # Given
        created_goal = await goal_manager.create_goal(sample_goal)
        
        # When
        delete_success = await goal_manager.delete_goal(created_goal.id)
        
        # Then
        print(f"Delete_Success: {delete_success}")
        assert delete_success is True
        deleted_goal = await goal_manager.get_goal(created_goal.id)
        assert deleted_goal is None

    @pytest.mark.asyncio
    async def test_get_non_existent_goal(self, goal_manager: GoalManager):
        """Test retrieving a non-existent goal."""
        # When
        non_existent = await goal_manager.get_goal(999)
        
        # Then
        assert non_existent is None

    @pytest.mark.asyncio
    async def test_update_non_existent_goal(self, goal_manager: GoalManager):
        """Test updating a non-existent goal."""
        # When
        updated_goal = await goal_manager.update_goal(
            999,
            name="Updated Goal",
            description="Updated Description"
        )
        
        # Then
        assert updated_goal is None

    @pytest.mark.asyncio
    async def test_delete_non_existent_goal(self, goal_manager: GoalManager):
        """Test deleting a non-existent goal."""
        # When
        delete_success = await goal_manager.delete_goal(999)
        
        # Then
        assert delete_success is False