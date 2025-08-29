<template>
  <div class="admin-dashboard">
    <!-- 页面头部 -->
    <div class="dashboard-header">
      <div class="header-content">
        <h1 class="page-title">
          <el-icon><DataAnalysis /></el-icon>
          系统仪表盘
        </h1>
        <p class="page-subtitle">欢迎回来，{{ userStore.user?.full_name }}</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <el-card class="stat-card users-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-details">
            <div class="stat-number">{{ stats.totalUsers }}</div>
            <div class="stat-label">总用户数</div>
            <div class="stat-change positive">
              <el-icon><CaretTop /></el-icon>
              +{{ stats.newUsersThisWeek }} 本周新增
            </div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card teachers-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon><UserFilled /></el-icon>
          </div>
          <div class="stat-details">
            <div class="stat-number">{{ stats.totalTeachers }}</div>
            <div class="stat-label">教师数量</div>
            <div class="stat-change">
              活跃教师 {{ stats.activeTeachers }}
            </div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card students-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon><Avatar /></el-icon>
          </div>
          <div class="stat-details">
            <div class="stat-number">{{ stats.totalStudents }}</div>
            <div class="stat-label">学生数量</div>
            <div class="stat-change">
              活跃学生 {{ stats.activeStudents }}
            </div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card attendance-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon><Calendar /></el-icon>
          </div>
          <div class="stat-details">
            <div class="stat-number">{{ stats.todayAttendance }}%</div>
            <div class="stat-label">今日出勤率</div>
            <div class="stat-change" :class="stats.attendanceTrend > 0 ? 'positive' : 'negative'">
              <el-icon><component :is="stats.attendanceTrend > 0 ? 'CaretTop' : 'CaretBottom'" /></el-icon>
              {{ Math.abs(stats.attendanceTrend) }}% 较昨日
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <!-- 签到趋势图 -->
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><DataLine /></el-icon>
              签到趋势分析
            </span>
            <el-select v-model="attendancePeriod" size="small" @change="loadAttendanceTrend">
              <el-option label="最近7天" value="7days" />
              <el-option label="最近30天" value="30days" />
              <el-option label="最近3个月" value="3months" />
            </el-select>
          </div>
        </template>
        <div class="chart-container">
          <!-- <v-chart :option="attendanceTrendOption" class="chart" /> -->
          <div class="chart-placeholder">
            <el-icon><DataLine /></el-icon>
            <p>图表加载中...</p>
          </div>
        </div>
      </el-card>

      <!-- 签到状态分布 -->
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><DataAnalysis /></el-icon>
              签到状态分布
            </span>
            <el-date-picker
              v-model="selectedDate"
              type="date"
              size="small"
              placeholder="选择日期"
              @change="loadStatusDistribution"
            />
          </div>
        </template>
        <div class="chart-container">
          <!-- <v-chart :option="statusDistributionOption" class="chart" /> -->
          <div class="chart-placeholder">
            <el-icon><DataAnalysis /></el-icon>
            <p>图表加载中...</p>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 活动数据 -->
    <div class="activity-section">
      <el-row :gutter="20">
        <!-- 最近活动 -->
        <el-col :span="12">
          <el-card class="activity-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><Bell /></el-icon>
                  最近活动
                </span>
                <el-link type="primary" @click="viewAllActivities">查看全部</el-link>
              </div>
            </template>
            <div class="activity-list">
              <div
                v-for="activity in recentActivities"
                :key="activity.id"
                class="activity-item"
              >
                <div class="activity-avatar">
                  <el-icon :class="getActivityIcon(activity.type)">
                    <component :is="getActivityIcon(activity.type)" />
                  </el-icon>
                </div>
                <div class="activity-content">
                  <div class="activity-text">{{ activity.message }}</div>
                  <div class="activity-time">{{ formatTime(activity.timestamp) }}</div>
                </div>
              </div>
              <div v-if="recentActivities.length === 0" class="no-data">
                暂无最近活动
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 系统状态 -->
        <el-col :span="12">
          <el-card class="system-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><Monitor /></el-icon>
                  系统状态
                </span>
                <el-tag :type="systemStatus.overall === 'healthy' ? 'success' : 'warning'" size="small">
                  {{ systemStatus.overall === 'healthy' ? '正常' : '异常' }}
                </el-tag>
              </div>
            </template>
            <div class="system-metrics">
              <div class="metric-item">
                <div class="metric-label">数据库连接</div>
                <el-progress
                  :percentage="systemStatus.database"
                  :status="systemStatus.database > 90 ? 'success' : 'warning'"
                  :stroke-width="8"
                />
              </div>
              <div class="metric-item">
                <div class="metric-label">API响应时间</div>
                <div class="metric-value">{{ systemStatus.apiResponseTime }}ms</div>
              </div>
              <div class="metric-item">
                <div class="metric-label">活跃会话</div>
                <div class="metric-value">{{ systemStatus.activeSessions }}</div>
              </div>
              <div class="metric-item">
                <div class="metric-label">存储使用</div>
                <el-progress
                  :percentage="systemStatus.storageUsage"
                  :status="systemStatus.storageUsage > 80 ? 'exception' : 'success'"
                  :stroke-width="8"
                />
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 快捷操作 -->
    <div class="quick-actions">
      <el-card shadow="hover">
        <template #header>
          <span class="card-title">
            <el-icon><Operation /></el-icon>
            快捷操作
          </span>
        </template>
        <div class="actions-grid">
          <el-button
            type="primary"
            size="large"
            class="action-btn"
            @click="$router.push('/admin/users')"
          >
            <el-icon><User /></el-icon>
            用户管理
          </el-button>
          <el-button
            type="success"
            size="large"
            class="action-btn"
            @click="$router.push('/admin/classrooms')"
          >
            <el-icon><OfficeBuilding /></el-icon>
            教室管理
          </el-button>
          <el-button
            type="warning"
            size="large"
            class="action-btn"
            @click="$router.push('/admin/courses')"
          >
            <el-icon><Reading /></el-icon>
            课程管理
          </el-button>
          <el-button
            type="info"
            size="large"
            class="action-btn"
            @click="$router.push('/admin/reports')"
          >
            <el-icon><Document /></el-icon>
            统计报表
          </el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { userAPI, commonAPI } from '@/api'

const userStore = useUserStore()

// 响应式数据
const loading = ref(false)
const attendancePeriod = ref('7days')
const selectedDate = ref(new Date())

// 统计数据
const stats = reactive({
  totalUsers: 0,
  totalTeachers: 0,
  totalStudents: 0,
  newUsersThisWeek: 0,
  activeTeachers: 0,
  activeStudents: 0,
  todayAttendance: 0,
  attendanceTrend: 0
})

// 最近活动
const recentActivities = ref([
  {
    id: 1,
    type: 'signin',
    message: '张三完成了《数据结构》课程签到',
    timestamp: new Date(Date.now() - 5 * 60 * 1000)
  },
  {
    id: 2,
    type: 'user',
    message: '李老师创建了新的签到场次',
    timestamp: new Date(Date.now() - 15 * 60 * 1000)
  },
  {
    id: 3,
    type: 'system',
    message: '系统完成了每日数据备份',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000)
  }
])

// 系统状态
const systemStatus = reactive({
  overall: 'healthy' as 'healthy' | 'warning',
  database: 95,
  apiResponseTime: 120,
  activeSessions: 45,
  storageUsage: 68
})

// 签到趋势图表配置
const attendanceTrendOption = computed(() => ({
  title: {
    text: '签到趋势',
    left: 'center',
    textStyle: {
      fontSize: 16,
      color: '#333'
    }
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'cross'
    }
  },
  legend: {
    data: ['出勤率', '迟到率'],
    bottom: 10
  },
  xAxis: {
    type: 'category',
    data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  },
  yAxis: {
    type: 'value',
    axisLabel: {
      formatter: '{value}%'
    }
  },
  series: [
    {
      name: '出勤率',
      type: 'line',
      data: [85, 92, 88, 94, 90, 86, 89],
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
          colorStops: [
            { offset: 0, color: 'rgba(33, 150, 243, 0.3)' },
            { offset: 1, color: 'rgba(33, 150, 243, 0.1)' }
          ]
        }
      }
    },
    {
      name: '迟到率',
      type: 'line',
      data: [12, 8, 10, 6, 9, 11, 8],
      smooth: true,
      lineStyle: {
        color: '#ff9800'
      }
    }
  ],
  grid: {
    top: 60,
    left: 50,
    right: 30,
    bottom: 60
  }
}))

// 签到状态分布图表配置
const statusDistributionOption = computed(() => ({
  title: {
    text: '今日签到状态分布',
    left: 'center',
    textStyle: {
      fontSize: 16,
      color: '#333'
    }
  },
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b}: {c} ({d}%)'
  },
  legend: {
    orient: 'vertical',
    left: 10,
    data: ['正常', '迟到', '早退', '缺勤']
  },
  series: [
    {
      name: '签到状态',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['60%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 20,
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: [
        { value: 156, name: '正常', itemStyle: { color: '#4caf50' } },
        { value: 23, name: '迟到', itemStyle: { color: '#ff9800' } },
        { value: 8, name: '早退', itemStyle: { color: '#f44336' } },
        { value: 12, name: '缺勤', itemStyle: { color: '#9e9e9e' } }
      ]
    }
  ]
}))

// 格式化时间
const formatTime = (timestamp: Date) => {
  const now = new Date()
  const diff = now.getTime() - timestamp.getTime()
  
  if (diff < 60 * 1000) {
    return '刚刚'
  } else if (diff < 60 * 60 * 1000) {
    return `${Math.floor(diff / (60 * 1000))}分钟前`
  } else if (diff < 24 * 60 * 60 * 1000) {
    return `${Math.floor(diff / (60 * 60 * 1000))}小时前`
  } else {
    return timestamp.toLocaleDateString()
  }
}

// 获取活动图标
const getActivityIcon = (type: string) => {
  switch (type) {
    case 'signin':
      return 'EditPen'
    case 'user':
      return 'User'
    case 'system':
      return 'Setting'
    default:
      return 'InfoFilled'
  }
}

// 加载统计数据
const loadStats = async () => {
  try {
    // 模拟API调用
    const users = await userAPI.getUsers()
    
    stats.totalUsers = users.length
    stats.totalTeachers = users.filter(u => u.role === 'teacher').length
    stats.totalStudents = users.filter(u => u.role === 'student').length
    stats.newUsersThisWeek = 5 // 模拟数据
    stats.activeTeachers = Math.floor(stats.totalTeachers * 0.8)
    stats.activeStudents = Math.floor(stats.totalStudents * 0.9)
    stats.todayAttendance = 89
    stats.attendanceTrend = 3.2
    
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

// 加载签到趋势
const loadAttendanceTrend = async () => {
  // 模拟加载不同时间段的数据
  console.log('加载签到趋势:', attendancePeriod.value)
}

// 加载状态分布
const loadStatusDistribution = async () => {
  // 模拟加载指定日期的数据
  console.log('加载状态分布:', selectedDate.value)
}

// 刷新数据
const refreshData = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadStats(),
      loadAttendanceTrend(),
      loadStatusDistribution()
    ])
  } finally {
    loading.value = false
  }
}

// 查看全部活动
const viewAllActivities = () => {
  // 跳转到活动日志页面
  console.log('查看全部活动')
}

onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.admin-dashboard {
  padding: 0;
}

.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e8eaec;
}

.header-content {
  .page-title {
    font-size: 28px;
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  border: none;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  }
  
  .stat-content {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  
  .stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    color: white;
  }
  
  .stat-details {
    flex: 1;
  }
  
  .stat-number {
    font-size: 32px;
    font-weight: 700;
    color: #333;
    line-height: 1;
  }
  
  .stat-label {
    font-size: 14px;
    color: #666;
    margin: 4px 0;
  }
  
  .stat-change {
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 4px;
    
    &.positive {
      color: #4caf50;
    }
    
    &.negative {
      color: #f44336;
    }
  }
}

.users-card .stat-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.teachers-card .stat-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.students-card .stat-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.attendance-card .stat-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  border: none;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
}

.chart-container {
  height: 300px;
}

.chart {
  width: 100%;
  height: 100%;
}

.chart-placeholder {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 16px;
  
  .el-icon {
    font-size: 48px;
    margin-bottom: 16px;
    opacity: 0.5;
  }
  
  p {
    margin: 0;
  }
}

.activity-section {
  margin-bottom: 24px;
}

.activity-card,
.system-card {
  border: none;
}

.activity-list {
  max-height: 300px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
  
  &:last-child {
    border-bottom: none;
  }
}

.activity-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #e3f2fd;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #2196f3;
  font-size: 16px;
}

.activity-content {
  flex: 1;
}

.activity-text {
  font-size: 14px;
  color: #333;
  margin-bottom: 4px;
}

.activity-time {
  font-size: 12px;
  color: #999;
}

.system-metrics {
  .metric-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  .metric-label {
    font-size: 14px;
    color: #666;
  }
  
  .metric-value {
    font-size: 16px;
    font-weight: 600;
    color: #333;
  }
}

.quick-actions {
  .actions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
  }
  
  .action-btn {
    height: 56px;
    font-size: 16px;
    font-weight: 500;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
  }
}

.no-data {
  text-align: center;
  color: #999;
  padding: 20px 0;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-container {
    height: 250px;
  }
}
</style>