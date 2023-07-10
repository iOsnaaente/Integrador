# from System.utils.Model import ModbusDatabase
# from System.utils.Serial import ModbusRTU
from System.utils.Model import ModbusDatabase 
from System.utils.Serial import ModbusRTU 

import struct 
import os 

DB_PATH = os.path.join(os.path.dirname(__file__).removesuffix('System'), 'Model', 'db', 'tags.db')

class Device(ModbusRTU):
    
    DB: ModbusDatabase

    def __init__(self, slave: int, port: str, baudrate: int, parity: str = 'N', stop_bits: int = 1, byte_size: int = 8, timeout: int = 1, init_registers : bool = False, debug: bool = False):
        super().__init__(slave, port, baudrate, parity, stop_bits, byte_size, timeout, debug = debug )
        self.device_address = slave 
        self.DB = ModbusDatabase( DB_PATH = DB_PATH, init_registers = init_registers, debug = debug )
        self._debug = debug

    def read_coil(self, register_type: str, address: int ) -> int | None :
        read_db = self.DB.read_tag( self.device_address, register_type, address )
        print( read_db )
        if read_db == {}:
            if self._debug:
                print( f'Something wrong - DB:{read_db}' )
            return None
        else: 
            read_modbus = super().read_coils( register_type, address, read_db['len'] )            
            if not isinstance( read_modbus, list ): 
                if self._debug:
                    print( f'Something wrong - Modbus:{read_modbus}' )
                return None 
            else: 
                value = read_modbus[0]
                self.DB.write_tag( self.device_address, tag_type = register_type, address = address, new_value = value )
                return value 

    def read_register(self, register_type: str, address: int ) -> int | float | None:
        read_db = self.DB.read_tag( self.device_address, register_type, address )
        if read_db == {}:
            if self._debug:
                print( f'Something wrong - DB:{read_db}' )
            return None
        else: 
            var_type = read_db['type']
            length = read_db['len']
            read_modbus = super().read_register(register_type, address, length, var_type )
            if not isinstance( read_modbus, list ): 
                if self._debug:
                    print( f'Something wrong - Modbus:{read_modbus}' )
                return None 
            else: 
                value = read_modbus[0]
                self.DB.write_tag( self.device_address, tag_type = register_type, address = address, new_value = value )
                return value 
            
    def write_coils(self, address: int, value: bool ) -> bool | None:
        register_type = 'coil_register'
        read_db = self.DB.read_tag( self.device_address, register_type, address )
        if read_db == {}:
            if self._debug:
                print( f'Something wrong - DB:{read_db}' )
            return None
        else: 
            if isinstance( value, int ):
                read_db['len']
            read_modbus = super().write_coils( address, value )
            if not isinstance( read_modbus, list ): 
                if self._debug:
                    print( f'Something wrong - Modbus:{read_modbus}' )
                return None 
            else: 
                value = read_modbus[0]
                self.DB.write_tag( self.device_address, tag_type = register_type, address = address, new_value = value )
                return value 

    def write_register(self, address: int, value: int | float ) -> bool | None:
        register_type = 'holding_register'
        read_db = self.DB.read_tag( self.device_address, register_type, address )
        if read_db == {}:
            if self._debug:
                print( f'Something wrong - DB:{read_db}' )
            return None
        else: 
            if isinstance( value, int ):
                read_db['len']
            read_modbus = super().write_registers( address, value )
            if not isinstance( read_modbus, list ): 
                if self._debug:
                    print( f'Something wrong - Modbus:{read_modbus}' )
                return None 
            else: 
                value = read_modbus[0]
                self.DB.write_tag( self.device_address, tag_type = register_type, address = address, new_value = value )
                return value 

