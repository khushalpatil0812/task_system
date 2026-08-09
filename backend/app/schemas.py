from datetime import datetime, date
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from .models import Role, TaskStatus, Priority

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8)
    role: Role = Role.member
class Login(BaseModel): email: EmailStr; password: str
class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    email: EmailStr | None = None
    current_password: str | None = None
    new_password: str | None = Field(default=None, min_length=8)
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; name: str; email: EmailStr; role: Role; created_at: datetime
class Token(BaseModel): access_token: str; token_type: str = "bearer"; user: UserOut
class ProjectCreate(BaseModel): name: str = Field(min_length=2, max_length=150); description: str | None = None; member_ids: list[int] = []
class ProjectUpdate(ProjectCreate): pass
class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; name: str; description: str | None; created_by: int; created_at: datetime; members: list[UserOut] = []
class TaskCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200); description: str | None = None
    status: TaskStatus = TaskStatus.todo; priority: Priority = Priority.medium; due_date: date | None = None
    assigned_to: int | None = None; project_id: int
class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200); description: str | None = None
    status: TaskStatus | None = None; priority: Priority | None = None; due_date: date | None = None
    assigned_to: int | None = None; project_id: int | None = None
class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; title: str; description: str | None; status: TaskStatus; priority: Priority; due_date: date | None; assigned_to: int | None; project_id: int; created_at: datetime
    assignee: UserOut | None = None; project: ProjectOut | None = None
