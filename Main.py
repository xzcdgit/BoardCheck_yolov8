import sys
import os
from configparser import ConfigParser
import time
import cv2
import logging
import ctypes
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap
from Ui_Main import Ui_MainWindow
from MyThreaing import AiDealThreading
import Modbus
import StsServer
import WatchDog

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")


class MyApp(QMainWindow, Ui_MainWindow):

    def __init__(self):
        # 设置界面
        super().__init__()
        self.setupUi(self)  
        # 获取预设参数
        conf = ConfigParser()
        res = conf.read(os.path.dirname(os.path.abspath(__file__)) +r'\config.ini', encoding='utf-8')
        self.img = None
        self.ori_img = None
        # 相机通讯参数
        camera_ip = conf['camera_info']['ip']
        camera_port = int(conf['camera_info']['port'])
        camera_user_name = conf['camera_info']['user_name']
        camera_password = conf['camera_info']['password']
        ## 通用参数
        img_save_folder_path = conf['common_info']['img_save_folder_path']
        module_path = conf['module_info']['path']
        io_module_ip = conf['io_module_info']['ip']
        io_module_port = int(conf['io_module_info']['port'])
        io_module_timeout = float(conf['io_module_info']['timeout'])
        self.img_save_folder_path = img_save_folder_path
        self.is_run = False #分析运行信号 防止重复运行ai分析线程
        self.last_update_time = 0  # 上次数据更新时间
        self.fps = 0  # fps记录
        self.image_fresh_time = 0  # 图像刷新时间

        ## 特殊设定部分
        self.stack_last_time = 0  # 最近一次出现叠板的时间
        self.handle_check_last_time = 0  # 最近一次出现人工检测的时间
        self.last_output_type = False
        self.last_output_time = 0

        # 设置modbus模块
        self.modbus_controller = Modbus.ModbusTcpClientClass(io_module_ip, io_module_port, io_module_timeout)

        # 设置图像Ai分析线程
        self.ai_deal_thread = AiDealThreading(camera_ip, camera_port, camera_user_name, camera_password, module_path)
        self.ai_deal_thread.imgSignal.connect(self.recall_show_img) 
        self.ai_deal_thread.infoSignal.connect(self.recall_show_info)
        self.ai_deal_thread.finishSignal.connect(self.recall_quit_info)
        # 设置tcpserver模块
        self.tcp_server = StsServer.SpeTcpServer()
        self.tcp_server.start()
        # 设置看门狗线程
        self.watch_dog = WatchDog.StdDog()
        self.watch_dog.param_set(self.img_save_folder_path, 10)
        self.watch_dog.infoSignal.connect(self.recall_self_checking)
        self.watch_dog.start()

        # 连接ui信号
        self.connect_ui_signal()
        #log文件参数设置
        self.init_log()

        #自启动设置
        if self.is_run == False:
            self.ai_deal_thread.start()
            self.is_run = True
            self.showMaximized()


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

    def connect_ui_signal(self):
        self.pushButton.clicked.connect(self.start_img_thread)  # 设置图像显示线程
        self.pushButton_2.clicked.connect(self.quit_img_thread)  # 退出图像显示线程

    # 启动取图线程
    def start_img_thread(self):
        if self.is_run == False:
            self.ai_deal_thread.start()
            self.is_run = True

    def quit_img_thread(self):
        self.ai_deal_thread.quit_thread()
        self.is_run = False

    # 状态自检测并同步至tcp服务器
    def recall_self_checking(self, requestion):

        # 相机状态检测
        if time.time() - self.image_fresh_time > 2:
            self.tcp_server.camera_sts = 7
            self.label_4.setStyleSheet("color: white; background-color: Red ")
        else:
            self.tcp_server.camera_sts = 0
            self.label_4.setStyleSheet("color: white; background-color: Green ")

        # IO模块状态检测
        res = self.modbus_controller.write_holding_register(0, 1)
        if res:
            self.tcp_server.io_sts = 0
            self.label_5.setStyleSheet("color: white; background-color: Green ")
        else:
            self.tcp_server.io_sts = 7
            self.label_5.setStyleSheet("color: white; background-color: Red ")

    # 图像回调
    def recall_show_img(self, pixs):
        self.image_fresh_time = time.time()
        if pixs[0] is not None:
            self.label.setPixmap(QPixmap(pixs[0]))
            self.label.setScaledContents(True)
            self.img = pixs[0]
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
            res = self.modbus_controller.write_holding_register(5, is_out+10)
            if not res: print("modbus communication error")

            file_name_attach = "common_"+str(is_stack)+"_"
            self.img_save(self.img, self.ori_img, self.img_save_folder_path, file_name_attach)

        # 输出信号变化日志记录 只有信号变化时记录日志
        if is_out != self.last_output_type:
            self.last_output_type = is_out
            self.logger.info("is_out " + str(is_out))

    # 退出信息回调
    def recall_quit_info(self, quit_info: tuple):
        if quit_info != 0:
            print(quit_info)
        else:
            print(quit_info)

    #图像记录
    def img_save(self, img, ori_img, folder_path:str, file_name_attach:str = "", max_num:int = 50000):
        full_path = folder_path + "\\" + file_name_attach + str(int(time.time()*1000))+".jpg"
        ori_full_path = folder_path + "\\" + file_name_attach + str(int(time.time()*1000))+"_ori.jpg"
        #保存图像
        if img is not None:
            img.save(full_path,"jpg", 100)
            cv2.imwrite(ori_full_path,ori_img)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = MyApp()
    myapp.show()
    sys.exit(app.exec_())


'''
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
'''
