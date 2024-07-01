from pymodbus.client import ModbusTcpClient
from pymodbus.bit_read_message import ReadCoilsResponse
from pymodbus.register_read_message import ReadInputRegistersResponse
from pymodbus.exceptions import ConnectionException      # 连接失败，用于异常处理
from PyQt5.QtCore import QThread, pyqtSignal
import time

class ModbusTcpClientClass(QThread):
    infoSignal = pyqtSignal(dict)
    connect_sts = False
    holding_register_val = None

    def __init__(
        self, host: str = "192.168.31.65", port: int = 502, parent=None) -> None:
        super().__init__(parent)
        self.host = host
        self.port = port
        self.client = ModbusTcpClient(host,port)
        
    def run(self):
        # 循环读取主函数
        self.is_quit = False
        while self.is_quit == False:
            #同步PLC保持寄存器状态
            self.connect_sts, self.holding_register_val = self.read_holding_register(10, 2)
            self.infoSignal.emit({"plc_sts":self.connect_sts,"holding_register":self.holding_register_val})
            if self.connect_sts:
                time.sleep(0.15)
            else:
                time.sleep(2)
                self.reconnect(0,1)
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
