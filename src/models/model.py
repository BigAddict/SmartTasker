# Standard library imports
from datetime import date, datetime, timedelta
from typing import Optional, Dict, List

# Third-party imports
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import JSON, Column
from pydantic import model_validator

class Goal(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(..., min_length=1)
    description: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = Field(
        default=None,
        description="Status of the goal (Not Started, In Progress, Completed, etc.)"
    )
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    tasks: List["Task"] = Relationship(back_populates="goal")

    def __init__(self, **data):
        super().__init__(**data)
        self._validate()
    
    def _validate(self):
        """Validate goal data."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Goal name cannot be empty")
            
        valid_statuses = {"Not Started", "In Progress", "Completed", None}
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
            
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("Start date cannot be after end date")


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    goal_id: Optional[int] = Field(default=None, foreign_key="goal.id")
    goal: Optional[Goal] = Relationship(back_populates="tasks")
    name: str
    description: str
    priority: Optional[int] = Field(default=3)
    status: Optional[str] = Field(default="In Progress")
    due_date: Optional[datetime] = Field(default=None)
    suggested_start_time: Optional[datetime] = Field(default=None)
    start_date: Optional[datetime] = Field(default=None)
    duration_seconds: Optional[int] = Field(default=None)
    is_time_fixed: Optional[bool] = Field(default=False)
    reccurence: Optional[str] = Field(default=None)
    ai_generated: Optional[bool] = Field(default=False)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    time_block: Optional["TimeBlock"] = Relationship(back_populates="task")
    ai_suggestion: Optional["AISuggestion"] = Relationship(back_populates="task")
    task_notification: Optional["TaskNotification"] = Relationship(back_populates="task")
    task_history: List["TaskHistory"] = Relationship(back_populates="task")

    def __init__(self, **data):
        super().__init__(**data)
        self._validate()
    
    def _validate(self):
        """Validate goal data."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Goal name cannot be empty")
            
        valid_statuses = {"Not Started", "In Progress", "Completed", None}
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")

    @property
    def duration(self):
        if self.duration_seconds is not None:
            return timedelta(seconds=self.duration_seconds)
        return None

    @duration.setter
    def duration(self, value: Optional[timedelta]):
        self.duration_seconds = value.total_seconds() if value else None


class TimeBlock(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    task: Task = Relationship(back_populates="time_block")
    start: Optional[datetime] = Field(default=None)
    end: Optional[datetime] = Field(default=None)
    actual_duration_seconds: Optional[int] = Field(default=None)
    productive_score: Optional[float] = Field(default=None)

    @property
    def actual_duration(self):
        if self.actual_duration_seconds is not None:
            return timedelta(seconds=self.actual_duration_seconds)
        return None

    @actual_duration.setter
    def actual_duration(self, value: Optional[timedelta]):
        self.actual_duration_seconds = value.total_seconds() if value else None


class TaskHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: Optional[int] = Field(default=None, foreign_key="task.id")
    task: Optional[Task] = Relationship(back_populates="task_history")
    change_type: str = Field()
    previous_state: Optional[str] = Field(default=None, sa_column=Column(JSON))
    new_state: Optional[str] = Field(default=None, sa_column=Column(JSON))
    timestamp: datetime = Field()


class AISuggestion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: Optional[int] = Field(default=None, foreign_key="task.id")
    task: Optional[Task] = Relationship(back_populates="ai_suggestion")
    name: str = Field()
    content: str = Field()
    confidence: Optional[int] = Field(default=None)
    implemented: Optional[bool] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    feedback: Optional["Feedback"] = Relationship(back_populates="ai_suggestion")


class TaskNotification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    task: Task = Relationship(back_populates="task_notification")
    name: str = Field()
    message: str = Field()
    sent_at: Optional[datetime] = Field(default=None)
    read_at: Optional[datetime] = Field(default=None)


class Feedback(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ai_suggestion_id: int = Field(foreign_key="aisuggestion.id")
    ai_suggestion: AISuggestion = Relationship(back_populates="feedback")
    feedback_type: Optional[bool] = Field(default=None)
    comment: Optional[str] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
