import tkinter as tk
from tkinter import ttk, messagebox
import time
from main import Apc, start_monitor

class SquadToolGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Squad载具创建工具")
        self.root.geometry("400x300")
        
        # 设置窗口样式
        self.style = ttk.Style()
        self.style.configure('TButton', padding=5)
        self.style.configure('TLabel', padding=5)
        
        self.observer = None
        self.event_handler = None
        self.is_monitoring = False
        
        self.create_widgets()
        
    def create_widgets(self):
        # 创建载具选择框
        vehicle_frame = ttk.LabelFrame(self.root, text="载具选择", padding=10)
        vehicle_frame.pack(fill='x', padx=10, pady=5)
        
        self.vehicle_var = tk.StringVar()
        vehicle_combo = ttk.Combobox(vehicle_frame, 
                                   textvariable=self.vehicle_var,
                                   state='readonly',
                                   width=30)
        vehicle_combo['values'] = [f"{name} ({code})" for name, code in Apc.items()]
        vehicle_combo.set("请选择载具")  # 设置默认值
        vehicle_combo.pack(pady=5)
        
        # 创建按钮框
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        
        self.start_button = ttk.Button(button_frame, 
                                     text="启动监控",
                                     command=self.start_monitoring)
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = ttk.Button(button_frame,
                                    text="停止监控",
                                    command=self.stop_monitoring,
                                    state='disabled')
        self.stop_button.pack(side='left', padx=5)
        
        # 创建日志显示区域
        log_frame = ttk.LabelFrame(self.root, text="运行日志", padding=10)
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.log_text = tk.Text(log_frame, height=10, wrap='word')
        self.log_text.pack(fill='both', expand=True)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
    def log_message(self, message):
        """添加日志消息到显示区域"""
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        self.log_text.insert('end', f'[{current_time}] {message}\n')
        self.log_text.see('end')  # 滚动到最新消息
        
    def start_monitoring(self):
        if not self.vehicle_var.get() or self.vehicle_var.get() == "请选择载具":
            messagebox.showerror("错误", "请先选择载具！")
            return
            
        # 清除之前的日志
        self.log_text.delete(1.0, tk.END)
            
        # 从选择的字符串中提取载具代码
        vehicle_code = self.vehicle_var.get().split('(')[1].strip(')')
        
        try:
            self.observer, self.event_handler = start_monitor(vehicle_code)
            self.is_monitoring = True
            
            # 更新按钮状态
            self.start_button.configure(state='disabled')
            self.stop_button.configure(state='normal')
            
            self.log_message(f"已选择载具: {self.vehicle_var.get()}")
            self.log_message("监控已启动")
            
            # 启动检查任务完成状态的定时器
            self.check_task_completion()
            
        except Exception as e:
            messagebox.showerror("错误", f"启动监控时出错：{str(e)}")
            
    def stop_monitoring(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.is_monitoring = False
            
            # 更新按钮状态
            self.start_button.configure(state='normal')
            self.stop_button.configure(state='disabled')
            
            self.log_message("监控已停止")
            
    def check_task_completion(self):
        """定期检查任务是否完成"""
        if self.is_monitoring and self.event_handler:
            if self.event_handler.task_completed:
                self.log_message("任务完成")
                self.stop_monitoring()
            else:
                # 每500毫秒检查一次
                self.root.after(500, self.check_task_completion)
                
    def run(self):
        """运行GUI程序"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        """窗口关闭时的处理"""
        if self.is_monitoring:
            if messagebox.askokcancel("确认", "监控正在运行，确定要退出吗？"):
                self.stop_monitoring()
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == "__main__":
    app = SquadToolGUI()
    app.run() 