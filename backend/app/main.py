from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .core.database import engine, get_db
from .core.security import get_password_hash
from .models import Base, User, UserRole
from .api import users, attendance
# from .api import export  # 暂时注释以解决依赖问题

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title="课程签到系统",
    description="支持密码+签名双重验证的课程签到管理系统",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176"],  # Vue开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(users.router, prefix="/api")
app.include_router(attendance.router, prefix="/api")
# app.include_router(export.router, prefix="/api")  # 暂时注释

@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化操作"""
    db = next(get_db())
    
    # 创建默认管理员账号
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin"),
            full_name="系统管理员",
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        print("默认管理员账号已创建: admin/admin")

@app.get("/")
async def root():
    return {
        "message": "课程签到系统API", 
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "message": "服务正常运行"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)