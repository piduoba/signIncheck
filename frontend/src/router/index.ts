import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

// 导入布局组件
import DefaultLayout from '@/layouts/DefaultLayout.vue'

// 导入页面组件
import LoginView from '@/views/LoginView.vue'
import AdminDashboard from '@/views/admin/AdminDashboard.vue'
import UserManagement from '@/views/admin/UserManagement.vue'
import StudentSigninView from '@/views/student/StudentSigninView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: LoginView,
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/admin',
      component: DefaultLayout,
      meta: { requiresAuth: true, roles: ['admin'] },
      children: [
        {
          path: '',
          name: 'AdminDashboard',
          component: AdminDashboard
        },
        {
          path: 'users',
          name: 'UserManagement',
          component: UserManagement
        },
        {
          path: 'classrooms',
          name: 'ClassroomManagement',
          component: () => import('@/views/admin/ClassroomManagement.vue')
        },
        {
          path: 'courses',
          name: 'CourseManagement', 
          component: () => import('@/views/admin/CourseManagement.vue')
        },
        {
          path: 'attendance',
          name: 'AttendanceManagement',
          component: () => import('@/views/admin/AttendanceManagement.vue')
        },
        {
          path: 'reports',
          name: 'ReportManagement',
          component: () => import('@/views/admin/ReportManagement.vue')
        }
      ]
    },
    {
      path: '/teacher',
      component: DefaultLayout,
      meta: { requiresAuth: true, roles: ['teacher', 'admin'] },
      children: [
        {
          path: '',
          name: 'TeacherDashboard',
          component: () => import('@/views/teacher/TeacherDashboard.vue')
        },
        {
          path: 'sessions',
          name: 'TeacherSessions',
          component: () => import('@/views/teacher/SessionManagement.vue')
        },
        {
          path: 'records',
          name: 'TeacherRecords',
          component: () => import('@/views/teacher/AttendanceRecords.vue')
        },
        {
          path: 'live-signin',
          name: 'TeacherLiveSignin',
          component: () => import('@/views/teacher/LiveSigninView.vue')
        }
      ]
    },
    {
      path: '/student',
      component: DefaultLayout,
      meta: { requiresAuth: true, roles: ['student', 'teacher', 'admin'] },
      children: [
        {
          path: '',
          name: 'StudentProfile',
          component: () => import('@/views/student/StudentProfile.vue')
        },
        {
          path: 'signin',
          name: 'StudentSignin',
          component: StudentSigninView
        },
        {
          path: 'history',
          name: 'StudentHistory',
          component: () => import('@/views/student/AttendanceHistory.vue')
        }
      ]
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('@/views/NotFound.vue')
    }
  ]
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  // 初始化用户状态
  userStore.init()
  
  // 检查是否需要认证
  if (to.meta.requiresAuth !== false) {
    if (!userStore.isLoggedIn) {
      ElMessage.warning('请先登录')
      next('/login')
      return
    }
    
    // 检查角色权限
    if (to.meta.roles && Array.isArray(to.meta.roles)) {
      const hasPermission = userStore.hasRole(to.meta.roles as string[])
      if (!hasPermission) {
        ElMessage.error('权限不足')
        // 根据用户角色重定向到对应页面
        const userRole = userStore.user?.role
        if (userRole === 'admin') {
          next('/admin')
        } else if (userRole === 'teacher') {
          next('/teacher')
        } else if (userRole === 'student') {
          next('/student')
        } else {
          next('/login')
        }
        return
      }
    }
  }
  
  // 如果已登录用户访问登录页，重定向到对应的仪表盘
  if (to.path === '/login' && userStore.isLoggedIn) {
    const userRole = userStore.user?.role
    if (userRole === 'admin') {
      next('/admin')
    } else if (userRole === 'teacher') {
      next('/teacher')
    } else if (userRole === 'student') {
      next('/student')
    } else {
      next()
    }
    return
  }
  
  next()
})

export default router
