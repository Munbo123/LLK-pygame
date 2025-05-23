# 欢乐连连看游戏

## 项目介绍

本项目是武汉理工大学数据结构与算法实验的最终成果，是一个基于 Pygame 开发的连连看游戏。游戏采用 Python 语言实现，利用数据结构和算法知识，完成了包括图结构、路径搜索算法等核心功能的开发。

### 游戏模式

- **基本模式**：传统的连连看玩法，通过点击相同的水果图标并找到有效连接路径来消除它们
- **休闲模式**：轻松休闲的连连看模式，无时间压力
- **联机模式**：支持多人在线对战，通过网络服务器连接，实现实时竞技

## 技术特点

- 使用 Pygame 开发图形界面
- 基于图结构实现路径搜索算法
- 使用 WebSocket 实现网络通信功能
- 利用矩阵数据结构存储和操作游戏地图

## 联机服务器

作者已在云服务器上部署了一个公开的游戏服务器，您可以直接连接体验多人对战模式，无需自行架设服务器：
- 服务器地址：`ws://114.55.75.39:8765`
- 在游戏的"设置"菜单中，将服务器URL设置为上述地址即可连接

## 启动方法

### 方法一：使用打包好的可执行文件（推荐）

项目已经打包成可执行文件，可以直接运行：

1. 在`dist`文件夹中找到以下文件：

   - `LLK_Client.exe`：游戏客户端
   - `LLK_Server.exe`：游戏服务端（仅需要进行联机模式时启动）

2. 使用方法：
   - 直接双击`LLK_Client.exe`启动游戏客户端
   - 如需联机对战，请先双击`LLK_Server.exe`启动服务端，然后再启动客户端并选择"联机模式"

注意：打包后的程序可以在任何 Windows 系统上运行，无需安装 Python 环境。

### 方法二：从源代码启动

如果你想要从源代码启动游戏，需要按照以下步骤操作：

1. **激活 Python 虚拟环境**：

   ```
   # Windows系统
   .venv\Scripts\activate

   # Linux/Mac系统
   source .venv/bin/activate
   ```

2. **安装依赖**（如果尚未安装）：

   ```
   pip install -r requirements.txt
   ```

3. **启动客户端**：

   ```
   python src/client.py
   ```

4. **启动服务端**（仅联机模式需要）：
   ```
   python src/server/server.py [选项]
   ```

#### 服务端启动选项

服务端程序支持以下启动选项：

- `--port PORT`：设置服务器监听的端口号，默认为 8765
- `--host HOST`：设置服务器监听的 IP 地址，默认为"localhost"（本地）
- `--element_len`:设置生成的元素的种类，要求小于客户端的数量，否则客户端会报错,默认为10

示例：

```
# 在9000端口启动服务端
python src/server/server.py --port 9000
```

## 游戏设置

客户端游戏可以在"设置"界面配置以下选项：

- 行数和列数：调整游戏棋盘大小（在基本模式和休闲模式中）
- 用户名：设置在联机模式中显示的名称
- 服务器地址：设置联机模式连接的服务器地址（格式：ws://IP 地址:端口）

## 开发信息

- 开发语言：Python 3
- 游戏引擎：Pygame
- 网络通信：WebSocket
- 开发时间：2024 年春季学期

## 致谢

感谢武汉理工大学数据结构与算法课程提供的学习机会和支持！
