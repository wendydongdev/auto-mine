# 游戏助手

一个简单的游戏辅助工具，支持以下功能：
- 自动挖矿
- 自动钓鱼
- 自动拾取

## 依赖安装

bash
pip install -r requirements.txt


## 使用方法
1. 运行 main.py 启动程序
2. 选择需要的功能模式（挖矿/钓鱼/拾取）
3. 点击开始或按 F6 开始运行
4. 按 ESC 或点击停止来结束运行

## 快捷键
- F6: 开始/停止脚本
- ESC: 停止脚本

## 打包成EXE

1. 安装 PyInstaller：
bash
pip install pyinstaller
2. 打包命令：
bash
单文件模式
pyinstaller --noconsole --onefile --add-data "templates/;templates/" main.py
文件夹模式（运行更快）
pyinstaller --noconsole --add-data "templates/;templates/" main.py
3. 打包后文件位置：
- 单文件模式: `dist/main.exe`
- 文件夹模式: `dist/main/main.exe`

注意：
- 使用 --noconsole 参数隐藏控制台窗口
- 使用 --add-data 参数包含模板图片
- 如需调试可去掉 --noconsole 参数

## 项目结构

project/
├── main.py # 主程序入口
├── script_controller.py # 脚本控制器
├── window_manager.py # 窗口管理
├── operations/ # 具体操作实现
│ ├── init.py
│ ├── mining.py # 挖矿
│ ├── fishing.py # 钓鱼
│ └── picking.py # 拾取
└── templates/ # 图片模板
├── chesnut.png # 栗子模板
├── dew.png # 露水模板
└── strawberry.png # 草莓模板

## 注意事项
1. 确保游戏窗口标题为 "AntYecai"
2. 运行前请确保已安装所有依赖
3. 拾取功能需要对应的模板图片
4. 窗口可以置顶/取消置顶
5. 打包成EXE后请确保templates文件夹在正确位置

## 开发说明
- 使用 Python 3.x
- 基于 OpenCV 实现图像识别
- 使用 tkinter 实现GUI
- 多线程处理自动化操作
- 使用 PyInstaller 打包

## 许可
仅供学习交流使用，请勿用于商业用途。

## 开发计划
- [ ] 支持钓鱼
- [ ] 支持拾取
- [ ] 支持五子棋
- [ ] 支持黑白棋
- [ ] 支持扫雷