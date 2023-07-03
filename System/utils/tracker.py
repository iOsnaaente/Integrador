from System.utils import *
# from .utils.Model import ModbusDatabase
# from .utils.Serial import ModbusRTU
import os 

DB_PATH = os.path.join(os.path.dirname(__file__).removesuffix('System'), 'db', 'tags.db')

class Device(ModbusRTU):
    
    DB: ModbusDatabase

    def __init__(self, slave: int, port: str, baudrate: int, parity: str = 'N', stop_bits: int = 1, byte_size: int = 8, timeout: int = 1, debug: bool = False):
        super().__init__(slave, port, baudrate, parity, stop_bits, byte_size, timeout, debug)
        self.DB = ModbusDatabase( DB_PATH = DB_PATH, debug = debug )
        self._debug = debug

    def read_coils(self, register_type: str, address: int, length: int):
        read = super().read_coils(register_type, address, length)
        return read 

    def read_register(self, register_type: str, address: int, length: int, var_type: str):
        read = super().read_register(register_type, address, length, var_type)
        return read 

    def write_coils(self, address: int, values: bool | list[bool]) -> bool:
        ans = super().write_coils(address, values)
        return ans 

    def write_registers(self, address: int, values: int | float | list[int | float]):
        ans = super().write_registers(address, values)
        return ans 
    

if __name__ == '__main__': 
    tracker = Device( 0x12, 'COM5', 19200, debug = True  )
