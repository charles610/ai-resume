<template>
  <div class="resume-generator">
    <div class="generator-card">
      <h2>创建您的专业简历</h2>
      
      <div class="form-section">
        <div class="form-group">
          <label for="template-select">选择模板：</label>
          <select 
            id="template-select"
            v-model="selectedTemplate"
            class="form-control"
          >
            <option value="" disabled selected>请选择一个模板</option>
            <option v-for="tpl in templates" :key="tpl.id" :value="tpl.id">{{ tpl.name }}</option>
          </select>
        </div>

        <div class="form-group">
          <label>个人信息</label>
          <div class="personal-info">
            <input 
              v-model="form.name" 
              placeholder="姓名"
              class="form-control"
            />
            <input 
              v-model="form.phone" 
              placeholder="电话"
              class="form-control"
            />
            <input 
              v-model="form.email" 
              placeholder="邮箱"
              class="form-control"
            />
          </div>
        </div>

        <div class="form-group">
          <label for="position">求职岗位：</label>
          <input 
            id="position"
            v-model="form.position" 
            placeholder="如：Java开发工程师"
            class="form-control"
          />
        </div>

        <button 
          class="generate-button" 
          @click="generateResume"
          :disabled="isGenerating || !isFormValid"
        >
          {{ isGenerating ? '生成中...' : '生成简历' }}
        </button>
      </div>
    </div>

    <div v-if="isGenerating" class="loading-indicator">
      <div class="spinner"></div>
      <p>AI 正在为您生成专业简历，请稍候...</p>
    </div>

    <div v-if="generatedResume && !isGenerating" class="resume-preview">
      <div class="preview-header">
        <h3>您的简历预览</h3>
        <button class="download-button" @click="downloadResume">下载简历</button>
      </div>
      <div class="resume-content" v-html="generatedResume"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const templates = ref([])
const selectedTemplate = ref('')
const form = ref({
  name: '',
  phone: '',
  email: '',
  position: ''
})
const generatedResume = ref('')
const isGenerating = ref(false)

const isFormValid = computed(() => {
  return selectedTemplate.value && 
         form.value.name && 
         form.value.phone && 
         form.value.email && 
         form.value.position
})

onMounted(async () => {
  try {
    const { data } = await axios.get('/api/templates')
    templates.value = data
    if (data.length > 0) {
      selectedTemplate.value = data[0].id
    }
  } catch (error) {
    console.error('获取模板失败:', error)
  }
})

async function generateResume() {
  if (!isFormValid.value) return
  
  try {
    isGenerating.value = true
    const { data } = await axios.post('/api/generate', {
      ...form.value,
      templateId: selectedTemplate.value
    })
    generatedResume.value = data.html
  } catch (error) {
    console.error('生成简历失败:', error)
    alert('生成简历失败，请稍后再试')
  } finally {
    isGenerating.value = false
  }
}

function downloadResume() {
  // 创建一个临时的a元素
  const element = document.createElement('a')
  const file = new Blob([generatedResume.value], {type: 'text/html'})
  element.href = URL.createObjectURL(file)
  element.download = `${form.value.name}-简历.html`
  document.body.appendChild(element)
  element.click()
  document.body.removeChild(element)
}
</script>

<style scoped>
.resume-generator {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.generator-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 30px;
  margin-bottom: 30px;
}

h2 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

.form-control {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.form-control:focus {
  border-color: #4a90e2;
  outline: none;
}

.personal-info {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.generate-button {
  width: 100%;
  padding: 12px;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-top: 10px;
}

.generate-button:hover {
  background-color: #3a7bc8;
}

.generate-button:disabled {
  background-color: #a0c0e8;
  cursor: not-allowed;
}

.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.spinner {
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

.resume-preview {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 30px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.download-button {
  padding: 8px 16px;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.download-button:hover {
  background-color: #3a7bc8;
}

.resume-content {
  padding: 20px;
  border: 1px solid #eee;
  border-radius: 4px;
  background-color: #fafafa;
  min-height: 500px;
}
</style>
