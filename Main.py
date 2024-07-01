import sys
import os
import time
import logging
import ctypes
import cv2
from configparser import ConfigParser
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap, QImage
from Ui_Main import Ui_MainWindow
from MyThreaing import AiDealThreading
import PLCSyn
import StsServer
import FilesClean
import threading

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")


class MyApp(QMainWindow, Ui_MainWindow):

    def __init__(self):
        # 设置界面
        super().__init__()
        self.setupUi(self)

        self.img = None
        self.ori_img = None
        #标识符
        self.is_out = False #全局输出信号
        self.is_in = False #全局输入信号
        self.last_update_time = time.time()  # 上次数据更新时间
        self.fps = 0  # fps记录
        self.image_fresh_time = 0  # 图像刷新时间
        
        self.stack_last_time = 0
        self.last_output_type = False
        self.last_output_time = time.time()
        self.last_exist_person_info = {"min_distance": 500}
        
        # 获取预设参数
        res = self.init_params()
        if res == False:
            print("预设参数初始化失败")
            return

        # 设置modbus模块
        self.modbus_controller = PLCSyn.ModbusTcpClientClass(
            self.io_module_ip, self.io_module_port)
        self.modbus_controller.infoSignal.connect(self.recall_plc_syn)
        self.modbus_controller.start()
        # 设置图像Ai分析线程
        self.ai_deal_thread = AiDealThreading(
            self.camera_ip, self.camera_port, self.camera_user_name, self.camera_password, self.module_path
        )
        self.ai_deal_thread.set_ori(self.ori_pt1_list, self.ori_pt2_list)
        self.ai_deal_thread.imgSignal.connect(self.recall_show_img)
        self.ai_deal_thread.infoSignal.connect(self.recall_show_info)
        self.ai_deal_thread.finishSignal.connect(self.recall_ai_sts_info)
        # 设置tcpserver模块
        self.tcp_server = StsServer.SpeTcpServer()
        self.tcp_server.start()
        # 设置看门狗线程
        self.watch_dog = FilesClean.StdDog()
        self.watch_dog.param_set(self.img_save_folder_path, 10000)
        self.watch_dog.infoSignal.connect(self.recall_files_full_checking)
        self.watch_dog.start()
        # 连接ui按钮信号
        self.connect_ui_signal()
        # 初始化log模块设置
        self.init_log()
        #自启动设置
        if self.ai_deal_thread.get_is_run() == False:
            self.ai_deal_thread.start()
            #self.showMaximized()
            self.tabWidget.setCurrentIndex(1)
            

    # 日志模块初始化
    def init_log(self):

        logger = logging.getLogger(__name__)
        logger.setLevel(level=logging.INFO)
        handler = logging.FileHandler("log.txt")
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        self.logger = logger

    # 参数设置初始化
    def init_params(self):
        try:
            # 获取预设参数
            conf = ConfigParser()
            res = conf.read(os.path.dirname(os.path.abspath(__file__)) +r'\config.ini', encoding='utf-8')
            # 相机通讯参数
            self.camera_ip = conf["camera_info"]["ip"]
            self.camera_port = int(conf["camera_info"]["port"])
            self.camera_user_name = conf["camera_info"]["user_name"]
            self.camera_password = conf["camera_info"]["password"]
            # 通用参数
            self.img_save_folder_path = conf["common_info"]["img_save_folder_path"]
            # 模型文件地址
            self.module_path = conf["module_info"]["path"]
            # io模块通讯参数
            self.io_module_ip = conf["io_module_info"]["ip"]
            self.io_module_port = int(conf["io_module_info"]["port"])
            self.io_module_timeout = float(conf["io_module_info"]["timeout"])

            #ori设置
            self.ori_pt1 = conf["ori_info"]["pt1"]
            self.ori_pt2 = conf["ori_info"]["pt2"]
            self.ori_pt1_list = [float(self.ori_pt1.split(',')[0]),float(self.ori_pt1.split(',')[1])]
            self.ori_pt2_list = [float(self.ori_pt2.split(',')[0]),float(self.ori_pt2.split(',')[1])]

            #ui界面设置
            self.lineEdit.setText(str(self.camera_ip))
            self.lineEdit_2.setText(str(self.camera_port))
            self.lineEdit_3.setText(str(self.camera_user_name))
            self.lineEdit_4.setText(str(self.camera_password))

            self.lineEdit_5.setText(str(self.io_module_ip))
            self.lineEdit_6.setText(str(self.io_module_port))
            self.lineEdit_7.setText(str(self.io_module_timeout))

            self.lineEdit_8.setText(str(self.module_path))
            self.lineEdit_9.setText(str(self.img_save_folder_path))

            self.doubleSpinBox_4.setValue(self.ori_pt1_list[0])
            self.doubleSpinBox_5.setValue(self.ori_pt1_list[1])
            self.doubleSpinBox_2.setValue(self.ori_pt2_list[0])
            self.doubleSpinBox_3.setValue(self.ori_pt2_list[1])

            return True
        except Exception as e:
            print(e)
            return False

    # ui按键信号连接
    def connect_ui_signal(self):
        self.pushButton.clicked.connect(self.start_img_thread)  # 设置图像显示线程
        self.pushButton_2.clicked.connect(self.quit_img_thread)  # 退出图像显示线程

    # 启动取图线程
    def start_img_thread(self):
        if self.ai_deal_thread.get_is_run() == False:
            self.ai_deal_thread.start()

    # 退出取图线程
    def quit_img_thread(self):
        self.ai_deal_thread.quit_thread()

    # 文件检测
    def recall_files_full_checking(self, res):
        print(res, "文件数量过多，自动清理部分旧文件")

    # PLC输入口状态同步
    def recall_plc_syn(self, infos:dict):
        # IO模块状态检测
        if infos["plc_sts"]:
            self.tcp_server.io_sts = 0
            self.label_5.setStyleSheet("color: white; background-color: Green ")
            self.is_in = infos["holding_register"][0] #记录全局状态
        else:
            self.tcp_server.io_sts = 7
            self.label_5.setStyleSheet("color: white; background-color: Red ")
            self.is_in = False #记录全局状态

    # 图像回调
    def recall_show_img(self, pixs):
        self.image_fresh_time = time.time()
        self.tcp_server.img_info = pixs #将图像同步至服务器
        if pixs[0] is not None:
            self.img = pixs[0]
            #cv2.Mat转QPixmap
            img = cv2.cvtColor(pixs[0], cv2.COLOR_BGR2RGB)
            height, width, depth = img.shape
            img = QImage(
                img.data, width, height, width * depth, QImage.Format.Format_RGB888
        )
            ratio = 0.5  # 图片尺寸变换比例
            img = img.scaled(int(img.width() * ratio), int(img.height() * ratio))
            self.label.setPixmap(QPixmap(img))
            self.label.setScaledContents(True)
        if pixs[1] is not None:
            self.ori_img = pixs[1]

    # 判定信息回调
    def recall_show_info(self, infos: dict):
        #通用设置
        current_time = time.time() # 当前时间记录
        # 帧率显示
        el_time = current_time - self.last_update_time
        if el_time:
            fps = 1 / el_time
        else:
            fps = 0
        self.label_2.setText("{:.1f}".format(fps))
        self.last_update_time = current_time


        # 堆叠判定
        is_stack = False
        is_handle_check = False
        if infos["is_stack"]:
            self.stack_last_time = time.time()
            self.label_3.setText("是")
            self.label_3.setStyleSheet("color: white; background-color: Red ")
            is_stack = True
        else:
            self.label_3.setText("否")
            self.label_3.setStyleSheet("color: white; background-color: Green ")
            is_stack = False

        # 人工检板判定
        if infos["is_handle_check"]:
            self.handle_check_last_time = time.time()
            is_handle_check = True
            self.label_6.setText("是")
            self.label_6.setStyleSheet("color: white; background-color: Red ")
        else:
            is_handle_check = False
            self.label_6.setText("否")
            self.label_6.setStyleSheet("color: white; background-color: Green ")

        # 调试信息输出
        self.statusbar.showMessage(
            "测试信息 板宽：{:.1f}px  板高：{:.1f}px  人工检板：{}  堆叠判定：{}".format(
                infos["board_width"],
                infos["board_height"],
                infos["is_handle_check"],
                infos["is_stack"],
            )
        )

        #信号输出
        if is_stack or (current_time - self.stack_last_time < 5):
            is_out = True
            self.label_7.setText("是")
            self.label_7.setStyleSheet("color: white; background-color: Red ")
        else:
            is_out = False
            self.label_7.setText("否")
            self.label_7.setStyleSheet("color: white; background-color: Green ")
            
        # 输出信号变化或者是距离上次更新信号的时间过去了1s 向plc下达一次指令并保存图像
        if (is_out != self.last_output_type) or (current_time - self.last_output_time) > 1:
            self.last_output_time = current_time
            # 存在信号判定输出
            task = threading.Thread(target=self.modbus_controller.write_holding_register,args=(5, is_out+10,))
            task.start()

        # 输出信号变化日志记录 只有信号变化时记录日志
        if is_out != self.last_output_type:
            self.last_output_type = is_out
            self.logger.info("is_out " + str(is_out))

            file_name_attach = "change_"+str(is_stack)+"_"
            self.img_save(self.img, self.ori_img, self.img_save_folder_path, file_name_attach)

    # ai分析线程状态信息回调
    def recall_ai_sts_info(self, ai_sts_info: tuple):
        if ai_sts_info[0] == 1 or ai_sts_info[0] == 2:
            self.tcp_server.camera_sts = 0
            self.label_4.setStyleSheet("color: white; background-color: Green ")
        else:
            self.tcp_server.camera_sts = 7
            self.label_4.setStyleSheet("color: white; background-color: Red ")

    #图像记录
    def img_save(self, img, ori_img, folder_path:str, file_name_attach:str = ""):
        full_path = folder_path + "\\" + file_name_attach + str(int(time.time()*1000))+".jpg"
        ori_full_path = folder_path + "\\" + file_name_attach + str(int(time.time()*1000))+"_ori.jpg"
        #保存图像
        if img is not None:
            cv2.imwrite(full_path, img)
            cv2.imwrite(ori_full_path, ori_img)

    #软件退出清理
    def closeEvent(self, event):
        """
        重写closeEvent方法，实现dialog窗体关闭时执行一些代码
        :param event: close()触发的事件
        :return: None
        """
        self.quit_img_thread()#退出取图线程
        event.accept()
        
def main():
    app = QApplication(sys.argv)
    myapp = MyApp()
    myapp.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()


"""
config.ini content

[camera_info]
ip = 10.70.37.10
port = 8000
user_name = admin
password = 13860368866xzc

[io_module_info]
ip = 192.168.31.65
port = 502
timeout = 0.1

[module_info]
path = D:\Code\Python\HumanDetection_yolov8\best_s.pt
"""
