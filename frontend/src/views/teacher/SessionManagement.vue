<template>
  <div class="session-management">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><Calendar /></el-icon>
        签到场次管理
      </h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        创建签到场次
      </el-button>
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
              v-for="course in myCourses"
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
        
        <el-form-item label="状态">
          <el-select
            v-model="filterForm.status"
            placeholder="选择状态"
            clearable
            style="width: 120px"
            @change="filterSessions"
          >
            <el-option label="进行中" value="active" />
            <el-option label="已结束" value="inactive" />
          </el-select>
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
    <el-card class="sessions-list-card">
      <template #header>
        <div class="card-header">
          <span>签到场次列表</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索场次名称..."
              prefix-icon="Search"
              clearable
              style="width: 250px"
            />
          </div>
        </div>
      </template>

      <el-table
        :data="filteredSessions"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="session_name" label="场次名称" min-width="150" />
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
        <el-table-column label="签到统计" width="250">
          <template #default="{ row }">
            <div v-if="row.stats" class="session-stats">
              <el-progress
                :percentage="row.stats.attendance_rate"
                :status="getProgressStatus(row.stats.attendance_rate)"
                :show-text="false"
                style="margin-bottom: 4px;"
              />
              <div class="stats-detail">
                <el-tag type="success" size="small">正常: {{ row.stats.present_count }}</el-tag>
                <el-tag type="warning" size="small">迟到: {{ row.stats.late_count }}</el-tag>
                <el-tag type="danger" size="small">缺勤: {{ row.stats.absent_count }}</el-tag>
              </div>
            </div>
            <el-button v-else text size="small" @click="loadSessionStats(row)">
              加载统计
            </el-button>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              text
              size="small"
              @click="viewDetails(row)"
            >
              查看详情
            </el-button>
            <el-button
              type="info"
              text
              size="small"
              @click="editSession(row)"
            >
              编辑
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
            <el-button
              type="danger"
              text
              size="small"
              @click="deleteSession(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑签到场次对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="isEdit ? '编辑签到场次' : '创建签到场次'"
      width="600px"
    >
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
        
        <el-form-item label="结束时间">
          <el-date-picker
            v-model="sessionForm.end_time"
            type="datetime"
            placeholder="选择结束时间（可选）"
            style="width: 100%"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        
        <el-form-item label="当日第几次">
          <el-input-number 
            v-model="sessionForm.daily_session_count" 
            :min="1" 
            :max="10" 
            placeholder="当日第几次签到"
          />
          <span class="form-tip">* 如果一天有多次签到，请标注这是第几次</span>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ submitting ? '提交中...' : '确定' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 签到详情对话框 -->
    <el-dialog
      v-model="showDetailsDialog"
      title="签到详情"
      width="900px"
      top="5vh"
    >
      <div v-if="selectedSession">
        <!-- 基本信息 -->
        <el-descriptions :column="3" border class="session-info">
          <el-descriptions-item label="场次名称">
            {{ selectedSession.session_name }}
          </el-descriptions-item>
          <el-descriptions-item label="课程">
            {{ getCourseName(selectedSession.course_id) }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="selectedSession.is_active ? 'success' : 'info'">
              {{ selectedSession.is_active ? '进行中' : '已结束' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">
            {{ formatDateTime(selectedSession.start_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="结束时间">
            {{ selectedSession.end_time ? formatDateTime(selectedSession.end_time) : '进行中' }}
          </el-descriptions-item>
          <el-descriptions-item label="当日第几次">
            第{{ selectedSession.daily_session_count }}次
          </el-descriptions-item>
        </el-descriptions>

        <!-- 统计信息 -->
        <div class="stats-section" v-if="sessionStats">
          <h4>签到统计</h4>
          <el-row :gutter="16">
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-number">{{ sessionStats.total_students }}</div>
                <div class="stat-label">总人数</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-number">{{ sessionStats.present_count }}</div>
                <div class="stat-label">正常签到</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-number">{{ sessionStats.late_count }}</div>
                <div class="stat-label">迟到</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-number">{{ sessionStats.absent_count }}</div>
                <div class="stat-label">缺勤</div>
              </div>
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
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-button text size="small" @click="viewSignature(row)">
                  查看签名
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { attendanceAPI, courseAPI, userAPI } from '@/api'
import type { 
  AttendanceSession, 
  AttendanceSessionCreate, 
  Course, 
  User, 
  AttendanceRecord, 
  AttendanceStats 
} from '@/types'

// 响应式数据
const sessions = ref<(AttendanceSession & { stats?: AttendanceStats })[]>([])
const allSessions = ref<(AttendanceSession & { stats?: AttendanceStats })[]>([])
const myCourses = ref<Course[]>([])
const students = ref<User[]>([])
const selectedSession = ref<AttendanceSession | null>(null)
const sessionStats = ref<AttendanceStats | null>(null)
const sessionRecords = ref<AttendanceRecord[]>([])
const loading = ref(false)
const recordsLoading = ref(false)
const submitting = ref(false)
const showCreateDialog = ref(false)
const showDetailsDialog = ref(false)
const isEdit = ref(false)
const searchKeyword = ref('')
const sessionFormRef = ref<FormInstance>()

// 筛选表单
const filterForm = reactive({
  course_id: undefined as number | undefined,
  date: '',
  status: ''
})

// 表单数据
const sessionForm = reactive<AttendanceSessionCreate & { id?: number; end_time?: string }>({
  course_id: 0,
  session_name: '',
  start_time: '',
  end_time: undefined,
  daily_session_count: 1
})

// 表单验证规则
const sessionRules = {
  session_name: [{ required: true, message: '请输入场次名称', trigger: 'blur' }],
  course_id: [{ required: true, message: '请选择课程', trigger: 'change' }],
  start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }]
}

// 计算属性
const filteredSessions = computed(() => {
  let result = sessions.value
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(session =>
      session.session_name.toLowerCase().includes(keyword) ||
      getCourseName(session.course_id).toLowerCase().includes(keyword)
    )
  }
  
  return result
})

// 获取课程名称
const getCourseName = (courseId: number) => {
  const course = myCourses.value.find(c => c.id === courseId)
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

// 获取进度条状态
const getProgressStatus = (rate: number) => {
  if (rate >= 90) return 'success'
  if (rate >= 70) return 'warning'
  return 'exception'
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
    
    allSessions.value = await attendanceAPI.getSessions(params)
    filterSessions()
  } catch (error) {
    console.error('加载签到场次失败:', error)
    ElMessage.error('加载签到场次失败')
  } finally {
    loading.value = false
  }
}

// 筛选场次
const filterSessions = () => {
  let result = allSessions.value
  
  if (filterForm.status === 'active') {
    result = result.filter(s => s.is_active)
  } else if (filterForm.status === 'inactive') {
    result = result.filter(s => !s.is_active)
  }
  
  sessions.value = result
}

// 加载课程列表
const loadCourses = async () => {
  try {
    myCourses.value = await courseAPI.getCourses()
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
    const index = sessions.value.findIndex(s => s.id === session.id)
    if (index !== -1) {
      sessions.value[index].stats = stats
    }
  } catch (error) {
    console.error('加载统计失败:', error)
    ElMessage.error('加载统计失败')
  }
}

// 重置表单
const resetForm = () => {
  Object.assign(sessionForm, {
    course_id: 0,
    session_name: '',
    start_time: '',
    end_time: undefined,
    daily_session_count: 1
  })
  delete sessionForm.id
  isEdit.value = false
}

// 编辑场次
const editSession = (session: AttendanceSession) => {
  isEdit.value = true
  Object.assign(sessionForm, {
    ...session,
    start_time: session.start_time.replace('T', ' ').slice(0, 19),
    end_time: session.end_time ? session.end_time.replace('T', ' ').slice(0, 19) : undefined
  })
  showCreateDialog.value = true
}

// 处理提交
const handleSubmit = async () => {
  if (!sessionFormRef.value) return

  try {
    const valid = await sessionFormRef.value.validate()
    if (!valid) return

    submitting.value = true

    if (isEdit.value) {
      // 编辑模式 - 这里需要后端支持更新API
      ElMessage.info('编辑功能待实现')
    } else {
      // 创建模式
      await attendanceAPI.createSession(sessionForm)
      ElMessage.success('签到场次创建成功')
      showCreateDialog.value = false
      resetForm()
      loadSessions()
    }
  } catch (error: any) {
    console.error('操作失败:', error)
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
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

// 删除场次
const deleteSession = async (session: AttendanceSession) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除签到场次"${session.session_name}"吗？此操作不可恢复！`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 这里需要后端支持删除API
    ElMessage.info('删除功能待实现')
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

// 查看签名
const viewSignature = (record: AttendanceRecord) => {
  // 这里可以打开签名查看对话框
  ElMessage.info('查看签名功能待实现')
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
.session-management {
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

.filter-card {
  margin-bottom: 24px;
}

.filter-form {
  margin: 0;
}

.sessions-list-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .session-stats {
    .stats-detail {
      display: flex;
      gap: 4px;
      flex-wrap: wrap;
    }
  }
}

.form-tip {
  color: #999;
  font-size: 12px;
  margin-left: 8px;
}

.session-info {
  margin-bottom: 24px;
}

.stats-section {
  margin: 24px 0;
  
  h4 {
    margin-bottom: 16px;
    color: #333;
  }
  
  .stat-item {
    text-align: center;
    
    .stat-number {
      font-size: 24px;
      font-weight: 600;
      color: #2196f3;
    }
    
    .stat-label {
      color: #666;
      font-size: 14px;
      margin-top: 4px;
    }
  }
  
  .attendance-rate {
    margin-top: 16px;
    text-align: center;
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