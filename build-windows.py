"""
连连看游戏打包脚本
用于打包客户端和服务端程序，包含所需的资源文件
"""
import os
import subprocess
import shutil
import platform

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
    
    # 虚拟环境中的PyInstaller路径
    if platform.system() == 'Windows':
        pyinstaller_path = os.path.join(project_root, '.venv', 'Scripts', 'pyinstaller')
    else:
        pyinstaller_path = os.path.join(project_root, '.venv', 'bin', 'pyinstaller')
    
    # 客户端打包命令 - 添加--onefile参数，移除config文件夹
    client_cmd = f'"{pyinstaller_path}" --onefile --noconfirm --name="LLK_Client" ' \
                 f'--add-data "assets{os.pathsep}assets" ' \
                 f'--icon="assets/LLK.ico" ' \
                 f'--windowed ' \
                 f'--hidden-import="pygame" ' \
                 f'--hidden-import="websockets" ' \
                 f'--hidden-import="asyncio" ' \
                 f'"src/client.py"'
    
    # 服务端打包命令 - 添加--onefile参数，移除config文件夹
    server_cmd = f'"{pyinstaller_path}" --onefile --noconfirm --name="LLK_Server" ' \
                 f'--icon="assets/LLK.ico" ' \
                 f'--console ' \
                 f'--hidden-import="websockets" ' \
                 f'--hidden-import="asyncio" ' \
                 f'"src/server/server.py"'
    
    # 在Windows系统下，需要使用引号包裹路径
    if platform.system() == 'Windows':
        client_cmd = client_cmd.replace('/', '\\')
        server_cmd = server_cmd.replace('/', '\\')
    
    # 首先安装pyinstaller（如果尚未安装）
    print("正在检查和安装PyInstaller...")
    run_command(f'"{os.path.join(project_root, ".venv", "Scripts", "pip")}" install pyinstaller')
    
    # 打包客户端
    print("\n开始打包客户端...")
    result_client = run_command(client_cmd)
    if result_client == 0:
        print("客户端打包成功！")
    else:
        print(f"客户端打包失败，错误码: {result_client}")
    
    # 打包服务端
    print("\n开始打包服务端...")
    result_server = run_command(server_cmd)
    if result_server == 0:
        print("服务端打包成功！")
    else:
        print(f"服务端打包失败，错误码: {result_server}")
    
    if result_client == 0 and result_server == 0:
        print("\n所有程序打包成功！")
        print(f"可执行文件位于: {os.path.join(project_root, 'dist')}")

if __name__ == "__main__":
    main()