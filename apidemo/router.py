from fastapi import APIRouter, WebSocket, Depends, HTTPException
from apidemo.models import ImageGenerationRequest
import uuid
from apidemo import get_output
import random
import os
from fastapi.responses import JSONResponse
from apidemo.utils import load_json_template
from apidemo.get_output import get_outputs
from sqlalchemy.orm import Session
from datetime import timedelta
from .database import SessionLocal, User
from .models import UserCreate, UserLogin, UserResponse, PasswordResetRequest, PasswordReset
from .auth import create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
import jwt
from .email_utils import send_reset_email

# 获取项目根目录路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 创建路由实例
router = APIRouter(
    prefix="",
    tags=["数字织造师"]
)

# 数据库会话依赖
def get_db():
    """
    创建数据库会话的依赖函数
    使用yield确保会话在请求结束后关闭
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册接口
    Args:
        user: 包含用户名和密码的注册信息
        db: 数据库会话
    Returns:
        包含用户名和token的响应
    """
    try:
        # 检查用户名是否已存在
        if db.query(User).filter(User.username == user.username).first():
            raise HTTPException(status_code=400, detail="用户名已被注册")
        
        # 检查邮箱是否已存在
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(status_code=400, detail="邮箱已被注册")
        
        # 创建新用户并保存
        hashed_password = User.hash_password(user.password)
        db_user = User(
            username=user.username, 
            email=user.email,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # 生成访问令牌
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {"username": user.username, "token": access_token}
    except Exception as e:
        print(f"注册错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login", response_model=UserResponse)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录接口
    Args:
        user: 包含邮箱和密码的登录信息
        db: 数据库会话
    Returns:
        包含用户名和token的响应
    """
    # 验证用户凭证
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not db_user.verify_password(user.password):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    
    # 生成访问令牌
    access_token = create_access_token(
        data={"sub": db_user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {"username": db_user.username, "token": access_token}

@router.post("/generate_img")
async def generate_img(data: ImageGenerationRequest, token: dict = Depends(verify_token)):
    """
    图像生成接口
    Args:
        data: 图像生成参数
        token: 用户认证token
    Returns:
        生成的图像URL列表
    """
    # 生成唯一客户端ID
    client_id = str(uuid.uuid4())
    
    # 加载工作流模板
    workflow_path = os.path.join(BASE_DIR, "apidemo", "work2.json")
    prompt = load_json_template(workflow_path)
    
    # 配置生成参数
    prompt["57"]["inputs"]["noise_seed"] = random.randrange(10 ** 14, 10 ** 15)
    prompt["65"]["inputs"]["t5xxl"] = data.prompt
    prompt["65"]["inputs"]["clip_l"] = data.prompt2
    prompt["56"]["inputs"]["width"] = data.width
    prompt["56"]["inputs"]["height"] = data.height
    prompt["59"]["inputs"]["steps"] = data.steps

    # 执行生成并返回结果
    images = await get_outputs(client_id, prompt)
    return JSONResponse(content={"images": images["images"], "tags": images["tags"]})

@router.websocket("/ws/progress/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket连接处理
    用于实时返回图像生成进度
    Args:
        websocket: WebSocket连接
        client_id: 客户端ID
    """
    await websocket.accept()
    
    try:
        # 验证用户token
        data = await websocket.receive_json()
        if data.get('type') != 'authorization':
            await websocket.close(code=4001)
            return
            
        try:
            token = data['token'].split(" ")[1]
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except Exception as e:
            print(f"Token验证失败: {e}")
            await websocket.close(code=4001)
            return
            
        # 处理生成请求
        async def progress_callback(progress_data):
            await websocket.send_json(progress_data)
        
        try:
            while True:
                data = await websocket.receive_json()
                if data['type'] == 'generate':
                    # 配置生成参数
                    workflow_path = os.path.join(BASE_DIR, "apidemo", "work2.json")
                    prompt = load_json_template(workflow_path)
                    prompt["57"]["inputs"]["noise_seed"] = random.randrange(10 ** 14, 10 ** 15)
                    prompt["65"]["inputs"]["t5xxl"] = data['prompt']
                    prompt["65"]["inputs"]["clip_l"] = data['prompt2']
                    prompt["56"]["inputs"]["width"] = data['width']
                    prompt["56"]["inputs"]["height"] = data['height']
                    prompt["59"]["inputs"]["steps"] = data['steps']

                    # 执行生成
                    result = await get_outputs(client_id, prompt, progress_callback)
                    await websocket.send_json({"type": "result", "data": result})
        except Exception as e:
            print(f"WebSocket处理错误: {e}")
        finally:
            await websocket.close()
    except Exception as e:
        print(f"WebSocket错误: {e}")
        await websocket.close()

@router.post("/forgot-password")
async def forgot_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            raise HTTPException(status_code=404, detail="该邮箱未注册")
        
        # 生成重置token
        reset_token = create_access_token(
            data={"sub": user.username, "type": "reset"},
            expires_delta=timedelta(minutes=30)
        )
        
        # 发送重置邮件
        email_sent = await send_reset_email(user.email, reset_token)
        if not email_sent:
            raise HTTPException(status_code=500, detail="邮件发送失败，请稍后重试")
        
        return {"message": "重置链接已发送到您的邮箱"}
    except Exception as e:
        print(f"密码重置错误: {str(e)}")  # 添加错误日志
        raise HTTPException(status_code=500, detail=f"密码重置失败: {str(e)}")

from pydantic import BaseModel

class CancelRequest(BaseModel):
    client_id: str

@router.post("/cancel")
async def cancel_generation(request: CancelRequest):
    """取消正在进行的生成任务"""
    success = await get_output.cancel_task(request.client_id)
    return {"success": success, "message": "任务已取消" if success else "未找到进行中的任务"}

@router.post("/reset-password")
async def reset_password(request: PasswordReset, db: Session = Depends(get_db)):
    try:
        # 验证token
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "reset":
            raise HTTPException(status_code=400, detail="无效的重置链接")
        
        username = payload.get("sub")
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 更新密码
        user.hashed_password = User.hash_password(request.new_password)
        db.commit()
        
        return {"message": "密码重置成功"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="重置链接已过期")
    except jwt.JWTError:
        raise HTTPException(status_code=400, detail="无效的重置链接")