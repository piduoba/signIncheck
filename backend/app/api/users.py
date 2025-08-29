from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd
from io import BytesIO

from ..core.database import get_db
from ..core.deps import get_current_user, get_admin_user, get_teacher_user
from ..core.security import get_password_hash, verify_password, create_access_token
from ..models import User, UserRole
from ..schemas.user import (
    UserCreate, UserResponse, UserUpdate, 
    LoginRequest, LoginResponse, UserImport,
    PasswordVerifyRequest, PasswordVerifyResponse
)

router = APIRouter(prefix="/users", tags=["用户管理"])

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账号已被禁用"
        )
    
    access_token = create_access_token(data={"sub": user.username})
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """创建用户（仅管理员）"""
    # 数据验证
    if not user_data.username or not user_data.username.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名不能为空"
        )
    
    if len(user_data.username.strip()) < 3 or len(user_data.username.strip()) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名长度必须在 3-20 个字符之间"
        )
    
    if not user_data.email or not user_data.email.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱地址不能为空"
        )
    
    if not user_data.full_name or not user_data.full_name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="真实姓名不能为空"
        )
    
    if not user_data.password or len(user_data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度不能少于 6 个字符"
        )
    
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == user_data.username.strip()).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if db.query(User).filter(User.email == user_data.email.strip()).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在"
        )
    
    # 检查学号是否已存在（如果提供）
    if user_data.student_id and user_data.student_id.strip():
        if db.query(User).filter(User.student_id == user_data.student_id.strip()).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="学号已存在"
            )
    
    try:
        # 创建新用户
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username.strip(),
            email=user_data.email.strip(),
            hashed_password=hashed_password,
            full_name=user_data.full_name.strip(),
            student_id=user_data.student_id.strip() if user_data.student_id else None,
            phone=user_data.phone.strip() if user_data.phone else None,
            subject=user_data.subject.strip() if user_data.subject else None,
            address=user_data.address.strip() if user_data.address else None,
            role=user_data.role,
            is_active=user_data.is_active
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return UserResponse.from_orm(db_user)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建用户失败: {str(e)}"
        )

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    course_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户列表（所有认证用户）"""
    query = db.query(User)
    
    if role:
        # 将字符串角色转换为UserRole枚举
        try:
            user_role = UserRole(role)
            query = query.filter(User.role == user_role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的角色 '{role}'。可用角色: {[r.value for r in UserRole]}"
            )
    
    # 按课程筛选学生
    if course_id and role == 'student':
        query = query.join(AttendanceRecord, AttendanceRecord.student_id == User.id)\
                     .join(AttendanceSession, AttendanceSession.id == AttendanceRecord.session_id)\
                     .filter(AttendanceSession.course_id == course_id)
    
    users = query.offset(skip).limit(limit).all()
    return [UserResponse.from_orm(user) for user in users]

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserResponse.from_orm(current_user)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """更新用户信息（仅管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 更新字段
    for field, value in user_data.dict(exclude_unset=True).items():
        if field == "password" and value:
            setattr(user, "hashed_password", get_password_hash(value))
        elif value is not None:
            setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return UserResponse.from_orm(user)

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """删除用户（仅管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": "用户删除成功"}

@router.post("/{user_id}/verify-password", response_model=PasswordVerifyResponse)
async def verify_password_api(
    user_id: int,
    password_data: PasswordVerifyRequest,
    db: Session = Depends(get_db)
):
    """验证用户密码"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    is_valid = verify_password(password_data.password, user.hashed_password)
    
    return PasswordVerifyResponse(is_valid=is_valid)

@router.post("/import")
async def import_users(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """批量导入用户（Excel文件）"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="仅支持Excel文件格式"
        )
    
    try:
        # 读取Excel文件
        content = await file.read()
        df = pd.read_excel(BytesIO(content))
        
        required_columns = ['username', 'email', 'password', 'full_name', 'role']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"缺少必需的列: {', '.join(missing_columns)}"
            )
        
        success_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # 验证角色
                try:
                    role = UserRole(row['role'])
                except ValueError:
                    errors.append(f"第{index+2}行: 无效的角色 '{row['role']}'")
                    continue
                
                # 检查必需字段
                if pd.isna(row['username']) or pd.isna(row['email']) or pd.isna(row['password']):
                    errors.append(f"第{index+2}行: 缺少必需字段")
                    continue
                
                # 检查用户是否已存在
                if db.query(User).filter(User.username == row['username']).first():
                    errors.append(f"第{index+2}行: 用户名 '{row['username']}' 已存在")
                    continue
                
                if db.query(User).filter(User.email == row['email']).first():
                    errors.append(f"第{index+2}行: 邮箱 '{row['email']}' 已存在")
                    continue
                
                # 创建用户
                db_user = User(
                    username=row['username'],
                    email=row['email'],
                    hashed_password=get_password_hash(str(row['password'])),
                    full_name=row['full_name'],
                    student_id=str(row.get('student_id', '')) if pd.notna(row.get('student_id')) else None,
                    phone=str(row.get('phone', '')) if pd.notna(row.get('phone')) else None,
                    subject=str(row.get('subject', '')) if pd.notna(row.get('subject')) else None,
                    address=str(row.get('address', '')) if pd.notna(row.get('address')) else None,
                    role=role
                )
                
                db.add(db_user)
                success_count += 1
                
            except Exception as e:
                errors.append(f"第{index+2}行: {str(e)}")
        
        db.commit()
        
        return {
            "message": f"成功导入 {success_count} 个用户",
            "errors": errors,
            "success_count": success_count,
            "error_count": len(errors)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件处理错误: {str(e)}"
        )