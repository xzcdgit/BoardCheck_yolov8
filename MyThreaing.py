import time
import cv2
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPainter
import numpy as np
import SdkGetStreaming
from ultralytics import YOLO


class FrameGetThread(QThread):
    finishSignal = pyqtSignal(str)
    imgSignal = pyqtSignal(QImage)
    infoSignal = pyqtSignal(dict)

    def __init__(self, camera_ip:str, camera_port:int, camera_user_name:str, camera_password:str, model_path:str, parent=None) -> None:
        super().__init__(parent)
        self.painter = QPainter()
        self.model_path = model_path
        self.img = None
        self.is_quit = False
        
        # sdk取图线程
        SdkGetStreaming.start_thread(camera_ip, camera_port, camera_user_name, camera_password)

    def quit_thread(self):
        self.is_quit = True

    def run(self) -> None:
        self.run_sdk()
        #self.run_video()
        
    def run_sdk(self) -> None:
        # 加载yolov8的神经网络模型
        self.model = YOLO(self.model_path)  # load a pretrained model (recommended for training)
        # 循环运算
        while self.is_quit == False:
            #如果队列中没有图像则直接继续
            if not SdkGetStreaming.data_chane1.empty():
                self.img = SdkGetStreaming.data_chane1.get()
            else:
                time.sleep(0.01)
                continue
            img = self.img[:, 1100:-200]
            qimg, infos = self.ai_deal_Yolov8(img)
            self.imgSignal.emit(qimg)
            self.infoSignal.emit(infos)
            time.sleep(0.02)
        self.is_quit = False
    
    #测试用函数，检测视频
    def run_video(self) -> None:
        # 加载yolov8的神经网络模型
        self.model = YOLO(self.model_path)  # load a pretrained model (recommended for training)
        video_path = r"C:\Users\ADMIN\Desktop\素材\通道人检\10.70.37.10_01_20240530141205550_1.mp4"
        cap = cv2.VideoCapture(video_path)
        # 循环运算
        while self.is_quit == False:
            ret, frame = cap.read()
            if ret == False:
                cap = cv2.VideoCapture(video_path)
                continue
            else:
                self.img = frame
            #如果队列中没有图像则直接继续
            #if not SdkGetStreaming.data_chane1.empty():
            #    self.img = SdkGetStreaming.data_chane1.get()
            #else:
            #    time.sleep(0.01)
            #    continue
            img = self.img
            qimg, infos = self.ai_deal_Yolov8(img)
            self.imgSignal.emit(qimg)
            self.infoSignal.emit(infos)
            time.sleep(0.02)
        self.is_quit = False

    def ai_deal_Yolov8(self, img) -> None:
        #if img is None:
        #    return None, {"person_num": -1, "exist_person": -1}
        count_person = 0
        count_arclights = 0
        trans_distance = 999
        results = self.model(img)
        #因为只传入了一张图所以results的长度只有1
        for result in results:
            conf = result.boxes.conf.cpu().numpy()
            cls = result.boxes.cls.cpu().numpy()
            xywh = result.boxes.xywh.cpu().numpy()
            count_person = np.sum(cls == 0)
            count_arclights = np.sum(cls == 1)
            im_bgr = result.plot()
            # 最近高度中心计算
            center_ys = xywh[:,1]
            # 加权计算，因为图像透视上方的图像距离需要放大
            trans_distances = np.where(center_ys<600, (600-center_ys)*1.8, center_ys-600)
            # 判定距离通道中心最近的识别框
            if len(trans_distances)>0:
                trans_distance = trans_distances.min()
        # 图像格式转换PIL.IMAGE转cv2图像
        img = np.asanyarray(im_bgr)
        # 图像格式转换 cv2图像转QImage
        cvimg = img
        height, width, depth = cvimg.shape
        cvimg = cv2.cvtColor(cvimg, cv2.COLOR_BGR2RGB)
        cvimg = QImage(
            cvimg.data, width, height, width * depth, QImage.Format.Format_RGB888
        )
        # 存在人员标识符
        if count_person > 0:
            exist_person = True
        else:
            exist_person = False
        # 弧光存在标识符
        if count_arclights > 0:
            exist_arclights = True
        else:
            exist_arclights = False
        # 回传图像数据和判定结果
        ratio = 0.5  # 图片尺寸变换比例
        qimg = cvimg.scaled(int(cvimg.width() * ratio), int(cvimg.height() * ratio))
        infos = {
            "person_num": count_person,
            "exist_person": exist_person,
            "arclight_num": count_arclights,
            "exist_arclights": exist_arclights,
            "min_distance": trans_distance,
        }
        return qimg, infos
    