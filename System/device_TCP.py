from pymodbus.client.tcp import ModbusTcpClient 
from System.utils.Model import ModbusDatabase
from Model.system_model import SystemModel
from System.device_base import * 
from kivy.logger import Logger 
from kivy.app import App
import threading
import struct 
import time 



"""
    Device_TCP implementa a comunicação via Modbus TCP
"""
class Device_TCP( DeviceBase ):

    shared_data: SystemModel

    def __init__(self, 
        slave: int, host: str, database: ModbusDatabase, port: int = 502, 
        timeout: int = 1, init_registers: bool = False, debug: bool = False
    ) -> None:
        self.database = database 
        self.timeout = timeout
        self.debug = debug
        self.slave = slave
        self.host = host
        self.port = port

        self.client = ModbusTcpClient( host, port = port, timeout = timeout )
        self.shared_data = App.get_running_app().system_model

        self.write_flag = False
        self.scan_on = True
        self.err_count = 0
        
        self.scan_routine = threading.Thread( target = self.auto_scan_routine)
        self.scan_routine.daemon = True
        self.scan_routine.start()

    def is_connected(self) -> bool:
        try:
            if isinstance( self.client, ModbusTcpClient ):
                return self.client.connected 
            else: 
                return False 
        except Exception as e:
            if self.debug:
                Logger.warning(f"Device_TCP is_connected error: {e}" )
            return False


    def open(self):
        try:
            self.client.connect()
        except Exception as e:
            if self.debug:
                Logger.warning(f"Device_TCP open error:{e}")


    def close(self):
        try:
            if isinstance( self.client, ModbusTcpClient ):
                self.client.close()
        except Exception as e:
            if self.debug:
                Logger.warning(f"Device_TCP close error:{e}")


    def read_coil(self, register_type: str, address: int, count: int = 1, DB: ModbusDatabase | None = None ) -> list[bool] | bool | None:
        if DB is None:
            DB = self.database
        try:
            rr = self.client.read_coils(address, count = count, slave = self.slave )
            if rr.isError():
                if self.debug:
                    Logger.warning(f"Device_TCP read_coil error:{rr}")
                return None
            result = rr.bits
            for addr in range(count):
                DB.write_tag(self.slave, tag_type=register_type, address=address + addr, new_value=result[addr])
            return result
        except Exception as e:
            if self.debug:
                Logger.warning(f"Device_TCP read_coil exception:{e}")
            return None


    def read_register(self, register_type: str, address: int, last_addres: int = 1, DB: ModbusDatabase | None = None) -> list[int | float] | bool | None:
        if DB is None:
            DB = self.database
        try:
            read_db = DB.read_tags(self.slave, register_type, address, last_addres)
            if not read_db:
                if self.debug:
                    Logger.warning(f"Device_TCP: Falha na leitura do DB para registradores.")
                return None
            num_reg = 0
            var_types = []
            for tag in read_db:
                var_types.append(tag['type'])
                num_reg += tag['len']
            rr = self.client.read_holding_registers(address, count = num_reg, slave=self.slave)
            if rr.isError():
                if self.debug:
                    Logger.warning(f"Device_TCP read_register error:{rr}")
                return None
            registers = rr.registers
            values = []
            count = 0
            for var in var_types:
                if var == 'FLOAT':
                    import struct
                    value = struct.unpack('f', struct.pack('<HH', registers[count+1], registers[count]))[0]
                    values.append(value)
                    DB.write_tag(self.slave, tag_type=register_type, address=address+count, new_value=value)
                    count += 2
                elif var == 'INT':
                    value = registers[count]
                    values.append(value)
                    DB.write_tag(self.slave, tag_type=register_type, address=address+count, new_value=value)
                    count += 1
            return values
        except Exception as e:
            if self.debug:
                Logger.warning(f"Device_TCP read_register exception:{e}")
            return None


    def write_coils(self, address: int, value: bool | list[bool]) -> bool:
        register_type = 'coil_register'
        try:
            value = [ value ] if isinstance( value, bool ) else value 
            rr = self.client.write_coils(address, values = value, slave = self.slave)
            if rr.isError():
                if self.debug:
                    Logger.warning(f"Device_TCP write_coils error:", rr)
                return False
            self.database.write_tag(self.slave, tag_type = register_type, address = address, new_value = value )
            return True 
        except Exception as e:
            if self.debug:
                Logger.warning(f"Device_TCP write_coils exception:{e}")
            return False


    def write_register(self, address: int, value: int | float) -> bool | None:
        register_type = 'holding_register'
        try:
            # Se for do tipo float, usa dois registradores 
            if isinstance( value, float ):
                packad = struct.pack( '<f', value )
                values = list( struct.unpack('<HH', packad) ) 
                rr = self.client.write_registers( address, values = values, slave = self.slave )
            else:
                rr = self.client.write_register(address, value = value, slave = self.slave)
            # Verifica se houve algum erro 
            if rr.isError():
                if self.debug:
                    Logger.warning(f"Device_TCP write_register error:", rr)
                return None
            
            self.database.write_tag(self.slave, tag_type = register_type, address = address, new_value = value )
            return True
        except Exception as e:
            if self.debug:
                Logger.warning(f"Device_TCP write_register exception:{e}")
            return None


    def read_modbus(self, register_type: str, address: int, num_regs: int = 1, reg_type: str = 'INT' ) -> (list[bool] | bool | None) | (list[float|int] | float | int) | None:
        if reg_type == 'BIT':
            return self.read_coil( register_type, address, num_regs )
        elif reg_type in ['INT', 'FLOAT']:
            return self.read_register(register_type, address, num_regs)
        else:
            if self.debug:
                Logger.warning(f"Device_TCP: Tipo de registrador desconhecido.")
            return None


    def auto_scan_routine(self):
        from System.utils.Model import ModbusDatabase  # Se necessário
        retry_conn_time = time.time()
        d_time = time.time()

        while App.get_running_app():
            current_screen = App.get_running_app().root.current
            time.sleep(0.01)
            
            try:
                # Se não estiver conectado, tenta estabelecer conexão
                if not self.client.connected:
                    if time.time() - retry_conn_time > 1:
                        retry_conn_time = time.time()
                        # Tenta reconectar e atualiza a flag de conexão no shared_data
                        self.client.connect()
                        self.shared_data.SYSTEM_TABLE['DISCRETE_CONNECTED'] = self.is_connected()
                
                # Se estiver conectado
                elif self.client.connected:
                    self.err_count = 0

                    # HOMESCREEN ou MAP SCREEN: lê valores de posição e geração
                    if current_screen in ['home screen', 'map screen']:
                        data = self.read_modbus('analog_input', 0x00, 4, 'FLOAT')
                        if data and isinstance( data, list ):
                            for dt, ind in zip(data, ["INPUT_POS_ELE", "INPUT_POS_GIR"]):
                                self.shared_data.SYSTEM_TABLE[ind] = dt
                        # Lê outros dados inteiros (exemplo de data/hora)
                        data_int = self.read_modbus('analog_input', 0x12, (0x17 - 0x12), 'INT')
                        if data_int and isinstance( data_int, list ):
                            for dt, ind in zip(data_int, ["INPUT_YEAR", "INPUT_MONTH", "INPUT_DAY", "INPUT_HOUR", "INPUT_MINUTE", "INPUT_SECOND"]):
                                self.shared_data.SYSTEM_TABLE[ind] = dt

                    # SERIAL SCREEN: lê mais valores analógicos (exemplo: posição, azimute e zenite)
                    if current_screen == 'serial screen':
                        data = self.read_modbus('analog_input', 0x00, 8, 'FLOAT')
                        if data and isinstance( data, list ):
                            for dt, ind in zip(data, ["INPUT_POS_ELE", "INPUT_POS_GIR", "INPUT_AZIMUTE", "INPUT_ZENITE"]):
                                self.shared_data.SYSTEM_TABLE[ind] = dt

                    # SENSOR SCREEN: lê valor de geração (ou outro sensor)
                    if current_screen == 'sensor screen':
                        value = self.read_modbus('analog_input', INPUT_GENERATION, 2, 'FLOAT')
                        if value is not None:
                            self.shared_data.SYSTEM_TABLE['INPUT_GENERATION'] = value

                    # Se a flag write estiver ativa, envia dados via Modbus
                    if self.write:
                        # Converte os valores dos coils para booleanos
                        coil_data = [bool(value) for key, value in self.shared_data.SYSTEM_TABLE.items() if 'COIL_' in key]
                        # Aqui, para TCP, chamamos o método write_coils da própria classe ou um método específico de escrita
                        self.write_coils(0x00, coil_data)
                        holding_data = [value for key, value in self.shared_data.SYSTEM_TABLE.items() if 'HR_' in key]
                        # Para registrar múltiplos valores, pode ser necessário um método write_registers (implementado conforme sua API)
                        self.client.write_registers(0x00, holding_data, slave = self.slave )
                        self.write = False

                    # Leitura periódica completa dos registradores
                    if time.time() - d_time > 2.5:
                        d_time = time.time()
                        try:
                            # Leitura de Coils
                            coils = self.read_modbus('coil_register', 0x00, 8, 'BIT')
                            if coils and isinstance( coils, list ):
                                for dt, ind in zip(coils, ["COIL_POWER", "COIL_LED", "COIL_M_GIR", "COIL_M_ELE", "COIL_LEDR", "COIL_LEDG", "COIL_LEDB", "COIL_SYNC_DATE"]):
                                    self.shared_data.SYSTEM_TABLE[ind] = dt
                                    
                            # Leitura de entradas discretas
                            disc_inputs = self.read_modbus('coil_input', 0x00, 5, 'BIT')
                            if disc_inputs and isinstance( disc_inputs, list ):
                                for dt, ind in zip(disc_inputs, ["DISCRETE_FAIL", "DISCRETE_POWER", "DISCRETE_TIME", "DISCRETE_GPS", "DISCRETE_CONNECTED"]):
                                    self.shared_data.SYSTEM_TABLE[ind] = dt

                            # Leitura de holdings (Float)
                            holdings_float = self.read_modbus('holding_register', 0x00, 22, 'FLOAT')
                            if holdings_float and isinstance( holdings_float, list ):
                                for dt, ind in zip(holdings_float, ["HR_PV_GIR", "HR_KP_GIR", "HR_KI_GIR", "HR_KD_GIR", "HR_AZIMUTE", "HR_PV_ELE", "HR_KP_ELE", "HR_KI_ELE", "HR_KD_ELE", "HR_ALTITUDE", "HR_LATITUDE", "HR_LONGITUDE"]):
                                    self.shared_data.SYSTEM_TABLE[ind] = dt

                            # Leitura de holdings (Int)
                            holdings_int = self.read_modbus('holding_register', 0x18, (0x1C - 0x18), 'INT')
                            if holdings_int and isinstance( holdings_int, list ):
                                for dt, ind in zip(holdings_int, ["HR_STATE", "HR_YEAR", "HR_MONTH", "HR_DAY", "HR_HOUR", "HR_MINUTE", "HR_SECOND"]):
                                    self.shared_data.SYSTEM_TABLE[ind] = dt

                            # Leitura de Analog (Float)
                            analog_float = self.read_modbus('analog_input', 0x00, 16, 'FLOAT')
                            if analog_float and isinstance( analog_float, list ):
                                for dt, ind in zip(analog_float, ["INPUT_POS_GIR", "INPUT_POS_ELE", "INPUT_AZIMUTE", "INPUT_ZENITE", "INPUT_GENERATION", "INPUT_TEMP", "INPUT_PRESURE", "INPUT_SENS_CONF_GIR", "INPUT_SENS_CONF_ELE"]):
                                    self.shared_data.SYSTEM_TABLE[ind] = dt

                            # Leitura de Analog (Int)
                            analog_int = self.read_modbus('analog_input', 0x12, (0x17 - 0x12), 'INT')
                            if analog_int and isinstance( analog_int, list ):
                                for dt, ind in zip(analog_int, ["INPUT_YEAR", "INPUT_MONTH", "INPUT_DAY", "INPUT_HOUR", "INPUT_MINUTE", "INPUT_SECOND"]):
                                    self.shared_data.SYSTEM_TABLE[ind] = dt

                        except Exception as err:
                            if self.debug:
                                Logger.warning(f"Device_TCP auto_scan_routine: Erro ao ler todos os registradores:{err}")
                            self.shared_data.SYSTEM_TABLE['DISCRETE_CONNECTED'] = self.is_connected()

            except Exception as err:
                self.err_count += 1
                self.shared_data.SYSTEM_TABLE['DISCRETE_CONNECTED'] = self.is_connected()
                if self.err_count > 25:
                    self.shared_data.SYSTEM_TABLE['DISCRETE_CONNECTED'] = False
                if self.debug:
                    Logger.warning( f"Device_TCP auto_scan_routine error:{err}")
