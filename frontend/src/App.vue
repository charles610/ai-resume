<template>
  <div id="app">
    <div v-if="isLoading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>
    <template v-else>
      <Login v-if="!isLoggedIn" @login-success="handleLoginSuccess" />
      <div v-else class="app-container">
        <header class="app-header">
          <h1>AI 简历生成器</h1>
          <div class="user-info">
            <span>欢迎，{{ user.username }}</span>
            <button class="logout-button" @click="handleLogout">退出登录</button>
          </div>
        </header>
        <main class="app-content">
          <ResumeGenerator />
        </main>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Login from './components/Login.vue'
import ResumeGenerator from './components/ResumeGenerator.vue'

const isLoggedIn = ref(false)
const user = ref(null)
const isLoading = ref(true)

onMounted(async () => {
  // 检查本地存储中是否有令牌
  const token = localStorage.getItem('token')
  const storedUser = localStorage.getItem('user')
  
  if (token && storedUser) {
    try {
      // 设置默认请求头
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      
      // 验证令牌有效性
      const { data } = await axios.get('/api/user/me')
      
      // 令牌有效，设置用户信息
      user.value = JSON.parse(storedUser)
      isLoggedIn.value = true
    } catch (error) {
      console.error('令牌验证失败:', error)
      // 令牌无效，清除本地存储
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
  
  isLoading.value = false
})

function handleLoginSuccess(userData) {
  user.value = userData
  isLoggedIn.value = true
}

function handleLogout() {
  // 清除用户信息和令牌并返回登录页
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  // 清除请求头中的授权信息
  delete axios.defaults.headers.common['Authorization']
  user.value = null
  isLoggedIn.value = false
}
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Arial', sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: #f5f5f5;
}

#app {
  min-height: 100vh;
}

.loading-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.loading-spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border-left-color: #4a90e2;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  background-color: #4a90e2;
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logout-button {
  background-color: transparent;
  border: 1px solid white;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.logout-button:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.app-content {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}
</style>