from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    xp: Optional[int] = 0
    streak: Optional[int] = 0
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    name: str
    email: str

class LearningProfileResponse(BaseModel):
    learning_style: str
    learning_pace: int
    goals: Optional[str] = ""
    motivation_type: str
    completed_interview: bool
    
    class Config:
        from_attributes = True

class ProfileFullResponse(BaseModel):
    # User fields
    id: int
    email: str
    full_name: str
    created_at: datetime
    xp: Optional[int] = 0
    streak: Optional[int] = 0
    # Learning Profile fields
    learning_style: str
    learning_pace: int
    goals: Optional[str] = ""
    motivation_type: str
    completed_interview: bool
    
    class Config:
        from_attributes = True

class LearningProfileCreate(BaseModel):
    learning_style: str
    learning_pace: int
    goals: Optional[str] = ""
    motivation_type: str

class LearningProfileUpdate(BaseModel):
    learning_style: Optional[str] = None
    learning_pace: Optional[int] = None
    goals: Optional[str] = None
    motivation_type: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    goal_id: Optional[int] = None
    priority: int = 3
    deadline: Optional[datetime] = None
    parent_id: Optional[int] = None
    task_type: Optional[str] = "task"

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    goal_id: Optional[int] = None
    priority: Optional[int] = None
    deadline: Optional[datetime] = None
    status: Optional[str] = None
    parent_id: Optional[int] = None
    task_type: Optional[str] = None

class TaskResponse(TaskCreate):
    id: int
    user_id: int
    status: str
    created_at: datetime
    parent_id: Optional[int] = None
    task_type: Optional[str] = "task"
    
    class Config:
        from_attributes = True

class GoalCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: int = 3
    deadline: Optional[datetime] = None

class GoalResponse(GoalCreate):
    id: int
    user_id: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
