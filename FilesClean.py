import time
import os
from PyQt5.QtCore import QThread, pyqtSignal

#看门狗模块主要功能是定期检测检测历史记录文件夹的大小
class StdDog(QThread):
    infoSignal = pyqtSignal(dict)
    last_clean_time = 0

    def __init__(self, folder_path:str=None, parent = None) -> None:
        super().__init__(parent)
        self.folder_path = folder_path
        self.max_num = 20000
        self.is_quit = False

    def param_set(self, folder_path:str, max_num:int):
        self.folder_path = folder_path
        self.max_num = max_num

    def quit_thread(self):
        self.is_quit = True

    #每x秒让检查一次文件数量溢出
    def run(self) -> None:
        # 循环读取主函数
        while self.is_quit == False:
            #文件数量检测
            res = self.file_clean(self.folder_path, self.max_num)
            self.infoSignal.emit({"files_num":res})
            time.sleep(3600)
        self.is_quit = False

    # 文件清理
    def file_clean(self, folder_path:str="",  max_num:int = 20000) -> None:
        files_num = -1
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
        return files_num


if __name__ == "__main__":
    myDemo = StdDog()
    myDemo.file_clean(r"D:\Code\Python\HumanDetection_yolov8\imgs", 40000)

    