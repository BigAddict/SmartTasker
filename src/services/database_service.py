# Standard library imports
from datetime import datetime
from typing import Optional, List, Any, TypeVar, Generic, Callable, Coroutine
import logging

# Third-party imports
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, SQLModel
from sqlalchemy import exc

# Local application imports
from src.models.model import Goal, Task, TaskHistory, AISuggestion, TaskNotification, Feedback
from src.services.db_setup import get_engine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

T = TypeVar('T')

class DatabaseService:
    """
    A service class for interacting with the database.
    
    This class provides methods to create, retrieve, update, and delete items in the database.
    """

    def __init__(self, engine):
        """
        Initializes the DatabaseService with a database engine.

        Args:
            engine: The database engine to be used for database operations.
        """
        self.engine = engine

    async def _execute_with_session(self, func: Callable[[AsyncSession], Coroutine[Any, Any, T]], *args, **kwargs) -> Optional[T]:
        """
        Helper function to manage asynchronous sessions and transactions.

        Args:
            func (Callable[[AsyncSession], Coroutine[Any, Any, T]]): The function to execute within the session.
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.

        Returns:
            Optional[T]: The result of the function execution, or None if an error occurred.
        """
        async with AsyncSession(self.engine) as session:
            try:
                result = await func(session, *args, **kwargs)  # Pass session to the func
                return result
            except exc.IntegrityError as e:
                await session.rollback()
                logger.error(f"Integrity error: {e}")
                raise ValueError(f"Integrity error: {e}")  # Re-raise for controller handling
            except Exception as e:  # Catch generic exceptions
                await session.rollback()
                logger.error(f"An error occurred: {e}")
                raise  # Re-raise the exception

    async def create(self, item: SQLModel) -> Optional[SQLModel]:
        """
        Creates a new item in the database.

        Args:
            item (SQLModel): The item to be created.

        Returns:
            Optional[SQLModel]: The created item, or None if an error occurred.
        """
        async def _create_internal(session: AsyncSession, item: SQLModel) -> SQLModel:
            session.add(item)
            await session.commit()
            await session.refresh(item)
            return item
        return await self._execute_with_session(_create_internal, item)

    async def get(self, item: SQLModel, item_id: int) -> Optional[SQLModel]:
        """
        Retrieves an item by its ID.

        Args:
            item (SQLModel): The type of item to retrieve.
            item_id (int): The ID of the item to retrieve.

        Returns:
            Optional[SQLModel]: The retrieved item, or None if not found or an error occurred.
        """
        async def _get_internal(session: AsyncSession, item: SQLModel, item_id: int) -> Optional[SQLModel]:
            return await session.get(item, item_id)
        return await self._execute_with_session(_get_internal, item, item_id)
        
    async def get_all(self, item: SQLModel) -> List[Any]:
        """
        Retrieves all items of a specific type.

        Args:
            item (SQLModel): The type of items to retrieve.

        Returns:
            List[SQLModel]: A list of retrieved items, or an empty list if an error occurred.
        """
        async def _get_all_internal(session: AsyncSession, item: SQLModel) -> List[Any]: # Or a more specific type if known
            return (await session.exec(select(item))).all()
        return await self._execute_with_session(_get_all_internal, item)
        
    async def update(self, item: SQLModel, item_id: int, **kwargs) -> Optional[SQLModel]:
        """
        Updates an existing item.

        Args:
            item (SQLModel): The type of item to update.
            item_id (int): The ID of the item to update.
            **kwargs: The fields to update and their new values.

        Returns:
            Optional[SQLModel]: The updated item, or None if not found or an error occurred.
        """
        async def _update_internal(session: AsyncSession, item: SQLModel, item_id: int, **kwargs) -> Optional[SQLModel]:
            item = await session.get(item, item_id)
            if item:
                for key, value in kwargs.items():
                    if hasattr(item, key):
                        setattr(item, key, value)
                session.add(item)
                await session.commit()
                await session.refresh(item)
                return item
            return None
        return await self._execute_with_session(_update_internal, item, item_id, **kwargs)
        
    async def delete(self, item: SQLModel, item_id: int) -> bool:
        """
        Deletes an item by its ID.

        Args:
            item (SQLModel): The type of item to delete.
            item_id (int): The ID of the item to delete.

        Returns:
            bool: True if the item was deleted, False if not found or an error occurred.
        """
        async def _delete_internal(session: AsyncSession, item: SQLModel, item_id: int) -> bool:
            item = await session.get(item, item_id)
            if item:
                await session.delete(item)
                await session.commit()
                return True
            return False
        return await self._execute_with_session(_delete_internal, item, item_id)
