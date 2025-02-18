import threading
from tkinter import messagebox
from operations.mining import MiningOperation
from operations.fishing import FishingOperation
from operations.picking import PickingOperation

class ScriptController:
    def __init__(self):
        self.mining_op = MiningOperation(self)
        self.fishing_op = FishingOperation(self)
        self.picking_op = PickingOperation(self)
        self.current_thread = None
        self.running = False
        self.current_mode = "挖矿"  # 默认模式
        self.lock = threading.Lock()

    def is_running(self):
        with self.lock:
            return self.running

    def change_mode(self, mode):
        if self.is_running():
            messagebox.showwarning("警告", "请先停止当前操作！")
            return
        self.current_mode = mode
        print(f"切换到{mode}模式")

    def start_script(self):
        # 先检查是否已在运行
        if self.is_running():
            messagebox.showwarning("警告", "脚本已经在运行！")
            return
            
        with self.lock:
            self.running = True
        
        print("开始运行脚本")
        
        # 创建新线程
        if self.current_mode == "挖矿":
            self.current_thread = threading.Thread(target=self.mining_op.start_mining)
        elif self.current_mode == "钓鱼":
            self.current_thread = threading.Thread(target=self.fishing_op.start_fishing)
        elif self.current_mode == "拾取":
            self.current_thread = threading.Thread(target=self.picking_op.start_picking)
            
        self.current_thread.daemon = True  # 设置为守护线程
        self.current_thread.start()
        print(f"开始{self.current_mode}模式")

    def stop_script(self):
        with self.lock:
            self.running = False
        
        # 等待线程结束
        if self.current_thread and self.current_thread.is_alive():
            self.current_thread.join(timeout=1.0)  # 最多等待1秒
        
        print("脚本已停止")

    def toggle_script(self, event=None):
        if self.is_running():
            self.stop_script()
        else:
            self.start_script()
            
        # 如果是通过F6触发，需要更新GUI状态
        if event and hasattr(event, 'widget'):
            event.widget.update_status_display() 