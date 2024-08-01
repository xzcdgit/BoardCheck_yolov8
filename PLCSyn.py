# 该模块用于和PLC通讯，通讯协议为modbus tcp


from pymodbus.client import ModbusTcpClient
from pymodbus.bit_read_message import ReadCoilsResponse
from pymodbus.register_read_message import ReadInputRegistersResponse
from pymodbus.exceptions import ConnectionException      # 连接失败，用于异常处理
from PyQt5.QtCore import QThread, pyqtSignal
import time

class ModbusTcpClientClass(QThread):
    infoSignal = pyqtSignal(dict)
    connect_sts = True
    holding_register_val = None

    def __init__(
        self, host: str = "192.168.31.65", port: int = 502, parent=None) -> None:
        super().__init__(parent)
        self.host = host
        self.port = port
        self.client = ModbusTcpClient(host,port)
        self.out = False
        
    def run(self):
        # 循环读取主函数
        self.is_quit = False
        count1 = 0 #心跳计数器1
        count2 = 0 #心跳计数器2
        while self.is_quit == False:
            count1 += 1
            #同步PLC保持寄存器状态
            self.connect_sts, self.holding_register_val = self.read_holding_register(0, 4)
            res = self.analog_trans(self.holding_register_val[2])
            self.infoSignal.emit({"plc_sts":self.connect_sts,"holding_register":self.holding_register_val,"thickness":res})
            self.write_holding_register(5, self.out+10) #写入数据
            if self.connect_sts:
                time.sleep(0.01)
            else:
                time.sleep(2)
                self.reconnect(0,1)
            #心跳信号设置
            if count1 > 3:
                time.sleep(0.01)
                count1 = 0
                count2 += 1
                self.write_holding_register(0, count2)
                if count2 > 100:
                    count2 = 0
        self.is_quit = False

    def write_single_coil(self, output_index: int = -1, output_val: bool = False):
        if self.connect_sts == False:
            return False
        try:
            self.client.write_coil(output_index, output_val)
            self.connect_sts = True
            return True
        except ConnectionException as e:
            self.connect_sts = False
            return False
        
    def write_holding_register(self, address:int, val:int):
        if self.connect_sts == False:
            return False
        try:
            self.client.write_register(address, val)
            self.connect_sts = True
            return True
        except ConnectionException as e:
            self.connect_sts = False
            return False
        
    def read_holding_register(self, address:int, length:int):
        if self.connect_sts == False:
            return False, [0]
        try:
            result:ReadInputRegistersResponse = self.client.read_holding_registers(address,count=length)
            self.connect_sts = True
            return True, result.registers
        except Exception as e:
            self.connect_sts = False
            return False, [0]
        
    def reconnect(self, address:int, length:int):
        try:
            result:ReadInputRegistersResponse = self.client.read_holding_registers(address,count=length)
            self.connect_sts = True
            return True, result.registers
        except Exception as e:
            self.connect_sts = False
            return False, ""
        
    def analog_trans(self, data):
        if data <13734:
            val = data/13734*280-140
        else:
            val = -1
        return val


    def close(self):
        self.is_quit = True
        self.client.close()

    def __del__(self):
        try:
            self.client.close()
            print("成功关闭端口")
        except Exception as e:
            print("关闭端口失败")

if __name__ == "__main__":
    myDemo = ModbusTcpClientClass('192.168.31.65',503)
    myDemo.write_single_coil(3, 0)
    res = myDemo.read_holding_register(0,20)
    print(res)
