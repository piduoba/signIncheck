<template>
  <div class="login-container bg-primary-gradient">
    <div ref="loginCardRef" class="login-card">
      <div class="login-header">
        <h1 class="login-title text-gradient typing-effect">课程签到系统</h1>
        <p class="login-subtitle fade-in">双重验证 智能签到管理</p>
      </div>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            size="large"
            placeholder="请输入用户名"
            prefix-icon="User"
            clearable
            class="slide-in-up hover-glow"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            size="large"
            placeholder="请输入密码"
            prefix-icon="Lock"
            show-password
            clearable
            class="slide-in-up hover-glow"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-button btn-ripple hover-lift"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-footer fade-in">
        <p>默认管理员账号：admin / admin</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { AnimationUtils } from '@/utils/animations'
import type { LoginRequest } from '@/types'

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref<FormInstance>()
const loginCardRef = ref<HTMLElement>()
const loading = ref(false)

const loginForm = reactive<LoginRequest>({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 4, message: '密码长度不能少于4位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  try {
    const valid = await loginFormRef.value.validate()
    if (!valid) return

    loading.value = true
    
    await userStore.login(loginForm)
    
    ElMessage.success('登录成功！')
    
    // 根据角色跳转到不同页面
    const user = userStore.user
    if (user?.role === 'admin') {
      router.push('/admin')
    } else if (user?.role === 'teacher') {
      router.push('/teacher')
    } else {
      router.push('/student')
    }
    
  } catch (error: any) {
    console.error('登录失败:', error)
    ElMessage.error(error.response?.data?.detail || '登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // 页面进入动效
  if (loginCardRef.value) {
    AnimationUtils.pageEnterAnimation(loginCardRef.value)
  }
  
  // 如果已经登录，直接跳转
  if (userStore.isLoggedIn) {
    const user = userStore.user
    if (user?.role === 'admin') {
      router.push('/admin')
    } else if (user?.role === 'teacher') {
      router.push('/teacher')
    } else {
      router.push('/student')
    }
  }
})
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-card {
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  backdrop-filter: blur(10px);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-title {
  font-size: 28px;
  font-weight: 600;
  color: #1976d2;
  margin: 0 0 8px 0;
}

.login-subtitle {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.login-form {
  .el-form-item {
    margin-bottom: 24px;
  }
}

.login-button {
  width: 100%;
  height: 44px;
  font-size: 16px;
  font-weight: 500;
  background: linear-gradient(90deg, #2196f3 0%, #21cbf3 100%);
  border: none;
}

.login-button:hover {
  background: linear-gradient(90deg, #1976d2 0%, #1ba8c7 100%);
}

.login-footer {
  text-align: center;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #eee;
  
  p {
    color: #999;
    font-size: 12px;
    margin: 0;
  }
}
</style>