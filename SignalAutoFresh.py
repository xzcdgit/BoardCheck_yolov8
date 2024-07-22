# 该模块主要用于定期刷新ui界面
import time
from PyQt5.QtCore import QThread, pyqtSignal

class UiAutoFresh(QThread):
    infoSignal = pyqtSignal(dict)
    last_clean_time = 0

    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.is_quit = False

    def quit_thread(self):
        self.is_quit = True

    #每x秒发送信号刷新ui
    def run(self) -> None:
        # 循环读取主函数
        while self.is_quit == False:
            self.infoSignal.emit({"jump":0})
            time.sleep(0.05)
        self.is_quit = False



if __name__ == "__main__":
    myDemo = UiAutoFresh()

    