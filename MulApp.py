import sys
from multiprocessing import Process,Queue
import time
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
import cv2
import Main
from Ui_MulApp import Ui_MainWindow


# 该模块主要用于定期刷新ui界面

class MulUiAutoFresh(QThread):
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


class MyApp(QMainWindow, Ui_MainWindow):

    def __init__(self):
        # 设置界面
        super().__init__()
        self.setupUi(self)
        #实时图像设置
        self.img = None
        self.ori_img = None
        self.p_num = 2
        self.p_list = []
        self.img_que = [Queue(maxsize=3) for i in range(self.p_num)]
        self.info_que = [Queue(maxsize=3) for i in range(self.p_num)]
        for i in range(self.p_num):
            self.p_list.append(Process(target=Main.main, args=(i,self.img_que[i],self.info_que[i],)))
            self.p_list[i].start()
        
        self.mul_ui_auto_fresh = MulUiAutoFresh()
        self.mul_ui_auto_fresh.infoSignal.connect(self.recall_ui_auto_fresh)
        self.mul_ui_auto_fresh.start()
        
    def recall_ui_auto_fresh(self, info):
        i = self.comboBox_channel_pick.currentIndex()
        if not self.img_que[i].empty():
            img = self.img_que[i].get()
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            height, width, depth = img.shape
            img = QImage(
                img.data, width, height, width * depth, QImage.Format.Format_RGB888
            )
            ratio = 0.5  # 图片尺寸变换比例 显示图片用
            img = img.scaled(int(img.width() * ratio), int(img.height() * ratio))
            self.label_single_img_show.setPixmap(QPixmap(img))
            self.label_single_img_show.setScaledContents(True)
        if not self.info_que[i].empty():
            info = self.info_que[i].get()
            #print(info)
            if info[0] == 0:
                self.label_camera_sts.setStyleSheet(
                "color: white; background-color: Green "
                )
            else:
                self.label_camera_sts.setStyleSheet(
                "color: white; background-color: Red "
                )
            if info[1] == 0:
                self.label_io_sts.setStyleSheet(
                "color: white; background-color: Green "
                )
            else:
                self.label_io_sts.setStyleSheet(
                "color: white; background-color: Red "
                )
            self.label_fps.setText("FPS:{:.1f}".format(info[2]))
            
            # 图像信息显示
            if info[3]:
                self.label_body_num.setStyleSheet("color: white; background-color: Red ")
            else:
                self.label_body_num.setStyleSheet("color: white; background-color: Green ")
                
            if info[5]:
                self.label_arclight_num.setStyleSheet(
                    "color: white; background-color: Red "
                )
            else:
                self.label_arclight_num.setStyleSheet(
                    "color: white; background-color: Green "
                )
                
            self.label_body_num.setText(
                "人体:{}".format(info[4])
            )
            self.label_arclight_num.setText(
                "弧光:{}".format(info[6])
            )
                
            # 同步ui plc输入状态
            if info[7]:
                self.label_input_sts.setStyleSheet("color: white; background-color: Red ")
            else:
                self.label_input_sts.setStyleSheet("color: white; background-color: Green ")
            # 同步ui plc输出信号
            if info[8]:
                self.label_output_sts.setStyleSheet("color: white; background-color: Red ")
            else:
                self.label_output_sts.setStyleSheet(
                    "color: white; background-color: Green "
                )
                
        
                
        
    # 软件退出清理
    def closeEvent(self, event):
        """
        重写closeEvent方法，实现dialog窗体关闭时执行一些代码
        :param event: close()触发的事件
        :return: None
        """
        for p in self.p_list:
            p.kill()
            print('关闭进程', p)
        event.accept()
        




def main():
    app = QApplication(sys.argv)
    myapp = MyApp()
    myapp.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()