import api from '@/utils/request'
import type {
  LoginRequest,
  LoginResponse,
  User,
  UserCreate,
  Classroom,
  ClassroomCreate,
  Course,
  CourseCreate,
  AttendanceSession,
  AttendanceSessionCreate,
  AttendanceRecord,
  AttendanceRecordCreate,
  AttendanceStats
} from '@/types'

// 用户API
export const userAPI = {
  // 登录
  login: (data: LoginRequest): Promise<LoginResponse> => {
    return api.post('/users/login', data)
  },

  // 获取当前用户信息
  getCurrentUser: (): Promise<User> => {
    return api.get('/users/me')
  },

  // 获取用户列表
  getUsers: (params?: { skip?: number; limit?: number; role?: string; course_id?: number }): Promise<User[]> => {
    return api.get('/users/', { params })
  },

  // 创建用户
  createUser: (data: UserCreate): Promise<User> => {
    return api.post('/users/', data)
  },

  // 更新用户
  updateUser: (id: number, data: Partial<UserCreate>): Promise<User> => {
    return api.put(`/users/${id}`, data)
  },

  // 删除用户
  deleteUser: (id: number): Promise<{ message: string }> => {
    return api.delete(`/users/${id}`)
  },

  // 批量导入用户
  importUsers: (file: File): Promise<any> => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/users/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 验证用户密码
  verifyPassword: (userId: number, password: string): Promise<boolean> => {
    return api.post(`/users/${userId}/verify-password`, { password })
  }
}

// 教室API
export const classroomAPI = {
  // 获取教室列表
  getClassrooms: (params?: { skip?: number; limit?: number }): Promise<Classroom[]> => {
    return api.get('/attendance/classrooms', { params })
  },

  // 创建教室
  createClassroom: (data: ClassroomCreate): Promise<Classroom> => {
    return api.post('/attendance/classrooms', data)
  },

  // 删除教室
  deleteClassroom: (id: number): Promise<{ message: string }> => {
    return api.delete(`/attendance/classrooms/${id}`)
  }
}

// 课程API
export const courseAPI = {
  // 获取课程列表
  getCourses: (teacherId?: number): Promise<Course[]> => {
    const params = teacherId ? { teacher_id: teacherId } : undefined
    return api.get('/attendance/courses', { params })
  },

  // 创建课程
  createCourse: (data: CourseCreate): Promise<Course> => {
    return api.post('/attendance/courses', data)
  }
}

// 签到API
export const attendanceAPI = {
  // 获取签到场次列表
  getSessions: (params?: { course_id?: number; date_filter?: string }): Promise<AttendanceSession[]> => {
    return api.get('/attendance/sessions', { params })
  },

  // 创建签到场次
  createSession: (data: AttendanceSessionCreate): Promise<AttendanceSession> => {
    return api.post('/attendance/sessions', data)
  },

  // 关闭签到场次
  closeSession: (id: number): Promise<{ message: string }> => {
    return api.put(`/attendance/sessions/${id}/close`)
  },

  // 学生签到
  studentSignin: (sessionId: number, data: AttendanceRecordCreate): Promise<AttendanceRecord> => {
    return api.post(`/attendance/signin/${sessionId}`, data)
  },

  // 获取签到记录
  getRecords: (sessionId: number): Promise<AttendanceRecord[]> => {
    return api.get(`/attendance/records/${sessionId}`)
  },

  // 获取签到统计
  getStats: (sessionId: number): Promise<AttendanceStats> => {
    return api.get(`/attendance/stats/${sessionId}`)
  },

  // 按课程直接签到（现场签到）
  signin: (courseId: number, data: AttendanceRecordCreate): Promise<AttendanceRecord> => {
    return api.post(`/attendance/courses/${courseId}/signin`, data)
  }
}

// 通用API
export const commonAPI = {
  // 健康检查
  healthCheck: (): Promise<{ status: string; message: string }> => {
    return api.get('/health')
  }
}