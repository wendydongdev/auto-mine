import pyautogui
import time
import random
import threading
import tkinter as tk
from tkinter import messagebox

# 全局变量，用于控制脚本的运行状态
running = False
lock = threading.Lock()

def calculate_coordinates():
    """
    根据屏幕分辨率，计算需要点击的坐标。
    """
    # 获取屏幕分辨率
    screen_width, screen_height = pyautogui.size()

    # 窗口比例参数
    k = screen_height / 900  # 高度与 900 的比例，原脚本中定义
    x0 = (screen_width / 2) - k * 800

    return {
        "mine_x": x0 + k * 848,  # 挖矿位置
        "mine_y": 600,  # 居中一点
        "button_x": x0 + k * 305,  # 按钮位置
        "button_y": k * 160,
    }

def automate_mining():
    """
    自动挖矿脚本，模拟右键挖矿和移动。
    """
    global running
    coords = calculate_coordinates()
    move_count = 0

    while True:
        with lock:
            if not running:
                break

        # 挖矿操作
        pyautogui.moveTo(coords["mine_x"], coords["mine_y"])
        pyautogui.click(button='right')  # 右键点击挖矿
        time.sleep(3)  # 等待 3 秒

        # 移动到新位置
        dx = 400 + random.randint(0, 200)
        if move_count % 2 == 0:
            new_x = coords["mine_x"] + dx
        else:
            new_x = coords["mine_x"] - dx
        new_y = 600 + random.randint(-200, 200)
        move_count += 1

        pyautogui.moveTo(new_x, new_y)
        pyautogui.click()

        # 打印调试信息
        print(f"移动到新位置: ({new_x}, {new_y})")



def start_script():
    """
    启动挖矿脚本。
    """
    global running
    with lock:
        if running:
            messagebox.showwarning("警告", "脚本已经在运行！")
            return
        running = True

    threading.Thread(target=automate_mining).start()
    # messagebox.showinfo("启动", "挖矿脚本已启动！")

def stop_script():
    """
    停止挖矿脚本。
    """
    global running
    with lock:
        running = False
    # messagebox.showinfo("停止", "挖矿脚本已停止！")

def toggle_script(event):
    """
    切换脚本的启动和停止状态。
    """
    global running
    with lock:
        if running:
            stop_script()
        else:
            start_script()

# 创建 GUI 界面
def create_gui():
    window = tk.Tk()
    window.title("麦门挖矿辅助脚本")
    window.geometry("300x200")

    # 启动脚本按钮
    start_button = tk.Button(window, text="启动脚本", command=start_script, width=20)
    start_button.pack(pady=20)

    # 停止脚本按钮
    stop_button = tk.Button(window, text="停止脚本", command=stop_script, width=20)
    stop_button.pack(pady=20)

    # 退出程序按钮
    exit_button = tk.Button(window, text="退出程序", command=window.destroy, width=20)
    exit_button.pack(pady=20)

    # 绑定快捷键
    window.bind('<c>', toggle_script)

    window.mainloop()

if __name__ == "__main__":
    create_gui()