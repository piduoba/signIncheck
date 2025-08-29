<template>
  <div class="user-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <el-icon><User /></el-icon>
          用户管理
        </h1>
        <p class="page-subtitle">管理系统中的所有用户账号</p>
      </div>
      
      <div class="header-actions">
        <el-dropdown @command="handleExport">
          <el-button type="info">
            <el-icon><Download /></el-icon>
            导出数据
            <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="all">导出所有用户</el-dropdown-item>
              <el-dropdown-item command="admin">导出管理员</el-dropdown-item>
              <el-dropdown-item command="teacher">导出教师</el-dropdown-item>
              <el-dropdown-item command="student">导出学生</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button type="success" @click="handleImport">
          <el-icon><Upload /></el-icon>
          批量导入
        </el-button>
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新增用户
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card" shadow="never">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="用户名">
          <el-input
            v-model="searchForm.username"
            placeholder="请输入用户名"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        
        <el-form-item label="姓名">
          <el-input
            v-model="searchForm.fullName"
            placeholder="请输入真实姓名"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        
        <el-form-item label="角色">
          <el-select v-model="searchForm.role" placeholder="请选择角色" clearable>
            <el-option label="管理员" value="admin" />
            <el-option label="老师" value="teacher" />
            <el-option label="学生" value="student" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><RefreshLeft /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 用户列表 -->
    <el-card class="table-card" shadow="never">
      <div class="table-header">
        <div class="table-info">
          <span>共 {{ total }} 个用户</span>
        </div>
        <div class="table-actions">
          <el-button size="small" @click="handleRefresh">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>

      <el-table
        v-loading="loading"
        :data="userList"
        stripe
        class="user-table"
        @sort-change="handleSortChange"
      >
        <el-table-column type="index" label="序号" width="60" />
        
        <el-table-column prop="username" label="用户名" min-width="120" sortable="custom">
          <template #default="{ row }">
            <div class="user-info">
              <el-avatar :size="32" class="user-avatar">
                {{ row.full_name.charAt(0) }}
              </el-avatar>
              <span>{{ row.username }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="full_name" label="真实姓名" min-width="120" sortable="custom" />
        
        <el-table-column prop="email" label="邮箱" min-width="200" />
        
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="getRoleTagType(row.role)" size="small">
              {{ getRoleText(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="student_id" label="学号" width="120">
          <template #default="{ row }">
            {{ row.student_id || '-' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="phone" label="联系电话" width="120">
          <template #default="{ row }">
            {{ row.phone || '-' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_active"
              @change="handleStatusChange(row)"
              :loading="row.statusLoading"
            />
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="160" sortable="custom">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button
                type="primary"
                size="small"
                @click="handleEdit(row)"
              >
                编辑
              </el-button>
              <el-button
                type="danger"
                size="small"
                @click="handleDelete(row)"
                :disabled="row.id === userStore.user?.id"
              >
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑用户' : '新增用户'"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userFormRules"
        label-width="80px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="userForm.username" placeholder="请输入用户名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="真实姓名" prop="full_name">
              <el-input v-model="userForm.full_name" placeholder="请输入真实姓名" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" type="email" placeholder="请输入邮箱地址" />
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="角色" prop="role">
              <el-select v-model="userForm.role" placeholder="请选择角色" class="w-full">
                <el-option label="管理员" value="admin" />
                <el-option label="老师" value="teacher" />
                <el-option label="学生" value="student" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="phone">
              <el-input v-model="userForm.phone" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="学号" prop="student_id" v-if="userForm.role === 'student'">
          <el-input v-model="userForm.student_id" placeholder="请输入学号" />
        </el-form-item>
        
        <el-form-item label="学科" prop="subject" v-if="userForm.role === 'teacher'">
          <el-input v-model="userForm.subject" placeholder="请输入教授学科" />
        </el-form-item>
        
        <el-form-item label="地址" prop="address">
          <el-input
            v-model="userForm.address"
            type="textarea"
            placeholder="请输入地址"
            :rows="3"
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input
            v-model="userForm.password"
            type="password"
            placeholder="请输入登录密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="状态">
          <el-switch
            v-model="userForm.is_active"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ submitting ? '保存中...' : '确定' }}
        </el-button>
      </template>
    </el-dialog>



    <!-- 批量导入对话框 -->
    <el-dialog v-model="importDialogVisible" title="批量导入用户" width="600px">
      <div class="import-content">
        <div class="import-tips">
          <el-alert
            title="导入说明"
            type="info"
            show-icon
            :closable="false"
          >
            <template #default>
              <p>1. 请下载模板文件，按照模板格式填写用户信息</p>
              <p>2. 支持的文件格式：.xlsx, .xls</p>
              <p>3. 必填字段：用户名、邮箱、密码、真实姓名、角色</p>
              <p>4. 角色值：admin（管理员）、teacher（老师）、student（学生）</p>
            </template>
          </el-alert>
        </div>
        
        <div class="import-actions">
          <el-button type="primary" @click="downloadTemplate">
            <el-icon><Download /></el-icon>
            下载模板
          </el-button>
        </div>
        
        <el-upload
          class="upload-demo"
          drag
          accept=".xlsx,.xls"
          :show-file-list="false"
          :before-upload="handleFileUpload"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              只能上传 xlsx/xls 文件，且不超过 5MB
            </div>
          </template>
        </el-upload>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import type { ElForm } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { userAPI } from '@/api'
import { ExportUtils } from '@/utils/export'
import type { User, UserCreate } from '@/types'

const userStore = useUserStore()

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const importDialogVisible = ref(false)
const isEdit = ref(false)
const selectedUser = ref<User | null>(null)
const userFormRef = ref<InstanceType<typeof ElForm>>()

// 用户列表
const userList = ref<User[]>([])
const total = ref(0)

// 搜索表单
const searchForm = reactive({
  username: '',
  fullName: '',
  role: '',
  status: null as boolean | null
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20
})

// 用户表单
const userForm = reactive<UserCreate>({
  username: '',
  email: '',
  password: '',
  full_name: '',
  phone: '',
  student_id: '',
  subject: '',
  address: '',
  role: 'student',
  is_active: true
})

// 表单验证规则
const userFormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' },
    { min: 5, max: 100, message: '邮箱地址长度在 5 到 100 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度在 6 到 50 个字符', trigger: 'blur' }
  ],
  full_name: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' },
    { min: 2, max: 50, message: '姓名长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  student_id: [
    { min: 4, max: 20, message: '学号长度在 4 到 20 个字符', trigger: 'blur' }
  ]
}

// 获取角色标签类型
const getRoleTagType = (role: string) => {
  switch (role) {
    case 'admin': return 'danger'
    case 'teacher': return 'warning'
    case 'student': return 'success'
    default: return 'info'
  }
}

// 获取角色文本
const getRoleText = (role: string) => {
  switch (role) {
    case 'admin': return '管理员'
    case 'teacher': return '老师'
    case 'student': return '学生'
    default: return '未知'
  }
}

// 格式化日期时间
const formatDateTime = (dateStr: string) => {
  return new Date(dateStr).toLocaleString()
}

// 加载用户列表
const loadUserList = async () => {
  try {
    loading.value = true
    
    const params: any = {
      skip: (pagination.page - 1) * pagination.size,
      limit: pagination.size
    }
    
    if (searchForm.role) {
      params.role = searchForm.role
    }
    
    const users = await userAPI.getUsers(params)
    
    // 简单过滤（实际应在后端实现）
    let filteredUsers = users
    
    if (searchForm.username) {
      filteredUsers = filteredUsers.filter(user => 
        user.username.toLowerCase().includes(searchForm.username.toLowerCase())
      )
    }
    
    if (searchForm.fullName) {
      filteredUsers = filteredUsers.filter(user => 
        user.full_name.toLowerCase().includes(searchForm.fullName.toLowerCase())
      )
    }
    
    if (searchForm.status !== null) {
      filteredUsers = filteredUsers.filter(user => user.is_active === searchForm.status)
    }
    
    userList.value = filteredUsers.map(user => ({
      ...user,
      statusLoading: false
    }))
    
    total.value = filteredUsers.length
    
  } catch (error) {
    console.error('加载用户列表失败:', error)
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索用户
const handleSearch = () => {
  pagination.page = 1
  loadUserList()
}

// 重置搜索
const handleReset = () => {
  Object.assign(searchForm, {
    username: '',
    fullName: '',
    role: '',
    status: null
  })
  handleSearch()
}

// 刷新列表
const handleRefresh = () => {
  loadUserList()
}

// 排序变化
const handleSortChange = ({ prop, order }: any) => {
  // 实现排序逻辑
  console.log('排序:', prop, order)
}

// 分页大小变化
const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.page = 1
  loadUserList()
}

// 页码变化
const handlePageChange = (page: number) => {
  pagination.page = page
  loadUserList()
}

// 新增用户
const handleCreate = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

// 编辑用户
const handleEdit = (user: User) => {
  isEdit.value = true
  Object.assign(userForm, {
    username: user.username,
    email: user.email,
    password: '', // 编辑时不显示密码
    full_name: user.full_name,
    phone: user.phone || '',
    student_id: user.student_id || '',
    subject: user.subject || '',
    address: user.address || '',
    role: user.role,
    is_active: user.is_active
  })
  selectedUser.value = user
  dialogVisible.value = true
}



// 删除用户
const handleDelete = async (user: User) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.full_name}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await userAPI.deleteUser(user.id)
    ElMessage.success('删除成功')
    loadUserList()
    
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除用户失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 状态变化
const handleStatusChange = async (user: any) => {
  try {
    user.statusLoading = true
    
    await userAPI.updateUser(user.id, {
      is_active: user.is_active
    })
    
    ElMessage.success('状态更新成功')
    
  } catch (error) {
    console.error('更新用户状态失败:', error)
    ElMessage.error('状态更新失败')
    
    // 恢复原状态
    user.is_active = !user.is_active
  } finally {
    user.statusLoading = false
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!userFormRef.value) return
  
  try {
    const valid = await userFormRef.value.validate()
    if (!valid) {
      ElMessage.error('请检查表单中的错误信息')
      return
    }
    
    // 详细的前端验证
    if (!userForm.username.trim()) {
      ElMessage.error('用户名不能为空')
      return
    }
    
    if (!userForm.email.trim()) {
      ElMessage.error('邮箱不能为空')
      return
    }
    
    if (!userForm.full_name.trim()) {
      ElMessage.error('真实姓名不能为空')
      return
    }
    
    if (!isEdit.value && !userForm.password.trim()) {
      ElMessage.error('密码不能为空')
      return
    }
    
    if (!userForm.role) {
      ElMessage.error('请选择角色')
      return
    }
    
    console.log('提交的表单数据:', userForm)
    
    submitting.value = true
    
    if (isEdit.value && selectedUser.value) {
      // 编辑用户
      const updateData: any = { ...userForm }
      delete updateData.password // 编辑时不更新密码
      
      console.log('更新用户数据:', updateData)
      await userAPI.updateUser(selectedUser.value.id, updateData)
      ElMessage.success('更新成功')
    } else {
      // 新增用户
      console.log('创建用户数据:', userForm)
      const result = await userAPI.createUser(userForm)
      console.log('创建用户结果:', result)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    loadUserList()
    
  } catch (error: any) {
    console.error('保存用户失败:', error)
    
    let errorMessage = '保存失败'
    
    if (error.response) {
      // 服务器响应错误
      console.error('服务器响应错误:', {
        status: error.response.status,
        data: error.response.data,
        headers: error.response.headers
      })
      
      if (error.response.status === 401) {
        errorMessage = '权限不足，请确保您已以管理员身份登录'
      } else if (error.response.status === 400) {
        errorMessage = error.response.data?.detail || '请求参数错误'
      } else if (error.response.status === 409) {
        errorMessage = '用户名或邮箱已存在'
      } else if (error.response.status === 422) {
        errorMessage = '数据验证失败，请检查输入格式'
      } else if (error.response.status >= 500) {
        errorMessage = '服务器内部错误，请联系管理员'
      } else {
        errorMessage = error.response.data?.detail || `保存失败 (${error.response.status})`
      }
    } else if (error.request) {
      // 网络错误
      console.error('网络请求错误:', error.request)
      errorMessage = '网络连接失败，请检查网络连接或后端服务状态'
    } else {
      // 其他错误
      console.error('其他错误:', error.message)
      errorMessage = error.message || '未知错误'
    }
    
    ElMessage.error(errorMessage)
  } finally {
    submitting.value = false
  }
}

// 对话框关闭
const handleDialogClose = () => {
  resetForm()
  if (userFormRef.value) {
    userFormRef.value.clearValidate()
  }
}

// 重置表单
const resetForm = () => {
  Object.assign(userForm, {
    username: '',
    email: '',
    password: '',
    full_name: '',
    phone: '',
    student_id: '',
    subject: '',
    address: '',
    role: 'student',
    is_active: true
  })
}

// 批量导入
const handleImport = () => {
  importDialogVisible.value = true
}

// 下载模板
const downloadTemplate = () => {
  // 创建模板数据
  const templateData = [
    {
      username: 'student001',
      email: 'student001@example.com',
      password: '123456',
      full_name: '张三',
      role: 'student',
      student_id: '2024001',
      phone: '13800138001',
      address: '北京市朝阳区'
    }
  ]
  
  // 简单实现，实际应该生成真正的Excel文件
  const jsonStr = JSON.stringify(templateData, null, 2)
  const blob = new Blob([jsonStr], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  
  const a = document.createElement('a')
  a.href = url
  a.download = 'user_template.json'
  a.click()
  
  URL.revokeObjectURL(url)
  ElMessage.success('模板下载成功')
}

// 文件上传
const handleFileUpload = async (file: File) => {
  try {
    if (file.size > 5 * 1024 * 1024) {
      ElMessage.error('文件大小不能超过 5MB')
      return false
    }
    
    const result = await userAPI.importUsers(file)
    
    ElMessage.success(`导入成功：${result.success_count} 个用户`)
    
    if (result.errors && result.errors.length > 0) {
      console.warn('导入警告:', result.errors)
    }
    
    importDialogVisible.value = false
    loadUserList()
    
  } catch (error: any) {
    console.error('导入失败:', error)
    ElMessage.error(error.response?.data?.detail || '导入失败')
  }
  
  return false // 阻止默认上传行为
}

// 导出数据
const handleExport = async (command: string) => {
  try {
    const role = command === 'all' ? undefined : command
    await ExportUtils.exportUsers(role)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

onMounted(() => {
  loadUserList()
})
</script>

<style scoped>
.user-management {
  padding: 0;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.header-content {
  .page-title {
    font-size: 24px;
    color: #1976d2;
    margin: 0 0 4px 0;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .page-subtitle {
    color: #666;
    margin: 0;
    font-size: 14px;
  }
}

.header-actions {
  display: flex;
  gap: 12px;
}

.search-card {
  margin-bottom: 20px;
  border: 1px solid #e8eaec;
}

.search-form {
  margin: 0;
}

.table-card {
  border: 1px solid #e8eaec;
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.table-info {
  font-size: 14px;
  color: #666;
}

.user-table {
  .user-info {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .user-avatar {
    background: linear-gradient(135deg, #2196f3, #21cbf3);
    color: white;
    font-weight: 600;
  }
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
  align-items: center;
}

.user-detail {
  .detail-item {
    display: flex;
    margin-bottom: 12px;
    
    label {
      width: 100px;
      color: #666;
      font-weight: 500;
    }
    
    span {
      flex: 1;
      color: #333;
    }
  }
}

.import-content {
  .import-tips {
    margin-bottom: 20px;
  }
  
  .import-actions {
    margin-bottom: 20px;
    text-align: center;
  }
}

.w-full {
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .search-form {
    .el-form-item {
      margin-bottom: 16px;
    }
  }
  
  .table-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
}
</style>