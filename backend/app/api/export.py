from fastapi import APIRouter, Depends, Response, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional, List
from datetime import datetime, date
import pandas as pd
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfutils
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from ..core.database import get_db
from ..core.deps import get_admin_user, get_teacher_user
from ..models import (
    User, AttendanceSession, AttendanceRecord, 
    Course, Classroom, AttendanceStatus, UserRole
)

router = APIRouter(prefix="/export", tags=["数据导出"])

@router.get("/users/excel")
async def export_users_excel(
    role: Optional[str] = Query(None, description="用户角色筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """导出用户数据为Excel"""
    try:
        # 查询用户数据
        query = db.query(User)
        if role:
            query = query.filter(User.role == role)
        
        users = query.all()
        
        # 准备数据
        data = []
        for user in users:
            data.append({
                'ID': user.id,
                '用户名': user.username,
                '真实姓名': user.full_name,
                '邮箱': user.email,
                '角色': get_role_text(user.role),
                '学号': user.student_id or '',
                '联系电话': user.phone or '',
                '学科': user.subject or '',
                '地址': user.address or '',
                '状态': '启用' if user.is_active else '禁用',
                '创建时间': user.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # 创建DataFrame
        df = pd.DataFrame(data)
        
        # 创建Excel文件
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='用户列表', index=False)
        
        output.seek(0)
        
        # 返回文件
        filename = f"用户列表_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            io.BytesIO(output.read()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")

@router.get("/attendance/excel")
async def export_attendance_excel(
    session_id: Optional[int] = Query(None, description="签到场次ID"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    course_id: Optional[int] = Query(None, description="课程ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """导出签到记录为Excel"""
    try:
        # 构建查询
        query = db.query(
            AttendanceRecord,
            User.full_name,
            User.student_id,
            AttendanceSession.session_name,
            Course.name.label('course_name'),
            Classroom.name.label('classroom_name')
        ).join(
            User, AttendanceRecord.student_id == User.id
        ).join(
            AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id
        ).join(
            Course, AttendanceSession.course_id == Course.id
        ).join(
            Classroom, Course.classroom_id == Classroom.id
        )
        
        # 权限控制：老师只能导出自己的课程数据
        if current_user.role == UserRole.TEACHER:
            query = query.filter(Course.teacher_id == current_user.id)
        
        # 应用筛选条件
        if session_id:
            query = query.filter(AttendanceRecord.session_id == session_id)
        
        if course_id:
            query = query.filter(Course.id == course_id)
            
        if start_date:
            query = query.filter(func.date(AttendanceRecord.signin_time) >= start_date)
            
        if end_date:
            query = query.filter(func.date(AttendanceRecord.signin_time) <= end_date)
        
        records = query.all()
        
        # 准备数据
        data = []
        for record, student_name, student_id, session_name, course_name, classroom_name in records:
            data.append({
                '学生姓名': student_name,
                '学号': student_id or '',
                '课程名称': course_name,
                '签到场次': session_name,
                '教室': classroom_name,
                '签到状态': get_status_text(record.status),
                '签到时间': record.signin_time.strftime('%Y-%m-%d %H:%M:%S'),
                '备注': record.notes or ''
            })
        
        # 创建DataFrame
        df = pd.DataFrame(data)
        
        # 创建Excel文件
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='签到记录', index=False)
        
        output.seek(0)
        
        # 返回文件
        filename = f"签到记录_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            io.BytesIO(output.read()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")

@router.get("/attendance/pdf")
async def export_attendance_pdf(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """导出签到记录为PDF报告"""
    try:
        # 获取签到场次信息
        session = db.query(AttendanceSession).filter(
            AttendanceSession.id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="签到场次不存在")
        
        # 获取课程和教室信息
        course = db.query(Course).filter(Course.id == session.course_id).first()
        classroom = db.query(Classroom).filter(Classroom.id == course.classroom_id).first()
        teacher = db.query(User).filter(User.id == course.teacher_id).first()
        
        # 权限检查
        if current_user.role == UserRole.TEACHER and course.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="权限不足")
        
        # 获取签到记录
        records = db.query(
            AttendanceRecord,
            User.full_name,
            User.student_id
        ).join(
            User, AttendanceRecord.student_id == User.id
        ).filter(
            AttendanceRecord.session_id == session_id
        ).order_by(User.full_name).all()
        
        # 统计数据
        total_count = len(records)
        present_count = sum(1 for r, _, _ in records if r.status == AttendanceStatus.PRESENT)
        late_count = sum(1 for r, _, _ in records if r.status == AttendanceStatus.LATE)
        early_leave_count = sum(1 for r, _, _ in records if r.status == AttendanceStatus.EARLY_LEAVE)
        
        # 创建PDF
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # 标题
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Title'],
            fontSize=16,
            spaceAfter=20,
            alignment=1  # 居中
        )
        story.append(Paragraph("签到记录报告", title_style))
        story.append(Spacer(1, 12))
        
        # 基本信息
        info_data = [
            ['课程名称', course.name],
            ['签到场次', session.session_name],
            ['教室', classroom.name],
            ['授课教师', teacher.full_name],
            ['签到时间', session.start_time.strftime('%Y-%m-%d %H:%M:%S')],
            ['总人数', str(total_count)],
            ['出席人数', str(present_count + late_count + early_leave_count)],
            ['出勤率', f"{((present_count + late_count + early_leave_count) / total_count * 100):.1f}%" if total_count > 0 else "0%"]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # 签到明细表头
        story.append(Paragraph("签到明细", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # 签到记录表格
        table_data = [['序号', '学生姓名', '学号', '签到状态', '签到时间']]
        
        for i, (record, student_name, student_id) in enumerate(records, 1):
            table_data.append([
                str(i),
                student_name,
                student_id or '',
                get_status_text(record.status),
                record.signin_time.strftime('%H:%M:%S')
            ])
        
        table = Table(table_data, colWidths=[0.6*inch, 2*inch, 1.5*inch, 1.2*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        story.append(table)
        
        # 生成PDF
        doc.build(story)
        output.seek(0)
        
        # 返回文件
        filename = f"签到报告_{session.session_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return StreamingResponse(
            io.BytesIO(output.read()),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")

@router.get("/statistics/excel")
async def export_statistics_excel(
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    teacher_id: Optional[int] = Query(None, description="教师ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """导出统计数据为Excel"""
    try:
        # 基础查询
        query = db.query(
            Course.name.label('course_name'),
            User.full_name.label('teacher_name'),
            func.count(AttendanceRecord.id).label('total_records'),
            func.sum(
                func.case(
                    (AttendanceRecord.status == AttendanceStatus.PRESENT, 1),
                    else_=0
                )
            ).label('present_count'),
            func.sum(
                func.case(
                    (AttendanceRecord.status == AttendanceStatus.LATE, 1),
                    else_=0
                )
            ).label('late_count'),
            func.sum(
                func.case(
                    (AttendanceRecord.status == AttendanceStatus.EARLY_LEAVE, 1),
                    else_=0
                )
            ).label('early_leave_count')
        ).select_from(
            AttendanceRecord
        ).join(
            AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id
        ).join(
            Course, AttendanceSession.course_id == Course.id
        ).join(
            User, Course.teacher_id == User.id
        )
        
        # 应用筛选条件
        if start_date:
            query = query.filter(func.date(AttendanceRecord.signin_time) >= start_date)
            
        if end_date:
            query = query.filter(func.date(AttendanceRecord.signin_time) <= end_date)
            
        if teacher_id:
            query = query.filter(Course.teacher_id == teacher_id)
        
        # 分组统计
        stats = query.group_by(Course.id, User.id).all()
        
        # 准备数据
        data = []
        for stat in stats:
            total = stat.total_records or 0
            present = stat.present_count or 0
            late = stat.late_count or 0
            early_leave = stat.early_leave_count or 0
            
            attendance_rate = ((present + late + early_leave) / total * 100) if total > 0 else 0
            
            data.append({
                '课程名称': stat.course_name,
                '授课教师': stat.teacher_name,
                '总签到次数': total,
                '正常出席': present,
                '迟到': late,
                '早退': early_leave,
                '缺勤': total - present - late - early_leave,
                '出勤率(%)': f"{attendance_rate:.1f}"
            })
        
        # 创建DataFrame
        df = pd.DataFrame(data)
        
        # 创建Excel文件
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='出勤统计', index=False)
        
        output.seek(0)
        
        # 返回文件
        filename = f"出勤统计_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            io.BytesIO(output.read()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")

# 辅助函数
def get_role_text(role: str) -> str:
    """获取角色中文名称"""
    role_map = {
        'admin': '管理员',
        'teacher': '老师', 
        'student': '学生'
    }
    return role_map.get(role, '未知')

def get_status_text(status: AttendanceStatus) -> str:
    """获取签到状态中文名称"""
    status_map = {
        AttendanceStatus.PRESENT: '正常',
        AttendanceStatus.LATE: '迟到',
        AttendanceStatus.EARLY_LEAVE: '早退',
        AttendanceStatus.ABSENT: '缺勤'
    }
    return status_map.get(status, '未知')