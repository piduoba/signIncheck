<template>
  <div class="student-signin-container">
    <div class="signin-header">
      <h2 class="page-title">
        <el-icon><EditPen /></el-icon>
        课程签到
      </h2>
      <p class="page-description">请选择您的姓名并完成签到验证</p>
    </div>

    <!-- 当前签到场次信息 -->
    <el-card v-if="currentSession" class="session-card" shadow="hover">
      <template #header>
        <div class="session-header">
          <el-icon class="session-icon"><Calendar /></el-icon>
          <span>当前签到场次</span>
          <el-tag v-if="currentSession.is_active" type="success" size="small">
            进行中
          </el-tag>
          <el-tag v-else type="info" size="small">
            已结束
          </el-tag>
        </div>
      </template>
      
      <div class="session-info">
        <div class="info-row">
          <span class="label">场次名称：</span>
          <span class="value">{{ currentSession.session_name }}</span>
        </div>
        <div class="info-row">
          <span class="label">开始时间：</span>
          <span class="value">{{ formatDateTime(currentSession.start_time) }}</span>
        </div>
        <div class="info-row" v-if="currentSession.end_time">
          <span class="label">结束时间：</span>
          <span class="value">{{ formatDateTime(currentSession.end_time) }}</span>
        </div>
      </div>
    </el-card>

    <!-- 学生选择区域 -->
    <div v-if="!selectedStudent" class="student-selection">
      <h3 class="selection-title">请选择您的姓名</h3>
      
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索学生姓名或学号..."
          prefix-icon="Search"
          clearable
          size="large"
        />
      </div>

      <div class="students-grid">
        <div
          v-for="student in filteredStudents"
          :key="student.id"
          class="student-card"
          :class="{ shake: shakeStudent === student.id }"
          @click="selectStudent(student)"
        >
          <div class="student-avatar">
            {{ student.full_name.charAt(0) }}
          </div>
          <div class="student-info">
            <div class="student-name">{{ student.full_name }}</div>
            <div class="student-id">{{ student.student_id }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 密码验证和签名区域 -->
    <div v-else class="signin-verification">
      <div class="selected-student-info">
        <el-avatar :size="60" class="student-avatar">
          {{ selectedStudent.full_name.charAt(0) }}
        </el-avatar>
        <div class="student-details">
          <h3>{{ selectedStudent.full_name }}</h3>
          <p>学号：{{ selectedStudent.student_id }}</p>
        </div>
        <el-button type="primary" text @click="resetSelection">
          <el-icon><Back /></el-icon>
          重新选择
        </el-button>
      </div>

      <!-- 步骤指示器 -->
      <el-steps :active="currentStep" class="signin-steps">
        <el-step title="密码验证" icon="Lock" />
        <el-step title="手写签名" icon="EditPen" />
        <el-step title="完成签到" icon="Select" />
      </el-steps>

      <!-- 密码验证 -->
      <el-card v-if="currentStep === 0" class="verification-card">
        <template #header>
          <span>密码验证</span>
        </template>
        
        <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules">
          <el-form-item prop="password">
            <el-input
              v-model="passwordForm.password"
              type="password"
              size="large"
              placeholder="请输入您的登录密码"
              prefix-icon="Lock"
              show-password
              @keyup.enter="verifyPassword"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" size="large" :loading="verifying" @click="verifyPassword">
              {{ verifying ? '验证中...' : '验证密码' }}
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 手写签名 -->
      <el-card v-if="currentStep === 1" class="signature-card">
        <template #header>
          <div class="signature-header">
            <span>手写签名</span>
            <el-button type="primary" text @click="clearSignature">
              <el-icon><RefreshLeft /></el-icon>
              重新签名
            </el-button>
          </div>
        </template>
        
        <div class="signature-container">
          <canvas
            ref="signatureCanvas"
            class="signature-canvas"
            width="600"
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
          <el-button @click="clearSignature">清除签名</el-button>
          <el-button type="primary" :disabled="!hasSignature" @click="confirmSignature">
            确认签名
          </el-button>
        </div>
      </el-card>

      <!-- 完成签到 -->
      <el-card v-if="currentStep === 2" class="completion-card">
        <template #header>
          <span>确认签到信息</span>
        </template>
        
        <div class="signin-summary">
          <div class="summary-row">
            <span class="label">学生姓名：</span>
            <span class="value">{{ selectedStudent.full_name }}</span>
          </div>
          <div class="summary-row">
            <span class="label">学号：</span>
            <span class="value">{{ selectedStudent.student_id }}</span>
          </div>
          <div class="summary-row">
            <span class="label">签到时间：</span>
            <span class="value">{{ new Date().toLocaleString() }}</span>
          </div>
          <div class="summary-row">
            <span class="label">签到状态：</span>
            <el-select v-model="signinStatus" size="large" style="width: 200px">
              <el-option label="正常" value="present" />
              <el-option label="迟到" value="late" />
            </el-select>
          </div>
        </div>

        <div class="signature-preview">
          <p class="preview-label">签名预览：</p>
          <img :src="signatureDataURL" alt="签名预览" class="signature-image" />
        </div>

        <div class="completion-actions">
          <el-button size="large" @click="goBack">上一步</el-button>
          <el-button 
            type="primary" 
            size="large" 
            :loading="submitting" 
            @click="submitSignin"
          >
            {{ submitting ? '提交中...' : '确认签到' }}
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 签到成功对话框 -->
    <el-dialog v-model="successDialogVisible" title="签到成功" width="400px" center>
      <div class="success-content">
        <el-icon class="success-icon" color="#67c23a" :size="64"><CircleCheck /></el-icon>
        <h3>签到成功！</h3>
        <p>{{ selectedStudent?.full_name }}，您已成功完成签到。</p>
      </div>
      
      <template #footer>
        <el-button type="primary" @click="resetAll">继续签到</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, type FormInstance } from 'element-plus'
import { userAPI, attendanceAPI } from '@/api'
import { useAttendanceStore } from '@/stores/attendance'
import type { User, AttendanceRecordCreate } from '@/types'

const attendanceStore = useAttendanceStore()

// 响应式数据
const students = ref<User[]>([])
const selectedStudent = ref<User | null>(null)
const currentSession = ref(attendanceStore.currentSession)
const searchKeyword = ref('')
const currentStep = ref(0)
const verifying = ref(false)
const submitting = ref(false)
const successDialogVisible = ref(false)
const shakeStudent = ref<number | null>(null)

// 密码表单
const passwordFormRef = ref<FormInstance>()
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
const signinStatus = ref<'present' | 'late'>('present')

// 计算属性
const filteredStudents = computed(() => {
  if (!searchKeyword.value) return students.value
  
  const keyword = searchKeyword.value.toLowerCase()
  return students.value.filter(student => 
    student.full_name.toLowerCase().includes(keyword) ||
    student.student_id?.toLowerCase().includes(keyword)
  )
})

// 格式化日期时间
const formatDateTime = (dateStr: string) => {
  return new Date(dateStr).toLocaleString()
}

// 加载学生列表
const loadStudents = async () => {
  try {
    const response = await userAPI.getUsers({ role: 'student' })
    students.value = response
  } catch (error) {
    console.error('加载学生列表失败:', error)
    ElMessage.error('加载学生列表失败')
  }
}

// 选择学生
const selectStudent = (student: User) => {
  // 添加晃动效果
  shakeStudent.value = student.id
  setTimeout(() => {
    shakeStudent.value = null
    selectedStudent.value = student
    currentStep.value = 0
  }, 500)
}

// 重置选择
const resetSelection = () => {
  selectedStudent.value = null
  currentStep.value = 0
  passwordForm.password = ''
}

// 验证密码
const verifyPassword = async () => {
  if (!passwordFormRef.value || !selectedStudent.value) return

  try {
    const valid = await passwordFormRef.value.validate()
    if (!valid) return

    verifying.value = true
    
    // 这里应该调用API验证密码，暂时模拟
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    currentStep.value = 1
    
    // 初始化签名画布
    await nextTick()
    initSignatureCanvas()
    
  } catch (error) {
    ElMessage.error('密码验证失败')
  } finally {
    verifying.value = false
  }
}

// 初始化签名画布
const initSignatureCanvas = () => {
  const canvas = signatureCanvas.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  ctx.strokeStyle = '#000000'
  ctx.lineWidth = 2
  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'
}

// 开始绘制
const startDrawing = (e: MouseEvent | TouchEvent) => {
  isDrawing.value = true
  const canvas = signatureCanvas.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const rect = canvas.getBoundingClientRect()
  const x = 'touches' in e ? e.touches[0].clientX - rect.left : e.offsetX
  const y = 'touches' in e ? e.touches[0].clientY - rect.top : e.offsetY

  ctx.beginPath()
  ctx.moveTo(x, y)
}

// 绘制
const draw = (e: MouseEvent | TouchEvent) => {
  if (!isDrawing.value) return

  const canvas = signatureCanvas.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const rect = canvas.getBoundingClientRect()
  const x = 'touches' in e ? e.touches[0].clientX - rect.left : e.offsetX
  const y = 'touches' in e ? e.touches[0].clientY - rect.top : e.offsetY

  ctx.lineTo(x, y)
  ctx.stroke()

  hasSignature.value = true
}

// 停止绘制
const stopDrawing = () => {
  isDrawing.value = false
}

// 清除签名
const clearSignature = () => {
  const canvas = signatureCanvas.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  ctx.clearRect(0, 0, canvas.width, canvas.height)
  hasSignature.value = false
  signatureDataURL.value = ''
}

// 确认签名
const confirmSignature = () => {
  const canvas = signatureCanvas.value
  if (!canvas || !hasSignature.value) return

  signatureDataURL.value = canvas.toDataURL('image/png')
  currentStep.value = 2
}

// 上一步
const goBack = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 提交签到
const submitSignin = async () => {
  if (!selectedStudent.value || !currentSession.value || !signatureDataURL.value) {
    ElMessage.error('签到信息不完整')
    return
  }

  try {
    submitting.value = true

    const signinData: AttendanceRecordCreate = {
      student_id: selectedStudent.value.id,
      password: passwordForm.password,
      signature_data: signatureDataURL.value,
      status: signinStatus.value
    }

    await attendanceStore.studentSignin(currentSession.value.id, signinData)
    
    successDialogVisible.value = true
    
  } catch (error: any) {
    console.error('签到失败:', error)
    ElMessage.error(error.response?.data?.detail || '签到失败')
  } finally {
    submitting.value = false
  }
}

// 重置所有状态
const resetAll = () => {
  selectedStudent.value = null
  currentStep.value = 0
  passwordForm.password = ''
  clearSignature()
  successDialogVisible.value = false
  signinStatus.value = 'present'
}

onMounted(() => {
  loadStudents()
})
</script>

<style scoped>
.student-signin-container {
  max-width: 1200px;
  margin: 0 auto;
}

.signin-header {
  text-align: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  color: #1976d2;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.page-description {
  color: #666;
  margin: 0;
}

.session-card {
  margin-bottom: 24px;
}

.session-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.session-icon {
  color: #2196f3;
}

.session-info {
  .info-row {
    display: flex;
    margin-bottom: 12px;
    
    .label {
      width: 100px;
      color: #666;
      font-weight: 500;
    }
    
    .value {
      color: #333;
    }
  }
}

.student-selection {
  .selection-title {
    text-align: center;
    color: #333;
    margin-bottom: 24px;
  }
  
  .search-bar {
    margin-bottom: 24px;
  }
}

.students-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.student-card {
  background: white;
  border: 2px solid #e8eaec;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #2196f3;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(33, 150, 243, 0.15);
  }
  
  &.shake {
    animation: shake 0.5s ease-in-out;
  }
  
  .student-avatar {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, #2196f3, #21cbf3);
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    font-weight: 600;
    margin: 0 auto 12px auto;
  }
  
  .student-name {
    font-size: 16px;
    font-weight: 600;
    color: #333;
    margin-bottom: 4px;
  }
  
  .student-id {
    font-size: 14px;
    color: #666;
  }
}

.signin-verification {
  .selected-student-info {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
    margin-bottom: 24px;
    
    .student-details {
      flex: 1;
      
      h3 {
        margin: 0 0 4px 0;
        color: #333;
      }
      
      p {
        margin: 0;
        color: #666;
        font-size: 14px;
      }
    }
  }
  
  .signin-steps {
    margin-bottom: 24px;
  }
}

.verification-card,
.signature-card,
.completion-card {
  margin-bottom: 24px;
}

.signature-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.signature-container {
  position: relative;
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  margin-bottom: 16px;
  
  .signature-canvas {
    display: block;
    cursor: crosshair;
  }
  
  .signature-placeholder {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: #999;
    font-size: 16px;
    pointer-events: none;
  }
}

.signature-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.signin-summary {
  margin-bottom: 24px;
  
  .summary-row {
    display: flex;
    align-items: center;
    margin-bottom: 12px;
    
    .label {
      width: 120px;
      color: #666;
      font-weight: 500;
    }
    
    .value {
      color: #333;
    }
  }
}

.signature-preview {
  margin-bottom: 24px;
  
  .preview-label {
    font-weight: 500;
    color: #333;
    margin-bottom: 8px;
  }
  
  .signature-image {
    max-width: 100%;
    border: 1px solid #dcdfe6;
    border-radius: 4px;
  }
}

.completion-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.success-content {
  text-align: center;
  
  .success-icon {
    margin-bottom: 16px;
  }
  
  h3 {
    color: #67c23a;
    margin-bottom: 8px;
  }
  
  p {
    color: #666;
    margin: 0;
  }
}
</style>