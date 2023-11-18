# from System.utils.Model import ModbusDatabase
# from System.utils.Serial import ModbusRTU
from System.utils.Model import ModbusDatabase 
from System.utils.Serial import ModbusRTU 

from kivy.app import App

import threading
import struct 
import time 
import os 

DB_PATH = os.path.join(os.path.dirname(__file__).removesuffix('System'), 'Model', 'db', 'tags.db')

class Device(ModbusRTU):
    
    DB: ModbusDatabase

    scan_on: bool = True

    def __init__(self, slave: int, port: str, baudrate: int, parity: str = 'E', stop_bits: int = 1, byte_size: int = 8, timeout: int = 1, init_registers : bool = False, debug: bool = False):
        super().__init__(slave, port, baudrate, parity, stop_bits, byte_size, timeout, debug = debug )
        self.device_address = slave 
        self.DB = ModbusDatabase( DB_PATH = DB_PATH, init_registers = init_registers, debug = debug )
        self._debug = debug
        
        self.scan_routine = threading.Thread( target = self.auto_scan_routine ) 
        self.scan_routine.start() 


    def is_open( self ): 
        return self.client.serial.is_open

    def open(self):
        try:
            self.client.serial.open()
        except: 
            pass
        
    def close( self ):
        self.client.serial.close() 

    def read_coil(self, register_type: str, address: int, count: int = 1, DB : ModbusDatabase | None = None  ) -> list | bool | None :
        if isinstance( DB, ModbusDatabase ):
            read_db = DB.read_tags( self.device_address, register_type, address, count )
        else:
            read_db = self.DB.read_tags( self.device_address, register_type, address, count )
        if read_db == {}:
            if self._debug:
                print( f'Something wrong - DB:{read_db}' )
            return None
        else: 
            # Verifica o tipo do primeiro elemento do dicionário, todos devem ser do mesmo tipo 
            var_type = read_db[0]['type']
            for tag in read_db: 
                if tag['type'] != var_type:
                    if self._debug:
                        print( f'Elements are no the same type: ', tag['type'], ' !== ', var_type )
                    return False
            # Se todos forem do mesmo tipo ler
            read_modbus = super().read_coils( register_type, address, read_db[0]['len']*count )         
            if not isinstance( read_modbus, list ): 
                if self._debug:
                    print( f'Something wrong - Modbus:{read_modbus}' )
                return None 
            else: 
                # Salva os novos valores lidos, dentro do DB
                for addr in range( count ):
                    if isinstance( DB, ModbusDatabase ):
                        DB.write_tag( self.device_address, tag_type = register_type, address = address+addr, new_value = read_modbus[addr] )
                    else: 
                        self.DB.write_tag( self.device_address, tag_type = register_type, address = address+addr, new_value = read_modbus[addr] )
                return read_modbus 


    def read_register(self, register_type: str, address: int, last_addres: int = 1, DB : ModbusDatabase | None = None  ) -> list[ int | float ] | bool | None:
        if isinstance( DB, ModbusDatabase ):
            read_db = DB.read_tags( self.device_address, register_type, address, last_addres )
        else:
            read_db = self.DB.read_tags( self.device_address, register_type, address, last_addres )
        if read_db == {}:
            if self._debug:
                print( f'Something wrong - DB:{read_db}' )
            return None
        else: 
            var_types = [] 
            num_reg = 0 
            for tag in read_db: 
                var_types.append( tag['type'] )
                num_reg += tag['len']
            read_modbus = super().read_registers(register_type, address, num_reg, 'INT' )
            if not isinstance( read_modbus, list ): 
                if self._debug:
                    print( f'Something wrong - Modbus:{read_modbus}' )
                return None 
            else: 
                values = [] 
                count = 0 
                for var in var_types:
                    if var == 'FLOAT':
                        values.append( struct.unpack( 'f', struct.pack('<HH', read_modbus[count+1], read_modbus[count] ) )[0] )
                        if isinstance( DB, ModbusDatabase ):
                            DB.write_tag( self.device_address, tag_type = register_type, address = address+count, new_value = values[-1] )
                        else: 
                            self.DB.write_tag( self.device_address, tag_type = register_type, address = address+count, new_value = values[-1] )
                        count += 2 
                    elif var == 'INT':
                        values.append( read_modbus[count])
                        if isinstance( DB, ModbusDatabase ):
                            DB.write_tag( self.device_address, tag_type = register_type, address = address+count, new_value = values[-1] )
                        else: 
                            self.DB.write_tag( self.device_address, tag_type = register_type, address = address+count, new_value = values[-1] )
                        count += 1
                return values 
            
    def write_coils(self, address: int, value: bool | list[bool] ) -> bool | None:
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

    def auto_scan_routine( self ):
        DB = ModbusDatabase( DB_PATH = DB_PATH )
        dtime = time.time()
        ptime = time.time()
        while App.get_running_app():
            if self.scan_on and self.is_open():
                # if time.time() - dtime > 1: 
                #     self.read_coil( 'coil_register', 0x00, 8, DB = DB )
                #     self.read_coil( 'coil_input'   , 0x00, 4, DB = DB )
                #     self.read_register( 'holding_register', 0x00, 0x1C, DB = DB )
                #     self.read_register( 'analog_input', 0x00, 0x14, DB = DB )
                #     dtime = time.time() 

                # SE HOMESCREEN 
                if time.time() - ptime > 0.1:
                    self.read_register( 'analog_input', 0x00, 0x04, DB = DB )
                    ptime = time.time()
                    print('velocidade')

                # SE SERIAL SCREEN

                # SE SENSOR SCREEN 
                






if __name__ == "__main__":

    tracker = Device(  0x12, "COM18", 57600, debug = True )
    tracker.write_coils( 0x00, [False, True, False, True] )
    print( tracker.read_coils( 'coil_register', 0x00, 8 ) )