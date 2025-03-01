from fastapi import FastAPI
from pydantic import BaseModel
import json
import openai

app = FastAPI()

with open('templates/resume-template.json', 'r', encoding='utf-8') as f:
    templates = json.load(f)

class ResumeRequest(BaseModel):
    name: str
    phone: str
    email: str
    position: str
    templateId: str

def generate_resume_text(position: str, name: str):
    prompt = f"请为求职者{name}生成一份适合{position}的简历内容，包括个人简介、项目经历、技能等，语言简洁专业。"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

@app.get("/api/templates")
def get_templates():
    return templates

@app.post("/api/generate")
def generate_resume(req: ResumeRequest):
    content = generate_resume_text(req.position, req.name)
    template = next(t for t in templates if t['id'] == req.templateId)

    html = template['html'].replace("{{name}}", req.name)\
                           .replace("{{phone}}", req.phone)\
                           .replace("{{email}}", req.email)\
                           .replace("{{content}}", content)

    return {"html": html}
