import json
import requests
import urllib.parse
import websockets
import os
import requests
from apidemo.utils import image_to_base64
from typing import Dict, List, Optional, Any
import logging
from typing import Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ComfyUI服务器地址
server_address = "127.0.0.1:8188"

# 全局任务跟踪
active_tasks: Dict[str, Any] = {}

# 新增取消任务函数
async def cancel_task(client_id: str):
    """取消正在进行的生成任务"""
    try:
        if client_id in active_tasks:
            task = active_tasks[client_id]
            task['cancelled'] = True
            
            # 向ComfyUI发送中断请求
            try:
                response = requests.post(f"http://{server_address}/interrupt")
                response.raise_for_status()
                logger.info(f"成功发送中断请求: {client_id}")
            except requests.RequestException as e:
                logger.warning(f"发送中断请求时出现错误: {str(e)}")
            
            # 关闭WebSocket连接
            if task.get('websocket'):
                try:
                    await task['websocket'].close()
                    logger.info(f"成功关闭WebSocket连接: {client_id}")
                except Exception as e:
                    logger.warning(f"关闭WebSocket连接时出现错误: {str(e)}")
            
            return True
        return False
    except Exception as e:
        logger.error(f"取消任务时出现错误: {str(e)}", exc_info=True)
        return False

# 工作流中的节点总数
TOTAL_NODES = 13

# 向ComfyUI服务器发送提示词
async def queue_prompt(prompt: Dict[str, Any], client_id: str) -> Dict[str, Any]:
    """
    将生成请求加入ComfyUI队列
    Args:
        prompt: 生成参数
        client_id: 客户端ID
    Returns:
        响应JSON
    Raises:
        HTTPError: 请求失败时
    """
    url = f"http://{server_address}/prompt"
    payload = {"prompt": prompt, "client_id": client_id}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"请求失败: {str(e)}")
        raise

# 构建图像URL
def get_image_url(filename, subfolder, folder_type):
    """
    构建图像访问URL
    Args:
        filename: 文件名
        subfolder: 子文件夹
        folder_type: 文件夹类型
    Returns:
        完整的图像URL
    """
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    # 确保返回完整的URL
    return f"http://{server_address}/view?{url_values}"

# 获取生成历史记录
def get_history(prompt_id):
    with urllib.request.urlopen(f"http://{server_address}/history/{prompt_id}") as response:
        return json.loads(response.read())

# 获取生成输出结果
async def get_outputs(client_id: str, prompt: Dict[str, Any], 
                     progress_callback: Optional[callable] = None) -> Dict[str, List[str]]:
    """
    获取图像生成结果
    """
    try:
        prompt_id = (await queue_prompt(prompt, client_id))['prompt_id']
        output_images = []  # 存储生成的图片URL
        output_tags = []
        
        async with websockets.connect(f"ws://{server_address}/ws?clientId={client_id}") as websocket:
            active_tasks[client_id] = {
                'websocket': websocket,
                'prompt_id': prompt_id,
                'cancelled': False
            }
            
            while True:
                try:
                    message = json.loads(await websocket.recv())
                    logger.debug(f"收到消息: {message}")  # 改用debug级别记录详细消息
                    
                    if progress_callback:
                        if message['type'] == 'progress':
                            data = message['data']
                            if data['node'] == '13' and data['prompt_id'] == prompt_id:
                                progress = int(data['value']) / int(data['max'])
                                await progress_callback({
                                    'status': 'processing',
                                    'progress': progress,
                                    'text': f"生成图像中... {int(progress * 100)}%"
                                })
                        elif message['type'] == 'executed':
                            # 当收到executed消息时，说明图像已生成
                            if 'images' in message['data']['output']:
                                image_data = message['data']['output']['images'][0]
                                image_url = get_image_url(
                                    image_data['filename'],
                                    image_data.get('subfolder', ''),
                                    image_data.get('type', '')
                                )
                                output_images.append(image_url)
                                await progress_callback({
                                    'type': 'result',
                                    'data': {'images': output_images}
                                })
                                break
                            
                except websockets.WebSocketException as e:
                    if active_tasks.get(client_id, {}).get('cancelled'):
                        logger.info(f"WebSocket连接已取消: {client_id}")
                    else:
                        logger.error(f"WebSocket连接错误: {str(e)}")
                    break

        return {"images": output_images, "tags": output_tags}
        
    except Exception as e:
        logger.error(f"生成过程错误: {str(e)}", exc_info=True)
        raise
    finally:
        if client_id in active_tasks:
            try:
                if active_tasks[client_id].get('websocket'):
                    await active_tasks[client_id]['websocket'].close()
            except Exception as e:
                logger.warning(f"清理WebSocket连接时出现错误: {str(e)}")
            finally:
                del active_tasks[client_id]