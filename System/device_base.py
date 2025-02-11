""" 
    Base Device armazena as implementações mínimas para um 
    Device Modbus RTU , TCP ou qualquer outro método Modbus 
"""

from System.utils.Model import ModbusDatabase 
from System.Tags import * 

import os 

DB_PATH = os.path.join(os.path.dirname(__file__).removesuffix('System'), 'Model', 'db', 'tags.db')

class DeviceBase:
    # Banco de dados 
    database: ModbusDatabase
    write_flag: bool = False 
    scan_on: bool = True
    err_count: int 

    """ Retorna se o dispositivo está conectado."""
    def is_connected(self) -> bool:
        raise NotImplementedError

    """ Abre a conexão com o dispositivo."""
    def open(self):
        raise NotImplementedError

    """ Fecha a conexão com o dispositivo."""
    def close(self):
        raise NotImplementedError
    
    """ Lê UMA bonina do dispositivo """
    def read_coil(self, register_type: str, address: int, count: int = 1, DB : ModbusDatabase | None = None  ) -> list [bool] | bool | None :
        raise NotImplementedError

    """ Lê UM registro do dispositivo """
    def read_register(self, register_type: str, address: int, last_addres: int = 1, DB : ModbusDatabase | None = None  ) -> list[ int | float ] | bool | None:
        raise NotImplementedError

    """ Escreve em N bonina do dispositivo """
    def write_coils(self, address: int, value: bool | list[bool] ) -> bool | None:
        raise NotImplementedError

    """ Escreve em UM registrador do dispositivo """
    def write_register(self, address: int, value: int | float ) -> bool | None:
        raise NotImplementedError

    """ Lê registradores definidor em 'register_type' e 'num_registers' do dispositivo """
    def read_modbus( self, register_type: str, address: int, num_regs: int = 1, reg_type: str = 'INT'  ) -> list[ int | float | bool ] | bool | None:
        raise NotImplementedError

    """ Inicia uma rotina de leitura automática do Dispositivo """
    def auto_scan_routine( self ):
        raise NotImplementedError