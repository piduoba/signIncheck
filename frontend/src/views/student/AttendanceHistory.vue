<template>
  <div class="attendance-history">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><Clock /></el-icon>
        签到历史
      </h2>
    </div>

    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm:ss"
            @change="applyFilter"
          />
        </el-form-item>
        
        <el-form-item label="签到状态">
          <el-select
            v-model="filterForm.status"
            placeholder="选择状态"
            clearable
            style="width: 120px"
            @change="applyFilter"
          >
            <el-option label="正常" value="present" />
            <el-option label="迟到" value="late" />
            <el-option label="缺勤" value="absent" />
            <el-option label="早退" value="early_leave" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="课程">
          <el-input
            v-model="filterForm.courseName"
            placeholder="搜索课程名称"
            clearable
            style="width: 200px"
            @input="applyFilter"
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

    <!-- 统计信息 -->
    <el-row :gutter="24" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-icon total-icon">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ historyStats.totalRecords }}</div>
              <div class="stat-label">总签到次数</div>
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
              <div class="stat-number">{{ historyStats.presentCount }}</div>
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
              <div class="stat-number">{{ historyStats.lateCount }}</div>
              <div class="stat-label">迟到次数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-icon rate-icon">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ historyStats.attendanceRate }}%</div>
              <div class="stat-label">出勤率</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 签到历史表格 -->
    <el-card class="history-table-card">
      <template #header>
        <div class="card-header">
          <span>签到记录</span>
          <div class="header-actions">
            <el-button type="success" @click="exportHistory">
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
        
        <el-table-column prop="status" label="签到状态" width="100" :filters="statusFilters" :filter-method="filterByStatus">
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
        
        <el-table-column prop="session_start_time" label="课程开始时间" width="180">
          <template #default="{ row }">
            {{ getSessionStartTime(row.session_id) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="delay_time" label="迟到时长" width="100">
          <template #default="{ row }">
            {{ calculateDelayTime(row) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="notes" label="备注" min-width="150">
          <template #default="{ row }">
            {{ row.notes || '-' }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="120" fixed="right">
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
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>

      <!-- 空状态 -->
      <div v-if="filteredRecords.length === 0 && !loading" class="empty-state">
        <el-empty description="暂无签到记录" />
      </div>
    </el-card>

    <!-- 签到详情对话框 -->
    <el-dialog v-model="showDetailsDialog" title="签到详情" width="600px">
      <div v-if="selectedRecord">
        <el-descriptions :column="2" border>
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
          <el-descriptions-item label="课程开始时间">
            {{ getSessionStartTime(selectedRecord.session_id) }}
          </el-descriptions-item>
          <el-descriptions-item label="迟到时长">
            {{ calculateDelayTime(selectedRecord) }}
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">
            {{ selectedRecord.notes || '无' }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 签名预览 -->
        <div class="signature-section" v-if="selectedRecord.signature_id">
          <h4>签名记录</h4>
          <div class="signature-container">
            <img :src="signatureImage" alt="签名" class="signature-image" />
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 签名查看对话框 -->
    <el-dialog v-model="showSignatureDialog" title="我的签名" width="700px">
      <div class="signature-viewer">
        <div class="signature-info">
          <p><strong>签到场次:</strong> {{ selectedRecord ? getSessionName(selectedRecord.session_id) : '' }}</p>
          <p><strong>签到时间:</strong> {{ selectedRecord ? formatDateTime(selectedRecord.signin_time) : '' }}</p>
        </div>
        <div class="signature-display">
          <img :src="signatureImage" alt="我的签名" class="signature-image" />
        </div>
      </div>
    </el-dialog>

    <!-- 导出对话框 -->
    <el-dialog v-model="showExportDialog" title="导出签到记录" width="400px">
      <div class="export-options">
        <el-form :model="exportForm" label-width="100px">
          <el-form-item label="导出格式">
            <el-radio-group v-model="exportForm.format">
              <el-radio value="excel">Excel文件</el-radio>
              <el-radio value="pdf">PDF文件</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item label="时间范围">
            <el-date-picker
              v-model="exportForm.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
            />
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <el-button @click="showExportDialog = false">取消</el-button>
        <el-button type="primary" :loading="exporting" @click="handleExport">
          {{ exporting ? '导出中...' : '确定导出' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import type { AttendanceRecord, AttendanceSession } from '@/types'

const userStore = useUserStore()

// 响应式数据
const records = ref<AttendanceRecord[]>([])
const allRecords = ref<AttendanceRecord[]>([])
const sessions = ref<AttendanceSession[]>([])
const selectedRecord = ref<AttendanceRecord | null>(null)
const loading = ref(false)
const exporting = ref(false)
const showDetailsDialog = ref(false)
const showSignatureDialog = ref(false)
const showExportDialog = ref(false)
const signatureImage = ref('')

// 筛选表单
const filterForm = reactive({
  dateRange: [] as string[],
  status: '',
  courseName: ''
})

// 导出表单
const exportForm = reactive({
  format: 'excel',
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

// 统计数据
const historyStats = computed(() => {
  const totalRecords = filteredRecords.value.length
  const presentCount = filteredRecords.value.filter(r => r.status === 'present').length
  const lateCount = filteredRecords.value.filter(r => r.status === 'late').length
  const attendanceRate = totalRecords > 0 ? Math.round((presentCount + lateCount) / totalRecords * 100) : 0

  return {
    totalRecords,
    presentCount,
    lateCount,
    attendanceRate
  }
})

// 筛选后的记录
const filteredRecords = computed(() => {
  let result = records.value

  // 时间范围筛选
  if (filterForm.dateRange && filterForm.dateRange.length === 2) {
    const startTime = new Date(filterForm.dateRange[0]).getTime()
    const endTime = new Date(filterForm.dateRange[1]).getTime()
    result = result.filter(record => {
      const recordTime = new Date(record.signin_time).getTime()
      return recordTime >= startTime && recordTime <= endTime
    })
  }

  // 状态筛选
  if (filterForm.status) {
    result = result.filter(record => record.status === filterForm.status)
  }

  // 课程名称筛选
  if (filterForm.courseName) {
    const keyword = filterForm.courseName.toLowerCase()
    result = result.filter(record => {
      const courseName = getCourseName(record.session_id).toLowerCase()
      return courseName.includes(keyword)
    })
  }

  pagination.total = result.length
  
  // 分页
  const start = (pagination.currentPage - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return result.slice(start, end)
})

// 获取会话名称
const getSessionName = (sessionId: number) => {
  const session = sessions.value.find(s => s.id === sessionId)
  return session?.session_name || '-'
}

// 获取课程名称
const getCourseName = (sessionId: number) => {
  // 模拟通过session获取课程名称
  return '数学课程'
}

// 获取会话开始时间
const getSessionStartTime = (sessionId: number) => {
  const session = sessions.value.find(s => s.id === sessionId)
  return session ? formatDateTime(session.start_time) : '-'
}

// 计算迟到时长
const calculateDelayTime = (record: AttendanceRecord) => {
  if (record.status !== 'late') return '-'
  
  const session = sessions.value.find(s => s.id === record.session_id)
  if (!session) return '-'
  
  const startTime = new Date(session.start_time).getTime()
  const signinTime = new Date(record.signin_time).getTime()
  const delayMinutes = Math.round((signinTime - startTime) / (1000 * 60))
  
  return delayMinutes > 0 ? `${delayMinutes}分钟` : '-'
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

// 状态筛选方法
const filterByStatus = (value: string, row: AttendanceRecord) => {
  return row.status === value
}

// 排序处理
const handleSortChange = ({ prop, order }: any) => {
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
  pagination.currentPage = 1
}

const handleCurrentChange = (val: number) => {
  pagination.currentPage = val
}

// 应用筛选
const applyFilter = () => {
  pagination.currentPage = 1
  // 筛选逻辑在计算属性中处理
}

// 重置筛选
const resetFilter = () => {
  Object.assign(filterForm, {
    dateRange: [],
    status: '',
    courseName: ''
  })
  pagination.currentPage = 1
}

// 查看详情
const viewDetails = async (record: AttendanceRecord) => {
  selectedRecord.value = record
  showDetailsDialog.value = true
  
  // 加载签名图片
  if (record.signature_id) {
    signatureImage.value = `data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==`
  }
}

// 查看签名
const viewSignature = (record: AttendanceRecord) => {
  selectedRecord.value = record
  showSignatureDialog.value = true
  
  // 加载签名图片
  if (record.signature_id) {
    signatureImage.value = `data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==`
  }
}

// 导出历史
const exportHistory = () => {
  showExportDialog.value = true
}

// 处理导出
const handleExport = async () => {
  try {
    exporting.value = true
    
    // 模拟导出过程
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    ElMessage.success(`${exportForm.format === 'excel' ? 'Excel' : 'PDF'}文件导出成功`)
    showExportDialog.value = false
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

// 加载签到历史
const loadAttendanceHistory = async () => {
  if (!userStore.user) return

  try {
    loading.value = true
    
    // 模拟加载学生的签到历史
    // 实际应该调用学生签到历史API
    
    // 模拟数据
    records.value = [
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
      },
      {
        id: 3,
        session_id: 3,
        student_id: userStore.user.id,
        status: 'present',
        signin_time: '2024-01-13 08:28:00',
        signature_id: 3,
        notes: ''
      },
      {
        id: 4,
        session_id: 4,
        student_id: userStore.user.id,
        status: 'absent',
        signin_time: '',
        signature_id: undefined,
        notes: '生病请假'
      }
    ]

    // 模拟会话数据
    sessions.value = [
      {
        id: 1,
        course_id: 1,
        session_name: '第一次签到',
        start_time: '2024-01-15 08:30:00',
        end_time: undefined,
        is_active: false,
        daily_session_count: 1,
        created_at: '2024-01-15 08:00:00'
      },
      {
        id: 2,
        course_id: 1,
        session_name: '第二次签到',
        start_time: '2024-01-14 08:30:00',
        end_time: '2024-01-14 10:30:00',
        is_active: false,
        daily_session_count: 1,
        created_at: '2024-01-14 08:00:00'
      }
    ]

    allRecords.value = [...records.value]

  } catch (error) {
    console.error('加载签到历史失败:', error)
    ElMessage.error('加载签到历史失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadAttendanceHistory()
})
</script>

<style scoped>
.attendance-history {
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
    padding: 16px;
    
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
      
      &.rate-icon {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
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

.history-table-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .pagination-container {
    margin-top: 20px;
    text-align: right;
  }
  
  .empty-state {
    padding: 40px 0;
  }
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

.export-options {
  padding: 20px 0;
}
</style>