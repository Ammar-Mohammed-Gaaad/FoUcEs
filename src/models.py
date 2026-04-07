from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String, nullable=True)  # nullable for OAuth-only users
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    xp = Column(Integer, default=0)
    streak = Column(Integer, default=0)
    oauth_provider = Column(String, nullable=True)   # 'google','github','facebook','linkedin'
    oauth_id = Column(String, nullable=True)          # provider's user ID

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
    title = Column(String)
    description = Column(Text)
    status = Column(String, default="to_do")
    priority = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.utcnow)
    deadline = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="tasks")
    goal = relationship("Goal", back_populates="tasks")

class FocusSession(Base):
    __tablename__ = "focus_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    duration_minutes = Column(Integer)
    focus_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Reminder(Base):
    __tablename__ = "reminders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    title = Column(String)                              # custom message shown in notification
    remind_at = Column(DateTime)                        # when to fire
    repeat = Column(String, default="none")             # none | daily | weekly
    is_active = Column(Boolean, default=True)
    snoozed_until = Column(DateTime, nullable=True)     # non-null when snoozed
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="reminders")
    task = relationship("Task", backref="reminders")
