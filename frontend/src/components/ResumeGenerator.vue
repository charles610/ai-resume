<template>
  <div class="resume-generator">
    <h2>AI 简历生成器</h2>
    <div>
      <label>选择模板：</label>
      <select v-model="selectedTemplate">
        <option v-for="tpl in templates" :key="tpl.id" :value="tpl.id">{{ tpl.name }}</option>
      </select>
    </div>

    <div>
      <label>填写个人信息：</label>
      <input v-model="form.name" placeholder="姓名"/>
      <input v-model="form.phone" placeholder="电话"/>
      <input v-model="form.email" placeholder="邮箱"/>
    </div>

    <div>
      <label>求职岗位：</label>
      <input v-model="form.position" placeholder="如：Java开发工程师"/>
    </div>

    <button @click="generateResume">生成简历</button>

    <div v-if="generatedResume" v-html="generatedResume"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
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

onMounted(async () => {
  const { data } = await axios.get('/api/templates')
  templates.value = data
})

async function generateResume() {
  const { data } = await axios.post('/api/generate', {
    ...form.value,
    templateId: selectedTemplate.value
  })
  generatedResume.value = data.html
}
</script>
