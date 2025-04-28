"""
连连看游戏服务端Linux打包脚本
用于在Ubuntu等Linux系统上打包服务端程序
"""
import os
import subprocess
import sys

def run_command(command):
    """运行命令行命令并打印输出"""
    print(f"执行命令: {command}")
    process = subprocess.Popen(
        command, 
        shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT, 
        universal_newlines=True
    )
    
    for line in process.stdout:
        print(line.strip())
        
    process.wait()
    return process.returncode

def main():
    # 项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 创建虚拟环境（如果不存在）
    venv_dir = os.path.join(project_root, 'linux_venv')
    if not os.path.exists(venv_dir):
        print("正在创建虚拟环境...")
        run_command(f'python3 -m venv {venv_dir}')
    
    # 虚拟环境中的pip和pyinstaller路径
    pip_path = os.path.join(venv_dir, 'bin', 'pip')
    pyinstaller_path = os.path.join(venv_dir, 'bin', 'pyinstaller')
    
    # 安装依赖
    print("正在安装依赖...")
    run_command(f'{pip_path} install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple')
    
    # 确保安装pyinstaller
    print("正在检查和安装PyInstaller...")
    run_command(f'{pip_path} install pyinstaller')
    
    # 服务端打包命令 - 使用--onefile参数生成单个文件
    server_cmd = f'{pyinstaller_path} --onefile --noconfirm --name="LLK_Server" ' \
                f'--add-data "config:config" ' \
                f'--console ' \
                f'"src/server/server.py"'
    
    # 打包服务端
    print("\n开始打包服务端...")
    result = run_command(server_cmd)
    if result == 0:
        print("服务端打包成功！")
        print(f"可执行文件位于: {os.path.join(project_root, 'dist', 'LLK_Server')}")
    else:
        print(f"服务端打包失败，错误码: {result}")

if __name__ == "__main__":
    main()