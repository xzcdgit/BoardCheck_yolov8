class ChannelParam:
    def __init__(self) -> None:
        self.camera = CameraParam()
        self.io = IoParam()
        self.ori = OriParam()
        self.web = WebParam()
        self.tcp = TcpParam()
        
        self.modle_path = None
        self.img_save_path = None
        self.log_save_path = None
        self.predict_device = None

class CameraParam:
    def __init__(self) -> None:
        self.ip = None
        self.port = None
        self.user_name = None
        self.password = None
        
class IoParam:
    def __init__(self) -> None:
        self.ip = None
        self.port = None
        self.timeout = None
        
class OriParam:
    def __init__(self) -> None:
        self.pt1 = None
        self.pt2 = None
        
class WebParam:
    def __init__(self) -> None:
        self.enable = False
        self.ip = None
        self.port = None
        
class TcpParam:
    def __init__(self) -> None:
        self.enable = False
        self.ip = None
        self.port = None

channels = [ChannelParam() for i in range(8)]
#参数1设置
channels[0].modle_path = r'D:\Code\Python\BoardCheck_yolov8\best_n.pt'
channels[0].img_save_path = r'D:\Code\Python\BoardCheck_yolov8\imgs'
channels[0].log_save_path = r'D:\Code\Python\BoardCheck_yolov8\imgs\log1.txt'
channels[0].predict_device = 0

channels[0].camera.ip = '192.168.31.64'
channels[0].camera.port = 8000
channels[0].camera.user_name = 'admin'
channels[0].camera.password = '13860368866xzc'
channels[0].io.ip = '192.168.31.65'
channels[0].io.port = 502
channels[0].io.timeout = 0.1
channels[0].ori.pt1 = [0, 0]
channels[0].ori.pt2 = [1, 1]
channels[0].web.enable = False
channels[0].web.ip = '0.0.0.0'
channels[0].web.port = 8200
channels[0].tcp.enable = False
channels[0].tcp.ip = ''
channels[0].tcp.port = 5000
        