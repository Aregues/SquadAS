import os
import time
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pynput.keyboard import Controller, Key


# 载具信息
Apc = {
    "TANK": "TANK",
    "BTR82A": "3030",
    "MTLB": "mtlb",
    "BMP1": "bmp1",
    "BMP2": "bmp2",
    "BMP3": "bmp3",
    "Stryker": "SCK_M2",
    "Stryker_1128": "1128",
    "LAV": "lav",
    "ZBL08": "0808",
    "BMD4M": "4M4M",
    "ZCCRWS": "ZCCRWS",

}

class LogMonitor(FileSystemEventHandler):
    def __init__(self, vehicle_code=None):
        # 自动获取用户名并确定监控日志文件路径
        username = os.getenv('USERNAME') or os.getenv('USER')
        self.log_file = os.path.join('C:', 'Users', username, 'AppData', 'Local', 'SquadGame', 'Saved', 'Logs', 'SquadGame.log')
        self.last_position = self.get_last_position()
        self.keyboard = Controller()
        self.task_completed = False
        self.current_vehicle = vehicle_code or "3030"  # 允许外部设置载具代码

    def set_vehicle(self, vehicle_code):
        """设置当前载具代码"""
        self.current_vehicle = vehicle_code
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 已更新载具代码: {vehicle_code}")

    def get_last_position(self):
        try:
            with open(self.log_file, 'r', encoding='utf-8') as file:
                file.seek(0, os.SEEK_END)  # 定位到文件末尾
                return file.tell()  # 返回文件末尾的位置
        except FileNotFoundError:
            print(f"日志文件 {self.log_file} 不存在，等待新文件创建...")
            return 0

    def on_modified(self, event):
        if event.src_path == self.log_file:
            self.check_log()

    def check_log(self):
        try:
            with open(self.log_file, 'r', encoding='utf-8') as file:
                file.seek(self.last_position)
                for line in file:
                    if "Bringing World /Game/Maps/TransitionMap" in line:
                        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 检测到输入目标行")
                        self.loot()
                    elif "BeginTearingDown for /Game/Maps/TransitionMap" in line:
                        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 检测到回车目标行")
                        self.execute()
                self.last_position = file.tell()
        except FileNotFoundError:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 日志文件 {self.log_file} 不存在，等待新文件创建...")
            self.last_position = 0

    def loot(self):
        time.sleep(0.2)
        self.keyboard.press('j')  # 按下j键
        self.keyboard.release('j')
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 已执行按键 'j'")
        time.sleep(0.5)
        #按下esc键
        self.keyboard.press(Key.esc)
        self.keyboard.release(Key.esc)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 已执行按键 'esc'")
        time.sleep(0.5)
        # 输入命令
        command = f'CreateSquad "{self.current_vehicle}" 1' # 创建小队 载具名称     
        for char in command:
            self.keyboard.press(char)
            self.keyboard.release(char)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 已输入命令: {command}")

    def execute(self):
        self.keyboard.press(Key.enter)
        self.keyboard.release(Key.enter)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 已执行按键 'enter'")
        self.task_completed = True  # 设置完成标志
        
def start_monitor(vehicle_code):
    """启动监控的函数，方便GUI调用"""
    observer = Observer()
    event_handler = LogMonitor(vehicle_code)
    
    log_dir = os.path.dirname(event_handler.log_file)
    observer.schedule(event_handler, path=log_dir, recursive=False)
    observer.start()
    
    # 查找载具名称
    vehicle_name = next((name for name, code in Apc.items() if code == vehicle_code), "未知载具")
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] 已选择载具: {vehicle_name} ({vehicle_code})")
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 日志监控已启动")
    
    return observer, event_handler

if __name__ == "__main__":
    # 命令行界面的载具选择逻辑
    print("\n可用载具列表：")
    for index, (name, code) in enumerate(Apc.items(), 1):
        print(f"{index}. {name} ({code})")
    
    while True:
        try:
            choice = int(input("\n请选择载具编号（1-{}）: ".format(len(Apc))))
            if 1 <= choice <= len(Apc):
                selected_vehicle = list(Apc.values())[choice-1]
                break
            else:
                print("无效的选择，请重新输入")
        except ValueError:
            print("请输入有效的数字")
    
    # 启动监控
    observer, event_handler = start_monitor(selected_vehicle)
    
    try:
        while not event_handler.task_completed:
            pass
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 任务完成，程序退出")
    except KeyboardInterrupt:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 监控已停止")
    finally:
        observer.stop()
        observer.join()

