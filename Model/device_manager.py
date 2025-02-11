from System.device_base import DeviceBase 
from System.device_RTU import Device_RTU
from System.device_TCP import Device_TCP 
from kivy.logger import Logger 

"""
    DeviceManager é responsável por gerenciar a conexão com o dispositivo 
    Serial ou outras abordagens como Modbus TCP. Ele instancia a classe 
    Device (definida em tracker.py) e oferece métodos para conectar e 
    desconectar o hardware.
    
    Hierarquia:
    1. 'Interface'   = DeviceBase
    2. 'Modulo'      = Device_TCP ou Device_RTU
    3. 'Controlador' = DeviceManager 
"""
class DeviceManager:
    # Valores do sistema 
    init_registers: bool = False 
    slave: int
    port: str 

    def __init__(self, debug: bool = False):
        self.device = None
        self.debug = debug


    """
        Tenta conectar com o dispositivo Serial e verifica se há uma conexão
    """
    def connect_device( self, 
        slave: int, port: str, baudrate: int, timeout: int = 1, 
        parity: str = 'E', stop_bits: int = 1, byte_size: int = 8, 
        init_registers: bool = False 
    ) -> bool:
        try:
            # Converte baudrate e timeout para inteiros 
            baudrate = int(baudrate)
            timeout = int(timeout)
            # Instancia o dispositivo com os parâmetros fornecidos.
            self.device = Device_RTU( 
                slave, port, baudrate, timeout = timeout, 
                parity = parity, stop_bits = stop_bits, byte_size = byte_size, 
                init_registers = init_registers, debug = self.debug )
            
            # Verifica se a conexão foi estabelecida com sucesso usando o método is_connected.
            is_connected = self.device.is_connected()
            if self.debug:
                if is_connected:
                    Logger.info("DeviceManager: Conexão estabelecida com sucesso.")
                else:
                    Logger.info("DeviceManager: Falha na conexão com o dispositivo.")
            return is_connected
        except Exception as err:
            if self.debug:
                Logger.warning( f"DeviceManager: Erro ao tentar conectar - {err}" )
            return False

    """
        Fecha a conexão com o dispositivo, se houver uma conexão ativa.
    """
    def disconnect(self) -> None:
        try:
            if self.device is not None:
                self.device.close()
                if self.debug:
                    Logger.info("DeviceManager: Dispositivo desconectado com sucesso.")
                self.device = None
        except Exception as e:
            if self.debug:
                Logger.warning( f"DeviceManager: Erro ao desconectar o dispositivo - {e}" )
