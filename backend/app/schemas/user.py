from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..models.user import UserRole

# 用户基础模式
class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    phone: Optional[str] = None
    student_id: Optional[str] = None
    subject: Optional[str] = None
    address: Optional[str] = None
    role: UserRole
    is_active: bool = True

# 用户创建模式
class UserCreate(UserBase):
    password: str

# 用户更新模式
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    student_id: Optional[str] = None
    subject: Optional[str] = None
    address: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

# 用户响应模式
class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# 登录相关模式
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# 批量导入用户模式
class UserImport(BaseModel):
    users: list[UserCreate]

# 密码验证模式
class PasswordVerifyRequest(BaseModel):
    password: str

class PasswordVerifyResponse(BaseModel):
    is_valid: bool