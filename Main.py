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
import WebService
from multiprocessing import process, Queue
import ConfigParams
from SignalAutoFresh import UiAutoFresh

# ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")


class MyApp(QMainWindow, Ui_MainWindow):

    def __init__(self, channel_index=0, img_que=None, info_que=None):
        # 设置界面
        super().__init__()
        self.setupUi(self)
        self.channel_index = channel_index
        self.img_que = img_que
        self.info_que = info_que
        # 实时图像设置
        self.img = None
        self.ori_img = None
        # 标识符设置
        self.is_out = False  # 全局输出信号
        self.is_in = False  # 全局输入信号
        self.img_save_lock = False  # 图像保存锁定
        self.last_update_time = time.time()  # 上次数据更新时间
        self.fps = 0  # fps记录
        self.connect_info = {"camera": 1, "plc": 1}
        self.output_enable = True

        self.is_stack = False
        self.is_handle_check = False
        self.ai_recall_info = None
        self.board_thickness_over_count = 0
        self.board_thickness_error_time = 0
        self.board_thickness = -1
        self.board_width = -1
        self.board_height = -1

        self.record_img_info = {"stamp": 0}  # 上次记录图像的时间
        self.last_is_stack_info = {"stamp": 0}  # 最近一次叠板记录
        self.last_is_handle_check_info = {"stamp": 0}  #

        # 获取预设参数
        res = self.init_params()
        if res == False:
            print("预设参数初始化失败")
            return
        # 设置modbus模块
        self.modbus_controller = PLCSyn.ModbusTcpClientClass(
            self.io_module_ip, self.io_module_port
        )
        self.modbus_controller.infoSignal.connect(self.recall_plc_syn)
        self.modbus_controller.start()
        # 设置图像Ai分析线程
        self.ai_deal_thread = AiDealThreading(
            self.camera_ip,
            self.camera_port,
            self.camera_user_name,
            self.camera_password,
            self.module_path,
            self.predict_device,
        )
        self.ai_deal_thread.set_ori(self.ori_pt1, self.ori_pt2)
        self.ai_deal_thread.imgSignal.connect(self.recall_show_img)
        self.ai_deal_thread.infoSignal.connect(self.recall_show_info)
        self.ai_deal_thread.finishSignal.connect(self.recall_ai_sts_info)
        # 设置文件自动清理线程
        self.file_auto_clean = FilesClean.StdDog()
        self.file_auto_clean.param_set(self.img_save_folder_path, 10000)
        self.file_auto_clean.infoSignal.connect(self.recall_files_full_checking)
        self.file_auto_clean.start()
        # 连接ui按钮信号
        self.connect_ui_signal()
        # 初始化log模块设置
        self.init_log()
        # 设置ui自动刷新线程
        self.ui_auto_fresh = UiAutoFresh()
        self.ui_auto_fresh.infoSignal.connect(self.recall_ui_auto_fresh)
        self.ui_auto_fresh.start()

        # 设置网页端线程
        if self.web_service_enable:
            self.web_service = WebService.main
            self.web_threading = threading.Thread(
                target=self.web_service,
                args=(self.web_service_ip, self.web_service_port),
            )
            self.web_threading.daemon = True
            self.web_threading.start()
        # 设置tcpserver模块
        if self.tcp_server_enable:
            self.tcp_server = StsServer.SpeTcpServer(
                self.tcp_server_ip, self.tcp_server_port
            )
            self.tcp_server.start()

        # 自启动设置
        if self.ai_deal_thread.get_is_run() == False:
            self.ai_deal_thread.start()
            self.tabWidget.setCurrentIndex(1)
            # self.showMaximized()

    # 日志模块初始化
    def init_log(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(level=logging.INFO)
        handler = logging.FileHandler(self.log_save_path)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        self.logger = logger

    # 参数设置初始化
    def init_params(self):
        index = self.channel_index
        try:
            # 相机通讯参数
            self.camera_ip = ConfigParams.channels[index].camera.ip
            self.camera_port = ConfigParams.channels[index].camera.port
            self.camera_user_name = ConfigParams.channels[index].camera.user_name
            self.camera_password = ConfigParams.channels[index].camera.password
            # 通用参数
            self.img_save_folder_path = ConfigParams.channels[index].img_save_path
            # 模型文件地址
            self.module_path = ConfigParams.channels[index].modle_path
            # io模块通讯参数
            self.io_module_ip = ConfigParams.channels[index].io.ip
            self.io_module_port = ConfigParams.channels[index].io.port
            self.io_module_timeout = ConfigParams.channels[index].io.timeout
            # web模块设置
            self.web_service_enable = ConfigParams.channels[index].web.enable
            self.web_service_ip = ConfigParams.channels[index].web.ip
            self.web_service_port = ConfigParams.channels[index].web.port
            # tcp模块设置
            self.tcp_server_enable = ConfigParams.channels[index].tcp.enable
            self.tcp_server_ip = ConfigParams.channels[index].tcp.ip
            self.tcp_server_port = ConfigParams.channels[index].tcp.port
            # ori设置
            self.ori_pt1 = ConfigParams.channels[index].ori.pt1
            self.ori_pt2 = ConfigParams.channels[index].ori.pt2
            # log文件保存地址
            self.log_save_path = ConfigParams.channels[index].log_save_path
            # 调用的计算显卡号
            self.predict_device = ConfigParams.channels[index].predict_device

            # ui界面设置
            self.lineEdit.setText(str(self.camera_ip))
            self.lineEdit_2.setText(str(self.camera_port))
            self.lineEdit_3.setText(str(self.camera_user_name))
            self.lineEdit_4.setText(str(self.camera_password))

            self.lineEdit_5.setText(str(self.io_module_ip))
            self.lineEdit_6.setText(str(self.io_module_port))
            self.lineEdit_7.setText(str(self.io_module_timeout))

            self.lineEdit_8.setText(str(self.module_path))
            self.lineEdit_9.setText(str(self.img_save_folder_path))

            self.doubleSpinBox_4.setValue(self.ori_pt1[0])
            self.doubleSpinBox_5.setValue(self.ori_pt1[1])
            self.doubleSpinBox_2.setValue(self.ori_pt2[0])
            self.doubleSpinBox_3.setValue(self.ori_pt2[1])
            return True
        except Exception as e:
            print(e)
            return False

    # ui按键信号连接
    def connect_ui_signal(self):
        self.pushButton.clicked.connect(self.start_img_thread)  # 设置图像显示线程
        self.pushButton_2.clicked.connect(self.quit_img_thread)  # 退出图像显示线程
        self.pushButton_output_enabled.clicked.connect(lambda: self.set_output(True))
        self.pushButton_output_shield.clicked.connect(lambda: self.set_output(False))
        
    def set_output(self, val):
        self.output_enable = val

    # 启动取图线程
    def start_img_thread(self):
        if self.ai_deal_thread.get_is_run() == False:
            self.ai_deal_thread.start()

    # 退出取图线程
    def quit_img_thread(self):
        self.ai_deal_thread.quit_thread()

    # 文件检测回调
    def recall_files_full_checking(self, res):
        print(res, "文件数量过多，自动清理部分旧文件")

    # ui界面自动刷新回调
    def recall_ui_auto_fresh(self, res):
        # 同步ui plc输入状态
        if self.is_in:
            self.label_input_sts.setStyleSheet("color: white; background-color: Red ")
        else:
            self.label_input_sts.setStyleSheet("color: white; background-color: Green ")
        # 同步ui plc输出信号
        if self.is_out:
            self.label_output_sts.setStyleSheet("color: white; background-color: Red ")
        else:
            self.label_output_sts.setStyleSheet(
                "color: white; background-color: Green "
            )

        # 同步plc modbus tcp服务器连接状态
        if self.connect_info["plc"] == 0:
            self.label_io_sts.setStyleSheet("color: white; background-color: Green ")
        else:
            self.label_io_sts.setStyleSheet("color: white; background-color: Red ")
        # 同步相机连接状态
        if self.connect_info["camera"] == 0:
            self.label_camera_sts.setStyleSheet(
                "color: white; background-color: Green "
            )
        else:
            self.label_camera_sts.setStyleSheet("color: white; background-color: Red ")

        # 同步fps
        self.label_fps.setText("FPS:{:.1f}".format(self.fps))

        # 同步板材尺寸
        self.label_board_size.setText(
            "板材尺寸：宽度:{:.2f} px  高度:{:.2f} px  厚度:{:.2f} mm".format(
                self.board_width, self.board_height, self.board_thickness
            )
        )

        # 处理图像显示
        # cv2.Mat转QPixmap
        if self.img is not None:
            img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
            height, width, depth = img.shape
            img = QImage(
                img.data, width, height, width * depth, QImage.Format.Format_RGB888
            )
            #ratio = 0.5  # 图片尺寸变换比例 显示图片用
            #img = img.scaled(int(img.width() * ratio), int(img.height() * ratio))
            self.label_img1_show.setPixmap(QPixmap(img))
            self.label_img1_show.setScaledContents(True)

        # 信息传输给父进程
        if self.img_que is not None and self.img is not None:
            if self.img_que.full():
                _ = self.img_que.get()
            self.img_que.put(self.img)
        if self.info_que is not None and self.ai_recall_info is not None:
            if self.info_que.full():
                _ = self.info_que.get()
            self.info_que.put(
                [
                    self.connect_info["camera"],
                    self.connect_info["plc"],
                    self.fps,
                    self.is_stack,
                    self.ai_recall_info["is_stack"],
                    self.is_handle_check,
                    self.ai_recall_info["is_handle_check"],
                    self.is_in,
                    self.is_out,
                ]
            )

        # 图像信息显示
        if self.is_stack:
            self.label_body_num.setStyleSheet("color: white; background-color: Red ")
        else:
            self.label_body_num.setStyleSheet("color: white; background-color: Green ")
        if self.is_handle_check:
            self.label_arclight_num.setStyleSheet(
                "color: white; background-color: Red "
            )
        else:
            self.label_arclight_num.setStyleSheet(
                "color: white; background-color: Green "
            )
        if self.ai_recall_info is not None:
            # ui界面调试信息显示
            self.statusbar.showMessage(
                "测试信息 叠板判定：{} 人检判定：{}  输出信号：{}".format(
                    self.ai_recall_info["is_stack"],
                    self.ai_recall_info["is_handle_check"],
                    self.is_out,
                )
            )
        # web端和tcp service 信息同步
        if self.web_service_enable:
            WebService.text_info = self.ai_recall_info
            WebService.img_info = self.img
        if self.tcp_server_enable:
            self.tcp_server.img_info = [self.img, self.ori_img]
            self.tcp_server.camera_sts = self.connect_info["camera"]
            self.tcp_server.io_sts = self.connect_info["plc"]

    # PLC输入输出口状态同步
    def recall_plc_syn(self, infos: dict):
        self.board_thickness = infos["thickness"]
        #计数
        if self.board_thickness>6.9:
            self.board_thickness_over_count += 1
            if self.board_thickness_over_count>5:
                self.board_thickness_error_time = time.time()
                self.board_thickness_error = True
        elif self.board_thickness<0 and time.time()-self.board_thickness_error_time>3:
            self.board_thickness_error = False
            self.board_thickness_over_count = 0
        #print(self.board_thickness_over_count,self.board_thickness_error_time)
        
        
        # 同步输出信号至plc
        self.modbus_controller.out = self.is_out
        # 同步输入信号至类变量
        self.is_in = infos["holding_register"][0]
        # 同步ui plc连接状态
        if infos["plc_sts"]:
            self.connect_info["plc"] = 0
        else:
            self.connect_info["plc"] = 7

    # ai分析线程 相机状态同步
    def recall_ai_sts_info(self, ai_sts_info: tuple):
        if ai_sts_info[0] == 1 or ai_sts_info[0] == 2:
            self.connect_info["camera"] = 0
        else:
            self.connect_info["camera"] = 7

    # 图像记录
    def img_save(self, img, ori_img, folder_path: str, file_name_attach: str = ""):
        full_path = (
            folder_path
            + "\\"
            + file_name_attach
            + str(int(time.time() * 1000))
            + ".jpg"
        )
        ori_full_path = (
            folder_path
            + "\\"
            + file_name_attach
            + str(int(time.time() * 1000))
            + "_ori.jpg"
        )
        # 保存图像
        if img is not None:
            cv2.imwrite(full_path, img)
            cv2.imwrite(ori_full_path, ori_img)

    # 软件退出清理
    def closeEvent(self, event):
        """
        重写closeEvent方法，实现dialog窗体关闭时执行一些代码
        :param event: close()触发的事件
        :return: None
        """
        self.quit_img_thread()  # 退出取图线程
        event.accept()

    # ai处理图像回调
    def recall_show_img(self, pixs):
        current_time = time.time()  # 当前时间记录
        # 图像帧率计算
        el_time = current_time - self.last_update_time
        self.last_update_time = current_time
        if el_time:
            fps = 1 / el_time
        else:
            fps = 0
        self.fps = fps  # 同步fps至类变量
        self.img = pixs[0]
        self.ori_img = pixs[1]

    # ai处理判定信息回调
    def recall_show_info(self, infos: dict):
        current_time = time.time()  # 当前时间记录
        self.ai_recall_info = infos
        self.board_width = infos['board_width']
        self.board_height = infos['board_height']
        # Ai叠板判定
        # 叠板判定判定
        if infos["is_stack"]:
            self.is_stack = True
            self.last_is_stack_info = {
                "stamp": current_time,
            }  # 记录最近一次有人的帧信息
        # 本帧图像未叠板并且距离最近出现叠板的时间超过了x秒
        elif current_time - self.last_is_stack_info["stamp"] > 5:
            self.is_stack = False

        # 人检存在判定
        if infos["is_handle_check"]:
            self.is_handle_check = True
            self.last_is_handle_check_info = {
                "stamp": current_time
            }  # 记录最近一次有人检的帧信息
        elif current_time - self.last_is_handle_check_info["stamp"] > 5:
            self.is_handle_check = False
            
        # 输出信号
        if self.output_enable:
            if self.board_thickness_error and self.is_stack:
                self.is_out = True
            else:
                self.is_out = False
        else:
            self.is_out = False
        
        #测试用信息    
        if self.board_thickness_error or self.is_stack: print(self.board_thickness, self.board_thickness_error, self.is_stack, self.is_out)

        # 异常图像记录
        if (self.board_thickness_error or self.is_stack) and current_time-self.record_img_info['stamp']>5:  # 输入为True并且图像保存锁定为False
        #    self.img_save_lock = True
            file_name_attach = "in_out:{}_stack:{}_thickness:{}".format(str(self.is_out), str(self.is_stack), str(int(self.board_thickness*10)))
            self.img_save(
                self.img, self.ori_img, self.img_save_folder_path, file_name_attach
            )
            self.record_img_info = {
                "stamp": current_time,
            }
        #elif self.is_out == False:
        #    self.img_save_lock = False


def main(channel_index=0, img_que=None, info_que=None):
    app = QApplication(sys.argv)
    myapp = MyApp(channel_index, img_que, info_que)
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
