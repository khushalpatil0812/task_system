from datetime import datetime, date
from enum import Enum
from sqlalchemy import String, Text, DateTime, Date, ForeignKey, Enum as SqlEnum, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class Role(str, Enum): admin = "admin"; member = "member"
class TaskStatus(str, Enum): todo = "Todo"; in_progress = "In Progress"; completed = "Completed"
class Priority(str, Enum): low = "Low"; medium = "Medium"; high = "High"

project_members = Table("project_members", Base.metadata,
    Column("project_id", ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True))

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(SqlEnum(Role), default=Role.member)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    projects_created: Mapped[list["Project"]] = relationship(back_populates="creator", foreign_keys="Project.created_by")

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    creator: Mapped[User] = relationship(back_populates="projects_created", foreign_keys=[created_by])
    members: Mapped[list[User]] = relationship(secondary=project_members)
    tasks: Mapped[list["Task"]] = relationship(back_populates="project", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(SqlEnum(TaskStatus), default=TaskStatus.todo)
    priority: Mapped[Priority] = mapped_column(SqlEnum(Priority), default=Priority.medium)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    assigned_to: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    assignee: Mapped[User | None] = relationship(foreign_keys=[assigned_to])
    project: Mapped[Project] = relationship(back_populates="tasks")
