import pyautogui
import time
import pygetwindow as gw
from window_manager import WindowManager

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
            print(f"点击位置: ({self.coords['button_pos']['x']}, {self.coords['button_pos']['y']})")
            pyautogui.moveTo(self.coords["button_pos"]["x"], self.coords["button_pos"]["y"])
            pyautogui.click()
            time.sleep(2)
            
            while True:
                if not self.controller.is_running():
                    break
                try:
                    # 检查上方判定条
                    bar_up = self.coords["bar_up"]
                    up_color = WindowManager.check_color_in_region(
                        bar_up["x1"], bar_up["y1"],
                        bar_up["x2"], bar_up["y2"],
                        "#2AEFF0",
                        tolerance=70
                    )
                    print(f"上方判定条状态: {'检测到红色' if up_color else '未检测到红色'}")
                    
                    if up_color:
                        print("开始按下向下键...")
                        n = 1
                        while WindowManager.check_color_in_region(
                            bar_up["x1"], bar_up["y1"],
                            bar_up["x2"], bar_up["y2"],
                            "#2AEFF0",
                            tolerance=70
                        ) and n <= 50:
                            n += 1
                            pyautogui.keyDown('down')
                            time.sleep(0.2)
                            pyautogui.keyUp('down')
                            time.sleep(0.2)
                        print(f"向下按键结束，按下了{n}次")
                    
                    # 检查下方判定条
                    bar_down = self.coords["bar_down"]
                    down_color = WindowManager.check_color_in_region(
                        bar_down["x1"], bar_down["y1"],
                        bar_down["x2"], bar_down["y2"],
                        "#FF7718",
                        tolerance=70
                    )
                    print(f"下方判定条状态: {'检测到橙色' if down_color else '未检测到橙色'}")
                    
                    if not down_color:
                        print("开始按下向上键...")
                        n = 1
                        while not WindowManager.check_color_in_region(
                            bar_down["x1"], bar_down["y1"],
                            bar_down["x2"], bar_down["y2"],
                            "#FF7718",
                            tolerance=70
                        ) and n <= 50:
                            n += 1
                            pyautogui.keyDown('up')
                            time.sleep(0.2)
                            pyautogui.keyUp('up')
                            time.sleep(0.2)
                        print(f"向上按键结束，按下了{n}次")
                    
                    time.sleep(0.05)
                    
                except Exception as e:
                    print("钓鱼过程出错:", e)
                    print(f"错误位置: {e.__traceback__.tb_lineno}")
                    time.sleep(1)
                    continue
                    
        except Exception as e:
            print("钓鱼自动化出错:", e)
        finally:
            print("钓鱼线程结束") 