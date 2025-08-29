<template>
  <div class="attendance-records">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><Document /></el-icon>
        签到记录
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
              v-for="course in myCourses"
              :key="course.id"
              :label="course.name"
              :value="course.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="签到场次">
          <el-select
            v-model="filterForm.session_id"
            placeholder="选择签到场次"
            clearable
            style="width: 250px"
            @change="loadRecords"
          >
            <el-option
              v-for="session in sessions"
              :key="session.id"
              :label="`${session.session_name} (${formatDateTime(session.start_time)})`"
              :value="session.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="签到状态">
          <el-select
            v-model="filterForm.status"
            placeholder="选择状态"
            clearable
            style="width: 120px"
            @change="filterRecords"
          >
            <el-option label="正常" value="present" />
            <el-option label="迟到" value="late" />
            <el-option label="缺勤" value="absent" />
            <el-option label="早退" value="early_leave" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            @change="loadSessions"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="applyFilter">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="resetFilter">
            <el-icon><RefreshLeft /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="24" class="stats-row" v-if="recordsStats">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-icon total-icon">
              <el-icon><UserFilled /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ recordsStats.totalRecords }}</div>
              <div class="stat-label">总记录数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-icon present-icon">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ recordsStats.presentCount }}</div>
              <div class="stat-label">正常签到</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-icon late-icon">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ recordsStats.lateCount }}</div>
              <div class="stat-label">迟到次数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-icon absent-icon">
              <el-icon><CircleClose /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ recordsStats.absentCount }}</div>
              <div class="stat-label">缺勤次数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 签到记录表格 -->
    <el-card class="records-table-card">
      <template #header>
        <div class="card-header">
          <span>签到记录</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索学生姓名或学号..."
              prefix-icon="Search"
              clearable
              style="width: 250px; margin-right: 12px"
            />
            <el-button type="success" @click="exportRecords">
              <el-icon><Download /></el-icon>
              导出记录
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="filteredRecords"
        v-loading="loading"
        stripe
        style="width: 100%"
        @sort-change="handleSortChange"
      >
        <el-table-column prop="session_name" label="签到场次" width="150">
          <template #default="{ row }">
            {{ getSessionName(row.session_id) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="course_name" label="课程" width="120">
          <template #default="{ row }">
            {{ getCourseName(row.session_id) }}
          </template>
        </el-table-column>
        
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
        
        <el-table-column prop="status" label="签到状态" width="100" :filters="statusFilters" :filter-method="filterStatus">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="signin_time" label="签到时间" width="180" sortable="custom">
          <template #default="{ row }">
            {{ formatDateTime(row.signin_time) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="notes" label="备注" min-width="150">
          <template #default="{ row }">
            {{ row.notes || '-' }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="viewDetails(row)">
              查看详情
            </el-button>
            <el-button type="info" text size="small" @click="viewSignature(row)">
              查看签名
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :small="false"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 记录详情对话框 -->
    <el-dialog v-model="showDetailsDialog" title="签到记录详情" width="600px">
      <div v-if="selectedRecord">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="学生姓名">
            {{ getStudentName(selectedRecord.student_id) }}
          </el-descriptions-item>
          <el-descriptions-item label="学号">
            {{ getStudentId(selectedRecord.student_id) }}
          </el-descriptions-item>
          <el-descriptions-item label="签到场次">
            {{ getSessionName(selectedRecord.session_id) }}
          </el-descriptions-item>
          <el-descriptions-item label="课程">
            {{ getCourseName(selectedRecord.session_id) }}
          </el-descriptions-item>
          <el-descriptions-item label="签到状态">
            <el-tag :type="getStatusType(selectedRecord.status)">
              {{ getStatusText(selectedRecord.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="签到时间">
            {{ formatDateTime(selectedRecord.signin_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">
            {{ selectedRecord.notes || '无' }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 签名显示 -->
        <div class="signature-section" v-if="selectedRecord.signature_id">
          <h4>签名记录</h4>
          <div class="signature-container">
            <img :src="signatureImage" alt="学生签名" class="signature-image" />
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 签名查看对话框 -->
    <el-dialog v-model="showSignatureDialog" title="学生签名" width="700px">
      <div class="signature-viewer">
        <div class="signature-info">
          <p><strong>学生:</strong> {{ selectedRecord ? getStudentName(selectedRecord.student_id) : '' }}</p>
          <p><strong>签到时间:</strong> {{ selectedRecord ? formatDateTime(selectedRecord.signin_time) : '' }}</p>
        </div>
        <div class="signature-display">
          <img :src="signatureImage" alt="学生签名" class="signature-image" />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { attendanceAPI, courseAPI, userAPI } from '@/api'
import type { 
  AttendanceRecord, 
  AttendanceSession, 
  Course, 
  User 
} from '@/types'

// 响应式数据
const records = ref<AttendanceRecord[]>([])
const allRecords = ref<AttendanceRecord[]>([])
const sessions = ref<AttendanceSession[]>([])
const myCourses = ref<Course[]>([])
const students = ref<User[]>([])
const selectedRecord = ref<AttendanceRecord | null>(null)
const loading = ref(false)
const showDetailsDialog = ref(false)
const showSignatureDialog = ref(false)
const searchKeyword = ref('')
const signatureImage = ref('')

// 统计数据
const recordsStats = ref<{
  totalRecords: number
  presentCount: number
  lateCount: number
  absentCount: number
} | null>(null)

// 筛选表单
const filterForm = reactive({
  course_id: undefined as number | undefined,
  session_id: undefined as number | undefined,
  status: '',
  dateRange: [] as string[]
})

// 分页
const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

// 状态筛选选项
const statusFilters = [
  { text: '正常', value: 'present' },
  { text: '迟到', value: 'late' },
  { text: '缺勤', value: 'absent' },
  { text: '早退', value: 'early_leave' }
]

// 计算属性
const filteredRecords = computed(() => {
  let result = records.value
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(record => {
      const studentName = getStudentName(record.student_id).toLowerCase()
      const studentId = getStudentId(record.student_id).toLowerCase()
      return studentName.includes(keyword) || studentId.includes(keyword)
    })
  }
  
  // 更新统计
  updateStats(result)
  
  return result
})

// 获取会话名称
const getSessionName = (sessionId: number) => {
  const session = sessions.value.find(s => s.id === sessionId)
  return session?.session_name || '-'
}

// 获取课程名称
const getCourseName = (sessionId: number) => {
  const session = sessions.value.find(s => s.id === sessionId)
  if (!session) return '-'
  const course = myCourses.value.find(c => c.id === session.course_id)
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

// 更新统计数据
const updateStats = (data: AttendanceRecord[]) => {
  recordsStats.value = {
    totalRecords: data.length,
    presentCount: data.filter(r => r.status === 'present').length,
    lateCount: data.filter(r => r.status === 'late').length,
    absentCount: data.filter(r => r.status === 'absent').length
  }
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

// 加载签到场次
const loadSessions = async () => {
  try {
    const params: any = {}
    
    if (filterForm.course_id) {
      params.course_id = filterForm.course_id
    }
    
    if (filterForm.dateRange && filterForm.dateRange.length === 2) {
      params.start_date = filterForm.dateRange[0]
      params.end_date = filterForm.dateRange[1]
    }
    
    sessions.value = await attendanceAPI.getSessions(params)
    
    // 如果选择了特定课程，自动加载该课程的记录
    if (filterForm.course_id && sessions.value.length > 0) {
      loadAllRecords()
    }
  } catch (error) {
    console.error('加载签到场次失败:', error)
    ElMessage.error('加载签到场次失败')
  }
}

// 加载签到记录
const loadRecords = async () => {
  if (!filterForm.session_id) {
    records.value = []
    return
  }
  
  try {
    loading.value = true
    records.value = await attendanceAPI.getRecords(filterForm.session_id)
  } catch (error) {
    console.error('加载签到记录失败:', error)
    ElMessage.error('加载签到记录失败')
  } finally {
    loading.value = false
  }
}

// 加载所有记录（当选择课程时）
const loadAllRecords = async () => {
  try {
    loading.value = true
    let allRecordsData: AttendanceRecord[] = []
    
    // 加载所有场次的记录
    for (const session of sessions.value) {
      try {
        const sessionRecords = await attendanceAPI.getRecords(session.id)
        allRecordsData = [...allRecordsData, ...sessionRecords]
      } catch (error) {
        console.warn(`加载场次 ${session.id} 的记录失败:`, error)
      }
    }
    
    allRecords.value = allRecordsData
    filterRecords()
  } catch (error) {
    console.error('加载签到记录失败:', error)
    ElMessage.error('加载签到记录失败')
  } finally {
    loading.value = false
  }
}

// 筛选记录
const filterRecords = () => {
  let result = allRecords.value
  
  if (filterForm.status) {
    result = result.filter(r => r.status === filterForm.status)
  }
  
  records.value = result
}

// 应用筛选
const applyFilter = () => {
  if (filterForm.session_id) {
    loadRecords()
  } else if (filterForm.course_id) {
    loadAllRecords()
  }
}

// 重置筛选
const resetFilter = () => {
  Object.assign(filterForm, {
    course_id: undefined,
    session_id: undefined,
    status: '',
    dateRange: []
  })
  records.value = []
  sessions.value = []
}

// 状态筛选
const filterStatus = (value: string, row: AttendanceRecord) => {
  return row.status === value
}

// 排序处理
const handleSortChange = ({ column, prop, order }: any) => {
  // 实现排序逻辑
  if (prop === 'signin_time') {
    records.value.sort((a, b) => {
      const timeA = new Date(a.signin_time).getTime()
      const timeB = new Date(b.signin_time).getTime()
      return order === 'ascending' ? timeA - timeB : timeB - timeA
    })
  }
}

// 分页处理
const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  // 重新加载数据
}

const handleCurrentChange = (val: number) => {
  pagination.currentPage = val
  // 重新加载数据
}

// 查看详情
const viewDetails = async (record: AttendanceRecord) => {
  selectedRecord.value = record
  showDetailsDialog.value = true
  
  // 加载签名图片（模拟）
  if (record.signature_id) {
    // 这里应该调用API获取签名图片
    signatureImage.value = '/api/signatures/' + record.signature_id
  }
}

// 查看签名
const viewSignature = async (record: AttendanceRecord) => {
  selectedRecord.value = record
  showSignatureDialog.value = true
  
  // 加载签名图片（模拟）
  if (record.signature_id) {
    // 这里应该调用API获取签名图片
    signatureImage.value = '/api/signatures/' + record.signature_id
  }
}

// 导出记录
const exportRecords = () => {
  ElMessage.info('导出功能开发中...')
}

onMounted(async () => {
  await Promise.all([
    loadCourses(),
    loadStudents()
  ])
})
</script>

<style scoped>
.attendance-records {
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

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  .stat-item {
    display: flex;
    align-items: center;
    
    .stat-icon {
      width: 50px;
      height: 50px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 12px;
      
      .el-icon {
        font-size: 20px;
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
      
      &.absent-icon {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
      }
    }
    
    .stat-content {
      .stat-number {
        font-size: 24px;
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

.records-table-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .header-actions {
    display: flex;
    align-items: center;
  }
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.signature-section {
  margin-top: 24px;
  
  h4 {
    margin-bottom: 12px;
    color: #333;
  }
  
  .signature-container {
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    padding: 16px;
    text-align: center;
    background-color: #fafafa;
  }
  
  .signature-image {
    max-width: 100%;
    max-height: 200px;
  }
}

.signature-viewer {
  .signature-info {
    margin-bottom: 16px;
    padding: 12px;
    background-color: #f8f9fa;
    border-radius: 4px;
    
    p {
      margin: 4px 0;
      color: #333;
    }
  }
  
  .signature-display {
    text-align: center;
    padding: 20px;
    border: 2px dashed #dcdfe6;
    border-radius: 8px;
    background-color: #fafafa;
  }
  
  .signature-image {
    max-width: 100%;
    max-height: 300px;
    border: 1px solid #ddd;
    border-radius: 4px;
  }
}
</style>