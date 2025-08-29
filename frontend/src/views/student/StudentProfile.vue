<template>
  <div class="student-profile">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><User /></el-icon>
        个人信息
      </h2>
    </div>

    <!-- 个人信息卡片 -->
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>基本信息</span>
          <el-button type="primary" text @click="showEditDialog = true">
            <el-icon><Edit /></el-icon>
            编辑信息
          </el-button>
        </div>
      </template>

      <div class="profile-content">
        <div class="avatar-section">
          <el-avatar :size="120" class="profile-avatar">
            {{ userStore.user?.full_name?.charAt(0) }}
          </el-avatar>
          <div class="avatar-info">
            <h3>{{ userStore.user?.full_name }}</h3>
            <p class="role-tag">
              <el-tag type="success">学生</el-tag>
            </p>
          </div>
        </div>

        <div class="info-section">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="姓名">
              {{ userStore.user?.full_name }}
            </el-descriptions-item>
            <el-descriptions-item label="学号">
              {{ userStore.user?.student_id || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="邮箱">
              {{ userStore.user?.email }}
            </el-descriptions-item>
            <el-descriptions-item label="电话">
              {{ userStore.user?.phone || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="地址" :span="2">
              {{ userStore.user?.address || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="注册时间" :span="2">
              {{ userStore.user?.created_at ? formatDateTime(userStore.user.created_at) : '-' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-card>

    <!-- 签到统计卡片 -->
    <el-card class="stats-card">
      <template #header>
        <span>签到统计</span>
      </template>

      <el-row :gutter="24">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-icon total-icon">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ attendanceStats.totalSessions }}</div>
              <div class="stat-label">总签到次数</div>
            </div>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-icon present-icon">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ attendanceStats.presentCount }}</div>
              <div class="stat-label">正常签到</div>
            </div>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-icon late-icon">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ attendanceStats.lateCount }}</div>
              <div class="stat-label">迟到次数</div>
            </div>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-icon rate-icon">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ attendanceStats.attendanceRate }}%</div>
              <div class="stat-label">出勤率</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 最近签到记录 -->
    <el-card class="recent-records-card">
      <template #header>
        <div class="card-header">
          <span>最近签到记录</span>
          <el-button type="primary" text @click="$router.push('/student/history')">
            查看全部
          </el-button>
        </div>
      </template>

      <el-table :data="recentRecords" v-loading="recordsLoading" stripe>
        <el-table-column prop="session_name" label="签到场次" width="180">
          <template #default="{ row }">
            {{ getSessionName(row.session_id) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="course_name" label="课程" width="120">
          <template #default="{ row }">
            {{ getCourseName(row.session_id) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="签到状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="signin_time" label="签到时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.signin_time) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="notes" label="备注" min-width="150">
          <template #default="{ row }">
            {{ row.notes || '-' }}
          </template>
        </el-table-column>
      </el-table>

      <div v-if="recentRecords.length === 0" class="empty-records">
        <el-empty description="暂无签到记录" />
      </div>
    </el-card>

    <!-- 编辑信息对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑个人信息" width="500px">
      <el-form
        ref="profileFormRef"
        :model="profileForm"
        :rules="profileRules"
        label-width="80px"
      >
        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="profileForm.full_name" placeholder="请输入姓名" />
        </el-form-item>
        
        <el-form-item label="电话" prop="phone">
          <el-input v-model="profileForm.phone" placeholder="请输入电话号码" />
        </el-form-item>
        
        <el-form-item label="地址" prop="address">
          <el-input
            v-model="profileForm.address"
            type="textarea"
            :rows="3"
            placeholder="请输入地址"
          />
        </el-form-item>
        
        <el-form-item label="新密码">
          <el-input
            v-model="profileForm.password"
            type="password"
            placeholder="留空则不修改密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="确认密码" v-if="profileForm.password">
          <el-input
            v-model="profileForm.confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" :loading="updating" @click="updateProfile">
          {{ updating ? '更新中...' : '确定' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, type FormInstance } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { userAPI, attendanceAPI } from '@/api'
import type { AttendanceRecord, AttendanceSession } from '@/types'

const userStore = useUserStore()

// 响应式数据
const recentRecords = ref<AttendanceRecord[]>([])
const sessions = ref<AttendanceSession[]>([])
const recordsLoading = ref(false)
const updating = ref(false)
const showEditDialog = ref(false)
const profileFormRef = ref<FormInstance>()

// 签到统计
const attendanceStats = ref({
  totalSessions: 0,
  presentCount: 0,
  lateCount: 0,
  attendanceRate: 0
})

// 编辑表单
const profileForm = reactive({
  full_name: '',
  phone: '',
  address: '',
  password: '',
  confirmPassword: ''
})

// 表单验证规则
const profileRules = {
  full_name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  confirmPassword: [
    {
      validator: (rule: any, value: string, callback: any) => {
        if (profileForm.password && value !== profileForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 获取会话名称
const getSessionName = (sessionId: number) => {
  const session = sessions.value.find(s => s.id === sessionId)
  return session?.session_name || '-'
}

// 获取课程名称（通过会话）
const getCourseName = (sessionId: number) => {
  // 这里需要通过会话信息获取课程名称
  // 由于数据结构限制，暂时返回固定值
  return '数学课'
}

// 获取状态类型
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    present: 'success',
    late: 'warning',
    absent: 'danger',
    early_leave: 'info'
  }
  return statusMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    present: '正常',
    late: '迟到',
    absent: '缺勤',
    early_leave: '早退'
  }
  return statusMap[status] || status
}

// 格式化日期时间
const formatDateTime = (dateStr: string) => {
  return new Date(dateStr).toLocaleString()
}

// 初始化编辑表单
const initProfileForm = () => {
  if (userStore.user) {
    profileForm.full_name = userStore.user.full_name
    profileForm.phone = userStore.user.phone || ''
    profileForm.address = userStore.user.address || ''
    profileForm.password = ''
    profileForm.confirmPassword = ''
  }
}

// 加载签到记录
const loadAttendanceData = async () => {
  if (!userStore.user) return

  try {
    recordsLoading.value = true
    
    // 模拟加载学生的签到记录
    // 实际应该调用专门的学生签到记录API
    
    // 模拟数据
    recentRecords.value = [
      {
        id: 1,
        session_id: 1,
        student_id: userStore.user.id,
        status: 'present',
        signin_time: '2024-01-15 08:30:00',
        signature_id: 1,
        notes: ''
      },
      {
        id: 2,
        session_id: 2,
        student_id: userStore.user.id,
        status: 'late',
        signin_time: '2024-01-14 08:35:00',
        signature_id: 2,
        notes: '交通堵塞'
      }
    ]

    // 计算统计数据
    const totalSessions = recentRecords.value.length
    const presentCount = recentRecords.value.filter(r => r.status === 'present').length
    const lateCount = recentRecords.value.filter(r => r.status === 'late').length
    const attendanceRate = totalSessions > 0 ? Math.round((presentCount + lateCount) / totalSessions * 100) : 0

    attendanceStats.value = {
      totalSessions,
      presentCount,
      lateCount,
      attendanceRate
    }

  } catch (error) {
    console.error('加载签到数据失败:', error)
    ElMessage.error('加载签到数据失败')
  } finally {
    recordsLoading.value = false
  }
}

// 更新个人信息
const updateProfile = async () => {
  if (!profileFormRef.value || !userStore.user) return

  try {
    const valid = await profileFormRef.value.validate()
    if (!valid) return

    updating.value = true

    const updateData: any = {
      full_name: profileForm.full_name,
      phone: profileForm.phone,
      address: profileForm.address
    }

    if (profileForm.password) {
      updateData.password = profileForm.password
    }

    // 调用更新API
    const updatedUser = await userAPI.updateUser(userStore.user.id, updateData)
    
    // 更新本地用户信息
    userStore.updateUserInfo(updatedUser)
    
    ElMessage.success('个人信息更新成功')
    showEditDialog.value = false
    
  } catch (error: any) {
    console.error('更新失败:', error)
    ElMessage.error(error.response?.data?.detail || '更新失败')
  } finally {
    updating.value = false
  }
}

onMounted(() => {
  initProfileForm()
  loadAttendanceData()
})
</script>

<style scoped>
.student-profile {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  color: #1976d2;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.profile-card {
  margin-bottom: 24px;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .profile-content {
    .avatar-section {
      display: flex;
      align-items: center;
      margin-bottom: 24px;
      padding: 20px;
      background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
      border-radius: 12px;
      
      .profile-avatar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 48px;
        font-weight: 600;
        margin-right: 24px;
      }
      
      .avatar-info {
        h3 {
          margin: 0 0 8px 0;
          color: #333;
          font-size: 24px;
        }
        
        .role-tag {
          margin: 0;
        }
      }
    }
  }
}

.stats-card {
  margin-bottom: 24px;
  
  .stat-item {
    display: flex;
    align-items: center;
    padding: 16px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    
    .stat-icon {
      width: 60px;
      height: 60px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 16px;
      
      .el-icon {
        font-size: 24px;
        color: white;
      }
      
      &.total-icon {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      }
      
      &.present-icon {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
      }
      
      &.late-icon {
        background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
      }
      
      &.rate-icon {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
      }
    }
    
    .stat-content {
      .stat-number {
        font-size: 28px;
        font-weight: 600;
        color: #333;
        line-height: 1;
      }
      
      .stat-label {
        font-size: 14px;
        color: #666;
        margin-top: 4px;
      }
    }
  }
}

.recent-records-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .empty-records {
    padding: 40px 0;
  }
}
</style>