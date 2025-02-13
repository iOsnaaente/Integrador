from System.device_base import DB_PATH 
from System.utils.Model import ModbusDatabase 
from System.device_RTU import Device_RTU
from System.device_TCP import Device_TCP 
from kivy.logger import Logger 


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

    # Valores do sistema 
    init_registers: bool = False 
    database: ModbusDatabase
    slave: int
    port: str 


    """ Inicia o Banco de dados """
    def __init__(self, debug: bool = False ):
        self.database = ModbusDatabase( DB_PATH = DB_PATH, init_registers = True, debug = debug )
        self.device = None
        self.state = self.IDLE 
        self._debug = debug        
    

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
