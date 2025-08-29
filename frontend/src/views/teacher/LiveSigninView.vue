<template>
  <div class="live-signin-container">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><UserFilled /></el-icon>
        现场签到
      </h2>
      <p class="page-description">请选择课程并查看学生签到状态</p>
    </div>

    <!-- 课程选择 -->
    <el-card class="course-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>选择课程</span>
        </div>
      </template>
      
      <el-select
        v-model="selectedCourseId"
        placeholder="请选择课程"
        size="large"
        style="width: 100%"
        @change="loadCourseStudents"
      >
        <el-option
          v-for="course in myCourses"
          :key="course.id"
          :label="course.name"
          :value="course.id"
        />
      </el-select>
    </el-card>

    <!-- 学生列表 -->
    <el-card v-if="selectedCourseId && students.length > 0" class="students-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>学生列表</span>
          <el-tag type="info">{{ students.length }} 名学生</el-tag>
        </div>
      </template>

      <div class="students-grid">
        <div
          v-for="student in sortedStudents"
          :key="student.id"
          class="student-tag"
          :class="{
            'signed-in': isStudentSignedIn(student.id),
            'not-signed': !isStudentSignedIn(student.id)
          }"
          @click="showSigninDialog(student)"
        >
          <div class="student-avatar">
            {{ student.full_name.charAt(0) }}
          </div>
          <div class="student-info">
            <div class="student-name">{{ student.full_name }}</div>
            <div class="student-id">{{ student.student_id }}</div>
          </div>
          <div class="signin-status">
            <el-icon v-if="isStudentSignedIn(student.id)" color="#67c23a">
              <CircleCheck />
            </el-icon>
            <el-icon v-else color="#909399">
              <Clock />
            </el-icon>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 签到统计 -->
    <el-card v-if="selectedCourseId" class="stats-card" shadow="hover">
      <template #header>
        <span>签到统计</span>
      </template>
      
      <div class="stats-content">
        <div class="stat-item">
          <div class="stat-number">{{ signedInCount }}</div>
          <div class="stat-label">已签到</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ notSignedCount }}</div>
          <div class="stat-label">未签到</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ attendanceRate }}%</div>
          <div class="stat-label">出勤率</div>
        </div>
      </div>
    </el-card>

    <!-- 密码验证对话框 -->
    <el-dialog
      v-model="showPasswordDialog"
      :title="`${selectedStudent?.full_name} - 密码验证`"
      width="400px"
      :close-on-click-modal="false"
    >
      <el-form :model="passwordForm" :rules="passwordRules">
        <el-form-item prop="password">
          <el-input
            v-model="passwordForm.password"
            type="password"
            placeholder="请输入学生密码"
            size="large"
            show-password
            @keyup.enter="verifyStudentPassword"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button
          type="primary"
          :loading="verifying"
          @click="verifyStudentPassword"
        >
          {{ verifying ? '验证中...' : '验证' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 签名对话框 -->
    <el-dialog
      v-model="showSignatureDialog"
      :title="`${selectedStudent?.full_name} - 手写签名`"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="signature-container">
        <canvas
          ref="signatureCanvas"
          class="signature-canvas"
          width="550"
          height="200"
          @mousedown="startDrawing"
          @mousemove="draw"
          @mouseup="stopDrawing"
          @touchstart="startDrawing"
          @touchmove="draw"
          @touchend="stopDrawing"
        />
        <div class="signature-placeholder" v-if="!hasSignature">
          请在此区域内签名
        </div>
      </div>

      <div class="signature-actions">
        <el-button @click="clearSignature">重新输入</el-button>
        <el-button type="primary" :disabled="!hasSignature" @click="confirmSignature">
          确定
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, type FormInstance } from 'element-plus'
import { courseAPI, userAPI, attendanceAPI } from '@/api'
import { useUserStore } from '@/stores/user'
import type { User, Course, AttendanceRecordCreate } from '@/types'

const userStore = useUserStore()

// 响应式数据
const myCourses = ref<Course[]>([])
const selectedCourseId = ref<number>()
const students = ref<User[]>([])
const attendanceRecords = ref<any[]>([])
const selectedStudent = ref<User | null>(null)
const showPasswordDialog = ref(false)
const showSignatureDialog = ref(false)
const verifying = ref(false)
const submitting = ref(false)

// 密码表单
const passwordForm = reactive({
  password: ''
})

const passwordRules = {
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

// 签名相关
const signatureCanvas = ref<HTMLCanvasElement>()
const isDrawing = ref(false)
const hasSignature = ref(false)
const signatureDataURL = ref('')

// 计算属性
const sortedStudents = computed(() => {
  return [...students.value].sort((a, b) => 
    a.full_name.localeCompare(b.full_name, 'zh-CN')
  )
})

const signedInCount = computed(() => {
  return attendanceRecords.value.filter(record => record.status !== 'absent').length
})

const notSignedCount = computed(() => {
  return students.value.length - signedInCount.value
})

const attendanceRate = computed(() => {
  if (students.value.length === 0) return 0
  return Math.round((signedInCount.value / students.value.length) * 100)
})

// 方法
const loadMyCourses = async () => {
  try {
    myCourses.value = await courseAPI.getCourses(userStore.user?.id)
  } catch (error) {
    console.error('加载课程失败:', error)
    ElMessage.error('加载课程失败')
  }
}

const loadCourseStudents = async () => {
  if (!selectedCourseId.value) return

  try {
    // 加载课程的学生列表
    students.value = await userAPI.getUsers({ 
      role: 'student',
      course_id: selectedCourseId.value
    })

    // 加载签到记录
    await loadAttendanceRecords()
  } catch (error) {
    console.error('加载学生列表失败:', error)
    ElMessage.error('加载学生列表失败')
  }
}

const loadAttendanceRecords = async () => {
  if (!selectedCourseId.value) return

  try {
    // 这里需要根据课程ID获取签到记录
    // 实际实现可能需要调整API
    const sessions = await attendanceAPI.getSessions({ 
      course_id: selectedCourseId.value 
    })
    
    if (sessions.length > 0) {
      const latestSession = sessions[0]
      attendanceRecords.value = await attendanceAPI.getRecords(latestSession.id)
    }
  } catch (error) {
    console.error('加载签到记录失败:', error)
    attendanceRecords.value = []
  }
}

const isStudentSignedIn = (studentId: number) => {
  return attendanceRecords.value.some(record => 
    record.student_id === studentId && record.status !== 'absent'
  )
}

const showSigninDialog = (student: User) => {
  if (isStudentSignedIn(student.id)) {
    ElMessage.info('该学生已经签到过了')
    return
  }

  selectedStudent.value = student
  showPasswordDialog.value = true
  passwordForm.password = ''
}

const verifyStudentPassword = async () => {
  if (!selectedStudent.value) return

  try {
    verifying.value = true

    // 这里需要调用API验证学生密码
    // 实际实现需要调整API调用
    const isValid = await userAPI.verifyPassword(
      selectedStudent.value.id,
      passwordForm.password
    )

    if (isValid) {
      showPasswordDialog.value = false
      showSignatureDialog.value = true
      await nextTick()
      initSignatureCanvas()
    } else {
      ElMessage.error('密码错误')
    }
  } catch (error: any) {
    console.error('密码验证失败:', error)
    ElMessage.error(error.response?.data?.detail || '密码验证失败')
  } finally {
    verifying.value = false
  }
}

// 签名相关方法
const initSignatureCanvas = () => {
  if (!signatureCanvas.value) return
  
  const ctx = signatureCanvas.value.getContext('2d')
  if (ctx) {
    ctx.fillStyle = 'white'
    ctx.fillRect(0, 0, signatureCanvas.value.width, signatureCanvas.value.height)
    ctx.strokeStyle = '#000'
    ctx.lineWidth = 2
    ctx.lineCap = 'round'
    ctx.lineJoin = 'round'
  }
  
  hasSignature.value = false
  signatureDataURL.value = ''
}

const startDrawing = (e: MouseEvent | TouchEvent) => {
  if (!signatureCanvas.value) return
  
  isDrawing.value = true
  const ctx = signatureCanvas.value.getContext('2d')
  if (!ctx) return

  const rect = signatureCanvas.value.getBoundingClientRect()
  let clientX, clientY

  if (e instanceof MouseEvent) {
    clientX = e.clientX
    clientY = e.clientY
  } else {
    clientX = e.touches[0].clientX
    clientY = e.touches[0].clientY
  }

  ctx.beginPath()
  ctx.moveTo(clientX - rect.left, clientY - rect.top)
}

const draw = (e: MouseEvent | TouchEvent) => {
  if (!isDrawing.value || !signatureCanvas.value) return

  const ctx = signatureCanvas.value.getContext('2d')
  if (!ctx) return

  const rect = signatureCanvas.value.getBoundingClientRect()
  let clientX, clientY

  if (e instanceof MouseEvent) {
    clientX = e.clientX
    clientY = e.clientY
  } else {
    clientX = e.touches[0].clientX
    clientY = e.touches[0].clientY
  }

  ctx.lineTo(clientX - rect.left, clientY - rect.top)
  ctx.stroke()
  
  hasSignature.value = true
}

const stopDrawing = () => {
  isDrawing.value = false
}

const clearSignature = () => {
  initSignatureCanvas()
}

const confirmSignature = async () => {
  if (!selectedStudent.value || !signatureCanvas.value) return

  try {
    submitting.value = true
    
    // 获取签名数据
    signatureDataURL.value = signatureCanvas.value.toDataURL('image/png')
    
    // 创建签到记录
    const signinData: AttendanceRecordCreate = {
      student_id: selectedStudent.value.id,
      password: passwordForm.password,
      signature_data: signatureDataURL.value,
      status: 'present'
    }

    // 这里需要调用签到API
    // 实际实现需要调整API调用
    await attendanceAPI.signin(selectedCourseId.value!, signinData)
    
    ElMessage.success('签到成功')
    showSignatureDialog.value = false
    
    // 重新加载签到记录
    await loadAttendanceRecords()
  } catch (error: any) {
    console.error('签到失败:', error)
    ElMessage.error(error.response?.data?.detail || '签到失败')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await loadMyCourses()
  // 页面加载时立即加载所有学生
  await loadAllStudents()
})

// 新增方法：加载所有学生
const loadAllStudents = async () => {
  try {
    // 加载所有学生（不按课程筛选）
    students.value = await userAPI.getUsers({ 
      role: 'student'
    })
    
    // 如果有选中的课程，加载对应的签到记录
    if (selectedCourseId.value) {
      await loadAttendanceRecords()
    }
  } catch (error) {
    console.error('加载学生列表失败:', error)
    ElMessage.error('加载学生列表失败')
  }
}
</script>

<style scoped>
.live-signin-container {
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

.page-description {
  color: #666;
  margin: 8px 0 0 0;
}

.course-card,
.students-card,
.stats-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.students-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.student-tag {
  display: flex;
  align-items: center;
  padding: 12px;
  border: 2px solid #e8eaec;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
}

.student-tag:hover {
  border-color: #409eff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.student-tag.signed-in {
  border-color: #67c23a;
  background-color: #f0f9eb;
}

.student-tag.not-signed {
  border-color: #dcdfe6;
  background-color: white;
}

.student-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  margin-right: 12px;
  flex-shrink: 0;
}

.student-info {
  flex: 1;
  min-width: 0;
}

.student-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.student-id {
  font-size: 12px;
  color: #909399;
}

.signin-status {
  margin-left: 8px;
  flex-shrink: 0;
}

.stats-content {
  display: flex;
  justify-content: space-around;
  text-align: center;
}

.stat-item {
  padding: 0 20px;
}

.stat-number {
  font-size: 32px;
  font-weight: 600;
  color: #1976d2;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}

.signature-container {
  position: relative;
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  margin-bottom: 16px;
}

.signature-canvas {
  display: block;
  width: 100%;
  height: 200px;
  cursor: crosshair;
}

.signature-placeholder {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #909399;
  font-size: 16px;
  pointer-events: none;
}

.signature-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}
</style>