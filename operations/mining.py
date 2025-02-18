import pyautogui
import time
import random
import pygetwindow as gw
from window_manager import WindowManager

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
                    continue
                    
        except Exception as e:
            print("错误: 未找到目标窗口")
        finally:
            print("挖矿线程结束") 