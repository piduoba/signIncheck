/**
 * 用户创建功能诊断工具
 * 用于测试和诊断新增用户功能的问题
 */

import axios from 'axios'

class UserCreateDiagnostic {
  constructor() {
    this.baseURL = 'http://localhost:8000/api'
    this.token = localStorage.getItem('token')
  }

  // 获取认证头
  getAuthHeaders() {
    return {
      'Authorization': `Bearer ${this.token}`,
      'Content-Type': 'application/json'
    }
  }

  // 1. 检查登录状态
  async checkAuthStatus() {
    console.log('🔍 步骤1: 检查登录状态')
    try {
      const response = await axios.get(`${this.baseURL}/users/me`, {
        headers: this.getAuthHeaders()
      })
      
      console.log('✅ 登录状态正常')
      console.log('当前用户:', response.data)
      
      if (response.data.role !== 'admin') {
        console.log('❌ 权限不足: 当前用户不是管理员')
        return false
      }
      
      return true
    } catch (error) {
      console.log('❌ 登录状态检查失败:', error.response?.data || error.message)
      return false
    }
  }

  // 2. 测试API连接
  async testAPIConnection() {
    console.log('\n🔍 步骤2: 测试API连接')
    try {
      const response = await axios.get(`${this.baseURL}/users/`, {
        headers: this.getAuthHeaders()
      })
      
      console.log('✅ API连接正常')
      console.log('现有用户数量:', response.data.length)
      return true
    } catch (error) {
      console.log('❌ API连接失败:', error.response?.data || error.message)
      return false
    }
  }

  // 3. 测试数据验证
  testDataValidation(userData) {
    console.log('\n🔍 步骤3: 测试数据验证')
    
    const errors = []
    
    // 基本验证
    if (!userData.username || userData.username.trim().length < 3) {
      errors.push('用户名必须至少3个字符')
    }
    
    if (!userData.email || !userData.email.includes('@')) {
      errors.push('邮箱格式不正确')
    }
    
    if (!userData.password || userData.password.length < 6) {
      errors.push('密码至少6个字符')
    }
    
    if (!userData.full_name || userData.full_name.trim().length < 2) {
      errors.push('真实姓名至少2个字符')
    }
    
    if (!userData.role || !['admin', 'teacher', 'student'].includes(userData.role)) {
      errors.push('角色必须是 admin、teacher 或 student')
    }
    
    if (errors.length > 0) {
      console.log('❌ 数据验证失败:')
      errors.forEach(error => console.log('  -', error))
      return false
    }
    
    console.log('✅ 数据验证通过')
    return true
  }

  // 4. 检查重复数据
  async checkDuplicateData(userData) {
    console.log('\n🔍 步骤4: 检查重复数据')
    
    try {
      const response = await axios.get(`${this.baseURL}/users/`, {
        headers: this.getAuthHeaders()
      })
      
      const existingUsers = response.data
      
      // 检查用户名重复
      const duplicateUsername = existingUsers.find(user => user.username === userData.username)
      if (duplicateUsername) {
        console.log('❌ 用户名已存在:', userData.username)
        return false
      }
      
      // 检查邮箱重复
      const duplicateEmail = existingUsers.find(user => user.email === userData.email)
      if (duplicateEmail) {
        console.log('❌ 邮箱已存在:', userData.email)
        return false
      }
      
      // 检查学号重复（如果提供）
      if (userData.student_id) {
        const duplicateStudentId = existingUsers.find(user => user.student_id === userData.student_id)
        if (duplicateStudentId) {
          console.log('❌ 学号已存在:', userData.student_id)
          return false
        }
      }
      
      console.log('✅ 无重复数据')
      return true
    } catch (error) {
      console.log('❌ 检查重复数据失败:', error.response?.data || error.message)
      return false
    }
  }

  // 5. 测试创建用户
  async testCreateUser(userData) {
    console.log('\n🔍 步骤5: 测试创建用户')
    console.log('提交的数据:', userData)
    
    try {
      const response = await axios.post(`${this.baseURL}/users/`, userData, {
        headers: this.getAuthHeaders()
      })
      
      console.log('✅ 用户创建成功!')
      console.log('创建的用户:', response.data)
      return response.data
    } catch (error) {
      console.log('❌ 用户创建失败')
      
      if (error.response) {
        console.log('状态码:', error.response.status)
        console.log('错误详情:', error.response.data)
        
        // 根据状态码提供建议
        switch (error.response.status) {
          case 400:
            console.log('💡 建议: 检查输入数据格式和内容')
            break
          case 401:
            console.log('💡 建议: 重新登录或检查管理员权限')
            break
          case 409:
            console.log('💡 建议: 用户名或邮箱可能已存在')
            break
          case 422:
            console.log('💡 建议: 检查数据类型和必填字段')
            break
          case 500:
            console.log('💡 建议: 联系管理员检查服务器日志')
            break
        }
      } else if (error.request) {
        console.log('💡 建议: 检查网络连接和后端服务状态')
      } else {
        console.log('💡 建议: 检查前端代码逻辑')
      }
      
      return null
    }
  }

  // 完整诊断流程
  async runFullDiagnostic(userData = null) {
    console.log('🚀 开始用户创建功能完整诊断')
    console.log('='.repeat(50))
    
    // 默认测试数据
    if (!userData) {
      userData = {
        username: 'test_' + Date.now(),
        email: `test_${Date.now()}@example.com`,
        password: '123456',
        full_name: '测试用户',
        role: 'student',
        is_active: true
      }
    }
    
    // 步骤1: 检查登录状态
    const authOk = await this.checkAuthStatus()
    if (!authOk) {
      console.log('\n🛑 诊断终止: 登录状态或权限问题')
      return false
    }
    
    // 步骤2: 测试API连接
    const apiOk = await this.testAPIConnection()
    if (!apiOk) {
      console.log('\n🛑 诊断终止: API连接问题')
      return false
    }
    
    // 步骤3: 测试数据验证
    const dataOk = this.testDataValidation(userData)
    if (!dataOk) {
      console.log('\n🛑 诊断终止: 数据验证问题')
      return false
    }
    
    // 步骤4: 检查重复数据
    const noDuplicates = await this.checkDuplicateData(userData)
    if (!noDuplicates) {
      console.log('\n🛑 诊断终止: 存在重复数据')
      return false
    }
    
    // 步骤5: 测试创建用户
    const result = await this.testCreateUser(userData)
    
    console.log('\n' + '='.repeat(50))
    if (result) {
      console.log('🎉 诊断完成: 用户创建功能正常!')
    } else {
      console.log('❌ 诊断完成: 发现用户创建问题')
    }
    
    return !!result
  }

  // 快速测试指定数据
  async quickTest(userData) {
    console.log('⚡ 快速测试用户创建')
    
    // 只进行基本验证和创建测试
    if (!this.testDataValidation(userData)) {
      return false
    }
    
    const result = await this.testCreateUser(userData)
    return !!result
  }
}

// 导出工具类
export default UserCreateDiagnostic

// 在浏览器控制台中使用的便捷函数
window.userDiagnostic = new UserCreateDiagnostic()

// 使用示例:
// 1. 完整诊断: await userDiagnostic.runFullDiagnostic()
// 2. 自定义数据诊断: await userDiagnostic.runFullDiagnostic({ username: 'test', email: 'test@example.com', ... })
// 3. 快速测试: await userDiagnostic.quickTest({ username: 'test', ... })