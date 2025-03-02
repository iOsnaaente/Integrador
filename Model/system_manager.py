from System.device_base import DB_PATH 
from System.utils.Model import ModbusDatabase 
from System.device_RTU import Device_RTU
from System.device_TCP import Device_TCP 
from kivy.logger import Logger 
from kivymd.app import MDApp 

import sqlite3
import datetime 
import threading 
import time 
import pytz


historical_mapping = {
    'history_sensor_gir': 'INPUT_POS_GIR',
    'history_sensor_ele': 'INPUT_POS_ELE',
    'history_azimute':   'INPUT_AZIMUTE',
    'history_zenite':    'INPUT_ZENITE',
    'history_generation':'INPUT_GENERATION'
}


"""
    SystemManager é responsável por gerenciar a conexão com o dispositivo 
    Serial ou outras abordagens como Modbus TCP. Ele instancia a classe 
    Device (definida em System.device_base.py) e oferece métodos para conectar e 
    desconectar o hardware.
    Além disso, ele gerencia as tags acessadas pelo dispositivo.
    
    Hierarquia:
    1. 'Interface'   = DeviceBase
    2. 'Modulo'      = Device_TCP ou Device_RTU
    3. 'Controlador' = SystemManager 
"""
class SystemManager:
    # Informações sobre o sistema 
    SYSTEM_TABLE = {
        "INPUT_POS_GIR"       : 0.0,  "INPUT_POS_ELE"       : 0.0,
        "INPUT_AZIMUTE"       : 0.0,  "INPUT_ZENITE"        : 0.0,
        "INPUT_GENERATION" 	  : 0.0,     
        "INPUT_TEMP"          : 0.0,  "INPUT_PRESURE"       : 0.0,
        "INPUT_SENS_CONF_GIR" : 0.0,  "INPUT_SENS_CONF_ELE" : 0.0,
        "INPUT_YEAR"          : 0  ,  "INPUT_MONTH"         : 0  ,  "INPUT_DAY"           : 0  ,
        "INPUT_HOUR"          : 0  ,  "INPUT_MINUTE"        : 0  ,  "INPUT_SECOND"        : 0  ,
        
        "HR_PV_GIR"           : 0.0,  "HR_KP_GIR"           : 0.0,  "HR_KI_GIR"           : 0.0, "HR_KD_GIR"           : 0.0,  
        "HR_AZIMUTE"          : 0.0,  
        "HR_PV_ELE"           : 0.0,  "HR_KP_ELE"           : 0.0,  "HR_KI_ELE"           : 0.0, "HR_KD_ELE"           : 0.0,
        "HR_ALTITUDE"         : 0.0,  "HR_LATITUDE"         : 0.0,  "HR_LONGITUDE"        : 0.0,
        "HR_STATE"            : 0,
        "HR_YEAR"             : 0,    "HR_MONTH"            : 0,  "HR_DAY"                : 0,
        "HR_HOUR"             : 0,    "HR_MINUTE"           : 0,  "HR_SECOND"             : 0,
        
        "DISCRETE_FAIL"       : False,
        "DISCRETE_POWER"      : False,
        "DISCRETE_TIME"       : False,
        "DISCRETE_GPS"        : False,
        "DISCRETE_CONNECTED"  : False,

        "COIL_POWER"          : False, "COIL_LED"            : False,
        "COIL_M_GIR"          : False, "COIL_M_ELE"          : False,
        "COIL_LEDR"           : False, "COIL_LEDG"           : False,   "COIL_LEDB"           : False,
        "COIL_SYNC_DATE"      : False,
    } 
    

    # Mapeia cada tag para o tipo (nome da tabela) e endereço conforme definido em initialize_tags.
    TAG_MAPPING = {
        # Analog Input
        "INPUT_POS_GIR": ("analog_input", 0x00),
        "INPUT_POS_ELE": ("analog_input", 0x02),
        "INPUT_AZIMUTE": ("analog_input", 0x04),
        "INPUT_ZENITE": ("analog_input", 0x06),
        "INPUT_GENERATION": ("analog_input", 0x08),
        "INPUT_TEMP": ("analog_input", 0x0A),
        "INPUT_PRESURE": ("analog_input", 0x0C),
        "INPUT_SENS_CONF_GIR": ("analog_input", 0x0E),
        "INPUT_SENS_CONF_ELE": ("analog_input", 0x10),
        "INPUT_YEAR": ("analog_input", 0x12),
        "INPUT_MONTH": ("analog_input", 0x13),
        "INPUT_DAY": ("analog_input", 0x14),
        "INPUT_HOUR": ("analog_input", 0x15),
        "INPUT_MINUTE": ("analog_input", 0x16),
        "INPUT_SECOND": ("analog_input", 0x17),

        # Holding Register
        "HR_PV_GIR": ("holding_register", 0x00),
        "HR_KP_GIR": ("holding_register", 0x02),
        "HR_KI_GIR": ("holding_register", 0x04),
        "HR_KD_GIR": ("holding_register", 0x06),
        "HR_AZIMUTE": ("holding_register", 0x08),
        "HR_PV_ELE": ("holding_register", 0x0A),
        "HR_KP_ELE": ("holding_register", 0x0C),
        "HR_KI_ELE": ("holding_register", 0x0E),
        "HR_KD_ELE": ("holding_register", 0x10),
        "HR_ALTITUDE": ("holding_register", 0x12),
        "HR_LATITUDE": ("holding_register", 0x14),
        "HR_LONGITUDE": ("holding_register", 0x16),
        "HR_STATE": ("holding_register", 0x18),
        "HR_YEAR": ("holding_register", 0x19),
        "HR_MONTH": ("holding_register", 0x1A),
        "HR_DAY": ("holding_register", 0x1B),
        "HR_HOUR": ("holding_register", 0x1C),
        "HR_MINUTE": ("holding_register", 0x1D),
        "HR_SECOND": ("holding_register", 0x1E),

        # Coil Input
        "DISCRETE_FAIL": ("coil_input", 0x00),
        "DISCRETE_POWER": ("coil_input", 0x01),
        "DISCRETE_TIME": ("coil_input", 0x02),
        "DISCRETE_GPS": ("coil_input", 0x03),
        "DISCRETE_CONNECTED": ("coil_input", 0x04),

        # Coil Register
        "COIL_POWER": ("coil_register", 0x00),
        "COIL_LED": ("coil_register", 0x01),
        "COIL_M_GIR": ("coil_register", 0x02),
        "COIL_M_ELE": ("coil_register", 0x03),
        "COIL_LEDR": ("coil_register", 0x04),
        "COIL_LEDG": ("coil_register", 0x05),
        "COIL_LEDB": ("coil_register", 0x06),
        "COIL_SYNC_DATE": ("coil_register", 0x07)
    }

    # Valores default  
    ZEN_HOME: int = 30
    AZI_HOME: int = 40 

    # STATES disponíveis 
    FAIL_STATE     = 0
    AUTOMATIC      = 1
    MANUAL         = 2
    REMOTE         = 3
    DEMO           = 4
    IDLE           = 5
    RESET          = 6
    PRE_RETURNING  = 7
    RETURNING      = 8
    SLEEPING       = 9
    
    # STATE atual 
    state: int

    time_between_save_history: float = 60.0

    # Valores do sistema 
    init_registers: bool = False 
    database: ModbusDatabase
    slave: int
    port: str 

    _db_lock: threading.Lock

    """ Inicia o Banco de dados """
    def __init__(self, db_lock: threading.Lock, debug: bool = False ):
        self.database = ModbusDatabase( DB_PATH = DB_PATH, init_registers = True, debug = True )
        self.device = None
        self.state = self.IDLE 
        self._debug = debug   
        self._db_lock = db_lock

        # Variável para controlar o término da thread
        self._stop_thread = threading.Event()
        self._data_thread = threading.Thread(target=self._save_system_data_thread, daemon = True )
        self._data_thread.start()
            
    

    """
        Tenta conectar com o dispositivo Serial e verifica se há uma conexão
    """
    def connect_device_RTU( self, slave: int, port: str, baudrate: int, timeout: int = 1, 
        parity: str = 'E', stop_bits: int = 1, byte_size: int = 8, init_registers: bool = False 
    ) -> bool:
        self.disconnect()
        try:
            # Converte baudrate e timeout para inteiros 
            baudrate = int(baudrate)
            timeout = int(timeout)
            # Instancia o dispositivo com os parâmetros fornecidos.
            self.device = Device_RTU( 
                slave, port, baudrate, self.database, timeout = timeout, 
                parity = parity, stop_bits = stop_bits, byte_size = byte_size, 
                init_registers = init_registers, debug = self._debug 
            )
            
            # Verifica se a conexão foi estabelecida com sucesso usando o método is_connected.
            is_connected = self.device.is_connected()
            if self._debug:
                if is_connected:
                    Logger.info("Device_RTU: Conexão estabelecida com sucesso.")
                else:
                    Logger.info("Device_RTU: Falha na conexão com o dispositivo.")
            return is_connected
        except Exception as err:
            if self._debug:
                Logger.warning( f"Device_RTU: Erro ao tentar conectar - {err}" )
            return False
    

    """
        Tenta conectar com o dispositivo TCP e verifica se há uma conexão
    """ 
    def connect_device_TCP( self, slave: int, IP: str, port: int, timeout: int = 1, init_registers: bool = False ) -> bool:
        self.disconnect()
        try:
            self.device = Device_TCP( 
                slave = slave, database = self.database, host = IP, port = port, 
                timeout = timeout, init_registers = init_registers, debug = self._debug 
            )
            is_connected = self.device.is_connected()
            if self._debug:
                if is_connected:
                    Logger.info("Device_TCP: Conexão estabelecida com sucesso.")
                else:
                    Logger.info("Device_TCP: Falha na conexão com o dispositivo.")
            return is_connected
        except Exception as err:
            if self._debug:
                Logger.warning( f"Device_TCP: Erro ao tentar conectar - {err}" )
            return False
    

    """
        Fecha a conexão com o dispositivo, se houver uma conexão ativa.
    """
    def disconnect(self) -> None:
        try:
            if self.device is not None:
                self.device.close()
                if self._debug:
                    Logger.info("DeviceManager: Dispositivo desconectado com sucesso.")
                self.device = None
        except Exception as e:
            if self._debug:
                Logger.warning( f"DeviceManager: Erro ao desconectar o dispositivo - {e}" )


    """ Retorna a Hora do sistema """
    def get_sys_time(self) -> str:
        return f"{self.SYSTEM_TABLE['INPUT_HOUR']}:{self.SYSTEM_TABLE['INPUT_MINUTE']}:{self.SYSTEM_TABLE['INPUT_SECOND']}"
    

    """ Retorna a Data do sistema """
    def get_sys_date(self) -> str:
        return f"{self.SYSTEM_TABLE['INPUT_YEAR']}:{self.SYSTEM_TABLE['INPUT_MONTH']}:{self.SYSTEM_TABLE['INPUT_DAY']}"
    

    """ Atualiza o valor da tabela de dados """
    def update( self, new_data: dict) -> None:
        self.SYSTEM_TABLE.update( new_data )


    """ Retorna os valores de posição dos motores  """
    def get_motor_pos( self ) -> list | None:
        return [ self.SYSTEM_TABLE['INPUT_POS_GIR'], self.SYSTEM_TABLE['INPUT_POS_ELE'] ]
    

    """ Retorna o valor de medição do sensor LDR """
    def get_system_generation( self ) -> float: 
        return ( ( ((2**16)-1) - self.SYSTEM_TABLE['INPUT_GENERATION'] )/((2**16)-1) )*100
    

    """ 
        Retorna a posição de Zenite e Azimute (MV e PV)
        1. MV - Variavel Manipulada 
        2. PV - Variavel de processo
    """
    def get_azimute_zenite_data( self ) -> list:
        return [ 
            self.SYSTEM_TABLE['INPUT_ZENITE'] , self.SYSTEM_TABLE['INPUT_POS_GIR'], 
            self.SYSTEM_TABLE['INPUT_AZIMUTE'], self.SYSTEM_TABLE['INPUT_POS_ELE'] 
        ]


    """ 
        Retorna o status da conexão do Sistema
    """
    def is_connected(self) -> bool: 
        return self.SYSTEM_TABLE["DISCRETE_CONNECTED"]


    def get_system_state( self ) -> int:
        self.state = self.SYSTEM_TABLE['HR_STATE']
        return self.state


    def _save_system_data_thread(self):
        # Cria uma nova conexão para esta thread
        con_thread = sqlite3.connect(self.database.db_path, timeout=10)
        con_thread.execute("PRAGMA journal_mode=WAL")
        con_thread.execute("PRAGMA busy_timeout = 3000")
        cursor_thread = con_thread.cursor()
        device_address = 0x12  

        while not self._stop_thread.is_set():
            init_time = time.time() 
            if self.device is not None and self.device.is_connected():
                for tag_name, value in self.SYSTEM_TABLE.items():
                    # Atualiza todos os registradores 
                    if tag_name in self.TAG_MAPPING:
                        tag_type, address = self.TAG_MAPPING[tag_name]
                        query = f"""UPDATE {tag_type} SET value = ?, last_update = ? WHERE device_address = ? AND address = ?"""
                        current_time = datetime.datetime.now(pytz.timezone('America/Sao_Paulo'))
                        # Usa o lock para sincronizar o acesso à conexão
                        with self._db_lock:
                            cursor_thread.execute(query, (value, current_time, device_address, address))
                            con_thread.commit()
                        Logger.debug(f"Atualizado {tag_name} em {tag_type} (endereço {address}) com valor: {value}")


                # Armazena as tags apropridas                    
                for hist_table, tag_key in historical_mapping.items():
                    current_time = datetime.datetime.now(pytz.timezone('America/Sao_Paulo'))
                    query = f"INSERT INTO {hist_table} (tag_id, value, update_time) VALUES (?, ?, ?)"
                    with self._db_lock:
                        cursor_thread.execute(query, (
                            self.TAG_MAPPING[tag_key][1],
                            self.SYSTEM_TABLE[tag_key],
                            current_time
                        ))
                        con_thread.commit()
                    Logger.info(f"Salvo no historico de {hist_table} o valor {self.SYSTEM_TABLE[tag_key]}")

                        
            time.sleep( 0 if (time.time() - init_time) >= self.time_between_save_history else (time.time() - init_time)  )
        con_thread.close()

    def stop_data_thread(self):
        self._stop_thread.set()
        if self._data_thread.is_alive():
            self._data_thread.join()