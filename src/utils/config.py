import json
import os
import sys

# 获取资源文件路径的函数
def get_resource_path(relative_path):
    """获取资源文件的绝对路径，适用于开发环境和打包环境
    
    Args:
        relative_path: 相对于应用根目录的路径
        
    Returns:
        str: 资源文件的绝对路径
    """
    if getattr(sys, 'frozen', False):
        # 如果是打包后的环境
        base_path = sys._MEIPASS
    else:
        # 开发环境
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    return os.path.join(base_path, relative_path)

# 配置文件路径
CONFIG_FILE = get_resource_path('config/game_config.json')

# 默认配置
DEFAULT_CONFIG = {
    "rows": 10,
    "columns": 10,
    "username": "player",  # 添加默认用户名
    "server_url": "ws://localhost:8765",  # 默认服务器地址
    # 可以在此添加更多默认配置项
}

def load_config():
    """
    加载游戏配置
    如果配置文件不存在，则创建默认配置文件
    """
    try:
        # 尝试读取配置文件
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 确保config目录存在
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            
            # 如果文件不存在，创建默认配置
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=4)
            return DEFAULT_CONFIG
    except Exception as e:
        print(f"加载配置文件时出错: {e}")
        return DEFAULT_CONFIG

def update_config(key, value):
    """
    更新任意配置项
    """
    try:
        # 确保config目录存在
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        
        # 读取现有配置或使用默认配置
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = DEFAULT_CONFIG
        
        # 更新配置
        config[key] = value
        
        # 写入配置文件
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        
        print(f"配置已更新: {key} = {value}")
        return True
    except Exception as e:
        print(f"更新配置时出错: {e}")
        return False