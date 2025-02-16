import json
import base64
import os

def load_json_template(file_path: str) -> dict:
    """
    加载JSON模板文件
    Args:
        file_path: JSON文件路径
    Returns:
        解析后的JSON字典
    Raises:
        FileNotFoundError: 文件不存在时
        json.JSONDecodeError: JSON格式错误时
    """
    try:
        with open(file_path, 'r', encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"模板文件未找到: {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON格式错误: {str(e)}")

def image_to_base64(filename: str) -> str:
    """
    将图像文件转换为base64编码
    Args:
        filename: 图像文件名
    Returns:
        base64编码的字符串
    Raises:
        FileNotFoundError: 图像文件不存在时
    """
    image_path = os.path.join("F:\\ComfyUI_windows_portable\\ComfyUI\\output", filename)
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图像文件未找到: {image_path}")
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        print(f"图像编码错误: {e}")
        return None