<template>
  <div class="classroom-management">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><School /></el-icon>
        教室管理
      </h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新增教室
      </el-button>
    </div>

    <!-- 教室列表 -->
    <el-card class="classroom-list-card">
      <template #header>
        <div class="card-header">
          <span>教室列表</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索教室名称或位置..."
              prefix-icon="Search"
              clearable
              style="width: 250px"
            />
          </div>
        </div>
      </template>

      <el-table
        :data="filteredClassrooms"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="name" label="教室名称" min-width="120" />
        <el-table-column prop="location" label="位置" min-width="150" />
        <el-table-column prop="room_number" label="门牌号" width="100" />
        <el-table-column prop="capacity" label="容量" width="80">
          <template #default="{ row }">
            {{ row.capacity || '-' }}人
          </template>
        </el-table-column>
        <el-table-column prop="equipment_info" label="设备情况" min-width="200">
          <template #default="{ row }">
            {{ row.equipment_info || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
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
                @click="editClassroom(row)"
              >
                编辑
              </el-button>
              <el-button
                type="danger"
                size="small"
                @click="deleteClassroom(row)"
              >
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑教室对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="isEdit ? '编辑教室' : '新增教室'"
      width="600px"
    >
      <el-form
        ref="classroomFormRef"
        :model="classroomForm"
        :rules="classroomRules"
        label-width="100px"
      >
        <el-form-item label="教室名称" prop="name">
          <el-input v-model="classroomForm.name" placeholder="请输入教室名称" />
        </el-form-item>
        
        <el-form-item label="位置" prop="location">
          <el-input v-model="classroomForm.location" placeholder="请输入教室位置" />
        </el-form-item>
        
        <el-form-item label="门牌号" prop="room_number">
          <el-input v-model="classroomForm.room_number" placeholder="请输入门牌号" />
        </el-form-item>
        
        <el-form-item label="容量">
          <el-input-number
            v-model="classroomForm.capacity"
            :min="1"
            :max="1000"
            placeholder="容量"
          />
        </el-form-item>
        
        <el-form-item label="设备情况">
          <el-input
            v-model="classroomForm.equipment_info"
            type="textarea"
            :rows="3"
            placeholder="请描述教室的设备情况"
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
import { classroomAPI } from '@/api'
import type { Classroom, ClassroomCreate } from '@/types'

// 响应式数据
const classrooms = ref<Classroom[]>([])
const loading = ref(false)
const submitting = ref(false)
const showCreateDialog = ref(false)
const isEdit = ref(false)
const searchKeyword = ref('')
const classroomFormRef = ref<FormInstance>()

// 表单数据
const classroomForm = reactive<ClassroomCreate & { id?: number }>({
  name: '',
  location: '',
  room_number: '',
  equipment_info: '',
  capacity: undefined
})

// 表单验证规则
const classroomRules = {
  name: [{ required: true, message: '请输入教室名称', trigger: 'blur' }],
  location: [{ required: true, message: '请输入教室位置', trigger: 'blur' }],
  room_number: [{ required: true, message: '请输入门牌号', trigger: 'blur' }]
}

// 计算属性
const filteredClassrooms = computed(() => {
  if (!searchKeyword.value) return classrooms.value
  
  const keyword = searchKeyword.value.toLowerCase()
  return classrooms.value.filter(classroom =>
    classroom.name.toLowerCase().includes(keyword) ||
    classroom.location.toLowerCase().includes(keyword) ||
    classroom.room_number.toLowerCase().includes(keyword)
  )
})

// 格式化日期时间
const formatDateTime = (dateStr: string) => {
  return new Date(dateStr).toLocaleString()
}

// 加载教室列表
const loadClassrooms = async () => {
  try {
    loading.value = true
    classrooms.value = await classroomAPI.getClassrooms()
  } catch (error) {
    console.error('加载教室列表失败:', error)
    ElMessage.error('加载教室列表失败')
  } finally {
    loading.value = false
  }
}

// 重置表单
const resetForm = () => {
  Object.assign(classroomForm, {
    name: '',
    location: '',
    room_number: '',
    equipment_info: '',
    capacity: undefined
  })
  delete classroomForm.id
  isEdit.value = false
}

// 编辑教室
const editClassroom = (classroom: Classroom) => {
  isEdit.value = true
  Object.assign(classroomForm, classroom)
  showCreateDialog.value = true
}

// 处理提交
const handleSubmit = async () => {
  if (!classroomFormRef.value) return

  try {
    const valid = await classroomFormRef.value.validate()
    if (!valid) return

    submitting.value = true

    if (isEdit.value) {
      // 编辑模式 - 这里需要后端支持更新API
      ElMessage.info('编辑功能待实现')
    } else {
      // 创建模式
      await classroomAPI.createClassroom(classroomForm)
      ElMessage.success('教室创建成功')
      showCreateDialog.value = false
      resetForm()
      loadClassrooms()
    }
  } catch (error: any) {
    console.error('操作失败:', error)
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

// 删除教室
const deleteClassroom = async (classroom: Classroom) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除教室"${classroom.name}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await classroomAPI.deleteClassroom(classroom.id)
    ElMessage.success('教室删除成功')
    loadClassrooms()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

onMounted(() => {
  loadClassrooms()
})
</script>

<style scoped>
.classroom-management {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.classroom-list-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
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