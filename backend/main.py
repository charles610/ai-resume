from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import openai
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

# 配置JWT
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # 在生产环境中应该使用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 密码哈希
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

app = FastAPI()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境中应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 加载简历模板
try:
    with open('templates/resume-template.json', 'r', encoding='utf-8') as f:
        templates = json.load(f)
except FileNotFoundError:
    # 如果文件不存在，使用一个空列表
    templates = []

# 用户数据模型
class User(BaseModel):
    username: str
    hashed_password: str

# 用户数据库 (示例，实际应使用真实数据库)
users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("password")
    }
}

# 令牌模型
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# 简历请求模型
class ResumeRequest(BaseModel):
    name: str
    phone: str
    email: str
    position: str
    templateId: str

# 用户注册模型
class UserCreate(BaseModel):
    username: str
    password: str

# 验证用户
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str):
    if username in users_db:
        return User(**users_db[username])
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# 创建访问令牌
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 获取当前用户
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# 生成简历文本
def generate_resume_text(position: str, name: str):
    prompt = f"请为求职者{name}生成一份适合{position}的简历内容，包括个人简介、项目经历、技能等，语言简洁专业。"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        # 如果API调用失败，返回一个示例内容
        print(f"OpenAI API调用失败: {e}")
        return f"""
# {name} - {position}

## 个人简介
资深{position}，拥有丰富的行业经验，擅长解决复杂问题和团队协作。

## 技能
- 专业技能1
- 专业技能2
- 专业技能3

## 工作经历
### ABC公司 (2018-2022)
- 主要职责和成就1
- 主要职责和成就2

### XYZ公司 (2015-2018)
- 主要职责和成就1
- 主要职责和成就2

## 教育背景
- 某大学 计算机科学学士 (2011-2015)
        """

# API路由
@app.post("/api/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/register")
async def register_user(user_data: UserCreate):
    if user_data.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = pwd_context.hash(user_data.password)
    users_db[user_data.username] = {
        "username": user_data.username,
        "hashed_password": hashed_password
    }
    
    return {"message": "User registered successfully"}

@app.get("/api/templates")
def get_templates():
    return templates

@app.post("/api/generate")
def generate_resume(req: ResumeRequest):
    # 查找匹配的模板
    try:
        template = next(t for t in templates if t['id'] == req.templateId)
    except StopIteration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # 生成简历内容
    content = generate_resume_text(req.position, req.name)
    
    # 替换模板中的占位符
    html = template['html'].replace("{{name}}", req.name)\
                           .replace("{{phone}}", req.phone)\
                           .replace("{{email}}", req.email)\
                           .replace("{{content}}", content)

    return {"html": html}

@app.get("/api/user/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username}
