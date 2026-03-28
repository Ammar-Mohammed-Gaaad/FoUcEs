from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    job_title = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    learning_profile = relationship("LearningProfile", back_populates="user", uselist=False)
    tasks = relationship("Task", back_populates="user")
    goals = relationship("Goal", back_populates="user")

class LearningProfile(Base):
    __tablename__ = "learning_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    learning_style = Column(String, default="visual")
    learning_pace = Column(Integer, default=3)
    goals = Column(Text)
    motivation_type = Column(String, default="achievement")
    completed_interview = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="learning_profile")

class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    description = Column(Text)
    status = Column(String, default="active")
    priority = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.utcnow)
    deadline = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="goals")
    tasks = relationship("Task", back_populates="goal")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    status = Column(String, default="to_do") # to_do, in_progress, completed
    priority = Column(Integer, default=3)
    
    # الجديدة
    parent_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    task_type = Column(String, default="task") # task, fork, parallel
    deadline = Column(DateTime, nullable=True)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # العلاقات
    user = relationship("User", back_populates="tasks")
    goal = relationship("Goal", back_populates="tasks")
    children = relationship("Task", backref="parent", remote_side=[id])

class FocusSession(Base):
    __tablename__ = "focus_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    duration_minutes = Column(Integer)
    focus_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
