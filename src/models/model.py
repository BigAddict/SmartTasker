from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey, DateTime, 
    JSON, Float, Interval, Date, Index, select
)
from datetime import datetime, timedelta
from sqlalchemy import TypeDecorator
import asyncio
import json

# Use the same Base for declarative models
Base = declarative_base()

# Custom JSON Encoder and Type Decorator
class CustomJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder to handle datetime and timedelta objects.
    """
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()  # Convert datetime to ISO format string
        if isinstance(obj, timedelta):
            return str(obj)  # Convert timedelta to string
        return super().default(obj)

class CustomJSON(TypeDecorator):
    """
    Custom JSON type decorator to use the custom JSON encoder.
    """
    impl = JSON

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value, cls=CustomJSONEncoder)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return value

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String, default="")
    priority = Column(Integer, default=2)  # 1-4 (Eisenhower Matrix)
    status = Column(String, default='pending')  # pending, in_progress, completed
    due_date = Column(Date)  # Final deadline
    start_time = Column(DateTime)  # When to start working on it
    duration = Column(Interval)  # Estimated time required
    is_time_fixed = Column(Boolean, default=False)  # Must happen at exact time
    recurrence = Column(String)  # Daily/weekly/monthly patterns
    ai_generated = Column(Boolean, default=False)  # AI-created task
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    parent_id = Column(Integer, ForeignKey('tasks.id'))
    
    # Relationships
    children = relationship("Task", back_populates="parent", remote_side=[id])
    parent = relationship("Task", back_populates="children", remote_side=[parent_id])
    history = relationship("TaskHistory", back_populates="task", cascade="all, delete")
    time_blocks = relationship("TimeBlock", back_populates="task")
    ai_suggestions = relationship("AISuggestion", back_populates="task")
    
    __table_args__ = (
        Index('ix_task_due_date', 'due_date'),
        Index('ix_task_start_time', 'start_time'),
    )

class TimeBlock(Base):
    """Actual time spent on tasks"""
    __tablename__ = "time_blocks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime)
    actual_duration = Column(Interval)
    productivity_score = Column(Float)  # 0-1 scale
    
    task = relationship("Task", back_populates="time_blocks")

class AISuggestion(Base):
    __tablename__ = "ai_suggestions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    suggestion_type = Column(String)  # schedule, priority, dependency
    content = Column(JSON, nullable=False)
    confidence = Column(Float)
    implemented = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    task = relationship("Task", back_populates="ai_suggestions")

class Memory(Base):
    __tablename__ = "memories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    memory_type = Column(String)  # schedule_change, user_preference, etc.
    content = Column(JSON, nullable=False)
    relevance_score = Column(Float)
    last_accessed = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class ClarificationRequest(Base):
    __tablename__ = "clarification_requests"
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    question = Column(String, nullable=False)
    context = Column(JSON)  # Related task/data snapshot
    status = Column(String, default='pending')  # pending, resolved
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)

    task = relationship("Task")

class TaskHistory(Base):
    __tablename__ = "task_history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    change_type = Column(String, nullable=False)  # status_change, reschedule, etc.
    previous_state = Column(CustomJSON)  # Use custom JSON type
    new_state = Column(CustomJSON)  # Use custom JSON type
    timestamp = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="history")

class Database:
    def __init__(self, db_url="sqlite+aiosqlite:///data.sqlite"):
        # Use create_async_engine for asynchronous database operations
        self.engine = create_async_engine(db_url, echo=False)
        # Use async_sessionmaker for creating async sessions
        self.Session = sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def _create_tables(self):
        # Use async connection to create tables
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    def get_session(self):
        # Return the sessionmaker object
        return self.Session()

# Example Use case
if __name__ == "__main__":
    import asyncio

    async def main():
        db = Database()  # Tables are automatically created during initialization
        await db._create_tables()

        # Use the sessionmaker to create a session
        async with db.get_session() as session:
            # Example: Add a new task
            new_task = Task(title="Learn Async SQLAlchemy", description="Study async database operations")
            session.add(new_task)
            await session.commit()

            # Example: Query tasks
            result = await session.execute(select(Task).where(Task.title == "Learn Async SQLAlchemy"))
            task = result.scalars().first()
            print(f"Task found: {task.title}")

    asyncio.run(main())
