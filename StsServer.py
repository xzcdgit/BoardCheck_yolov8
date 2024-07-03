import time
import os
import socket
from PyQt5.QtCore import QThread
import numpy as np
import threading
import cv2


class SpeTcpServer(QThread):
    camera_sts = 0
    io_sts = 0
    img_info = None

    def __init__(self, server_ip:str="", server_port:int=8234, parent=None) -> None:
        super().__init__(parent)
        self.is_quit = False

        # 创建tcp服务端套接字
        # 参数同客户端配置一致，这里不再重复
        self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        # 设置端口号复用，让程序退出端口号立即释放，否则的话在30秒-2分钟之内这个端口是不会被释放的，这是TCP的为了保证传输可靠性的机制。
        self.tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    
        # 给客户端绑定端口号，客户端需要知道服务器的端口号才能进行建立连接。IP地址不用设置，默认就为本机的IP地址。
        self.tcp_server.bind((server_ip, server_port))
        # listen后的这个套接字只负责接收客户端连接请求，不能收发消息，收发消息使用返回的这个新套接字tcp_client来完成
        self.tcp_server.listen(4)
        print("tcp service 启动成功")

    def quit_thread(self):
        self.is_quit = True
        
    def dispose_client_request(self, tcp_client_1,tcp_client_address):
        # 5 循环接收和发送数据
        while True:
            try:
                recv_data = tcp_client_1.recv(1024)
                # 6 有消息就回复数据，消息长度为0就是说明客户端下线了
                if recv_data:
                    print("客户端是:", tcp_client_address)
                    recv_trans = recv_data.decode()
                    print("客户端发来的消息是:", recv_trans)
                    if recv_trans == "状态":
                        send_data=f"相机状态:{self.camera_sts} io模块状态:{self.io_sts}\n".encode()
                    elif recv_trans == "识别图像":
                        if self.img_info is not None:
                            _, img_encode = cv2.imencode('.jpg', self.img_info[0])
                            img_data = img_encode.tobytes()
                        else:
                            img_data = 'None'.encode()
                        send_data=img_data
                    elif recv_trans == "原始图像":
                        if self.img_info is not None:
                            _, img_encode = cv2.imencode('.jpg', self.img_info[1])
                            img_data = img_encode.tobytes()
                        else:
                            img_data = 'None'.encode()
                        send_data=img_data
                    else:
                        send_data="不支持的命令\n".encode()
                    tcp_client_1.send(send_data)
                else:
                    print("%s 客户端下线了..." % tcp_client_address[1])
                    tcp_client_1.close()
                    break
            except Exception as e:
                print(e, '发生异常，连接断开')
                break

    #每秒让主线程自检测
    def run(self) -> None:
        # 循环读取主函数
        while self.is_quit == False:
            tcp_client_1, tcp_client_address = self.tcp_server.accept()
            thd = threading.Thread(target = self.dispose_client_request, args=(tcp_client_1, tcp_client_address,))
            thd.setDaemon(True)
            thd.start()
        self.tcp_server.close()
        self.is_quit = False

if __name__ == "__main__":
    myDemo = SpeTcpServer()
    task = threading.Thread(target=myDemo.run)
    task.setDaemon(True)
    task.start()
    time.sleep(10000)
    