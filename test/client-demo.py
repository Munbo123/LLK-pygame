import asyncio
import websockets
import json
import sys
import uuid
import time

# 全局变量存储连接状态和UUID
connected = False
client_uuid = None
websocket = None

async def connect_to_server():
    global connected, client_uuid, websocket
    
    if connected:
        print("已经连接到服务器，无需重复连接")
        return
        
    uri = "ws://localhost:8766"
    try:
        websocket = await websockets.connect(uri)
        
        # 等待服务器的连接响应
        response = await websocket.recv()
        data = json.loads(response)
        
        if data["type"] == "connection_response":
            client_uuid = data["uuid"]
            print(f"连接成功! 你的UUID是: {client_uuid}")
            print(f"连接消息: {data['message']}")
            connected = True
        else:
            print("服务器响应格式不正确")
            await websocket.close()
    except Exception as e:
        print(f"连接失败: {e}")

async def send_message():
    global connected, client_uuid, websocket
    
    if not connected or not websocket:
        print("未连接到服务器，请先连接")
        return
        
    content = input("请输入要发送的消息内容: ")
    
    message = {
        "type": "message",
        "uuid": client_uuid,
        "content": content
    }
    
    try:
        await websocket.send(json.dumps(message))
        response = await websocket.recv()
        data = json.loads(response)
        print(f"服务器回复: {data['content']}")
    except Exception as e:
        print(f"发送消息失败: {e}")
        connected = False
        websocket = None

async def disconnect():
    global connected, client_uuid, websocket
    
    if not connected or not websocket:
        print("未连接到服务器")
        return
        
    try:
        message = {
            "type": "disconnect",
            "uuid": client_uuid
        }
        await websocket.send(json.dumps(message))
        await websocket.close()
        print("已断开与服务器的连接")
    except Exception as e:
        print(f"断开连接时出错: {e}")
    finally:
        connected = False
        websocket = None

async def main_menu():
    global connected
    
    while True:
        print("\n===== WebSocket客户端菜单 =====")
        print("1. 连接到服务器")
        print("2. 发送消息")
        print("3. 断开连接")
        print("0. 退出程序")
        
        try:
            choice = int(input("请选择操作: "))
            
            if choice == 1:
                await connect_to_server()
            elif choice == 2:
                await send_message()
            elif choice == 3:
                await disconnect()
            elif choice == 0:
                if connected:
                    print("正在关闭连接...")
                    await disconnect()
                print("程序退出")
                break
            else:
                print("无效的选择，请重新输入")
        except ValueError:
            print("请输入有效的数字")
        except Exception as e:
            print(f"发生错误: {e}")
            
        # 短暂延迟，避免CPU使用率过高
        await asyncio.sleep(0.1)
        
if __name__ == "__main__":
    try:
        asyncio.run(main_menu())
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序发生未捕获的异常: {e}")