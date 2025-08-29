<template>
  <div class="layout-container">
    <!-- 头部 Banner -->
    <el-header class="header">
      <div class="header-left">
        <h1 class="system-title">
          <el-icon class="title-icon"><House /></el-icon>
          课程签到系统
        </h1>
      </div>
      
      <div class="header-right">
        <div class="user-info">
          <el-avatar :size="32" class="user-avatar">
            {{ userStore.user?.full_name?.charAt(0) }}
          </el-avatar>
          <span class="user-name">{{ userStore.user?.full_name }}</span>
          <el-tag :type="getRoleTagType(userStore.user?.role)" size="small" class="role-tag">
            {{ getRoleText(userStore.user?.role) }}
          </el-tag>
        </div>
        
        <el-button type="danger" size="small" @click="handleLogout">
          <el-icon><SwitchButton /></el-icon>
          退出登录
        </el-button>
      </div>
    </el-header>

    <el-container class="main-container">
      <!-- 左侧导航栏 -->
      <el-aside :width="sidebarWidth" class="sidebar">
        <el-menu
          :default-active="$route.path"
          :collapse="isCollapse"
          router
          class="sidebar-menu"
        >
          <!-- 管理员菜单 -->
          <template v-if="userStore.isAdmin">
            <el-menu-item index="/admin">
              <el-icon><DataAnalysis /></el-icon>
              <span>仪表盘</span>
            </el-menu-item>
            <el-menu-item index="/admin/users">
              <el-icon><User /></el-icon>
              <span>用户管理</span>
            </el-menu-item>
            <el-menu-item index="/admin/classrooms">
              <el-icon><OfficeBuilding /></el-icon>
              <span>教室管理</span>
            </el-menu-item>
            <el-menu-item index="/admin/courses">
              <el-icon><Reading /></el-icon>
              <span>课程管理</span>
            </el-menu-item>
            <el-menu-item index="/admin/attendance">
              <el-icon><Calendar /></el-icon>
              <span>签到管理</span>
            </el-menu-item>
            <el-menu-item index="/admin/reports">
              <el-icon><Document /></el-icon>
              <span>统计报表</span>
            </el-menu-item>
          </template>

          <!-- 老师菜单 -->
          <template v-else-if="userStore.isTeacher">
            <el-menu-item index="/teacher">
              <el-icon><DataAnalysis /></el-icon>
              <span>我的课程</span>
            </el-menu-item>
            <el-menu-item index="/teacher/sessions">
              <el-icon><Calendar /></el-icon>
              <span>签到管理</span>
            </el-menu-item>
            <el-menu-item index="/teacher/records">
              <el-icon><Document /></el-icon>
              <span>签到记录</span>
            </el-menu-item>
            <el-menu-item index="/teacher/live-signin">
              <el-icon><UserFilled /></el-icon>
              <span>现场签到</span>
            </el-menu-item>
          </template>

          <!-- 学生菜单 -->
          <template v-else-if="userStore.isStudent">
            <el-menu-item index="/student">
              <el-icon><User /></el-icon>
              <span>个人信息</span>
            </el-menu-item>
            <el-menu-item index="/student/signin">
              <el-icon><EditPen /></el-icon>
              <span>课程签到</span>
            </el-menu-item>
            <el-menu-item index="/student/history">
              <el-icon><Document /></el-icon>
              <span>签到历史</span>
            </el-menu-item>
          </template>
        </el-menu>

        <!-- 折叠按钮 -->
        <div class="collapse-btn" @click="toggleSidebar">
          <el-icon>
            <component :is="isCollapse ? 'Expand' : 'Fold'" />
          </el-icon>
        </div>
      </el-aside>

      <!-- 主内容区域 -->
      <el-main class="main-content">
        <div class="content-wrapper">
          <router-view />
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const isCollapse = ref(false)

const sidebarWidth = computed(() => isCollapse.value ? '64px' : '200px')

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

const getRoleTagType = (role?: string) => {
  switch (role) {
    case 'admin': return 'danger'
    case 'teacher': return 'warning'
    case 'student': return 'success'
    default: return 'info'
  }
}

const getRoleText = (role?: string) => {
  switch (role) {
    case 'admin': return '管理员'
    case 'teacher': return '老师'
    case 'student': return '学生'
    default: return '未知'
  }
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  } catch {
    // 用户取消
  }
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.header {
  background: linear-gradient(90deg, #2196f3 0%, #21cbf3 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
}

.system-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-icon {
  font-size: 24px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-avatar {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  font-weight: 600;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
}

.role-tag {
  font-size: 12px;
}

.main-container {
  height: calc(100vh - 60px);
}

.sidebar {
  background-color: white;
  border-right: 1px solid #e8eaec;
  position: relative;
  transition: width 0.3s ease;
}

.sidebar-menu {
  border: none;
  height: 100%;
}

.sidebar-menu .el-menu-item {
  height: 48px;
  line-height: 48px;
}

.sidebar-menu .el-menu-item.is-active {
  background-color: #e6f3ff;
  color: #2196f3;
}

.collapse-btn {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 32px;
  height: 32px;
  background-color: #f5f7fa;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.collapse-btn:hover {
  background-color: #2196f3;
  color: white;
  border-color: #2196f3;
}

.main-content {
  background-color: #f5f7fa;
  padding: 20px;
}

.content-wrapper {
  background-color: white;
  border-radius: 8px;
  padding: 24px;
  min-height: calc(100vh - 140px);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}
</style>