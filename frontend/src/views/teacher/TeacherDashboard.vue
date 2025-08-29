<template>
  <div class="teacher-dashboard">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><User /></el-icon>
        老师仪表盘
      </h2>
      <div class="header-info">
        <span>欢迎，{{ userStore.user?.full_name }} 老师</span>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="24" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-icon course-icon">
              <el-icon><Reading /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ dashboardData.totalCourses }}</div>
              <div class="stat-label">我的课程</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-icon session-icon">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ dashboardData.todaySessions }}</div>
              <div class="stat-label">今日签到场次</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-icon attendance-icon">
              <el-icon><UserFilled /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ dashboardData.todayAttendance }}%</div>
              <div class="stat-label">今日出勤率</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-icon active-icon">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ dashboardData.activeSessions }}</div>
              <div class="stat-label">进行中的签到</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快速操作 -->
    <el-card class="quick-actions-card">
      <template #header>
        <span>快速操作</span>
      </template>
      
      <div class="quick-actions">
        <el-button type="primary" size="large" @click="createSession">
          <el-icon><Plus /></el-icon>
          创建签到场次
        </el-button>
        <el-button type="success" size="large" @click="viewRecords">
          <el-icon><Document /></el-icon>
          查看签到记录
        </el-button>
        <el-button type="warning" size="large" @click="manageSessions">
          <el-icon><Setting /></el-icon>
          管理签到场次
        </el-button>
      </div>
    </el-card>

    <!-- 我的课程 -->
    <el-card class="courses-card">
      <template #header>
        <div class="card-header">
          <span>我的课程</span>
          <el-button type="primary" text @click="$router.push('/teacher/sessions')">
            查看全部
          </el-button>
        </div>
      </template>

      <el-row :gutter="16">
        <el-col :span="8" v-for="course in myCourses" :key="course.id">
          <el-card class="course-item" shadow="hover">
            <div class="course-header">
              <h4>{{ course.name }}</h4>
              <el-tag size="small">{{ course.classroom_name }}</el-tag>
            </div>
            <p class="course-description">{{ course.description || '暂无描述' }}</p>
            <div class="course-footer">
              <el-button size="small" @click="viewCourseDetails(course)">
                查看详情
              </el-button>
              <el-button type="primary" size="small" @click="createSessionForCourse(course)">
                创建签到
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <!-- 最近签到场次 -->
    <el-card class="recent-sessions-card">
      <template #header>
        <div class="card-header">
          <span>最近签到场次</span>
          <el-button type="primary" text @click="$router.push('/teacher/records')">
            查看全部
          </el-button>
        </div>
      </template>

      <el-table :data="recentSessions" stripe>
        <el-table-column prop="session_name" label="场次名称" width="150" />
        <el-table-column prop="course_name" label="课程" width="120">
          <template #default="{ row }">
            {{ getCourseName(row.course_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开始时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '进行中' : '已结束' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="签到统计" min-width="200">
          <template #default="{ row }">
            <div v-if="row.stats" class="session-stats">
              <el-tag type="success" size="small">正常: {{ row.stats.present_count }}</el-tag>
              <el-tag type="warning" size="small">迟到: {{ row.stats.late_count }}</el-tag>
              <el-tag type="danger" size="small">缺勤: {{ row.stats.absent_count }}</el-tag>
            </div>
            <el-button v-else text size="small" @click="loadSessionStats(row)">
              加载统计
            </el-button>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="viewSessionDetails(row)">
              查看详情
            </el-button>
            <el-button 
              v-if="row.is_active" 
              type="warning" 
              text 
              size="small" 
              @click="closeSession(row)"
            >
              关闭签到
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建签到场次对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建签到场次" width="600px">
      <el-form
        ref="sessionFormRef"
        :model="sessionForm"
        :rules="sessionRules"
        label-width="120px"
      >
        <el-form-item label="场次名称" prop="session_name">
          <el-input v-model="sessionForm.session_name" placeholder="请输入场次名称" />
        </el-form-item>
        
        <el-form-item label="选择课程" prop="course_id">
          <el-select v-model="sessionForm.course_id" placeholder="请选择课程" style="width: 100%">
            <el-option
              v-for="course in myCourses"
              :key="course.id"
              :label="course.name"
              :value="course.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="开始时间" prop="start_time">
          <el-date-picker
            v-model="sessionForm.start_time"
            type="datetime"
            placeholder="选择开始时间"
            style="width: 100%"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        
        <el-form-item label="当日第几次">
          <el-input-number v-model="sessionForm.daily_session_count" :min="1" :max="10" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreateSession">
          {{ creating ? '创建中...' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { ElForm } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { courseAPI, attendanceAPI } from '@/api'
import type { Course, AttendanceSession, AttendanceSessionCreate } from '@/types'

const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const dashboardData = ref({
  totalCourses: 0,
  todaySessions: 0,
  todayAttendance: 0,
  activeSessions: 0
})

const myCourses = ref<Course[]>([])
const recentSessions = ref<(AttendanceSession & { stats?: any })[]>([])
const showCreateDialog = ref(false)
const creating = ref(false)
const sessionFormRef = ref<InstanceType<typeof ElForm>>()

// 表单数据
const sessionForm = reactive<AttendanceSessionCreate>({
  course_id: 0,
  session_name: '',
  start_time: '',
  daily_session_count: 1
})

// 表单验证规则
const sessionRules = {
  session_name: [{ required: true, message: '请输入场次名称', trigger: 'blur' }],
  course_id: [{ required: true, message: '请选择课程', trigger: 'change' }],
  start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }]
}

// 获取课程名称
const getCourseName = (courseId: number) => {
  const course = myCourses.value.find(c => c.id === courseId)
  return course?.name || '-'
}

// 格式化日期时间
const formatDateTime = (dateStr: string) => {
  return new Date(dateStr).toLocaleString()
}

// 加载仪表盘数据
const loadDashboardData = async () => {
  try {
    // 加载我的课程
    myCourses.value = await courseAPI.getCourses()
    
    // 加载最近的签到场次
    recentSessions.value = await attendanceAPI.getSessions()
    
    // 计算统计数据
    dashboardData.value = {
      totalCourses: myCourses.value.length,
      todaySessions: recentSessions.value.filter(s => 
        new Date(s.start_time).toDateString() === new Date().toDateString()
      ).length,
      todayAttendance: 92, // 模拟数据
      activeSessions: recentSessions.value.filter(s => s.is_active).length
    }
  } catch (error) {
    console.error('加载仪表盘数据失败:', error)
    ElMessage.error('加载仪表盘数据失败')
  }
}

// 加载签到统计
const loadSessionStats = async (session: AttendanceSession) => {
  try {
    const stats = await attendanceAPI.getStats(session.id)
    const index = recentSessions.value.findIndex(s => s.id === session.id)
    if (index !== -1) {
      recentSessions.value[index].stats = stats
    }
  } catch (error) {
    console.error('加载统计失败:', error)
    ElMessage.error('加载统计失败')
  }
}

// 创建签到场次
const createSession = () => {
  showCreateDialog.value = true
  // 设置默认开始时间为当前时间
  sessionForm.start_time = new Date().toISOString().slice(0, 19).replace('T', ' ')
}

// 为特定课程创建签到场次
const createSessionForCourse = (course: Course) => {
  sessionForm.course_id = course.id
  sessionForm.session_name = `${course.name} - ${new Date().toLocaleDateString()}`
  createSession()
}

// 处理创建签到场次
const handleCreateSession = async () => {
  if (!sessionFormRef.value) return

  try {
    const valid = await sessionFormRef.value.validate()
    if (!valid) return

    creating.value = true
    
    await attendanceAPI.createSession(sessionForm)
    
    ElMessage.success('签到场次创建成功')
    showCreateDialog.value = false
    
    // 重置表单
    Object.assign(sessionForm, {
      course_id: 0,
      session_name: '',
      start_time: '',
      daily_session_count: 1
    })
    
    // 重新加载数据
    loadDashboardData()
  } catch (error: any) {
    console.error('创建失败:', error)
    ElMessage.error(error.response?.data?.detail || '创建失败')
  } finally {
    creating.value = false
  }
}

// 查看课程详情
const viewCourseDetails = (course: Course) => {
  // 跳转到课程详情页面或显示详情对话框
  ElMessage.info(`查看课程"${course.name}"的详情`)
}

// 查看签到场次详情
const viewSessionDetails = (session: AttendanceSession) => {
  router.push(`/teacher/sessions/${session.id}`)
}

// 关闭签到场次
const closeSession = async (session: AttendanceSession) => {
  try {
    await ElMessageBox.confirm(
      `确定要关闭签到场次"${session.session_name}"吗？`,
      '确认关闭',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await attendanceAPI.closeSession(session.id)
    ElMessage.success('签到场次已关闭')
    loadDashboardData()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('关闭失败:', error)
      ElMessage.error(error.response?.data?.detail || '关闭失败')
    }
  }
}

// 快速操作
const viewRecords = () => {
  router.push('/teacher/records')
}

const manageSessions = () => {
  router.push('/teacher/sessions')
}

onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.teacher-dashboard {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.header-info {
  color: #666;
  font-size: 14px;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  .stat-item {
    display: flex;
    align-items: center;
    
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
      
      &.course-icon {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      }
      
      &.session-icon {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
      }
      
      &.attendance-icon {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
      }
      
      &.active-icon {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
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

.quick-actions-card {
  margin-bottom: 24px;
  
  .quick-actions {
    display: flex;
    gap: 16px;
    justify-content: center;
  }
}

.courses-card {
  margin-bottom: 24px;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .course-item {
    margin-bottom: 16px;
    
    .course-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
      
      h4 {
        margin: 0;
        color: #333;
      }
    }
    
    .course-description {
      color: #666;
      font-size: 14px;
      margin-bottom: 12px;
      min-height: 40px;
    }
    
    .course-footer {
      display: flex;
      justify-content: space-between;
    }
  }
}

.recent-sessions-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .session-stats {
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
  }
}
</style>