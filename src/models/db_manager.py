# Standard library imports
from datetime import datetime
from typing import Optional, List, TypeVar, Generic
import logging

# Third-party imports
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

# Local application imports
from src.models.model import Goal, Task, TaskHistory, AISuggestion, TaskNotification, Feedback
from src.services.db_setup import get_engine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

T = TypeVar('T')

class BaseManager(Generic[T]):
    """Base class for managing database operations."""

    def __init__(self, engine):
        """Initialize the BaseManager with the database engine."""
        self._engine = engine

    async def create(self, item: T) -> T:  
        """Create a new item in the database."""
        try:
            async with AsyncSession(self._engine) as session:
                item.created_at = datetime.now()
                session.add(item)
                await session.commit()
                await session.refresh(item)
                return item
        except IntegrityError as e:
            await session.rollback()
            raise ValueError(f"Integrity error: {e}")
        except SQLAlchemyError as e:
            await session.rollback()
            raise SQLAlchemyError(f"Failed to create item: {str(e)}")

    async def get(self, item_id: int, model: T) -> Optional[T]:
        """Retrieve an item from the database."""
        try:
            async with AsyncSession(self._engine) as session:
                return await session.get(model, item_id)
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Failed to retrieve item: {str(e)}")

    async def get_all(self, model: T) -> List[T]:
        """Retrieve all items from the database."""
        try:
            async with AsyncSession(self._engine) as session:
                return list(await session.exec(select(model)))
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Failed to retrieve items: {str(e)}")

    async def update(self, item_id: int, model: T, **kwargs) -> Optional[T]:
        """Update an existing item in the database."""
        try:
            async with AsyncSession(self._engine) as session:
                item = await session.get(model, item_id)

                if item:
                    for key, value in kwargs.items():
                        if hasattr(item, key):
                            setattr(item, key, value)
                    session.add(item)
                    await session.commit()
                    await session.refresh(item)
                    return item
                return None
        except SQLAlchemyError as e:
            await session.rollback()
            raise SQLAlchemyError(f"Failed to update item: {str(e)}")

    async def delete(self, item_id: int, model: T) -> bool:
        """Delete an item from the database."""
        try:
            async with AsyncSession(self._engine) as session:
                item = await session.get(model, item_id)

                if item:
                    await session.delete(item)
                    await session.commit()
                    return True
                return False
        except SQLAlchemyError as e:
            await session.rollback()
            raise SQLAlchemyError(f"Failed to delete item: {str(e)}")

class GoalManager(BaseManager[Goal]):
    """Manages database operations for Goal entities."""

    def __init__(self):
        super().__init__(get_engine())
    
    async def create_goal(self, goal: Goal) -> Goal:
        return await self.create(goal)
        
    async def get_goal(self, goal_id: int) -> Optional[Goal]:
        return await self.get(goal_id, Goal)
        
    async def get_all_goals(self) -> List[Goal]:
        return await self.get_all(Goal)
        
    async def update_goal(self, goal_id: int, **kwargs) -> Optional[Goal]:
        return await self.update(goal_id, Goal, **kwargs)
        
    async def delete_goal(self, goal_id: int) -> bool:
        return await self.delete(goal_id, Goal)

class TaskManager(BaseManager[Task]):
    """Manages database operations for Task entities."""
    
    def __init__(self):
        super().__init__(get_engine())

    async def create_task(self, task: Task) -> Task:
        return await self.create(task)
        
    async def get_task(self, task_id: int) -> Optional[Task]:
        return await self.get(task_id, Task)
        
    async def get_all_tasks(self) -> List[Task]:
        return await self.get_all(Task)
        
    async def update_task(self, task_id: int, **kwargs) -> Optional[Task]:
        return await self.update(task_id, Task, **kwargs)
        
    async def delete_task(self, task_id: int) -> bool:
        return await self.delete(task_id, Task)
    
class TaskHistoryManager(BaseManager[TaskHistory]):
    """Manages database operations for TaskHistory entities."""

    def __init__(self):
        super().__init__(get_engine())

    async def create_task_history(self, task_history: TaskHistory) -> TaskHistory:
        return await self.create(task_history)
    
    async def get_task_history(self, task_history_id: int) -> Optional[TaskHistory]:
        return await self.get(task_history_id, TaskHistory)
    
    async def get_all_task_histories(self) -> List[TaskHistory]:
        return await self.get_all(TaskHistory)
    
    async def update_task_history(self, task_history_id: int, **kwargs) -> Optional[TaskHistory]:
        return await self.update(task_history_id, TaskHistory, **kwargs)
    
    async def delete_task_history(self, task_history_id: int) -> bool:
        return await self.delete(task_history_id, TaskHistory)
    
class AISuggestionManager(BaseManager[AISuggestion]):
    """Manages database operations for AISuggestion entities."""

    def __init__(self):
        super().__init__(get_engine())

    async def create_AIsuggestion(self, AIsuggestion: AISuggestion) -> AISuggestion:
        return await self.create(AIsuggestion)
    
    async def get_AIsuggestion(self, AIsuggestion_id: int) -> Optional[AISuggestion]:
        return await self.get(AIsuggestion_id, AISuggestion)
    
    async def get_all_AIsuggestions(self) -> List[AISuggestion]:
        return await self.get_all(AISuggestion)
    
    async def update_AIsuggestion(self, AIsuggestion_id: int, **kwargs) -> Optional[AISuggestion]:
        return await self.update(AIsuggestion_id, AISuggestion, **kwargs)
    
    async def delete_AIsuggestion(self, AIsuggestion_id: int) -> bool:
        return await self.delete(AIsuggestion_id, AISuggestion)
    
class TaskNotificationManager(BaseManager[TaskNotification]):
    """Manages database operations for TaskNotification entities."""

    def __init__(self):
        super().__init__(get_engine())

    async def create_task_notification(self, task_notification: TaskNotification) -> TaskNotification:
        return await self.create(task_notification)
    
    async def get_task_notification(self, task_notification_id: int) -> Optional[TaskNotification]:
        return await self.get(task_notification_id, TaskNotification)
    
    async def get_all_task_notifications(self) -> List[TaskNotification]:
        return await self.get_all(TaskNotification)
    
    async def update_task_notification(self, task_notification_id: int, **kwargs) -> Optional[TaskNotification]:
        return await self.update(task_notification_id, TaskNotification, **kwargs)
    
    async def delete_task_notfication(self, task_notification_id: int) -> bool:
        return await self.delete(task_notification_id, TaskNotification)
    
class FeedbackManager(BaseManager[Feedback]):
    """Manages database operations for Feedback entities."""

    def __init__(self):
        super().__init__(get_engine())

    async def create_feedback(self, feedback: Feedback) -> Feedback:
        return await self.create(feedback)
    
    async def get_feedback(self, feedback_id: int) -> Optional[Feedback]:
        return await self.get(feedback_id, Feedback)
    
    async def get_all_feedbacks(self) -> List[Feedback]:
        return await self.get_all(Feedback)
    
    async def update_feedback(self, feedback_id: int, **kwargs) -> Optional[Feedback]:
        return await self.update(feedback_id, Feedback, **kwargs)
    
    async def delete_feedback(self, feedback_id: int) -> bool:
        return await self.delete(feedback_id, Feedback)