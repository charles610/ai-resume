<template>
  <div class="login-container">
    <div class="login-card">
      <h2>AI 简历生成器</h2>
      <div class="login-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input 
            id="username" 
            v-model="form.username" 
            type="text" 
            placeholder="请输入用户名"
            @keyup.enter="handleLogin"
          />
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input 
            id="password" 
            v-model="form.password" 
            type="password" 
            placeholder="请输入密码"
            @keyup.enter="handleLogin"
          />
        </div>
        <div class="form-actions">
          <button 
            class="login-button" 
            @click="handleLogin" 
            :disabled="isLoading"
          >
            {{ isLoading ? '登录中...' : '登录' }}
          </button>
        </div>
        <div class="register-link">
          还没有账号？<a href="#" @click.prevent="toggleRegister">立即注册</a>
        </div>
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
      </div>
    </div>

    <!-- 注册表单 -->
    <div v-if="showRegister" class="register-modal">
      <div class="register-card">
        <h2>注册新账号</h2>
        <div class="form-group">
          <label for="reg-username">用户名</label>
          <input 
            id="reg-username" 
            v-model="registerForm.username" 
            type="text" 
            placeholder="请输入用户名"
          />
        </div>
        <div class="form-group">
          <label for="reg-password">密码</label>
          <input 
            id="reg-password" 
            v-model="registerForm.password" 
            type="password" 
            placeholder="请输入密码"
          />
        </div>
        <div class="form-group">
          <label for="reg-confirm">确认密码</label>
          <input 
            id="reg-confirm" 
            v-model="registerForm.confirmPassword" 
            type="password" 
            placeholder="请再次输入密码"
          />
        </div>
        <div class="form-actions">
          <button 
            class="register-button" 
            @click="handleRegister" 
            :disabled="isLoading"
          >
            {{ isLoading ? '注册中...' : '注册' }}
          </button>
          <button 
            class="cancel-button" 
            @click="toggleRegister"
          >
            取消
          </button>
        </div>
        <div v-if="registerError" class="error-message">
          {{ registerError }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const emit = defineEmits(['login-success'])

const form = ref({
  username: '',
  password: ''
})

const registerForm = ref({
  username: '',
  password: '',
  confirmPassword: ''
})

const isLoading = ref(false)
const errorMessage = ref('')
const showRegister = ref(false)
const registerError = ref('')

async function handleLogin() {
  if (!form.value.username || !form.value.password) {
    errorMessage.value = '请输入用户名和密码'
    return
  }

  try {
    isLoading.value = true
    errorMessage.value = ''
    
    // 使用FormData格式发送请求，符合OAuth2规范
    const formData = new FormData()
    formData.append('username', form.value.username)
    formData.append('password', form.value.password)
    
    const { data } = await axios.post('/api/token', formData)
    
    // 保存令牌到本地存储
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('user', JSON.stringify({ username: form.value.username }))
    
    // 设置axios默认请求头，包含授权令牌
    axios.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`
    
    // 通知父组件登录成功
    emit('login-success', { username: form.value.username })
  } catch (error) {
    console.error('登录失败:', error)
    if (error.response?.status === 401) {
      errorMessage.value = '用户名或密码错误'
    } else {
      errorMessage.value = error.response?.data?.detail || '登录失败，请稍后再试'
    }
  } finally {
    isLoading.value = false
  }
}

function toggleRegister() {
  showRegister.value = !showRegister.value
  registerError.value = ''
}

async function handleRegister() {
  if (!registerForm.value.username || !registerForm.value.password) {
    registerError.value = '请输入用户名和密码'
    return
  }

  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    registerError.value = '两次输入的密码不一致'
    return
  }

  try {
    isLoading.value = true
    registerError.value = ''
    
    // 连接到后端API进行注册
    const { data } = await axios.post('/api/register', {
      username: registerForm.value.username,
      password: registerForm.value.password
    })
    
    // 注册成功，准备登录
    showRegister.value = false
    form.value.username = registerForm.value.username
    form.value.password = registerForm.value.password
    registerForm.value = { username: '', password: '', confirmPassword: '' }
    
    // 显示成功消息
    errorMessage.value = '注册成功，请登录'
  } catch (error) {
    console.error('注册失败:', error)
    if (error.response?.status === 400) {
      registerError.value = '用户名已被注册'
    } else {
      registerError.value = error.response?.data?.detail || '注册失败，请稍后再试'
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
  font-family: 'Arial', sans-serif;
}

.login-card {
  width: 400px;
  padding: 30px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

h2 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  transition: border-color 0.3s;
}

input:focus {
  border-color: #4a90e2;
  outline: none;
}

.form-actions {
  margin-top: 30px;
}

.login-button, .register-button {
  width: 100%;
  padding: 12px;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.login-button:hover, .register-button:hover {
  background-color: #3a7bc8;
}

.login-button:disabled, .register-button:disabled {
  background-color: #a0c0e8;
  cursor: not-allowed;
}

.error-message {
  margin-top: 15px;
  color: #e74c3c;
  text-align: center;
}

.register-link {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  color: #666;
}

.register-link a {
  color: #4a90e2;
  text-decoration: none;
}

.register-link a:hover {
  text-decoration: underline;
}

.register-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.register-card {
  width: 400px;
  padding: 30px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.cancel-button {
  width: 100%;
  padding: 12px;
  background-color: #e0e0e0;
  color: #333;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-top: 10px;
}

.cancel-button:hover {
  background-color: #d0d0d0;
}
</style>