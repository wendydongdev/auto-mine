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

# 定义操作模式
class OperationMode(Enum):
    MINING = "挖矿"
    FISHING = "钓鱼"
    PICKING = "拾取"  # 新增拾取模式

# 全局变量
running = False
lock = threading.Lock()
move_range = 200
interval_time = 3
current_mode = OperationMode.MINING

def calculate_coordinates():
    # 获取游戏窗口尺寸
    try:
        game_window = gw.getWindowsWithTitle('AntYecai')[0]
        window_rect = game_window.box
        client_width = window_rect.width
        client_height = window_rect.height
    except:
        # 如果找不到窗口，使用屏幕尺寸
        client_width, client_height = pyautogui.size()

    # 计算缩放比例（相对于1600x900）
    scale_x = client_width / 1600
    scale_y = client_height / 900

    # 使用较小的缩放比例以确保坐标在窗口内
    k = min(scale_x, scale_y)
    
    # 计算窗口中心位置
    center_x = client_width / 2
    x0 = center_x - k * 800  # 800是相对于1600分辨率的中心偏移

    coordinates = {
        "mining": {
            "mining_area": {
                "x1": center_x + k * (-100),  # 调整采矿区域相对于中心的位置
                "y1": client_height * 0.44,   # 相对高度
                "x2": center_x + k * 100,
                "y2": client_height * 0.5
            }
        },
        "fishing": {
            "fish_pos": {
                "x": center_x + k * 48,  # 相对于中心的偏移
                "y": client_height * 0.83
            },
            "button_pos": {
                "x": center_x - k * 495,  # 相对于中心的偏移
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
    return coordinates

def check_color_in_region(x1, y1, x2, y2, target_color, tolerance=30):
    """检查指定区域是否存在目标颜色"""
    region = (int(x1), int(y1), int(x2), int(y2))
    screenshot = ImageGrab.grab(bbox=region)
    img_np = np.array(screenshot)
    
    # 转换目标颜色格式
    target_rgb = np.array([
        int(target_color[5:7], 16),  # R
        int(target_color[3:5], 16),  # G
        int(target_color[1:3], 16)   # B
    ])
    
    # 检查区域内是否存在目标颜色
    color_diff = np.abs(img_np - target_rgb)
    match_pixels = np.all(color_diff < tolerance, axis=2)
    return np.any(match_pixels)

def automate_mining():
    global running, move_range, interval_time
    coords = calculate_coordinates()["mining"]
    
    try:
        target_window = gw.getWindowsWithTitle('AntYecai')[0]
        print("找到目标窗口:", target_window)
        
        while True:
            with lock:
                if not running:
                    break

            try:
                target_window.activate()
                
                # 计算随机采矿点，使用move_range来控制范围
                mining_area = coords["mining_area"]
                center_x = (mining_area["x1"] + mining_area["x2"]) / 2
                center_y = (mining_area["y1"] + mining_area["y2"]) / 2
                
                # 根据move_range计算实际范围
                actual_range = move_range * 0.5  # 将0-1000的范围转换为更合适的值
                random_x = center_x + random.uniform(-actual_range, actual_range)
                random_y = center_y + random.uniform(-actual_range, actual_range)
                
                # 确保坐标不超出采矿区域
                random_x = max(mining_area["x1"], min(mining_area["x2"], random_x))
                random_y = max(mining_area["y1"], min(mining_area["y2"], random_y))
                
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
                
                # 使用设置的间隔时间
                time.sleep(interval_time)
                
            except Exception as e:
                print("自动化过程出错:", e)
                break
                
    except Exception as e:
        print("错误: 未找到目标窗口")
        return

def automate_fishing():
    global running
    coords = calculate_coordinates()["fishing"]
    
    try:
        target_window = gw.getWindowsWithTitle('AntYecai')[0]
        target_window.activate()
        
        # 初始化钓鱼
        print("开始钓鱼...")
        # 点击钓鱼按钮开始
        pyautogui.moveTo(coords["button_pos"]["x"], coords["button_pos"]["y"])
        pyautogui.click()
        time.sleep(1)  # 等待钓鱼动画
        
        while True:
            with lock:
                if not running:
                    break
            
            try:
                # 检查上方判定条
                bar_up = coords["bar_up"]
                if check_color_in_region(
                    bar_up["x1"], bar_up["y1"],
                    bar_up["x2"], bar_up["y2"],
                    "#2AEFF0",  # 上方判定条颜色
                    tolerance=50
                ):
                    n = 1
                    while check_color_in_region(
                        bar_up["x1"], bar_up["y1"],
                        bar_up["x2"], bar_up["y2"],
                        "#2AEFF0",
                        tolerance=50
                    ) and n <= 50:
                        n += 1
                        pyautogui.keyDown('down')
                        time.sleep(0.2)
                        pyautogui.keyUp('down')
                
                # 检查下方判定条
                bar_down = coords["bar_down"]
                if not check_color_in_region(
                    bar_down["x1"], bar_down["y1"],
                    bar_down["x2"], bar_down["y2"],
                    "#FF7718",  # 下方判定条颜色
                    tolerance=50
                ):
                    n = 1
                    while not check_color_in_region(
                        bar_down["x1"], bar_down["y1"],
                        bar_down["x2"], bar_down["y2"],
                        "#FF7718",
                        tolerance=50
                    ) and n <= 50:
                        n += 1
                        pyautogui.keyDown('up')
                        time.sleep(0.2)
                        pyautogui.keyUp('up')
                
                time.sleep(0.05)  # 短暂延迟
                
            except Exception as e:
                print("钓鱼过程出错:", e)
                break
                
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
    try:
        game_window = gw.getWindowsWithTitle('AntYecai')[0]
        window_rect = game_window.box
        left, top, width, height = window_rect
        right = left + width
        bottom = top + height
        
        screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        
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
            if not running:  # 检查是否需要停止
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
                    # 计算物品中心点
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
            if not running:  # 再次检查是否需要停止
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
    
    # 使用实际的道具模板
    item_templates = {
        "栗子": "templates/chesnut.png",
        "露水": "templates/dew.png",
        "草莓": "templates/strawberry.png"
    }
    
    # 记录已尝试过的位置
    tried_positions = set()
    
    try:
        target_window = gw.getWindowsWithTitle('AntYecai')[0]
        print("\n=== 开始拾取模式 ===")
        print(f"已加载模板: {list(item_templates.keys())}")
        
        while True:
            with lock:
                if not running:
                    print("拾取模式停止")
                    break
                    
            try:
                try:
                    target_window.activate()
                except Exception as e:
                    pass
                    
                print("\n--- 开始新一轮扫描 ---")
                found_items = False
                
                for item_name, template_path in item_templates.items():
                    if not running:
                        break
                        
                    print(f"\n正在扫描{item_name}...")
                    item_positions, is_confident = find_items_in_screen(
                        template_path, 
                        threshold=0.75,  # 高可信度阈值
                        try_threshold=0.5  # 尝试点击阈值
                    )
                    
                    if item_positions:
                        found_items = True
                        for pos in item_positions:
                            if not running:
                                break
                                
                            # 检查是否已经尝试过这个位置
                            pos_key = (int(pos[0]/30), int(pos[1]/30))  # 将坐标转换为网格位置
                            if pos_key in tried_positions:
                                print(f"位置 {pos} 已尝试过，跳过")
                                continue
                                
                            try:
                                original_pos = pyautogui.position()
                                confidence = "高" if is_confident else "低"
                                print(f"尝试拾取{item_name} ({confidence}可信度), 移动到位置: {pos}")
                                
                                pyautogui.moveTo(pos[0], pos[1])
                                time.sleep(0.2)
                                pyautogui.click()
                                time.sleep(0.2)
                                print(f"已点击位置: {pos}")
                                
                                pyautogui.moveTo(original_pos)
                                
                                # 记录已尝试的位置
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
                    
                # 定期清理较旧的尝试记录（每100次扫描）
                if len(tried_positions) > 1000:
                    tried_positions.clear()
                    print("清理历史尝试记录")
                
            except Exception as e:
                print(f"拾取过程出错: {e}")
                time.sleep(1)
                continue
                
    except Exception as e:
        print(f"拾取自动化出错: {e}")
        return

def start_script():
    global running
    with lock:
        if running:
            messagebox.showwarning("警告", "脚本已经在运行！")
            return
        running = True

    if current_mode == OperationMode.MINING:
        threading.Thread(target=automate_mining).start()
    elif current_mode == OperationMode.FISHING:
        threading.Thread(target=automate_fishing).start()
    else:
        threading.Thread(target=automate_picking).start()
    print(f"开始{current_mode.value}模式")

def stop_script():
    global running
    with lock:
        running = False
    print("脚本已停止")

def toggle_script(event=None):
    global running
    with lock:
        if running:
            stop_script()
        else:
            start_script()
    # 如果是通过F6触发，需要更新GUI状态
    if event and hasattr(event, 'widget'):
        event.widget.update_status_display()

def show_instructions():
    messagebox.showinfo("说明", "1. 挖矿模式：打开矿山地图后运行即可\n"
                              "2. 钓鱼模式：请先到水库地图钓鱼区域，再运行脚本\n"
                              "按F6可以开始/停止脚本。")

def create_gui():
    global move_range, interval_time, current_mode

    def change_mode(event):
        global current_mode
        selected = mode_combo.get()
        if selected == "挖矿":
            current_mode = OperationMode.MINING
        elif selected == "钓鱼":
            current_mode = OperationMode.FISHING
        else:
            current_mode = OperationMode.PICKING
        print(f"切换到{current_mode.value}模式")
        update_status_display()

    def update_status_display():
        if running:
            status_label.config(text="● 运行中", fg="green")
            toggle_button.config(text="停止")
        else:
            status_label.config(text="● 已停止", fg="red")
            toggle_button.config(text="开始")

    def toggle_with_update():
        global running
        if running:
            stop_script()
        else:
            start_script()
        update_status_display()

    def on_closing():
        global running
        if running:
            stop_script()
        window.quit()
        window.destroy()

    def on_escape(event):
        global running
        running = False  # 直接修改全局变量
        stop_script()
        update_status_display()
        print("ESC键被按下，强制停止所有脚本")

    window = tk.Tk()
    window.title("麦门辅助脚本")
    window.geometry("300x250")  # 减小窗口高度

    # 状态显示框架
    status_frame = tk.Frame(window)
    status_frame.pack(pady=5)

    # 状态指示器
    status_label = tk.Label(status_frame, text="● 已停止", fg="red", font=("Arial", 12, "bold"))
    status_label.pack(side=tk.LEFT, padx=5)

    # 添加模式选择下拉框
    tk.Label(window, text="选择模式:").pack(pady=5)
    mode_combo = ttk.Combobox(window, values=["挖矿", "钓鱼", "拾取"], state="readonly")
    mode_combo.set("挖矿")
    mode_combo.bind('<<ComboboxSelected>>', change_mode)
    mode_combo.pack(pady=5)

    # 创建单个开始/停止按钮
    toggle_button = tk.Button(window, text="开始", command=toggle_with_update, width=20)
    toggle_button.pack(pady=10)

    # 创建说明框架
    info_frame = tk.LabelFrame(window, text="使用说明", padx=5, pady=5)
    info_frame.pack(fill="x", padx=10, pady=5)

    # 添加说明文本
    info_text = (
        "1. 挖矿：打开矿山地图后运行\n"
        "2. 钓鱼：打开水库地图钓鱼区域，再运行\n"
        "3. 拾取：自动拾取地图上的道具\n"
        "快捷键：F6 开始/停止"
    )
    tk.Label(info_frame, text=info_text, justify=tk.LEFT, font=("Arial", 9)).pack()

    # 绑定关闭窗口事件
    window.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 将update_status_display方法添加到window对象
    window.update_status_display = update_status_display
    
    # 绑定快捷键
    window.bind('<Escape>', on_escape)
    window.bind('<F6>', toggle_script)
    
    window.mainloop()

if __name__ == "__main__":
    print("启动GUI...")
    create_gui()