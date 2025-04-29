import json
import os
import sys

# 获取资源文件路径的函数 - 仍然保留此函数用于其他资源文件
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

# 获取用户配置目录
def get_config_dir():
    """
    获取配置文件目录，在工作目录下创建llk-config文件夹
    
    Returns:
        str: 配置文件目录的绝对路径
    """
    # 获取程序的当前工作目录
    if getattr(sys, 'frozen', False):
        # 如果是打包后的环境，使用可执行文件所在目录
        work_dir = os.path.dirname(sys.executable)
    else:
        # 开发环境使用项目根目录
        work_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 创建llk-config目录
    config_dir = os.path.join(work_dir, 'llk-config')
    os.makedirs(config_dir, exist_ok=True)
    return config_dir

# 配置文件路径
CONFIG_FILE = os.path.join(get_config_dir(), 'game_config.json')

# 默认配置
DEFAULT_CONFIG = {
    "rows": 10,
    "columns": 10,
    "username": "player",  # 默认用户名
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
                config = json.load(f)
                print(f"已加载配置文件: {CONFIG_FILE}")
                return config
        else:
            # 如果文件不存在，创建默认配置
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=4)
            print(f"创建默认配置文件: {CONFIG_FILE}")
            return DEFAULT_CONFIG
    except Exception as e:
        print(f"加载配置文件时出错: {e}")
        return DEFAULT_CONFIG

def update_config(key, value):
    """
    更新任意配置项
    """
    try:
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
        print(f"配置文件位置: {CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"更新配置时出错: {e}")
        return False