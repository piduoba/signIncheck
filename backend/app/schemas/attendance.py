from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..models.attendance import AttendanceStatus

# 教室模式
class ClassroomBase(BaseModel):
    name: str
    location: str
    room_number: str
    equipment_info: Optional[str] = None
    capacity: Optional[int] = None

class ClassroomCreate(ClassroomBase):
    pass

class ClassroomResponse(ClassroomBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# 课程模式
class CourseBase(BaseModel):
    name: str
    description: Optional[str] = None

class CourseCreate(CourseBase):
    teacher_id: int
    classroom_id: int

class CourseResponse(CourseBase):
    id: int
    teacher_id: int
    classroom_id: int
    classroom_name: str
    created_at: datetime

    class Config:
        from_attributes = True

# 签到场次模式
class AttendanceSessionBase(BaseModel):
    session_name: str
    daily_session_count: int = 1

class AttendanceSessionCreate(AttendanceSessionBase):
    course_id: int
    start_time: datetime
    end_time: Optional[datetime] = None

class AttendanceSessionResponse(AttendanceSessionBase):
    id: int
    course_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# 签名模式
class SignatureCreate(BaseModel):
    signature_data: str  # Base64编码的签名数据

class SignatureResponse(BaseModel):
    id: int
    student_id: int
    signature_data: str
    created_at: datetime

    class Config:
        from_attributes = True

# 签到记录模式
class AttendanceRecordCreate(BaseModel):
    student_id: int
    password: str
    signature_data: str
    status: AttendanceStatus = AttendanceStatus.PRESENT
    notes: Optional[str] = None

class AttendanceRecordResponse(BaseModel):
    id: int
    session_id: int
    student_id: int
    status: AttendanceStatus
    signin_time: datetime
    signature_id: Optional[int] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True

# 签到统计模式
class AttendanceStats(BaseModel):
    total_students: int
    present_count: int
    absent_count: int
    late_count: int
    early_leave_count: int
    attendance_rate: float