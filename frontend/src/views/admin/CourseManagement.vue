<template>
  <div class="course-management">
    <div class="page-header">
      <div class="page-title-section">
        <el-icon class="title-icon"><Reading /></el-icon>
        <h2 class="page-title">课程管理</h2>
      </div>
      <el-button type="primary" @click="showCreateDialog = true" class="add-course-btn">
        <el-icon><Plus /></el-icon>
        新增课程
      </el-button>
    </div>

    <!-- 课程列表 -->
    <el-card class="course-list-card">
      <template #header>
        <div class="card-header">
          <span>课程列表</span>
          <div class="header-actions">
            <el-select
              v-model="selectedTeacher"
              placeholder="筛选老师"
              clearable
              style="width: 180px; margin-right: 12px"
              @change="loadCourses"
            >
              <el-option
                v-for="teacher in teachers"
                :key="teacher.id"
                :label="teacher.full_name"
                :value="teacher.id"
              />
            </el-select>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索课程名称..."
              prefix-icon="Search"
              clearable
              style="width: 250px"
            />
          </div>
        </div>
      </template>

      <el-table
        :data="filteredCourses"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="name" label="课程名称" min-width="150" />
        <el-table-column prop="teacher_name" label="授课老师" width="120">
          <template #default="{ row }">
            {{ getTeacherName(row.teacher_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="classroom_name" label="教室" width="120">
          <template #default="{ row }">
            {{ getClassroomName(row.classroom_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="description" label="课程描述" min-width="200">
          <template #default="{ row }">
            {{ row.description || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button
                type="primary"
                size="small"
                @click="editCourse(row)"
              >
                编辑
              </el-button>
              <el-button
                type="danger"
                size="small"
                @click="deleteCourse(row)"
              >
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑课程对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="isEdit ? '编辑课程' : '新增课程'"
      width="600px"
    >
      <el-form
        ref="courseFormRef"
        :model="courseForm"
        :rules="courseRules"
        label-width="100px"
      >
        <el-form-item label="课程名称" prop="name">
          <el-input v-model="courseForm.name" placeholder="请输入课程名称" />
        </el-form-item>
        
        <el-form-item label="授课老师" prop="teacher_id">
          <el-select
            v-model="courseForm.teacher_id"
            placeholder="请选择授课老师"
            style="width: 100%"
          >
            <el-option
              v-for="teacher in teachers"
              :key="teacher.id"
              :label="teacher.full_name"
              :value="teacher.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="上课教室" prop="classroom_id">
          <el-select
            v-model="courseForm.classroom_id"
            placeholder="请选择上课教室"
            style="width: 100%"
          >
            <el-option
              v-for="classroom in classrooms"
              :key="classroom.id"
              :label="`${classroom.name} (${classroom.location})`"
              :value="classroom.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="课程描述">
          <el-input
            v-model="courseForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入课程描述"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ submitting ? '提交中...' : '确定' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Edit, Delete } from '@element-plus/icons-vue'
import { courseAPI, userAPI, classroomAPI } from '@/api'
import type { Course, CourseCreate, User, Classroom } from '@/types'

// 响应式数据
const courses = ref<Course[]>([])
const teachers = ref<User[]>([])
const classrooms = ref<Classroom[]>([])
const loading = ref(false)
const submitting = ref(false)
const showCreateDialog = ref(false)
const isEdit = ref(false)
const searchKeyword = ref('')
const selectedTeacher = ref<number>()
const courseFormRef = ref<FormInstance>()

// 表单数据
const courseForm = reactive<CourseCreate & { id?: number }>({
  name: '',
  description: '',
  teacher_id: 0,
  classroom_id: 0
})

// 表单验证规则
const courseRules = {
  name: [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
  teacher_id: [{ required: true, message: '请选择授课老师', trigger: 'change' }],
  classroom_id: [{ required: true, message: '请选择上课教室', trigger: 'change' }]
}

// 计算属性
const filteredCourses = computed(() => {
  if (!searchKeyword.value) return courses.value
  
  const keyword = searchKeyword.value.toLowerCase()
  return courses.value.filter(course =>
    course.name.toLowerCase().includes(keyword) ||
    course.description?.toLowerCase().includes(keyword)
  )
})

// 获取老师姓名
const getTeacherName = (teacherId: number) => {
  const teacher = teachers.value.find(t => t.id === teacherId)
  return teacher?.full_name || '-'
}

// 获取教室名称
const getClassroomName = (classroomId: number) => {
  const classroom = classrooms.value.find(c => c.id === classroomId)
  return classroom?.name || '-'
}

// 格式化日期时间
const formatDateTime = (dateStr: string) => {
  return new Date(dateStr).toLocaleString()
}

// 加载课程列表
const loadCourses = async () => {
  try {
    loading.value = true
    courses.value = await courseAPI.getCourses(selectedTeacher.value)
  } catch (error) {
    console.error('加载课程列表失败:', error)
    ElMessage.error('加载课程列表失败')
  } finally {
    loading.value = false
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

// 加载教室列表
const loadClassrooms = async () => {
  try {
    classrooms.value = await classroomAPI.getClassrooms()
  } catch (error) {
    console.error('加载教室列表失败:', error)
    ElMessage.error('加载教室列表失败')
  }
}

// 重置表单
const resetForm = () => {
  Object.assign(courseForm, {
    name: '',
    description: '',
    teacher_id: 0,
    classroom_id: 0
  })
  delete courseForm.id
  isEdit.value = false
}

// 编辑课程
const editCourse = (course: Course) => {
  isEdit.value = true
  Object.assign(courseForm, course)
  showCreateDialog.value = true
}

// 处理提交
const handleSubmit = async () => {
  if (!courseFormRef.value) return

  try {
    const valid = await courseFormRef.value.validate()
    if (!valid) return

    submitting.value = true

    if (isEdit.value) {
      // 编辑模式 - 这里需要后端支持更新API
      ElMessage.info('编辑功能待实现')
    } else {
      // 创建模式
      await courseAPI.createCourse(courseForm)
      ElMessage.success('课程创建成功')
      showCreateDialog.value = false
      resetForm()
      loadCourses()
    }
  } catch (error: any) {
    console.error('操作失败:', error)
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

// 删除课程
const deleteCourse = async (course: Course) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除课程"${course.name}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 这里需要后端支持删除API
    ElMessage.info('删除功能待实现')
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

onMounted(async () => {
  await Promise.all([
    loadCourses(),
    loadTeachers(),
    loadClassrooms()
  ])
})
</script>

<style scoped>
.course-management {
  padding: 24px;
  background: #f5f7fa;
  min-height: calc(100vh - 64px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  background: white;
  padding: 20px 24px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.page-title-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-icon {
  font-size: 28px;
  color: #1976d2;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.add-course-btn {
  height: 40px;
  font-weight: 500;
}

.course-list-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
  }
  
  .header-actions {
    display: flex;
    align-items: center;
    gap: 12px;
  }
}

:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table__header) {
  background: #f5f7fa;
}

:deep(.el-table th) {
  background: #f5f7fa;
  color: #606266;
  font-weight: 600;
}

:deep(.el-table .el-button) {
  margin-right: 8px;
}

:deep(.el-table .el-button:last-child) {
  margin-right: 0;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.action-buttons .el-button {
  min-width: 60px;
  font-weight: 500;
}
</style>