<template>
  <div class="report-management">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><Document /></el-icon>
        报表管理
      </h2>
    </div>

    <!-- 报表筛选 -->
    <el-card class="filter-card">
      <template #header>
        <span>报表筛选条件</span>
      </template>
      
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
          />
        </el-form-item>
        
        <el-form-item label="课程">
          <el-select
            v-model="filterForm.course_id"
            placeholder="选择课程"
            clearable
            style="width: 200px"
          >
            <el-option
              v-for="course in courses"
              :key="course.id"
              :label="course.name"
              :value="course.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="老师">
          <el-select
            v-model="filterForm.teacher_id"
            placeholder="选择老师"
            clearable
            style="width: 160px"
          >
            <el-option
              v-for="teacher in teachers"
              :key="teacher.id"
              :label="teacher.full_name"
              :value="teacher.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="generateReport">
            <el-icon><Search /></el-icon>
            生成报表
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 报表概览 -->
    <el-row :gutter="24" v-if="reportData">
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="总签到次数" :value="reportData.totalSessions" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="总学生数" :value="reportData.totalStudents" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="平均出勤率" :value="reportData.averageAttendanceRate" suffix="%" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="迟到次数" :value="reportData.totalLateCount" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表展示 -->
    <el-row :gutter="24" v-if="reportData">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>出勤率趋势</span>
          </template>
          <div ref="attendanceChartRef" style="height: 300px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>签到状态分布</span>
          </template>
          <div ref="statusChartRef" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 详细数据表格 -->
    <el-card class="table-card" v-if="reportData">
      <template #header>
        <div class="table-header">
          <span>详细签到记录</span>
          <div class="header-actions">
            <el-button type="success" @click="exportExcel">
              <el-icon><Download /></el-icon>
              导出Excel
            </el-button>
            <el-button type="primary" @click="exportPDF">
              <el-icon><Download /></el-icon>
              导出PDF
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="reportData.detailRecords"
        v-loading="loading"
        stripe
        style="width: 100%"
        max-height="400"
      >
        <el-table-column prop="sessionName" label="签到场次" width="150" />
        <el-table-column prop="courseName" label="课程" width="120" />
        <el-table-column prop="teacherName" label="老师" width="100" />
        <el-table-column prop="studentName" label="学生" width="100" />
        <el-table-column prop="studentId" label="学号" width="120" />
        <el-table-column prop="status" label="签到状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="signinTime" label="签到时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.signinTime) }}
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" min-width="150">
          <template #default="{ row }">
            {{ row.notes || '-' }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 导出进度对话框 -->
    <el-dialog v-model="showExportDialog" title="导出进度" width="400px" :close-on-click-modal="false">
      <div class="export-progress">
        <el-progress :percentage="exportProgress" />
        <p class="progress-text">{{ exportProgressText }}</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { courseAPI, userAPI, attendanceAPI } from '@/api'
import type { Course, User } from '@/types'

// 响应式数据
const courses = ref<Course[]>([])
const teachers = ref<User[]>([])
const reportData = ref<any>(null)
const loading = ref(false)
const showExportDialog = ref(false)
const exportProgress = ref(0)
const exportProgressText = ref('')

// 图表引用
const attendanceChartRef = ref<HTMLElement>()
const statusChartRef = ref<HTMLElement>()

// 筛选表单
const filterForm = reactive({
  dateRange: [] as string[],
  course_id: undefined as number | undefined,
  teacher_id: undefined as number | undefined
})

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

// 加载课程列表
const loadCourses = async () => {
  try {
    courses.value = await courseAPI.getCourses()
  } catch (error) {
    console.error('加载课程列表失败:', error)
    ElMessage.error('加载课程列表失败')
  }
}

// 加载老师列表
const loadTeachers = async () => {
  try {
    teachers.value = await userAPI.getUsers({ role: 'teacher' })
  } catch (error) {
    console.error('加载老师列表失败:', error)
    ElMessage.error('加载老师列表失败')
  }
}

// 生成报表
const generateReport = async () => {
  try {
    loading.value = true
    
    // 模拟生成报表数据
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 这里应该调用实际的报表API
    reportData.value = {
      totalSessions: 45,
      totalStudents: 120,
      averageAttendanceRate: 92.5,
      totalLateCount: 23,
      attendanceTrend: [
        { date: '2024-01-01', rate: 90 },
        { date: '2024-01-02', rate: 95 },
        { date: '2024-01-03', rate: 88 },
        { date: '2024-01-04', rate: 92 },
        { date: '2024-01-05', rate: 96 }
      ],
      statusDistribution: [
        { name: '正常', value: 850 },
        { name: '迟到', value: 45 },
        { name: '缺勤', value: 25 },
        { name: '早退', value: 10 }
      ],
      detailRecords: [
        {
          sessionName: '第一次签到',
          courseName: '数学',
          teacherName: '张老师',
          studentName: '李同学',
          studentId: '20240001',
          status: 'present',
          signinTime: '2024-01-01 08:30:00',
          notes: ''
        }
        // 更多记录...
      ]
    }
    
    // 生成图表
    await nextTick()
    generateCharts()
    
    ElMessage.success('报表生成成功')
  } catch (error) {
    console.error('生成报表失败:', error)
    ElMessage.error('生成报表失败')
  } finally {
    loading.value = false
  }
}

// 生成图表
const generateCharts = () => {
  if (!reportData.value) return
  
  // 出勤率趋势图
  if (attendanceChartRef.value) {
    const chart = echarts.init(attendanceChartRef.value)
    chart.setOption({
      title: {
        text: '出勤率趋势',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: reportData.value.attendanceTrend.map((item: any) => item.date)
      },
      yAxis: {
        type: 'value',
        min: 0,
        max: 100,
        axisLabel: {
          formatter: '{value}%'
        }
      },
      series: [{
        name: '出勤率',
        type: 'line',
        data: reportData.value.attendanceTrend.map((item: any) => item.rate),
        smooth: true,
        lineStyle: {
          color: '#2196f3'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [{
              offset: 0, color: 'rgba(33, 150, 243, 0.3)'
            }, {
              offset: 1, color: 'rgba(33, 150, 243, 0.1)'
            }]
          }
        }
      }]
    })
  }
  
  // 签到状态分布饼图
  if (statusChartRef.value) {
    const chart = echarts.init(statusChartRef.value)
    chart.setOption({
      title: {
        text: '签到状态分布',
        left: 'center'
      },
      tooltip: {
        trigger: 'item'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [{
        name: '签到状态',
        type: 'pie',
        radius: '50%',
        data: reportData.value.statusDistribution,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
    })
  }
}

// 导出Excel
const exportExcel = async () => {
  try {
    showExportDialog.value = true
    exportProgress.value = 0
    exportProgressText.value = '正在准备数据...'
    
    // 模拟导出进度
    const timer = setInterval(() => {
      exportProgress.value += 10
      if (exportProgress.value <= 30) {
        exportProgressText.value = '正在处理数据...'
      } else if (exportProgress.value <= 70) {
        exportProgressText.value = '正在生成Excel文件...'
      } else if (exportProgress.value < 100) {
        exportProgressText.value = '正在下载文件...'
      } else {
        exportProgressText.value = '导出完成！'
        clearInterval(timer)
        setTimeout(() => {
          showExportDialog.value = false
          ElMessage.success('Excel文件导出成功')
        }, 1000)
      }
    }, 200)
    
  } catch (error) {
    console.error('导出Excel失败:', error)
    ElMessage.error('导出Excel失败')
    showExportDialog.value = false
  }
}

// 导出PDF
const exportPDF = async () => {
  try {
    showExportDialog.value = true
    exportProgress.value = 0
    exportProgressText.value = '正在准备数据...'
    
    // 模拟导出进度
    const timer = setInterval(() => {
      exportProgress.value += 10
      if (exportProgress.value <= 30) {
        exportProgressText.value = '正在处理数据...'
      } else if (exportProgress.value <= 70) {
        exportProgressText.value = '正在生成PDF文件...'
      } else if (exportProgress.value < 100) {
        exportProgressText.value = '正在下载文件...'
      } else {
        exportProgressText.value = '导出完成！'
        clearInterval(timer)
        setTimeout(() => {
          showExportDialog.value = false
          ElMessage.success('PDF文件导出成功')
        }, 1000)
      }
    }, 200)
    
  } catch (error) {
    console.error('导出PDF失败:', error)
    ElMessage.error('导出PDF失败')
    showExportDialog.value = false
  }
}

onMounted(async () => {
  await Promise.all([
    loadCourses(),
    loadTeachers()
  ])
})
</script>

<style scoped>
.report-management {
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

.stat-card {
  margin-bottom: 24px;
}

.chart-card {
  margin-bottom: 24px;
}

.table-card {
  .table-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .header-actions {
    display: flex;
    gap: 8px;
  }
}

.export-progress {
  text-align: center;
  
  .progress-text {
    margin-top: 16px;
    color: #666;
  }
}
</style>