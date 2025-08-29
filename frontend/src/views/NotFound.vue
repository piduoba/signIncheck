<template>
  <div class="not-found">
    <div class="not-found-container">
      <div class="error-animation">
        <div class="error-number">
          <span class="four">4</span>
          <span class="zero">0</span>
          <span class="four">4</span>
        </div>
        <div class="error-icon">
          <el-icon><Warning /></el-icon>
        </div>
      </div>
      
      <div class="error-content">
        <h1 class="error-title">页面未找到</h1>
        <p class="error-description">
          抱歉，您访问的页面不存在或已被移除。
        </p>
        <p class="error-suggestion">
          请检查网址是否正确，或返回首页继续浏览。
        </p>
      </div>
      
      <div class="error-actions">
        <el-button type="primary" size="large" @click="goHome">
          <el-icon><HomeFilled /></el-icon>
          返回首页
        </el-button>
        <el-button size="large" @click="goBack">
          <el-icon><Back /></el-icon>
          返回上一页
        </el-button>
      </div>
      
      <!-- 可能的链接建议 -->
      <div class="suggestions">
        <h3>您可能想要访问：</h3>
        <div class="suggestion-links">
          <router-link to="/login" class="suggestion-link">
            <el-icon><User /></el-icon>
            <span>用户登录</span>
          </router-link>
          <router-link v-if="userStore.isAdmin" to="/admin" class="suggestion-link">
            <el-icon><Setting /></el-icon>
            <span>管理后台</span>
          </router-link>
          <router-link v-if="userStore.isTeacher" to="/teacher" class="suggestion-link">
            <el-icon><Reading /></el-icon>
            <span>教师中心</span>
          </router-link>
          <router-link v-if="userStore.isStudent" to="/student" class="suggestion-link">
            <el-icon><UserFilled /></el-icon>
            <span>学生中心</span>
          </router-link>
        </div>
      </div>
    </div>
    
    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="floating-shape shape-1"></div>
      <div class="floating-shape shape-2"></div>
      <div class="floating-shape shape-3"></div>
      <div class="floating-shape shape-4"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// 返回首页
const goHome = () => {
  if (userStore.isLoggedIn) {
    const role = userStore.user?.role
    if (role === 'admin') {
      router.push('/admin')
    } else if (role === 'teacher') {
      router.push('/teacher')
    } else if (role === 'student') {
      router.push('/student')
    } else {
      router.push('/login')
    }
  } else {
    router.push('/login')
  }
}

// 返回上一页
const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    goHome()
  }
}
</script>

<style scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.not-found-container {
  text-align: center;
  background: white;
  padding: 60px 40px;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  max-width: 600px;
  width: 90%;
  position: relative;
  z-index: 2;
}

.error-animation {
  position: relative;
  margin-bottom: 40px;
}

.error-number {
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 120px;
  font-weight: 800;
  color: #667eea;
  margin-bottom: 20px;
  position: relative;
}

.error-number span {
  display: inline-block;
  animation: bounce 2s infinite;
}

.error-number .four:first-child {
  animation-delay: 0s;
}

.error-number .zero {
  animation-delay: 0.2s;
  color: #764ba2;
}

.error-number .four:last-child {
  animation-delay: 0.4s;
}

.error-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 80px;
  color: #ffa726;
  opacity: 0.3;
  animation: pulse 2s infinite;
}

.error-content {
  margin-bottom: 40px;
}

.error-title {
  font-size: 32px;
  color: #333;
  margin: 0 0 16px 0;
  font-weight: 600;
}

.error-description {
  font-size: 16px;
  color: #666;
  margin: 0 0 12px 0;
  line-height: 1.6;
}

.error-suggestion {
  font-size: 14px;
  color: #999;
  margin: 0;
  line-height: 1.6;
}

.error-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 40px;
  flex-wrap: wrap;
}

.suggestions {
  border-top: 1px solid #eee;
  padding-top: 32px;
}

.suggestions h3 {
  font-size: 18px;
  color: #333;
  margin: 0 0 20px 0;
  font-weight: 500;
}

.suggestion-links {
  display: flex;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

.suggestion-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: #f8f9fa;
  border-radius: 8px;
  text-decoration: none;
  color: #333;
  transition: all 0.3s ease;
  font-size: 14px;
}

.suggestion-link:hover {
  background: #e9ecef;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.suggestion-link .el-icon {
  font-size: 16px;
  color: #667eea;
}

/* 背景装饰 */
.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.floating-shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
}

.shape-1 {
  width: 100px;
  height: 100px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.shape-2 {
  width: 60px;
  height: 60px;
  top: 20%;
  right: 15%;
  animation-delay: 1s;
}

.shape-3 {
  width: 80px;
  height: 80px;
  bottom: 20%;
  left: 15%;
  animation-delay: 2s;
}

.shape-4 {
  width: 40px;
  height: 40px;
  bottom: 15%;
  right: 10%;
  animation-delay: 3s;
}

/* 动画 */
@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

@keyframes pulse {
  0% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.3;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.1);
    opacity: 0.5;
  }
  100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.3;
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  33% {
    transform: translateY(-20px) rotate(120deg);
  }
  66% {
    transform: translateY(10px) rotate(240deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .not-found-container {
    padding: 40px 20px;
    margin: 20px;
  }
  
  .error-number {
    font-size: 80px;
  }
  
  .error-icon {
    font-size: 60px;
  }
  
  .error-title {
    font-size: 24px;
  }
  
  .error-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .suggestion-links {
    flex-direction: column;
    align-items: center;
  }
  
  .suggestion-link {
    width: 200px;
    justify-content: center;
  }
}
</style>