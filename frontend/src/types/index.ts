// 用户相关类型
export interface User {
  id: number
  username: string
  email: string
  full_name: string
  phone?: string
  student_id?: string
  subject?: string
  address?: string
  role: 'admin' | 'teacher' | 'student'
  is_active: boolean
  created_at: string
  updated_at?: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface UserCreate {
  username: string
  email: string
  password: string
  full_name: string
  phone?: string
  student_id?: string
  subject?: string
  address?: string
  role: 'admin' | 'teacher' | 'student'
  is_active?: boolean
}

// 教室相关类型
export interface Classroom {
  id: number
  name: string
  location: string
  room_number: string
  equipment_info?: string
  capacity?: number
  is_active: boolean
  created_at: string
}

export interface ClassroomCreate {
  name: string
  location: string
  room_number: string
  equipment_info?: string
  capacity?: number
}

// 课程相关类型
export interface Course {
  id: number
  name: string
  description?: string
  teacher_id: number
  classroom_id: number
  classroom_name: string
  created_at: string
}

export interface CourseCreate {
  name: string
  description?: string
  teacher_id: number
  classroom_id: number
}

// 签到相关类型
export interface AttendanceSession {
  id: number
  course_id: number
  session_name: string
  start_time: string
  end_time?: string
  is_active: boolean
  daily_session_count: number
  created_at: string
}

export interface AttendanceSessionCreate {
  course_id: number
  session_name: string
  start_time: string
  end_time?: string
  daily_session_count?: number
}

export interface AttendanceRecord {
  id: number
  session_id: number
  student_id: number
  status: 'present' | 'absent' | 'late' | 'early_leave'
  signin_time: string
  signature_id?: number
  notes?: string
}

export interface AttendanceRecordCreate {
  student_id: number
  password: string
  signature_data: string
  status?: 'present' | 'absent' | 'late' | 'early_leave'
  notes?: string
}

export interface AttendanceStats {
  total_students: number
  present_count: number
  absent_count: number
  late_count: number
  early_leave_count: number
  attendance_rate: number
}

export interface Signature {
  id: number
  student_id: number
  signature_data: string
  created_at: string
}