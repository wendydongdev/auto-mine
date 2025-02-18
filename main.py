import pyautogui
import time
import random
import threading
import tkinter as tk
from tkinter import messagebox, ttk
import pygetwindow as gw
from enum import Enum
from PIL import ImageGrab
import numpy as np
import cv2
from time import sleep
from script_controller import ScriptController

# 定义操作模式
class OperationMode(Enum):
    MINING = "挖矿"
    FISHING = "钓鱼"
    PICKING = "拾取"  # 取消注释

class WindowManager:
    @staticmethod
    def calculate_coordinates():
        """计算游戏窗口坐标和各功能区域"""
        try:
            game_window = gw.getWindowsWithTitle('AntYecai')[0]
            window_rect = game_window.box
            client_width = window_rect.width
            client_height = window_rect.height
        except:
            client_width, client_height = pyautogui.size()

        # 计算缩放比例（相对于1600x900）
        scale_x = client_width / 1600
        scale_y = client_height / 900
        k = min(scale_x, scale_y)
        
        # 计算窗口中心位置
        center_x = client_width / 2
        x0 = center_x - k * 800

        return {
            "mining": {
                "mining_area": {
                    "x1": center_x + k * (-100),
                    "y1": client_height * 0.44,
                    "x2": center_x + k * 100,
                    "y2": client_height * 0.5
                }
            },
            "fishing": {
                "fish_pos": {
                    "x": center_x + k * 48,
                    "y": client_height * 0.83
                },
                "button_pos": {
                    "x": center_x - k * 495,
                    "y": client_height * 0.18
                },
                "bar_up": {
                    "x1": center_x + k * 126,
                    "y1": client_height * 0.748,
                    "x2": center_x + k * 130,
                    "y2": client_height * 0.753
                },
                "bar_down": {
                    "x1": center_x + k * 126,
                    "y1": client_height * 0.793,
                    "x2": center_x + k * 130,
                    "y2": client_height * 0.799
                }
            }
        }

    @staticmethod
    def check_color_in_region(x1, y1, x2, y2, target_color, tolerance=30):
        """检查指定区域是否存在目标颜色"""
        region = (int(x1), int(y1), int(x2), int(y2))
        screenshot = ImageGrab.grab(bbox=region)
        img_np = np.array(screenshot)
        
        target_rgb = np.array([
            int(target_color[5:7], 16),
            int(target_color[3:5], 16),
            int(target_color[1:3], 16)
        ])
        
        color_diff = np.abs(img_np - target_rgb)
        match_pixels = np.all(color_diff < tolerance, axis=2)
        return np.any(match_pixels)

class MiningOperation:
    def __init__(self, controller):
        self.controller = controller
        self.coords = None
        
    def start_mining(self):
        self.coords = WindowManager.calculate_coordinates()["mining"]
        
        try:
            target_window = gw.getWindowsWithTitle('AntYecai')[0]
            print("找到目标窗口:", target_window)
            
            while True:
                if not self.controller.is_running():  # 添加运行状态检查
                    break
                try:
                    target_window.activate()
                    
                    # 计算随机采矿点
                    mining_area = self.coords["mining_area"]
                    random_x = random.uniform(mining_area["x1"], mining_area["x2"])
                    random_y = random.uniform(mining_area["y1"], mining_area["y2"])
                    
                    # 保存当前鼠标位置
                    original_pos = pyautogui.position()
                    
                    # 移动到随机位置并点击
                    pyautogui.moveTo(random_x, random_y)
                    time.sleep(0.05)
                    pyautogui.click()
                    
                    # 稍微向下移动并右键点击
                    pyautogui.moveTo(random_x, random_y + 20)
                    pyautogui.click(button='right')
                    time.sleep(0.05)
                    
                    # 恢复鼠标位置
                    pyautogui.moveTo(original_pos)
                    
                    # 等待采矿完成
                    time.sleep(3)  # 默认3秒间隔
                    time.sleep(0.1)  # 添加短暂延迟
                    
                except Exception as e:
                    print("自动化过程出错:", e)
                    time.sleep(1)  # 出错时等待较长时间
                    if not self.controller.is_running():  # 再次检查是否需要退出
                        break
                    continue
                    
        except Exception as e:
            print("错误: 未找到目标窗口")
        finally:
            print("挖矿线程结束")

class FishingOperation:
    def __init__(self, controller):
        self.controller = controller
        self.coords = None
        
    def start_fishing(self):
        self.coords = WindowManager.calculate_coordinates()["fishing"]
        
        try:
            target_window = gw.getWindowsWithTitle('AntYecai')[0]
            target_window.activate()
            
            # 初始化钓鱼
            print("开始钓鱼...")
            pyautogui.moveTo(self.coords["button_pos"]["x"], self.coords["button_pos"]["y"])
            pyautogui.click()
            time.sleep(1)
            
            while True:
                if not self.controller.is_running():  # 添加运行状态检查
                    break
                try:
                    # 检查上方判定条
                    bar_up = self.coords["bar_up"]
                    if WindowManager.check_color_in_region(
                        bar_up["x1"], bar_up["y1"],
                        bar_up["x2"], bar_up["y2"],
                        "#2AEFF0",
                        tolerance=50
                    ):
                        n = 1
                        while WindowManager.check_color_in_region(
                            bar_up["x1"], bar_up["y1"],
                            bar_up["x2"], bar_up["y2"],
                            "#2AEFF0",
                            tolerance=50
                        ) and n <= 50 and self.controller.is_running():
                            n += 1
                            pyautogui.keyDown('down')
                            time.sleep(0.08)
                            pyautogui.keyUp('down')
                            time.sleep(0.1)
                    
                    # 检查下方判定条
                    bar_down = self.coords["bar_down"]
                    if not WindowManager.check_color_in_region(
                        bar_down["x1"], bar_down["y1"],
                        bar_down["x2"], bar_down["y2"],
                        "#FF7718",
                        tolerance=50
                    ):
                        n = 1
                        while not WindowManager.check_color_in_region(
                            bar_down["x1"], bar_down["y1"],
                            bar_down["x2"], bar_down["y2"],
                            "#FF7718",
                            tolerance=50
                        ) and n <= 50 and self.controller.is_running():
                            n += 1
                            pyautogui.keyDown('up')
                            time.sleep(0.08)
                            pyautogui.keyUp('up')
                            time.sleep(0.1)
                    
                    time.sleep(0.05)
                    
                except Exception as e:
                    print("钓鱼过程出错:", e)
                    time.sleep(1)
                    continue
                    
        except Exception as e:
            print("钓鱼自动化出错:", e)
            return

def rotate_image(image, angle):
    """旋转图片"""
    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, rotation_matrix, (width, height), flags=cv2.INTER_LINEAR)
    return rotated

def find_items_in_screen(template_path, threshold=0.75, try_threshold=0.65, angles=[0, 90, 180, 270]):
    """在屏幕中寻找匹配的道具，支持多角度匹配"""
    print(f"\n开始识别模板: {template_path}")
    start_time = time.time()  # 添加超时检查
    try:
        game_window = gw.getWindowsWithTitle('AntYecai')[0]
        window_rect = game_window.box
        left, top, width, height = window_rect
        right = left + width
        bottom = top + height
        
        screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2BGR)
        
        template = cv2.imread(template_path)
        if template is None:
            print(f"错误: 无法读取模板文件 {template_path}")
            return [], False
            
        template_height, template_width = template.shape[:2]
        print(f"模板尺寸: {template.shape}")
        
        all_points = []
        best_angle = None
        best_max_val = -1
        
        for angle in angles:
            # 检查是否需要停止或超时
            if not self.controller.is_running() or time.time() - start_time > 10:  # 10秒超时
                print("识别超时或被终止")
                return [], False
                
            rotated_template = rotate_image(template, angle)
            result = cv2.matchTemplate(screenshot, rotated_template, cv2.TM_CCOEFF_NORMED)
            max_val = np.max(result)
            
            print(f"角度 {angle}° 的最大匹配值: {max_val:.4f}" + 
                  (" (尝试点击)" if max_val >= try_threshold else "") +
                  (" (高可信度)" if max_val >= threshold else ""))
            
            if max_val >= try_threshold:
                locations = np.where(result >= try_threshold)
                for pt in zip(*locations[::-1]):
                    if not self.controller.is_running():  # 再次检查是否需要停止
                        return [], False
                    center_x = left + pt[0] + template_width//2
                    center_y = top + pt[1] + template_height//2
                    all_points.append((center_x, center_y, angle, max_val))
                
                if max_val > best_max_val:
                    best_max_val = max_val
                    best_angle = angle
        
        # 按匹配度排序
        all_points.sort(key=lambda x: x[3], reverse=True)
        final_points = []
        used_positions = set()
        
        for x, y, angle, val in all_points:
            if not self.controller.is_running():  # 再次检查是否需要停止
                return [], False
                
            # 检查是否与已尝试过的位置太近
            too_close = False
            for used_x, used_y in used_positions:
                if abs(x - used_x) < 30 and abs(y - used_y) < 30:
                    too_close = True
                    break
            
            if not too_close:
                final_points.append((x, y))
                used_positions.add((x, y))
        
        if final_points:
            confidence_level = "高" if best_max_val >= threshold else "低"
            print(f"找到 {len(final_points)} 个匹配位置，匹配度: {best_max_val:.4f} ({confidence_level}可信度，将尝试点击)")
            
            # 保存调试图像
            debug_image = screenshot.copy()
            rotated_template = rotate_image(template, best_angle)
            h, w = rotated_template.shape[:2]
            for pt in final_points:
                x, y = pt
                screen_x = int(x - left - w//2)
                screen_y = int(y - top - h//2)
                # 画出中心点和匹配框
                cv2.circle(debug_image, (screen_x + w//2, screen_y + h//2), 2, (0, 0, 255), -1)  # 红色中心点
                color = (0, 255, 0) if best_max_val >= threshold else (0, 255, 255)
                cv2.rectangle(debug_image, (screen_x, screen_y), (screen_x + w, screen_y + h), color, 2)
            cv2.imwrite("debug_match.png", debug_image)
            
        else:
            if best_max_val >= try_threshold:
                print(f"匹配度 {best_max_val:.4f} 超过尝试阈值，但位置已被尝试过")
            else:
                print("未找到足够匹配的位置")
        
        return final_points, best_max_val >= threshold
        
    except Exception as e:
        print(f"截图识别出错: {e}")
        import traceback
        print(traceback.format_exc())
        return [], False

def automate_picking():
    global running
    
    item_templates = {
        "栗子": "templates/chesnut.png",
        "露水": "templates/dew.png",
        "草莓": "templates/strawberry.png"
    }
    
    tried_positions = set()
    last_scan_time = time.time()  # 添加扫描时间检查
    
    try:
        target_window = gw.getWindowsWithTitle('AntYecai')[0]
        print("\n=== 开始拾取模式 ===")
        print(f"已加载模板: {list(item_templates.keys())}")
        
        while running:  # 修改循环条件
            try:
                # 检查扫描间隔
                current_time = time.time()
                if current_time - last_scan_time < 1:  # 至少等待1秒
                    time.sleep(0.1)
                    continue
                
                last_scan_time = current_time
                
                try:
                    target_window.activate()
                except Exception as e:
                    pass
                    
                print("\n--- 开始新一轮扫描 ---")
                found_items = False
                
                for item_name, template_path in item_templates.items():
                    if not running:  # 检查是否需要停止
                        print("拾取模式被终止")
                        return
                        
                    print(f"\n正在扫描{item_name}...")
                    item_positions, is_confident = find_items_in_screen(
                        template_path, 
                        threshold=0.75,
                        try_threshold=0.65
                    )
                    
                    if item_positions:
                        found_items = True
                        for pos in item_positions:
                            if not running:
                                return
                                
                            pos_key = (int(pos[0]/30), int(pos[1]/30))
                            if pos_key in tried_positions:
                                print(f"位置 {pos} 已尝试过，跳过")
                                continue
                                
                            try:
                                original_pos = pyautogui.position()
                                print(f"尝试拾取{item_name}, 移动到位置: {pos}")
                                pyautogui.moveTo(pos[0], pos[1])
                                time.sleep(0.2)
                                pyautogui.click()
                                time.sleep(0.2)
                                pyautogui.moveTo(original_pos)
                                tried_positions.add(pos_key)
                                
                            except Exception as e:
                                print(f"点击过程出错: {e}")
                                continue
                
                if not found_items:
                    print("\n本轮未发现物品，等待5秒后重新扫描...")
                    time.sleep(5)
                else:
                    print("\n本轮完成拾取，短暂等待后继续扫描...")
                    time.sleep(1)
                    
                # 定期清理历史记录
                if len(tried_positions) > 1000:
                    tried_positions.clear()
                    print("清理历史尝试记录")
                
            except Exception as e:
                print(f"拾取过程出错: {e}")
                time.sleep(1)
                
    except Exception as e:
        print(f"拾取自动化出错: {e}")
        return

class GameAssistantGUI:
    def __init__(self):
        self.window = None
        self.status_label = None
        self.toggle_button = None
        self.controller = ScriptController()
        self.create_main_window()

    def create_main_window(self):
        self.window = tk.Tk()
        self.window.title("野菜部落辅助脚本")
        self.window.geometry("300x250")
        self.window.attributes('-topmost', True)

        # 创建状态显示框架
        self.create_status_display()
        
        # 创建模式选择
        self.create_mode_selection()
        
        # 创建控制按钮
        self.create_control_buttons()
        
        # 创建说明信息
        self.create_info_section()
        
        # 绑定事件
        self.bind_events()

    def create_status_display(self):
        status_frame = tk.Frame(self.window)
        status_frame.pack(pady=5)

        self.status_label = tk.Label(
            status_frame, 
            text="● 已停止", 
            fg="red", 
            font=("Arial", 12, "bold")
        )
        self.status_label.pack(side=tk.LEFT, padx=5)

    def create_mode_selection(self):
        tk.Label(self.window, text="选择模式:").pack(pady=5)
        self.mode_combo = ttk.Combobox(
            self.window, 
            values=[mode.value for mode in OperationMode], 
            state="readonly"
        )
        self.mode_combo.set(OperationMode.MINING.value)
        self.mode_combo.bind('<<ComboboxSelected>>', self.handle_mode_change)
        self.mode_combo.pack(pady=5)

    def create_control_buttons(self):
        self.toggle_button = tk.Button(
            self.window, 
            text="开始", 
            command=self.toggle_with_update, 
            width=20
        )
        self.toggle_button.pack(pady=10)

        # 添加置顶切换按钮
        self.topmost_button = tk.Button(
            self.window, 
            text="取消置顶", 
            command=self.toggle_topmost
        )
        self.topmost_button.pack(pady=5)

    def create_info_section(self):
        info_frame = tk.LabelFrame(self.window, text="使用说明", padx=5, pady=5)
        info_frame.pack(fill="x", padx=10, pady=5)

        info_text = (
            "挖矿和钓鱼要打开相应地图后运行\n"
            "快捷键：F6 开始/停止"
        )
        tk.Label(
            info_frame, 
            text=info_text, 
            justify=tk.LEFT, 
            font=("Arial", 9)
        ).pack()

    def bind_events(self):
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.bind('<Escape>', self.on_escape)
        self.window.bind('<F6>', self.controller.toggle_script)
        self.window.update_status_display = self.update_status_display

    def handle_mode_change(self, event):
        selected = self.mode_combo.get()
        self.controller.change_mode(selected)
        self.update_status_display()

    def update_status_display(self):
        if self.controller.is_running():
            self.status_label.config(text="● 运行中", fg="green")
            self.toggle_button.config(text="停止")
        else:
            self.status_label.config(text="● 已停止", fg="red")
            self.toggle_button.config(text="开始")

    def toggle_with_update(self):
        self.controller.toggle_script()
        self.update_status_display()

    def toggle_topmost(self):
        is_topmost = self.window.attributes('-topmost')
        self.window.attributes('-topmost', not is_topmost)
        self.topmost_button.config(
            text="取消置顶" if not is_topmost else "窗口置顶"
        )

    def on_closing(self):
        if self.controller.is_running():
            self.controller.stop_script()
        self.window.quit()
        self.window.destroy()

    def on_escape(self, event):
        self.controller.stop_script()
        self.update_status_display()
        print("ESC键被按下，停止脚本")

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    print("启动GUI...")
    gui = GameAssistantGUI()
    gui.run()