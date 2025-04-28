import asyncio
import websockets
import uuid
import json

# 存储所有活跃连接
active_connections = {}

async def handle_client(websocket):
    # 为新连接生成UUID
    client_id = str(uuid.uuid4())
    active_connections[client_id] = websocket
    
    try:
        # 发送连接成功消息和UUID给客户端
        connection_response = {
            "type": "connection_response",
            "uuid": client_id,
            "message": "连接成功"
        }
        await websocket.send(json.dumps(connection_response))
        print(f"新客户端连接: {client_id}")
        
        # 处理客户端消息
        async for message in websocket:
            try:
                data = json.loads(message)
                
                # 验证消息格式
                if "type" not in data:
                    continue
                    
                if data["type"] == "message" and "uuid" in data and "content" in data:
                    client_uuid = data["uuid"]
                    content = data["content"]
                    
                    print(f"{client_uuid}: {content}")
                    
                    # 回复客户端
                    response = {
                        "type": "message_response",
                        "content": f"服务器已收到: {content}"
                    }
                    await websocket.send(json.dumps(response))
                    
                elif data["type"] == "disconnect" and "uuid" in data:
                    client_uuid = data["uuid"]
                    print(f"{client_uuid} 断开连接")
                    break
                    
            except json.JSONDecodeError:
                print(f"收到非JSON格式消息: {message}")
                
    except websockets.exceptions.ConnectionClosed:
        print("连接异常关闭")
    finally:
        # 清理断开的连接
        if client_id in active_connections:
            del active_connections[client_id]
            print(f"客户端 {client_id} 已从活跃连接列表中移除")

async def main():
    # 启动websocket服务器，使用8766端口
    async with websockets.serve(handle_client, "localhost", 8766):
        print("WebSocket服务器已启动，监听端口8766...")
        # 保持服务器运行
        await asyncio.Future()  # 运行至被取消

# 启动异步事件循环
if __name__ == "__main__":
    asyncio.run(main())