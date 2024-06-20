import time
import os
import socket
from PyQt5.QtCore import QThread, pyqtSignal

#看门狗模块主要功能是定期检测主线程连接状态和检测历史记录文件夹的大小
class StdDog(QThread):
    infoSignal = pyqtSignal(dict)
    last_clean_time = 0

    def __init__(self, file_path:str=None, parent = None) -> None:
        super().__init__(parent)
        self.folder_path = ""
        self.max_num = 20000
        self.is_quit = False

    def param_set(self, folder_path:str, max_num:int):
        self.folder_path = folder_path
        self.max_num = max_num

    def quit_thread(self):
        self.is_quit = True

    #每秒让主线程自检测
    def run(self) -> None:
        # 循环读取主函数
        while self.is_quit == False:
            #心跳信号
            infos = {"heartbeat":0}
            self.infoSignal.emit(infos)
            #文件数量检测
            if time.time()-self.last_clean_time>3600:
                self.file_clean(self.folder_path, self.max_num)
                self.last_clean_time = time.time()
            time.sleep(1)
        self.is_quit = False

    # 文件清理
    def file_clean(self, folder_path:str="",  max_num:int = 20000) -> None:
        if os.path.isdir(folder_path):
            files = os.listdir(folder_path)
            files_num = len(files)
            extra_num = files_num-max_num
            if extra_num > 0:
                for file in files:
                    os.remove(folder_path + "\\" + file)
                    extra_num -= 1
                    if extra_num < 0:
                        break


if __name__ == "__main__":
    myDemo = StdDog()
    myDemo.file_clean(r"C:\Users\01477483\Desktop\新建文件夹", 80)
    