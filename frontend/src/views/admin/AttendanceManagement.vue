<template>
  <div class="attendance-management">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><Calendar /></el-icon>
        签到管理
      </h2>
    </div>

    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="课程">
          <el-select
            v-model="filterForm.course_id"
            placeholder="选择课程"
            clearable
            style="width: 200px"
            @change="loadSessions"
          >
            <el-option
              v-for="course in courses"
              :key="course.id"
              :label="course.name"
              :value="course.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="日期">
          <el-date-picker
            v-model="filterForm.date"
            type="date"
            placeholder="选择日期"
            clearable
            @change="loadSessions"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="loadSessions">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 签到场次列表 -->
    <el-card class="sessions-card">
      <template #header>
        <span>签到场次列表</span>
      </template>

      <el-table
        :data="sessions"
        v-loading="loading"
        stripe
        style="width: 100%"
        @row-click="viewDetails"
      >
        <el-table-column prop="session_name" label="场次名称" min-width="150" />
        <el-table-column prop="course_name" label="课程" width="150">
          <template #default="{ row }">
            {{ getCourseName(row.course_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开始时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="end_time" label="结束时间" width="180">
          <template #default="{ row }">
            {{ row.end_time ? formatDateTime(row.end_time) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '进行中' : '已结束' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="daily_session_count" label="当日第几次" width="120" />
        <el-table-column label="签到统计" width="200">
          <template #default="{ row }">
            <div class="stats-preview" v-if="row.stats">
              <el-tag type="success" size="small">正常: {{ row.stats.present_count }}</el-tag>
              <el-tag type="warning" size="small">迟到: {{ row.stats.late_count }}</el-tag>
              <el-tag type="danger" size="small">缺勤: {{ row.stats.absent_count }}</el-tag>
            </div>
            <el-button v-else text size="small" @click.stop="loadSessionStats(row)">
              加载统计
            </el-button>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              text
              size="small"
              @click.stop="viewDetails(row)"
            >
              查看详情
            </el-button>
            <el-button
              v-if="row.is_active"
              type="warning"
              text
              size="small"
              @click.stop="closeSession(row)"
            >
              关闭签到
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 签到详情对话框 -->
    <el-dialog
      v-model="showDetailsDialog"
      title="签到详情"
      width="800px"
      top="5vh"
    >
      <div v-if="selectedSession">
        <!-- 基本信息 -->
        <el-descriptions :column="2" border>
          <el-descriptions-item label="场次名称">
            {{ selectedSession.session_name }}
          </el-descriptions-item>
          <el-descriptions-item label="课程">
            {{ getCourseName(selectedSession.course_id) }}
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">
            {{ formatDateTime(selectedSession.start_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="结束时间">
            {{ selectedSession.end_time ? formatDateTime(selectedSession.end_time) : '进行中' }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 统计信息 -->
        <div class="stats-section" v-if="sessionStats">
          <h4>签到统计</h4>
          <el-row :gutter="16">
            <el-col :span="6">
              <el-statistic title="总人数" :value="sessionStats.total_students" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="正常签到" :value="sessionStats.present_count" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="迟到" :value="sessionStats.late_count" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="缺勤" :value="sessionStats.absent_count" />
            </el-col>
          </el-row>
          <div class="attendance-rate">
            出勤率: {{ sessionStats.attendance_rate }}%
          </div>
        </div>

        <!-- 签到记录 -->
        <div class="records-section">
          <h4>签到记录</h4>
          <el-table
            :data="sessionRecords"
            v-loading="recordsLoading"
            stripe
            size="small"
            max-height="300"
          >
            <el-table-column prop="student_name" label="学生姓名" width="120">
              <template #default="{ row }">
                {{ getStudentName(row.student_id) }}
              </template>
            </el-table-column>
            <el-table-column prop="student_id_number" label="学号" width="120">
              <template #default="{ row }">
                {{ getStudentId(row.student_id) }}
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
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { attendanceAPI, courseAPI, userAPI } from '@/api'
import type { 
  AttendanceSession, 
  Course, 
  User, 
  AttendanceRecord, 
  AttendanceStats 
} from '@/types'

// 响应式数据
const sessions = ref<(AttendanceSession & { stats?: AttendanceStats })[]>([])
const courses = ref<Course[]>([])
const students = ref<User[]>([])
const selectedSession = ref<AttendanceSession | null>(null)
const sessionStats = ref<AttendanceStats | null>(null)
const sessionRecords = ref<AttendanceRecord[]>([])
const loading = ref(false)
const recordsLoading = ref(false)
const showDetailsDialog = ref(false)

// 筛选表单
const filterForm = reactive({
  course_id: undefined as number | undefined,
  date: ''
})

// 获取课程名称
const getCourseName = (courseId: number) => {
  const course = courses.value.find(c => c.id === courseId)
  return course?.name || '-'
}

// 获取学生姓名
const getStudentName = (studentId: number) => {
  const student = students.value.find(s => s.id === studentId)
  return student?.full_name || '-'
}

// 获取学号
const getStudentId = (studentId: number) => {
  const student = students.value.find(s => s.id === studentId)
  return student?.student_id || '-'
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

// 加载签到场次
const loadSessions = async () => {
  try {
    loading.value = true
    const params: any = {}
    
    if (filterForm.course_id) {
      params.course_id = filterForm.course_id
    }
    
    if (filterForm.date) {
      params.date_filter = filterForm.date
    }
    
    sessions.value = await attendanceAPI.getSessions(params)
  } catch (error) {
    console.error('加载签到场次失败:', error)
    ElMessage.error('加载签到场次失败')
  } finally {
    loading.value = false
  }
}

// 加载课程列表
const loadCourses = async () => {
  try {
    courses.value = await courseAPI.getCourses()
  } catch (error) {
    console.error('加载课程列表失败:', error)
    ElMessage.error('加载课程列表失败')
  }
}

// 加载学生列表
const loadStudents = async () => {
  try {
    students.value = await userAPI.getUsers({ role: 'student' })
  } catch (error) {
    console.error('加载学生列表失败:', error)
    ElMessage.error('加载学生列表失败')
  }
}

// 加载签到统计
const loadSessionStats = async (session: AttendanceSession) => {
  try {
    const stats = await attendanceAPI.getStats(session.id)
    // 更新会话的统计信息
    const index = sessions.value.findIndex(s => s.id === session.id)
    if (index !== -1) {
      sessions.value[index].stats = stats
    }
  } catch (error) {
    console.error('加载统计失败:', error)
    ElMessage.error('加载统计失败')
  }
}

// 查看详情
const viewDetails = async (session: AttendanceSession) => {
  selectedSession.value = session
  showDetailsDialog.value = true
  
  try {
    recordsLoading.value = true
    
    // 并行加载统计和记录
    const [stats, records] = await Promise.all([
      attendanceAPI.getStats(session.id),
      attendanceAPI.getRecords(session.id)
    ])
    
    sessionStats.value = stats
    sessionRecords.value = records
  } catch (error) {
    console.error('加载详情失败:', error)
    ElMessage.error('加载详情失败')
  } finally {
    recordsLoading.value = false
  }
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
    loadSessions()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('关闭失败:', error)
      ElMessage.error(error.response?.data?.detail || '关闭失败')
    }
  }
}

onMounted(async () => {
  await Promise.all([
    loadSessions(),
    loadCourses(), 
    loadStudents()
  ])
})
</script>

<style scoped>
.attendance-management {
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

.filter-card {
  margin-bottom: 24px;
}

.filter-form {
  margin: 0;
}

.sessions-card {
  .stats-preview {
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
  }
}

.stats-section {
  margin: 24px 0;
  
  h4 {
    margin-bottom: 16px;
    color: #333;
  }
  
  .attendance-rate {
    margin-top: 16px;
    font-size: 16px;
    font-weight: 600;
    color: #2196f3;
  }
}

.records-section {
  h4 {
    margin-bottom: 16px;
    color: #333;
  }
}
</style>