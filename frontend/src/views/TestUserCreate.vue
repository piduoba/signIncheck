<template>
  <div class="test-user-create">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>新增用户功能诊断</span>
        </div>
      </template>
      
      <div class="test-section">
        <h3>🔍 诊断步骤</h3>
        
        <!-- 步骤1: 检查登录状态 -->
        <div class="test-item">
          <h4>1. 检查登录状态</h4>
          <p>当前用户: {{ userStore.user?.username }} ({{ userStore.user?.role }})</p>
          <p>是否为管理员: {{ userStore.isAdmin ? '✅ 是' : '❌ 否' }}</p>
          <el-button @click="checkLoginStatus" type="primary" size="small">重新检查</el-button>
        </div>
        
        <!-- 步骤2: 测试API连接 -->
        <div class="test-item">
          <h4>2. 测试API连接</h4>
          <p>后端状态: {{ apiStatus }}</p>
          <el-button @click="testAPIConnection" type="primary" size="small" :loading="testing">测试连接</el-button>
        </div>
        
        <!-- 步骤3: 测试新增用户 -->
        <div class="test-item">
          <h4>3. 测试新增用户功能</h4>
          <el-form :model="testForm" label-width="100px" size="small">
            <el-form-item label="用户名">
              <el-input v-model="testForm.username" placeholder="输入测试用户名" />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="testForm.email" placeholder="输入测试邮箱" />
            </el-form-item>
            <el-form-item label="密码">
              <el-input v-model="testForm.password" placeholder="输入测试密码" />
            </el-form-item>
            <el-form-item label="姓名">
              <el-input v-model="testForm.full_name" placeholder="输入测试姓名" />
            </el-form-item>
            <el-form-item label="角色">
              <el-select v-model="testForm.role">
                <el-option label="学生" value="student" />
                <el-option label="老师" value="teacher" />
                <el-option label="管理员" value="admin" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button @click="testCreateUser" type="success" :loading="creating">创建测试用户</el-button>
            </el-form-item>
          </el-form>
          
          <div v-if="createResult" class="result">
            <h5>创建结果:</h5>
            <pre>{{ createResult }}</pre>
          </div>
        </div>
        
        <!-- 步骤4: 常见问题解决方案 -->
        <div class="test-item">
          <h4>4. 常见问题解决方案</h4>
          <el-collapse>
            <el-collapse-item title="权限不足" name="1">
              <p>确保您以管理员身份登录。只有管理员才能创建新用户。</p>
              <p>当前用户角色: {{ userStore.user?.role }}</p>
            </el-collapse-item>
            <el-collapse-item title="网络连接问题" name="2">
              <p>检查后端服务是否正常运行在 http://localhost:8000</p>
              <p>检查CORS配置是否正确</p>
            </el-collapse-item>
            <el-collapse-item title="表单验证失败" name="3">
              <p>确保所有必填字段都已填写：</p>
              <ul>
                <li>用户名: 3-20个字符</li>
                <li>邮箱: 有效的邮箱格式</li>
                <li>密码: 至少6位</li>
                <li>姓名: 必填</li>
                <li>角色: 必选</li>
              </ul>
            </el-collapse-item>
            <el-collapse-item title="重复数据" name="4">
              <p>用户名和邮箱必须唯一，如果已存在相同的用户名或邮箱会导致创建失败。</p>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { userAPI } from '@/api'
import axios from 'axios'

const userStore = useUserStore()

// 测试状态
const testing = ref(false)
const creating = ref(false)
const apiStatus = ref('未测试')
const createResult = ref('')

// 测试表单
const testForm = reactive({
  username: 'test' + Date.now(),
  email: 'test' + Date.now() + '@example.com',
  password: '123456',
  full_name: '测试用户',
  role: 'student'
})

// 检查登录状态
const checkLoginStatus = () => {
  userStore.init()
  ElMessage.info('已刷新登录状态')
}

// 测试API连接
const testAPIConnection = async () => {
  testing.value = true
  try {
    // 测试健康检查
    const response = await axios.get('http://localhost:8000/api/health')
    if (response.status === 200) {
      apiStatus.value = '✅ 连接正常'
      ElMessage.success('API连接正常')
    }
  } catch (error) {
    apiStatus.value = '❌ 连接失败'
    ElMessage.error('API连接失败: ' + error)
  } finally {
    testing.value = false
  }
}

// 测试创建用户
const testCreateUser = async () => {
  creating.value = true
  createResult.value = ''
  
  try {
    // 验证基本字段
    if (!testForm.username || !testForm.email || !testForm.password || !testForm.full_name) {
      throw new Error('请填写所有必填字段')
    }
    
    // 检查权限
    if (!userStore.isAdmin) {
      throw new Error('权限不足：只有管理员才能创建用户')
    }
    
    // 创建用户
    const result = await userAPI.createUser({
      username: testForm.username,
      email: testForm.email,
      password: testForm.password,
      full_name: testForm.full_name,
      role: testForm.role as 'admin' | 'teacher' | 'student',
      is_active: true
    })
    
    createResult.value = '✅ 创建成功!\n' + JSON.stringify(result, null, 2)
    ElMessage.success('测试用户创建成功')
    
    // 更新表单为下一次测试
    testForm.username = 'test' + Date.now()
    testForm.email = 'test' + Date.now() + '@example.com'
    
  } catch (error: any) {
    createResult.value = '❌ 创建失败!\n' + JSON.stringify({
      message: error.message,
      response: error.response?.data,
      status: error.response?.status
    }, null, 2)
    ElMessage.error('创建失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    creating.value = false
  }
}
</script>

<style scoped>
.test-user-create {
  padding: 20px;
}

.test-section {
  max-width: 800px;
}

.test-item {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
}

.test-item h4 {
  margin-top: 0;
  color: #409eff;
}

.result {
  margin-top: 15px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.result pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>