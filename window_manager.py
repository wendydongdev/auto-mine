import pygetwindow as gw
import pyautogui
import numpy as np
from PIL import ImageGrab

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