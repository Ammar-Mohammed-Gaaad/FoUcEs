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

class LearningProfileCreate(BaseModel):
    learning_style: str
    learning_pace: int
    goals: Optional[str] = ""
    motivation_type: str

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    goal_id: Optional[int] = None
    priority: int = 3
    deadline: Optional[datetime] = None

class TaskResponse(TaskCreate):
    id: int
    user_id: int
    status: str
    created_at: datetime
    
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
