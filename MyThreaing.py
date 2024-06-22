import time
import cv2
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage
import numpy as np
import SdkGetStreaming
from ultralytics import YOLO
import threading

class AiDealThreading(QThread):
    finishSignal = pyqtSignal(tuple)
    imgSignal = pyqtSignal(tuple)
    infoSignal = pyqtSignal(dict)

    def __init__(self, camera_ip:str, camera_port:int, camera_user_name:str, camera_password:str, model_path:str, parent=None) -> None:
        super().__init__(parent)
        self.camera_ip = camera_ip
        self.camera_port = camera_port
        self.camera_user_name = camera_user_name
        self.camera_password = camera_password
        self.model_path = model_path
        self.last_nonempty_time = time.time()+10 #加10是因为sdk取图初始化需要时间，而取图超时会判定异常
        self.is_quit = False
        self.is_run = False
        self.sdk_streaming = SdkGetStreaming.GetSdkStreaming(self.camera_ip, self.camera_port, self.camera_user_name, self.camera_password)

    def get_is_run(self):
        return self.is_run

    def quit_thread(self):
        if self.is_run:
            self.is_quit = True

    def run(self) -> None:
        self.is_run = True
        self.is_quit = False
        self.run_sdk()
        self.is_quit = False
        self.is_run = False
        
    def run_sdk(self) -> None:
        error_code = 0
        error_dict = {0:"正常结束",7:"sdk取图超时"}
        # 加载yolov8的神经网络模型
        self.model = YOLO(self.model_path)  # load a pretrained model (recommended for training)
        # 循环运算
        self.sdk_streaming.preview()
        while self.is_quit == False:
            #如果队列中没有图像则直接继续
            if not SdkGetStreaming.GetSdkStreaming.image_que.empty():
                self.last_nonempty_time = time.time()
                img = SdkGetStreaming.GetSdkStreaming.image_que.get()
            elif time.time()-self.last_nonempty_time>3:
                error_code = 7
                break
            else:
                time.sleep(0.1)
                continue
            qimg, infos = self.ai_deal_board(img)
            self.imgSignal.emit((qimg, img))
            self.infoSignal.emit(infos)
            time.sleep(0.05)
        self.is_quit = False
        self.sdk_streaming.stop_get_streaming()
        self.finishSignal.emit((error_code,error_dict[error_code]))
    
    #测试用函数，检测视频
    def run_video(self) -> None:
        # 加载yolov8的神经网络模型
        self.model = YOLO(self.model_path)  # load a pretrained model (recommended for training)
        video_path = r"C:\Users\01477483\Desktop\堆叠检测现场录像\20240611.mp4"
        cap = cv2.VideoCapture(video_path)
        # 循环运算
        while self.is_quit == False:
            ret, frame = cap.read()
            if ret == False:
                cap = cv2.VideoCapture(video_path)
                continue
            else:
                self.img = frame
            img = self.img
            qimg, infos = self.ai_deal_board(img)
            self.imgSignal.emit(qimg)
            self.infoSignal.emit(infos)
            time.sleep(0.02)
        self.is_quit = False

    def ai_deal_board(self, img) -> None:
        is_stack = False
        is_handle_check = False
        board_width = -1
        board_height = -1
        img_width = img.shape[1]
        img_height = img.shape[0]
        check_left = img_width*0.29
        check_right = img_width*0.59
        check_up = img_height*0.083
        results = self.model(img, verbose=False)
        #因为只传入了一张图所以results的长度只有1
        for result in results:
            conf = result.boxes.conf.cpu().numpy() #置信率
            cls = result.boxes.cls.cpu().numpy() #标签号
            xywhs = result.boxes.xywh.cpu().numpy()
            xywhs = xywhs[np.argsort(xywhs[:,0])] #按x整体排序
            box_num = len(xywhs)
            for index,xywh in enumerate(xywhs):
                left = xywh[0] - 0.5*xywh[2]
                up = xywh[1] - 0.5*xywh[3]
                # 双板间距判定
                if left > check_left and left < check_right:
                        if index<box_num-1:
                            #两板中心距离小于两板宽度和的一半(如果第二块板位于图像x轴末端，阈值适当减小)
                            if xywhs[index+1][0] > img_width*0.93:
                                ratio = 0.47
                            else:
                                ratio = 0.5
                            if (abs(xywhs[index+1][0] - xywhs[index][0]) < 0.5*(xywhs[index+1][2] + xywhs[index][2])) and up>check_up:
                                is_stack = True
                #人工检板判定
                if up<check_up:
                    is_handle_check = True
            im_bgr = result.plot()
        # 图像格式转换PIL.IMAGE转cv2图像
        img = np.asanyarray(im_bgr)
        # 图像格式转换 cv2图像转QImage
        cvimg = img
        height, width, depth = cvimg.shape
        cvimg = cv2.cvtColor(cvimg, cv2.COLOR_BGR2RGB)
        cvimg = QImage(
            cvimg.data, width, height, width * depth, QImage.Format.Format_RGB888
        )
        # 回传图像数据和判定结果
        ratio = 0.5  # 图片尺寸变换比例
        qimg = cvimg.scaled(int(cvimg.width() * ratio), int(cvimg.height() * ratio))
        infos = {
            "is_handle_check": is_handle_check,
            "is_stack": is_stack,
            "board_width": board_width,
            "board_height": board_height
        }
        return qimg, infos
    