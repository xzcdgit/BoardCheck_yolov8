import time
import os
import cv2
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPainter
import numpy as np
import SdkGetStreaming
from ultralytics import YOLO


class FrameGetThread(QThread):
    infoSignal = pyqtSignal(dict)

    def __init__(self, camera_ip:str, camera_port:int, camera_user_name:str, camera_password:str, model_path:str, parent=None) -> None:
        super().__init__(parent)
        self.painter = QPainter()
        self.model_path = model_path
        self.is_quit = False

    def quit_thread(self):
        self.is_quit = True
        
    #每秒让主线程自检测
    def run(self) -> None:
        # 循环读取主函数
        while self.is_quit == False:
            infos = {"heartbeat":0}
            self.infoSignal.emit(infos)
            time.sleep(1)
        self.is_quit = False
    