from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, date

from ..core.database import get_db
from ..core.deps import get_current_user, get_teacher_user, get_admin_user
from ..core.security import verify_password
from ..models import (
    User, Classroom, Course, AttendanceSession, 
    AttendanceRecord, Signature, AttendanceStatus, UserRole
)
from ..schemas.attendance import (
    ClassroomCreate, ClassroomResponse,
    CourseCreate, CourseResponse,
    AttendanceSessionCreate, AttendanceSessionResponse,
    AttendanceRecordCreate, AttendanceRecordResponse,
    SignatureCreate, SignatureResponse,
    AttendanceStats
)

router = APIRouter(prefix="/attendance", tags=["签到管理"])

# 教室管理
@router.post("/classrooms", response_model=ClassroomResponse)
async def create_classroom(
    classroom_data: ClassroomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """创建教室（仅管理员）"""
    db_classroom = Classroom(**classroom_data.dict())
    db.add(db_classroom)
    db.commit()
    db.refresh(db_classroom)
    return ClassroomResponse.from_orm(db_classroom)

@router.get("/classrooms", response_model=List[ClassroomResponse])
async def get_classrooms(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取教室列表"""
    classrooms = db.query(Classroom).filter(
        Classroom.is_active == True
    ).offset(skip).limit(limit).all()
    return [ClassroomResponse.from_orm(classroom) for classroom in classrooms]

@router.delete("/classrooms/{classroom_id}")
async def delete_classroom(
    classroom_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """删除教室（仅管理员）"""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="教室不存在"
        )
    
    classroom.is_active = False
    db.commit()
    return {"message": "教室删除成功"}

# 课程管理
@router.post("/courses", response_model=CourseResponse)
async def create_course(
    course_data: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """创建课程（仅管理员）"""
    # 验证老师是否存在且角色正确
    teacher = db.query(User).filter(
        User.id == course_data.teacher_id,
        User.role == UserRole.TEACHER
    ).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定的老师不存在"
        )
    
    # 验证教室是否存在
    classroom = db.query(Classroom).filter(Classroom.id == course_data.classroom_id).first()
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定的教室不存在"
        )
    
    db_course = Course(**course_data.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    
    # 手动构建CourseResponse对象，包含classroom_name
    course_data = db_course.__dict__.copy()
    course_data["classroom_name"] = classroom.name
    return CourseResponse(**course_data)

@router.get("/courses", response_model=List[CourseResponse])
async def get_courses(
    teacher_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取课程列表"""
    query = db.query(Course).join(Classroom)
    
    # 如果是老师，只能看自己的课程
    if current_user.role == UserRole.TEACHER:
        query = query.filter(Course.teacher_id == current_user.id)
    elif teacher_id:  # 管理员可以筛选指定老师的课程
        query = query.filter(Course.teacher_id == teacher_id)
    
    courses = query.all()
    
    # 手动构建CourseResponse对象，包含classroom_name
    course_responses = []
    for course in courses:
        course_data = course.__dict__.copy()
        course_data["classroom_name"] = course.classroom.name
        course_responses.append(CourseResponse(**course_data))
    
    return course_responses

# 签到场次管理
@router.post("/sessions", response_model=AttendanceSessionResponse)
async def create_attendance_session(
    session_data: AttendanceSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """创建签到场次（老师和管理员）"""
    # 验证课程是否存在且老师有权限
    course = db.query(Course).filter(Course.id == session_data.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    
    if current_user.role == UserRole.TEACHER and course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能为自己的课程创建签到场次"
        )
    
    db_session = AttendanceSession(**session_data.dict())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return AttendanceSessionResponse.from_orm(db_session)

@router.get("/sessions", response_model=List[AttendanceSessionResponse])
async def get_attendance_sessions(
    course_id: Optional[int] = None,
    date_filter: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取签到场次列表"""
    query = db.query(AttendanceSession)
    
    if course_id:
        query = query.filter(AttendanceSession.course_id == course_id)
    
    if date_filter:
        query = query.filter(func.date(AttendanceSession.start_time) == date_filter)
    
    # 如果是老师，只能看自己课程的签到场次
    if current_user.role == UserRole.TEACHER:
        query = query.join(Course).filter(Course.teacher_id == current_user.id)
    
    sessions = query.order_by(AttendanceSession.start_time.desc()).all()
    return [AttendanceSessionResponse.from_orm(session) for session in sessions]

@router.put("/sessions/{session_id}/close")
async def close_attendance_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """关闭签到场次"""
    session = db.query(AttendanceSession).filter(AttendanceSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="签到场次不存在"
        )
    
    # 验证权限
    if current_user.role == UserRole.TEACHER:
        course = db.query(Course).filter(Course.id == session.course_id).first()
        if course.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能关闭自己课程的签到场次"
            )
    
    session.is_active = False
    session.end_time = datetime.utcnow()
    db.commit()
    
    return {"message": "签到场次已关闭"}

# 按课程直接签到（现场签到）
@router.post("/courses/{course_id}/signin", response_model=AttendanceRecordResponse)
async def course_signin(
    course_id: int,
    signin_data: AttendanceRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """按课程直接签到（现场签到功能）"""
    # 验证课程是否存在
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    
    # 验证老师权限
    if current_user.role == UserRole.TEACHER and course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能为自己的课程进行现场签到"
        )
    
    # 验证学生信息
    student = db.query(User).filter(
        User.id == signin_data.student_id,
        User.role == UserRole.STUDENT
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学生信息不存在"
        )
    
    # 验证学生密码
    if not verify_password(signin_data.password, student.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="密码错误"
        )
    
    # 创建或获取当天的签到场次
    today = datetime.utcnow().date()
    session = db.query(AttendanceSession).filter(
        AttendanceSession.course_id == course_id,
        func.date(AttendanceSession.start_time) == today
    ).first()
    
    if not session:
        # 创建新的签到场次
        session_data = AttendanceSessionCreate(
            session_name=f"{course.name} {today} 签到",
            course_id=course_id,
            start_time=datetime.utcnow(),
            end_time=None,
            is_active=True
        )
        session = AttendanceSession(**session_data.dict())
        db.add(session)
        db.flush()
    
    # 检查是否已经签到
    existing_record = db.query(AttendanceRecord).filter(
        AttendanceRecord.session_id == session.id,
        AttendanceRecord.student_id == signin_data.student_id
    ).first()
    
    if existing_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已经签到过了"
        )
    
    # 保存签名
    signature = Signature(
        student_id=signin_data.student_id,
        signature_data=signin_data.signature_data
    )
    db.add(signature)
    db.flush()  # 获取signature的id
    
    # 创建签到记录
    attendance_record = AttendanceRecord(
        session_id=session.id,
        student_id=signin_data.student_id,
        status=signin_data.status,
        signature_id=signature.id,
        notes=signin_data.notes
    )
    
    db.add(attendance_record)
    db.commit()
    db.refresh(attendance_record)
    
    return AttendanceRecordResponse.from_orm(attendance_record)

# 学生签到
@router.post("/signin/{session_id}", response_model=AttendanceRecordResponse)
async def student_signin(
    session_id: int,
    signin_data: AttendanceRecordCreate,
    db: Session = Depends(get_db)
):
    """学生签到"""
    # 验证签到场次是否存在且激活
    session = db.query(AttendanceSession).filter(
        AttendanceSession.id == session_id,
        AttendanceSession.is_active == True
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="签到场次不存在或已关闭"
        )
    
    # 验证学生信息
    student = db.query(User).filter(
        User.id == signin_data.student_id,
        User.role == UserRole.STUDENT
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学生信息不存在"
        )
    
    # 验证学生密码
    if not verify_password(signin_data.password, student.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="密码错误"
        )
    
    # 检查是否已经签到
    existing_record = db.query(AttendanceRecord).filter(
        AttendanceRecord.session_id == session_id,
        AttendanceRecord.student_id == signin_data.student_id
    ).first()
    
    if existing_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已经签到过了"
        )
    
    # 保存签名
    signature = Signature(
        student_id=signin_data.student_id,
        signature_data=signin_data.signature_data
    )
    db.add(signature)
    db.flush()  # 获取signature的id
    
    # 创建签到记录
    attendance_record = AttendanceRecord(
        session_id=session_id,
        student_id=signin_data.student_id,
        status=signin_data.status,
        signature_id=signature.id,
        notes=signin_data.notes
    )
    
    db.add(attendance_record)
    db.commit()
    db.refresh(attendance_record)
    
    return AttendanceRecordResponse.from_orm(attendance_record)

# 获取签到记录
@router.get("/records/{session_id}", response_model=List[AttendanceRecordResponse])
async def get_attendance_records(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取签到记录"""
    # 验证权限
    session = db.query(AttendanceSession).filter(AttendanceSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="签到场次不存在"
        )
    
    if current_user.role == UserRole.TEACHER:
        course = db.query(Course).filter(Course.id == session.course_id).first()
        if course.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
    
    records = db.query(AttendanceRecord).filter(
        AttendanceRecord.session_id == session_id
    ).all()
    
    return [AttendanceRecordResponse.from_orm(record) for record in records]

# 获取签到统计
@router.get("/stats/{session_id}", response_model=AttendanceStats)
async def get_attendance_stats(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取签到统计"""
    # 验证权限（同上）
    session = db.query(AttendanceSession).filter(AttendanceSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="签到场次不存在"
        )
    
    if current_user.role == UserRole.TEACHER:
        course = db.query(Course).filter(Course.id == session.course_id).first()
        if course.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
    
    # 统计各状态的人数
    stats = db.query(
        AttendanceRecord.status,
        func.count(AttendanceRecord.id).label('count')
    ).filter(
        AttendanceRecord.session_id == session_id
    ).group_by(AttendanceRecord.status).all()
    
    # 获取总学生数（这里简化为已签到的学生数，实际应该根据课程获取应到学生数）
    total_students = db.query(User).filter(User.role == UserRole.STUDENT).count()
    
    present_count = next((s.count for s in stats if s.status == AttendanceStatus.PRESENT), 0)
    absent_count = next((s.count for s in stats if s.status == AttendanceStatus.ABSENT), 0)
    late_count = next((s.count for s in stats if s.status == AttendanceStatus.LATE), 0)
    early_leave_count = next((s.count for s in stats if s.status == AttendanceStatus.EARLY_LEAVE), 0)
    
    signed_count = present_count + late_count + early_leave_count
    attendance_rate = (signed_count / total_students * 100) if total_students > 0 else 0
    
    return AttendanceStats(
        total_students=total_students,
        present_count=present_count,
        absent_count=total_students - signed_count,  # 未签到的算作缺勤
        late_count=late_count,
        early_leave_count=early_leave_count,
        attendance_rate=round(attendance_rate, 2)
    )