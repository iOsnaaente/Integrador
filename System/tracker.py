# from System.utils.Model import ModbusDatabase
# from System.utils.Serial import ModbusRTU
from System.utils.Model import ModbusDatabase 
from System.utils.Serial import ModbusRTU 
from System.Tags import * 

from kivy.app import App

import threading
import struct 
import time 
import os 

DB_PATH = os.path.join( os.path.dirname(__file__).removesuffix('System'), 'Model', 'db', 'tags.db')

class Device( ModbusRTU ):
    
    # Banco de dados 
    DB: ModbusDatabase
    write: bool = False 
    scan_on: bool = True
    err_count: int 

    def __init__(self, slave: int, port: str, baudrate: int, parity: str = 'E', stop_bits: int = 1, byte_size: int = 8, timeout: int = 1, init_registers : bool = False, debug: bool = False):
        super().__init__(slave, port, baudrate, parity, stop_bits, byte_size, timeout, debug = debug )
        self.device_address = slave 
        # Objeto Modbus 
        self.DB = ModbusDatabase( DB_PATH = DB_PATH, init_registers = init_registers, debug = debug )
        # Pega o Datashared do aplicativo 
        self.shared_data = App.get_running_app().shared_data
        # Thread para fazer o escaneamento automatico da Serial 
        self.scan_routine = threading.Thread( target = self.auto_scan_routine ) 
        self.scan_routine.start() 
        
        self.err_count = 0 
        self._debug = True


    def is_connected( self ) -> bool: 
        try: 
            return False if self.read_coil( 'coil_register', DISCRETE_CONNECTED ) == None else True 
        except Exception as err:
            print( err )
            return False

    def open(self):
        try:
            self.client.serial.open()
        except: 
            pass
        
    def close( self ):
        self.client.serial.close() 
    
    def check_connection( self ): 
        return self.is_connected()              


    def read_coil(self, register_type: str, address: int, count: int = 1, DB : ModbusDatabase | None = None  ) -> list [bool] | bool | None :
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

    def read_modbus( self, register_type: str, address: int, num_regs: int = 1, reg_type: str = 'INT'  ) -> list[ int | float | bool ] | bool | None:
        if reg_type == 'BIT':
            return super().read_coils( register_type, address, num_regs )
        elif reg_type == 'INT' or reg_type == 'FLOAT':
            return super().read_registers(register_type, address, num_regs, reg_type )

    def auto_scan_routine( self ):
        DB = ModbusDatabase( DB_PATH = DB_PATH )
        d_time = time.time()
        h_time = time.time()
        while App.get_running_app():
            current_screen = App.get_running_app().root.current
            try:
                # Se precisa escrever via Modbus, a flag Write_modbus irá ser True 
                if self.write: 
                    coil_data = [bool(value) for key, value in self.shared_data.SYSTEM_TABLE.items() if 'COIL_' in key]
                    count = 0 
                    while self.is_connected():       
                        status = super().write_coils( 0x00, coil_data )   
                        if status:
                            break 
                        else:
                            count+=1
                            if count == 10:
                                print( 'COUNT == 10')
                                break 

                    holding_data = [value for key, value in self.shared_data.SYSTEM_TABLE.items() if 'HR_' in key]        
                    super().write_registers( 0x00, holding_data )
                    self.write = False

                # Lê todos a cada um segundo 
                else: 
                    if time.time() - d_time > 1:
                        d_time = time.time() 
                        for dt, ind in zip( self.read_modbus( 'coil_register' , 0x00, 0x08, 'BIT' ), [ "COIL_POWER", "COIL_LED",   "COIL_M_GIR", "COIL_M_ELE", "COIL_LEDR",  "COIL_LEDG",  "COIL_LEDB",  "COIL_SYNC_DATE" ] ):
                            self.shared_data.SYSTEM_TABLE[ind] = dt 
                        for dt, ind in zip( self.read_modbus( 'coil_input', 0x00, 0x05, 'BIT' ), [ "DISCRETE_FAIL", "DISCRETE_POWER", "DISCRETE_TIME", "DISCRETE_GPS", "DISCRETE_CONNECTED"] ):
                            self.shared_data.SYSTEM_TABLE[ind] = dt 
                        for dt, ind in zip( self.read_modbus( 'holding_register', 0x00, 0x16, 'FLOAT'), [ "HR_PV_GIR", "HR_KP_GIR", "HR_KI_GIR", "HR_KD_GIR", "HR_AZIMUTE", "HR_PV_ELE", "HR_KP_ELE", "HR_KI_ELE", "HR_KD_ELE", "HR_ALTITUDE", "HR_LATITUDE", "HR_LONGITUDE" ] ):
                            self.shared_data.SYSTEM_TABLE[ind] = dt 
                        for dt, ind in zip( self.read_modbus( 'holding_register', 0x18, 0x1C-0x18, 'INT'), [ "HR_STATE", "HR_YEAR", "HR_MONTH", "HR_DAY", "HR_HOUR", "HR_MINUTE", "HR_SECOND" ] ):
                            self.shared_data.SYSTEM_TABLE[ind] = dt 
                        for dt, ind in zip( self.read_modbus( 'analog_input', 0x00, 0x10, 'FLOAT'), [ "INPUT_POS_GIR", "INPUT_POS_ELE", "INPUT_AZIMUTE", "INPUT_ZENITE", "INPUT_GENERATION", "INPUT_TEMP", "INPUT_PRESURE", "INPUT_SENS_CONF_GIR", "INPUT_SENS_CONF_ELE" ] ):
                            self.shared_data.SYSTEM_TABLE[ind] = dt 
                        for dt, ind in zip( self.read_modbus( 'analog_input', 0x12, 0x17-0x12, 'INT' ), [ "INPUT_YEAR", "INPUT_MONTH", "INPUT_DAY", "INPUT_HOUR", "INPUT_MINUTE", "INPUT_SECOND" ] ):
                            self.shared_data.SYSTEM_TABLE[ind] = dt 

                    # Leitura a no mínimo 100ms 
                    if time.time() - h_time > 0.100:
                        # HOMESCREEN então lê somente os valores de Posição e geração  
                        if current_screen == 'home screen':
                            data = self.read_modbus( 'analog_input', 0x00, 4, 'FLOAT'  )
                            for dt, ind in zip( data, ["INPUT_POS_ELE", "INPUT_POS_GIR"]):
                                self.shared_data.SYSTEM_TABLE[ind] = dt
                        # SE SERIAL SCREEN
                        if current_screen == 'serial screen':
                            data = self.read_modbus( 'analog_input', 0x00, 8, 'FLOAT'  )
                            for dt, ind in zip( data, ["INPUT_POS_ELE", "INPUT_POS_GIR", 'INPUT_AZIMUTE', 'INPUT_ZENITE']):
                                self.shared_data.SYSTEM_TABLE[ind] = dt
                        # SE SENSOR SCREEN 
                        if current_screen == 'sensor screen':
                            self.shared_data.SYSTEM_TABLE['INPUT_GENERATION'] = self.read_modbus( 'analog_input', INPUT_GENERATION, 2, 'FLOAT'  )
                        h_time = time.time()

            except Exception as err :
                self.err_count += 1 
                if self.err_count > 100: 
                    self.check_connection() 
                    self.err_count = 0 
                    print( 'System/Tracker error: ', err )
