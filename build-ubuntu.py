"""
连连看游戏打包脚本 - Ubuntu服务端专用版本
用于生成可在Ubuntu服务器上运行的服务端程序
"""
import os
import subprocess
import sys
import platform

def run_command(command):
    """运行命令行命令并打印输出"""
    print(f"执行命令: {command}")
    # 修改执行方式，明确使用bash作为shell
    process = subprocess.Popen(
        command, 
        shell=True, 
        executable='/bin/bash',  # 指定使用bash
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
    
    # 检查当前平台
    if platform.system() != "Linux":
        print("警告: 此脚本应在Ubuntu系统上运行以生成适用于Ubuntu的可执行文件!")
        print("在非Linux系统上继续操作可能会导致生成的文件在Ubuntu上无法正常运行。")
        response = input("是否继续？(y/n): ")
        if response.lower() != 'y':
            print("操作已取消")
            return

    # 确保虚拟环境存在
    venv_path = os.path.join(project_root, '.venv')
    if not os.path.exists(venv_path):
        print("创建虚拟环境...")
        run_command(f"python3 -m venv {venv_path}")
    
    # 激活虚拟环境并安装依赖
    # 使用点命令(.)替代source，两者都是bash内置命令，但点命令兼容性更好
    activate_cmd = f". {os.path.join(venv_path, 'bin', 'activate')}" if platform.system() != "Windows" else f"{os.path.join(venv_path, 'Scripts', 'activate')}"
    print("安装依赖...")
    run_command(f"{activate_cmd} && pip install -r requirements.txt && pip install pyinstaller")
    
    # 虚拟环境中的PyInstaller路径
    if platform.system() == 'Windows':
        pyinstaller_path = os.path.join(venv_path, 'Scripts', 'pyinstaller')
    else:
        pyinstaller_path = os.path.join(venv_path, 'bin', 'pyinstaller')
    
    # 服务端打包命令 - 为Ubuntu环境打包，移除config文件夹配置
    server_cmd = f'"{pyinstaller_path}" --onefile --noconfirm --name="LLK_Server_Ubuntu" ' \
                 f'--icon="assets/LLK.ico" ' \
                 f'--console ' \
                 f'--hidden-import="websockets" ' \
                 f'--hidden-import="asyncio" ' \
                 f'"src/server/server.py"'
    
    # 在Windows系统下，需要使用引号包裹路径
    if platform.system() == 'Windows':
        server_cmd = server_cmd.replace('/', '\\')
    
    # 打包服务端
    print("\n开始打包Ubuntu服务端...")
    result_server = run_command(f"{activate_cmd} && {server_cmd}")
    if result_server == 0:
        print("Ubuntu服务端打包成功！")
        output_path = os.path.join(project_root, 'dist', 'LLK_Server_Ubuntu')
        print(f"可执行文件位于: {output_path}")
        
        # 添加可执行权限（仅限Linux）
        if platform.system() == "Linux":
            run_command(f"chmod +x {output_path}")
            print(f"已添加可执行权限")
        
        print("\n要在Ubuntu服务器上运行，请按以下步骤操作：")
        print("1. 将生成的 LLK_Server_Ubuntu 文件传输到Ubuntu服务器")
        print("2. 通过SSH登录到服务器，如: ssh 用户名@服务器IP")
        print("3. 添加可执行权限: chmod +x LLK_Server_Ubuntu")
        print("4. 运行服务器程序: ./LLK_Server_Ubuntu [选项]")
        print("\n可用选项:")
        print("  --port PORT      设置服务器端口，默认为8765")
        print("  --host HOST      设置服务器监听地址，默认为0.0.0.0（监听所有网络接口）")
    else:
        print(f"Ubuntu服务端打包失败，错误码: {result_server}")

if __name__ == "__main__":
    main()