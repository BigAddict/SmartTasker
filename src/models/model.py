from datetime import date, datetime, timedelta
from typing import Optional, Dict, List
from sqlmodel import Field, SQLModel, Relationship, JSON, Column
from pydantic import model_validator

class Goal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(..., min_length=1)
    description: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = Field(default=None, description="Status of the goal")
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    tasks: List["Task"] = Relationship(back_populates="goal")

    @model_validator(mode="before")
    def validate_goal(cls, data):
        name = data.get("name")
        if not name or len(name.strip()) == 0:
            raise ValueError("Goal name cannot be empty")

        status = data.get("status")
        valid_statuses = {"Not Started", "In Progress", "Completed", None}
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")

        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if start_date and end_date and start_date > end_date:
            raise ValueError("Start date cannot be after end date")
        return data


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    goal_id: Optional[int] = Field(default=None, foreign_key="goal.id")  # Foreign key is essential
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
    ai_suggestion: Optional["AISuggestion"] = Relationship(back_populates="task")
    task_notification: Optional["TaskNotification"] = Relationship(back_populates="task")
    task_history: List["TaskHistory"] = Relationship(back_populates="task")

    @model_validator(mode="before")
    def validate_task(cls, data):
        name = data.get("name")
        if not name or len(name.strip()) == 0:
            raise ValueError("Task name cannot be empty")

        status = data.get("status")
        valid_statuses = {"Not Started", "In Progress", "Completed", None}
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        return data

    @property
    def duration(self):
        if self.duration_seconds is not None:
            return timedelta(seconds=self.duration_seconds)
        return None

    @duration.setter
    def duration(self, value: Optional[timedelta]):
        self.duration_seconds = value.total_seconds() if value else None


class TaskHistory(SQLModel, table=True):  
    @model_validator(mode="before")  
    def validate_task_history(cls, task_history):  
        task = task_history.task  
        if task is None:  
            raise ValueError("Task cannot be None")  
        return task_history
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: Optional[int] = Field(default=None, foreign_key="task.id")  # Foreign key
    task: Task = Relationship(back_populates="task_history")
    change_type: str = Field()
    previous_state: Optional[Dict] = Field(default=None, sa_column=Column(JSON))
    new_state: Optional[Dict] = Field(default=None, sa_column=Column(JSON))
    created_at: Optional[datetime] = Field(default=None)


class AISuggestion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: Optional[int] = Field(default=None, foreign_key="task.id")  # Foreign key
    task: Optional[Task] = Relationship(back_populates="ai_suggestion")
    name: str = Field()
    content: str = Field()
    confidence: Optional[int] = Field(default=None)
    implemented: Optional[bool] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    feedback: Optional["Feedback"] = Relationship(back_populates="ai_suggestion")


class TaskNotification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: Optional[int] = Field(default=None, foreign_key="task.id")  # Foreign key
    task: Task = Relationship(back_populates="task_notification")
    name: str = Field()
    message: str = Field()
    sent_at: Optional[datetime] = Field(default=None)
    read_at: Optional[datetime] = Field(default=None)


class Feedback(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ai_suggestion_id: Optional[int] = Field(default=None, foreign_key="aisuggestion.id") # Foreign key
    ai_suggestion: AISuggestion = Relationship(back_populates="feedback")
    feedback_type: Optional[bool] = Field(default=None)
    comment: Optional[str] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)