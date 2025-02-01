# Standard library imports
from datetime import datetime
from typing import Optional, List

# Third-party imports
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.exc import SQLAlchemyError

# Local application imports
from src.models.model import Goal, Task
from src.services.db_setup import get_engine

class GoalManager:
    """Manages database operations for Goal entities."""
    
    def __init__(self):
        """Initialize the GoalManager with database engine."""
        self._engine = get_engine()

    async def create_goal(self, goal: Goal) -> Goal:
        """
        Create a new goal in the database.
        
        Args:
            goal (Goal): The goal object to create
            
        Returns:
            Goal: The created goal object with updated ID and timestamps
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            async with AsyncSession(self._engine) as session:
                goal.created_at = datetime.now()
                session.add(goal)
                await session.commit()
                await session.refresh(goal)
                return goal
        except SQLAlchemyError as e:
            await session.rollback()
            raise SQLAlchemyError(f"Failed to create goal: {str(e)}")
            
    async def get_goal(self, goal_id: int) -> Optional[Goal]:
        """
        Retrieve a goal from the database.
        
        Args:
            goal_id (int): ID of the goal to retrieve
            
        Returns:
            Optional[Goal]: The goal object if found, None otherwise
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            async with AsyncSession(self._engine) as session:
                return (await session.exec(select(Goal).where(Goal.id == goal_id))).one_or_none()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Failed to retrieve goal: {str(e)}")
            
    async def get_all_goals(self) -> List[Goal]:
        """
        Retrieve all goals from the database.
        
        Returns:
            List[Goal]: List of all goal objects
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            async with AsyncSession(self._engine) as session:
                return list(await session.exec(select(Goal)))
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Failed to retrieve goals: {str(e)}")
            
    async def update_goal(self, goal_id: int, **kwargs) -> Optional[Goal]:
        """
        Update an existing goal in the database.
        
        Args:
            goal_id (int): ID of the goal to update
            **kwargs: Fields to update and their new values
            
        Returns:
            Optional[Goal]: Updated goal object if found, None otherwise
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            async with AsyncSession(self._engine) as session:
                goal = (await session.exec(select(Goal).where(Goal.id == goal_id))).one_or_none()
                
                if goal:
                    for key, value in kwargs.items():
                        if hasattr(goal, key):
                            setattr(goal, key, value)
                    await session.commit()
                    await session.refresh(goal)
                    return goal
                return None
        except SQLAlchemyError as e:
            await session.rollback()
            raise SQLAlchemyError(f"Failed to update goal: {str(e)}")
            
    async def delete_goal(self, goal_id: int) -> bool:
        """
        Delete a goal from the database.
        
        Args:
            goal_id (int): ID of the goal to delete
            
        Returns:
            bool: True if goal was deleted, False if not found
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            async with AsyncSession(self._engine) as session:
                goal = (await session.exec(select(Goal).where(Goal.id == goal_id))).one_or_none()
                
                if goal:
                    await session.delete(goal)
                    await session.commit()
                    return True
                return False
        except SQLAlchemyError as e:
            await session.rollback()

class TaskManager:
    def __init__(self):
        self.engine = get_engine()

    async def create_task(self, task: Task) -> Task:
        try:
            async with AsyncSession(self.engine) as session:
                session.add(task)
                await session.commit()
                await session.refresh(task)
                return task
        except SQLAlchemyError as e:
            await session.rollback()
            raise SQLAlchemyError(f"Failed to create task: {str(e)}")
        
    async def get_task(self, task_id: int) -> Task:
        try:
            async with AsyncSession(self.engine) as session:
                return (await session.exec(select(Task).where(Task.id == task_id))).one_or_none()
        except SQLAlchemyError as e:
            await session.rollback()
            raise SQLAlchemyError(f"Failed to get task: {str(e)}")
        
    async def get_all_tasks(self) -> List[Task]:
        try:
            async with AsyncSession(self.engine) as session:
                return list(await session.exec(select(Task)))
        except SQLAlchemyError as e:
            await session.rollback()
            raise SQLAlchemyError(f"Failed to get tasks: {str(e)}")
        
    async def update_task(self, task_id: int, **kwargs) -> Optional[Task]:
        try:
            async with AsyncSession(self.engine) as session:
                task = (await session.exec(select(Task).where(Task.id == task_id))).one()

            if task:
                for key, value in kwargs.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
                await session.commit()
                await session.refresh(task)
                return task
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Failed to update task: {str(e)}")
        
    async def delete_task(self, task_id: int) -> bool:
        try:
            async with AsyncSession(self.engine) as session:
                task = (await session.exec(select(Task).where(Task.id == task_id))).one()

            if task:
                session.delete(task)
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            await session.rollback()
            raise SQLAlchemyError(f"Failed to delete task: {str(e)}")