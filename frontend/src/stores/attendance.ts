import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { AttendanceSession, AttendanceRecordCreate, AttendanceRecord } from '@/types'
import { attendanceAPI } from '@/api'

export const useAttendanceStore = defineStore('attendance', () => {
  // 状态
  const currentSession = ref<AttendanceSession | null>(null)
  const activeSessions = ref<AttendanceSession[]>([])

  // 设置当前签到场次
  function setCurrentSession(session: AttendanceSession | null) {
    currentSession.value = session
  }

  // 学生签到
  async function studentSignin(sessionId: number, signinData: AttendanceRecordCreate): Promise<AttendanceRecord> {
    try {
      const result = await attendanceAPI.studentSignin(sessionId, signinData)
      return result
    } catch (error) {
      console.error('签到失败:', error)
      throw error
    }
  }

  // 加载活跃的签到场次
  async function loadActiveSessions() {
    try {
      const sessions = await attendanceAPI.getSessions()
      activeSessions.value = sessions.filter(s => s.is_active)
      
      // 如果没有当前场次但有活跃场次，设置第一个为当前场次
      if (!currentSession.value && activeSessions.value.length > 0) {
        currentSession.value = activeSessions.value[0]
      }
    } catch (error) {
      console.error('加载活跃签到场次失败:', error)
      throw error
    }
  }

  return {
    // 状态
    currentSession,
    activeSessions,
    
    // 方法
    setCurrentSession,
    studentSignin,
    loadActiveSessions
  }
})