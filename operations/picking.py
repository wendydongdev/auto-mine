import pyautogui
import time
import cv2
import numpy as np
from PIL import ImageGrab
import pygetwindow as gw
from window_manager import WindowManager

class PickingOperation:
    def __init__(self, controller):
        self.controller = controller
        self.item_templates = {
            "栗子": "templates/chesnut.png",
            "露水": "templates/dew.png",
            "草莓": "templates/strawberry.png"
        }
        self.tried_positions = set()
        
    def rotate_image(self, image, angle):
        """旋转图片"""
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, rotation_matrix, (width, height), flags=cv2.INTER_LINEAR)
        return rotated

    def find_items_in_screen(self, template_path, threshold=0.75, try_threshold=0.65, angles=[0, 90, 180, 270]):
        """在屏幕中寻找匹配的道具，支持多角度匹配"""
        print(f"\n开始识别模板: {template_path}")
        start_time = time.time()
        
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
                # 检查是否需要停止或超时
                if time.time() - start_time > 10:  # 10秒超时
                    print("识别超时")
                    return [], False
                    
                rotated_template = self.rotate_image(template, angle)
                result = cv2.matchTemplate(screenshot, rotated_template, cv2.TM_CCOEFF_NORMED)
                max_val = np.max(result)
                
                print(f"角度 {angle}° 的最大匹配值: {max_val:.4f}" + 
                      (" (尝试点击)" if max_val >= try_threshold else "") +
                      (" (高可信度)" if max_val >= threshold else ""))
                
                if max_val >= try_threshold:
                    locations = np.where(result >= try_threshold)
                    for pt in zip(*locations[::-1]):
                        center_x = left + pt[0] + template_width//2
                        center_y = top + pt[1] + template_height//2
                        all_points.append((center_x, center_y, angle, max_val))
                    
                    if max_val > best_max_val:
                        best_max_val = max_val
                        best_angle = angle
            
            # 按匹配度排序并去重
            all_points.sort(key=lambda x: x[3], reverse=True)
            final_points = []
            used_positions = set()
            
            for x, y, angle, val in all_points:
                too_close = False
                for used_x, used_y in used_positions:
                    if abs(x - used_x) < 30 and abs(y - used_y) < 30:
                        too_close = True
                        break
                
                if not too_close:
                    final_points.append((x, y))
                    used_positions.add((x, y))
            
            return final_points, best_max_val >= threshold
            
        except Exception as e:
            print(f"识别过程出错: {e}")
            return [], False

    def start_picking(self):
        print("\n=== 开始拾取模式 ===")
        print(f"已加载模板: {list(self.item_templates.keys())}")
        last_scan_time = time.time()
        
        try:
            target_window = gw.getWindowsWithTitle('AntYecai')[0]
            
            while True:
                if not self.controller.is_running():
                    break
                try:
                    # 检查扫描间隔
                    current_time = time.time()
                    if current_time - last_scan_time < 1:  # 至少等待1秒
                        time.sleep(0.1)
                        continue
                    
                    last_scan_time = current_time
                    target_window.activate()
                    
                    print("\n--- 开始新一轮扫描 ---")
                    found_items = False
                    
                    for item_name, template_path in self.item_templates.items():
                        print(f"\n正在扫描{item_name}...")
                        item_positions, is_confident = self.find_items_in_screen(
                            template_path, 
                            threshold=0.75,
                            try_threshold=0.65
                        )
                        
                        if item_positions:
                            found_items = True
                            for pos in item_positions:
                                pos_key = (int(pos[0]/30), int(pos[1]/30))
                                if pos_key in self.tried_positions:
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
                                    self.tried_positions.add(pos_key)
                                    
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
                    if len(self.tried_positions) > 1000:
                        self.tried_positions.clear()
                        print("清理历史尝试记录")
                    
                except Exception as e:
                    print(f"拾取过程出错: {e}")
                    time.sleep(1)
                    
        except Exception as e:
            print(f"拾取自动化出错: {e}")
        finally:
            print("拾取线程结束") 