from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
import enum

class AttendanceStatus(enum.Enum):
    PRESENT = "present"      # 正常
    ABSENT = "absent"        # 缺勤
    LATE = "late"           # 迟到
    EARLY_LEAVE = "early_leave"  # 早退

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    teacher = relationship("User", foreign_keys=[teacher_id])
    classroom = relationship("Classroom")

class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    session_name = Column(String(100), nullable=False)  # 签到场次名称
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    daily_session_count = Column(Integer, default=1)  # 当日第几次签到
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    course = relationship("Course")
    attendance_records = relationship("AttendanceRecord", back_populates="session")

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("attendance_sessions.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(AttendanceStatus), nullable=False)
    signin_time = Column(DateTime(timezone=True), server_default=func.now())
    signature_id = Column(Integer, ForeignKey("signatures.id"), nullable=True)
    notes = Column(Text, nullable=True)
    
    # 关系
    session = relationship("AttendanceSession", back_populates="attendance_records")
    student = relationship("User", foreign_keys=[student_id])
    signature = relationship("Signature")

class Signature(Base):
    __tablename__ = "signatures"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    signature_data = Column(Text, nullable=False)  # Base64编码的签名数据
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    student = relationship("User")