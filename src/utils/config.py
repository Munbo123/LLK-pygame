import json
import os

# 配置文件路径
CONFIG_FILE = './config/game_config.json'

# 默认配置
DEFAULT_CONFIG = {
    "rows": 10,
    "columns": 10,
    "username": "player",  # 添加默认用户名
    # 可以在此添加更多默认配置项
}

def load_config():
    """
    加载游戏配置
    如果配置文件不存在，则创建默认配置文件
    """
    try:
        # 确保config目录存在
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        
        # 尝试读取配置文件
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 如果文件不存在，创建默认配置
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=4)
            return DEFAULT_CONFIG
    except Exception as e:
        print(f"加载配置文件时出错: {e}")
        return DEFAULT_CONFIG

def update_game_size(rows, columns):
    """
    更新游戏的行数和列数
    """
    config = load_config()
    config["rows"] = rows
    config["columns"] = columns
    
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"保存配置文件时出错: {e}")
        return False

def update_config(key, value):
    """
    更新任意配置项
    """
    config = load_config()
    config[key] = value
    
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"保存配置文件时出错: {e}")
        return False