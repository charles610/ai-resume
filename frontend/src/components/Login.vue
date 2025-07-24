<template>
  <div class="login-container">
    <div class="login-card">
      <h2>AI 简历生成器</h2>
      <div class="login-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <div class="input-wrapper">
            <input 
              id="username" 
              v-model="form.username" 
              type="text" 
              placeholder="请输入用户名"
              @keyup.enter="handleLogin"
            />
            <span v-if="form.username" class="input-icon" @click="form.username = ''">
              <i class="icon-clear">✕</i>
            </span>
          </div>
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <div class="input-wrapper">
            <input 
              id="password" 
              v-model="form.password" 
              :type="showPassword ? 'text' : 'password'" 
              placeholder="请输入密码"
              @keyup.enter="handleLogin"
            />
            <span class="input-icon" @click="showPassword = !showPassword">
              <i class="icon-eye">{{ showPassword ? '👁️' : '👁️‍🗨️' }}</i>
            </span>
          </div>
        </div>
        <div class="form-group remember-me">
          <label class="checkbox-container">
            <input type="checkbox" v-model="rememberMe">
            <span class="checkmark"></span>
            记住我
          </label>
          <a href="#" class="forgot-password" @click.prevent="forgotPassword">忘记密码?</a>
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
          <div class="input-wrapper">
            <input 
              id="reg-username" 
              v-model="registerForm.username" 
              type="text" 
              placeholder="请输入用户名 (至少3个字符)"
              @input="validateUsername"
            />
            <span v-if="registerForm.username" class="input-icon" @click="registerForm.username = ''">
              <i class="icon-clear">✕</i>
            </span>
          </div>
          <div v-if="usernameError" class="field-error">{{ usernameError }}</div>
        </div>
        <div class="form-group">
          <label for="reg-password">密码</label>
          <div class="input-wrapper">
            <input 
              id="reg-password" 
              v-model="registerForm.password" 
              :type="showRegPassword ? 'text' : 'password'" 
              placeholder="请输入密码 (至少6个字符)"
              @input="validatePassword"
            />
            <span class="input-icon" @click="showRegPassword = !showRegPassword">
              <i class="icon-eye">{{ showRegPassword ? '👁️' : '👁️‍🗨️' }}</i>
            </span>
          </div>
          <div v-if="passwordStrength" class="password-strength">
            <div class="strength-text">密码强度: {{ passwordStrengthText }}</div>
            <div class="strength-bar">
              <div 
                class="strength-indicator" 
                :style="{ width: `${passwordStrength}%`, backgroundColor: passwordStrengthColor }"
              ></div>
            </div>
          </div>
          <div v-if="passwordError" class="field-error">{{ passwordError }}</div>
        </div>
        <div class="form-group">
          <label for="reg-confirm">确认密码</label>
          <div class="input-wrapper">
            <input 
              id="reg-confirm" 
              v-model="registerForm.confirmPassword" 
              :type="showRegPassword ? 'text' : 'password'" 
              placeholder="请再次输入密码"
              @input="validateConfirmPassword"
            />
          </div>
          <div v-if="confirmPasswordError" class="field-error">{{ confirmPasswordError }}</div>
        </div>
        <div class="form-actions">
          <button 
            class="register-button" 
            @click="handleRegister" 
            :disabled="isLoading || !isRegisterFormValid"
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
import { ref, computed, onMounted } from 'vue'
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
const showPassword = ref(false)
const showRegPassword = ref(false)
const rememberMe = ref(false)
const usernameError = ref('')
const passwordError = ref('')
const confirmPasswordError = ref('')
const passwordStrength = ref(0)

// 密码强度相关计算属性
const passwordStrengthText = computed(() => {
  if (passwordStrength.value < 30) return '弱'
  if (passwordStrength.value < 60) return '中'
  return '强'
})

const passwordStrengthColor = computed(() => {
  if (passwordStrength.value < 30) return '#ff4d4f'
  if (passwordStrength.value < 60) return '#faad14'
  return '#52c41a'
})

const isRegisterFormValid = computed(() => {
  return !usernameError.value && 
         !passwordError.value && 
         !confirmPasswordError.value && 
         registerForm.value.username && 
         registerForm.value.password && 
         registerForm.value.confirmPassword
})

onMounted(() => {
  // 检查本地存储中是否有保存的用户名
  const savedUsername = localStorage.getItem('rememberedUsername')
  if (savedUsername) {
    form.value.username = savedUsername
    rememberMe.value = true
  }
})

// 表单验证函数
function validateUsername() {
  usernameError.value = ''
  
  if (!registerForm.value.username) {
    usernameError.value = '用户名不能为空'
    return
  }
  
  if (registerForm.value.username.length < 3) {
    usernameError.value = '用户名至少需要3个字符'
    return
  }
  
  if (!/^[a-zA-Z0-9_]+$/.test(registerForm.value.username)) {
    usernameError.value = '用户名只能包含字母、数字和下划线'
  }
}

function validatePassword() {
  passwordError.value = ''
  
  if (!registerForm.value.password) {
    passwordStrength.value = 0
    return
  }
  
  if (registerForm.value.password.length < 6) {
    passwordError.value = '密码至少需要6个字符'
    passwordStrength.value = 10
    return
  }
  
  // 计算密码强度
  let strength = 0
  
  // 长度检查
  strength += Math.min(registerForm.value.password.length * 4, 25)
  
  // 包含数字
  if (/\d/.test(registerForm.value.password)) strength += 10
  
  // 包含小写字母
  if (/[a-z]/.test(registerForm.value.password)) strength += 10
  
  // 包含大写字母
  if (/[A-Z]/.test(registerForm.value.password)) strength += 15
  
  // 包含特殊字符
  if (/[^a-zA-Z0-9]/.test(registerForm.value.password)) strength += 15
  
  // 字符多样性
  const uniqueChars = new Set(registerForm.value.password.split('')).size
  strength += uniqueChars * 2
  
  passwordStrength.value = Math.min(strength, 100)
  
  // 根据强度给出提示
  if (passwordStrength.value < 30) {
    passwordError.value = '密码强度较弱，建议包含字母、数字和特殊字符'
  }
}

function validateConfirmPassword() {
  confirmPasswordError.value = ''
  
  if (!registerForm.value.confirmPassword) {
    return
  }
  
  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    confirmPasswordError.value = '两次输入的密码不一致'
  }
}

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
    
    // 如果选择了"记住我"，保存用户名
    if (rememberMe.value) {
      localStorage.setItem('rememberedUsername', form.value.username)
    } else {
      localStorage.removeItem('rememberedUsername')
    }
    
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
  
  // 重置表单错误
  usernameError.value = ''
  passwordError.value = ''
  confirmPasswordError.value = ''
  passwordStrength.value = 0
  
  // 重置注册表单
  if (showRegister.value) {
    registerForm.value = { username: '', password: '', confirmPassword: '' }
  }
}

function forgotPassword() {
  // 这里可以实现忘记密码功能，例如显示一个模态框或导航到密码重置页面
  alert('密码重置功能正在开发中，请联系管理员重置密码。')
}

async function handleRegister() {
  // 先验证所有字段
  validateUsername()
  validatePassword()
  validateConfirmPassword()
  
  // 如果有错误，不继续注册
  if (!isRegisterFormValid.value) {
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