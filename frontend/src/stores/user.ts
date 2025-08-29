import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginRequest } from '@/types'
import { userAPI } from '@/api'

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref<User | null>(null)
  const token = ref<string>('')
  const isLoggedIn = computed(() => !!token.value)

  // 初始化（从localStorage恢复状态）
  function init() {
    const savedToken = localStorage.getItem('access_token')
    const savedUser = localStorage.getItem('user_info')
    
    if (savedToken) {
      token.value = savedToken
    }
    
    if (savedUser) {
      try {
        user.value = JSON.parse(savedUser)
      } catch (error) {
        console.error('解析用户信息失败:', error)
        logout()
      }
    }
  }

  // 登录
  async function login(loginData: LoginRequest) {
    try {
      const response = await userAPI.login(loginData)
      
      token.value = response.access_token
      user.value = response.user
      
      // 保存到localStorage
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('user_info', JSON.stringify(response.user))
      
      return response
    } catch (error) {
      console.error('登录失败:', error)
      throw error
    }
  }

  // 登出
  function logout() {
    user.value = null
    token.value = ''
    
    // 清除localStorage
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_info')
  }

  // 更新用户信息
  function updateUserInfo(newUser: User) {
    user.value = newUser
    localStorage.setItem('user_info', JSON.stringify(newUser))
  }

  // 权限检查
  function hasRole(roles: string | string[]): boolean {
    if (!user.value) return false
    
    const userRole = user.value.role
    if (Array.isArray(roles)) {
      return roles.includes(userRole)
    }
    
    return userRole === roles
  }

  // 是否是管理员
  const isAdmin = computed(() => user.value?.role === 'admin')
  
  // 是否是老师
  const isTeacher = computed(() => user.value?.role === 'teacher')
  
  // 是否是学生
  const isStudent = computed(() => user.value?.role === 'student')

  return {
    // 状态
    user,
    token,
    isLoggedIn,
    isAdmin,
    isTeacher,
    isStudent,
    
    // 方法
    init,
    login,
    logout,
    updateUserInfo,
    hasRole
  }
})