import time
import os
import cv2
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPainter
import numpy as np
import SdkGetStreaming
from ultralytics import YOLO
import threading


class AiDealThreading(QThread):
    finishSignal = pyqtSignal(tuple)
    imgSignal = pyqtSignal(tuple)
    infoSignal = pyqtSignal(dict)

    def __init__(self, camera_ip, camera_port, camera_user_name, camera_password, model_path:str) -> None:
        super().__init__(None)
        self.camera_ip = camera_ip
        self.camera_port = camera_port
        self.camera_user_name = camera_user_name
        self.camera_password = camera_password
        self.model_path = model_path
        # 加载yolov8的神经网络模型
        self.model = YOLO(self.model_path)  # load a pretrained model (recommended for training)
        self.last_nonempty_time = time.time()+10 #加10是因为sdk取图初始化需要时间，而取图超时会判定异常
        self.is_run = False
        self.is_quit = False
        #sdk部分
        self.sdk_streaming = SdkGetStreaming.GetSdkStreaming(self.camera_ip, self.camera_port, self.camera_user_name, self.camera_password)
        self.sdk_streaming.btn_login()
        self.sdk_streaming.btn_preview()

        # ori区域设置 xyx1y1
        self.ori = [[0,0],[1,1]]
        self.ori_x = 0.5*(self.ori[0][0]+self.ori[1][0])
        self.ori_y = 0.5*(self.ori[0][1]+self.ori[1][1])
        self.ori_width = self.ori[1][0] - self.ori[0][0]
        self.ori_height = self.ori[1][1] - self.ori[0][1]

    def get_is_run(self):
        return self.is_run

    def set_ori(self,point1:list,point2:list):
        self.ori = [point1,point2]
        self.ori_x = 0.5*(self.ori[0][0]+self.ori[1][0])
        self.ori_y = 0.5*(self.ori[0][1]+self.ori[1][1])
        self.ori_width = self.ori[1][0] - self.ori[0][0]
        self.ori_height = self.ori[1][1] - self.ori[0][1]

    def quit_thread(self):
        st_time = time.time()
        if self.is_run:
            self.is_quit = True
            while True:
                time.sleep(0.2)
                if self.is_run == False or st_time-time.time()>2:
                    print("图像线程退出")
                    break

    def run(self) -> None:
        self.is_run = True
        self.is_quit = False
        self.run_sdk()
        self.is_quit = False
        self.is_run = False
        
    def run_sdk(self) -> None:
        sts_dict = {0:"正常结束", 1:"正常取图", 2:"跳帧", 7:"sdk取图超时"}
        while self.is_quit == False:
            #如果队列中没有图像则直接继续
            if not self.sdk_streaming.image_que.empty():
                self.last_nonempty_time = time.time()
                img = self.sdk_streaming.image_que.get()
                self.finishSignal.emit((1,sts_dict[1]))
            elif time.time()-self.last_nonempty_time>2:
                self.finishSignal.emit((7,sts_dict[7]))
                time.sleep(0.5)
                continue
            else:
                self.finishSignal.emit((2,sts_dict[2]))
                time.sleep(0.01)
                continue
            qimg, infos = self.ai_deal_board(img)
            self.imgSignal.emit((qimg, img))
            self.infoSignal.emit(infos)
            time.sleep(0.01)
        self.is_quit = False
        self.sdk_streaming.stop_get_streaming()
        self.finishSignal.emit((0,sts_dict[0]))

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
        input_img = img[:,1200:]
        results = self.model(input_img, verbose=False)
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
        # #绘制ori
        height, width, depth = img.shape
        dt1 = (int(self.ori[0][0]*width),int(self.ori[0][1]*height))
        dt2 = (int(self.ori[1][0]*width-3),int(self.ori[1][1]*height-3))
        img = cv2.rectangle(img,dt1,dt2,(0,255,0),3) 

        # 回传图像数据和判定结果
        infos = {
            "is_handle_check": is_handle_check,
            "is_stack": is_stack,
            "board_width": board_width,
            "board_height": board_height
        }
        return img, infos
    
if __name__ == "__main__":
    # 设置图像Ai分析线程
    ai_deal_thread = AiDealThreading('',0,'','',model_path=r"D:\Code\Python\HumanDetection_yolov8\best_s.pt")
    ai_deal_thread.set_ori([0,0.23],[1,1])
    img = cv2.imread(r"D:\Code\Python\HumanDetection_yolov8\imgs\Test_1719471114058_ori.jpg")
    img, infos = ai_deal_thread.ai_deal_body(img)
    img = cv2.resize(img,dsize=None, dst=None,fx=0.5,fy=0.5)
    cv2.imshow("test",img)
    print(infos)
    cv2.waitKey(0)
    