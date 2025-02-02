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
        """Initialize the GoalManager with the database engine."""
        self._engine = get_engine()

    async def create_goal(self, goal: Goal) -> Goal:
        """
        Create a new goal in the database.

        :param goal: The goal object to create
        :type goal: Goal
        :return: The created goal object with updated ID and timestamps
        :rtype: Goal
        :raises SQLAlchemyError: If database operation fails
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

        :param goal_id: ID of the goal to retrieve
        :type goal_id: int
        :return: The goal object if found, None otherwise
        :rtype: Optional[Goal]
        :raises SQLAlchemyError: If database operation fails
        """
        try:
            async with AsyncSession(self._engine) as session:
                return await session.get(Goal, goal_id)
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Failed to retrieve goal: {str(e)}")
            
    async def get_all_goals(self) -> List[Goal]:
        """
        Retrieve all goals from the database.

        :return: List of all goal objects
        :rtype: List[Goal]
        :raises SQLAlchemyError: If database operation fails
        """
        try:
            async with AsyncSession(self._engine) as session:
                return list(await session.exec(select(Goal)))
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Failed to retrieve goals: {str(e)}")
            
    async def update_goal(self, goal_id: int, **kwargs) -> Optional[Goal]:
        """
        Update an existing goal in the database.

        :param goal_id: ID of the goal to update
        :type goal_id: int
        :param kwargs: Fields to update and their new values
        :return: Updated goal object if found, None otherwise
        :rtype: Optional[Goal]
        :raises SQLAlchemyError: If database operation fails
        """
        try:
            async with AsyncSession(self._engine) as session:
                goal = await session.get(Goal, goal_id)
                
                if goal:
                    for key, value in kwargs.items():
                        if hasattr(goal, key):
                            setattr(goal, key, value)
                    await session.commit()
                    await session.refresh(goal)
                    return goal
                return None
        except SQLAlchemyError as e:
            await session.rollback()  # Ensure rollback on error
            raise SQLAlchemyError(f"Failed to update goal: {str(e)}")
            
    async def delete_goal(self, goal_id: int) -> bool:
        """
        Delete a goal from the database.

        :param goal_id: ID of the goal to delete
        :type goal_id: int
        :return: True if goal was deleted, False if not found
        :rtype: bool
        :raises SQLAlchemyError: If database operation fails
        """
        try:
            async with AsyncSession(self._engine) as session:
                goal = await session.get(Goal, goal_id)
                
                if goal:
                    await session.delete(goal)
                    await session.commit()
                    return True
                return False
        except SQLAlchemyError as e:
            await session.rollback()  # Ensure rollback on error
            raise SQLAlchemyError(f"Failed to delete goal: {str(e)}")

class TaskManager:
    """Manages database operations for Task entities."""

    def __init__(self):
        """Initialize the TaskManager with the database engine."""
        self.engine = get_engine()

    async def create_task(self, task: Task) -> Task:
        """
        Create a new task in the database.

        :param task: The task object to create
        :type task: Task
        :return: The created task object with updated ID and timestamps
        :rtype: Task
        :raises SQLAlchemyError: If database operation fails
        """
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
        """
        Retrieve a task from the database.

        :param task_id: ID of the task to retrieve
        :type task_id: int
        :return: The task object if found, None otherwise
        :rtype: Optional[Task]
        :raises SQLAlchemyError: If database operation fails
        """
        try:
            async with AsyncSession(self.engine) as session:
                return await session.get(Task, task_id)
        except SQLAlchemyError as e:
            await session.rollback()
            raise SQLAlchemyError(f"Failed to get task: {str(e)}")
        
    async def get_all_tasks(self) -> List[Task]:
        """
        Retrieve all tasks from the database.

        :return: List of all task objects
        :rtype: List[Task]
        :raises SQLAlchemyError: If database operation fails
        """
        try:
            async with AsyncSession(self.engine) as session:
                return list(await session.exec(select(Task)))
        except SQLAlchemyError as e:
            await session.rollback()
            raise SQLAlchemyError(f"Failed to get tasks: {str(e)}")
        
    async def update_task(self, task_id: int, **kwargs) -> Optional[Task]:
        """
        Update an existing task in the database.

        :param task_id: ID of the task to update
        :type task_id: int
        :param kwargs: Fields to update and their new values
        :return: Updated task object if found, None otherwise
        :rtype: Optional[Task]
        :raises SQLAlchemyError: If database operation fails
        """
        try:
            async with AsyncSession(self.engine) as session:
                task = await session.get(Task, task_id)

                if task:
                    for key, value in kwargs.items():
                        if hasattr(task, key):
                            setattr(task, key, value)
                    await session.commit()
                    await session.refresh(task)
                    return task
        except SQLAlchemyError as e:
            await session.rollback()  # Ensure rollback on error
            raise SQLAlchemyError(f"Failed to update task: {str(e)}")
        
    async def delete_task(self, task_id: int) -> bool:
        """
        Delete a task from the database.

        :param task_id: ID of the task to delete
        :type task_id: int
        :return: True if task was deleted, False if not found
        :rtype: bool
        :raises SQLAlchemyError: If database operation fails
        """
        try:
            async with AsyncSession(self.engine) as session:
                task = await session.get(Task, task_id)

                if task:
                    await session.delete(task)
                    await session.commit()
                    return True
                return False
        except SQLAlchemyError as e:
            await session.rollback()  # Ensure rollback on error
            raise SQLAlchemyError(f"Failed to delete task: {str(e)}")
