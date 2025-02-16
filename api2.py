import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from apidemo.router import router
from apidemo.models import ImageGenerationRequest
from apidemo.auth import verify_token, HTTPBearer, HTTPAuthorizationCredentials
import logging
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用实例
app = FastAPI(
    title="数字织造师",
    description="AI图像生成服务"
)

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 配置静态文件
app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")

security = HTTPBearer(auto_error=False)

# 添加路由处理
@app.get("/login", response_class=HTMLResponse)
async def serve_index():
    """登录页面"""
    return FileResponse("1.html")

@app.get("/", response_class=HTMLResponse)
async def root():
    """重定向到登录页面"""
    return RedirectResponse(url="/login")

@app.get("/home", response_class=HTMLResponse)
async def serve_main():
    """主应用页面"""
    return FileResponse("4_start.html")

@app.get("/reset", response_class=HTMLResponse)
async def serve_reset_password():
    """密码重置页面"""
    return FileResponse("reset-password.html")

@app.get("/reset-password.html", response_class=HTMLResponse)
async def serve_reset_password_with_token():
    """带token的密码重置页面"""
    return FileResponse("reset-password.html")

# 添加新的路由处理图片下载
@app.get("/download")
async def download_image(filename: str, subfolder: str = "", type: str = "output"):
    """
    处理图片下载请求
    Args:
        filename: 图片文件名
        subfolder: 子文件夹名称
        type: 输出类型
    Returns:
        FileResponse: 文件下载响应
    """
    try:
        # 图片文件路径
        file_path = os.path.join("F:\\ComfyUI_windows_portable\\ComfyUI", type, subfolder, filename)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            raise HTTPException(status_code=404, detail="图片不存在")
            
        # 返回文件下载响应
        return FileResponse(
            file_path,
            media_type="image/png",
            filename=filename,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        logger.error(f"下载图片错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 更新CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "Content-Type", "Content-Length"]
)

# 注册路由
app.include_router(router)

# 主程序入口
if __name__ == "__main__":
    logger.info("Starting FastAPI application...")
    uvicorn.run("api2:app", host="127.0.0.1", port=8000, reload=True)
