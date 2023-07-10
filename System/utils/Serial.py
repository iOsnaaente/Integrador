from typing import Union
import minimalmodbus 
import struct


class ModbusRTU:
    
    connected: bool
    port: str 
    baudrate: int 
    parity: str 
    stop_bits: int 
    byte_size: int 
    timeout: int 


    def __init__(self, slave : int, port: str,  baudrate: int , parity: str = 'N', stop_bits: int = 1, byte_size: int = 8, timeout: int = 1, debug: bool = False, **kwargs):
        self.port = port
        self.baudrate = baudrate
        self.parity = parity
        self.stop_bits = stop_bits
        self.byte_size = byte_size
        self.timeout = timeout
        self.connected = False
        self.__debug = debug
        # Try to open serial port
        try:
            self.client = minimalmodbus.Instrument(port=port, slaveaddress=slave, mode=minimalmodbus.MODE_RTU, debug=debug)
            self.client.serial.baudrate = baudrate 
            self.client.serial.timeout = timeout
            self.client.serial.bytesize = byte_size 
            self.client.serial.parity = parity 
            self.client.serial.stopbits = stop_bits  
            self.connected = True 
            if debug:
                print('Modbus connection OK')
        except Exception as err:
            self.client = None 
            if debug:
                print('Serial Modbus Exception: ', err )
                
    def update_connection(self, port: str, baudrate: int , parity: str = 'N', stop_bits: int = 1, byte_size: int = 8, timeout: int = 1, __debug: bool=False, **kwargs):
        back = self.client
        try:
            # Try to connect to the modbus 
            self.client = minimalmodbus.Instrument(port=port, slaveaddress=slave, mode=minimalmodbus.MODE_RTU, debug=debug)
            self.client.serial.baudrate = baudrate 
            self.client.serial.timeout = timeout
            self.client.serial.bytesize = byte_size 
            self.client.serial.parity = parity 
            self.client.serial.stopbits = stop_bits  
            # Update the values 
            self.port = port
            self.baudrate = baudrate
            self.parity = parity
            self.stop_bits = stop_bits
            self.byte_size = byte_size
            self.timeout = timeout
            return True 
        except Exception as err:
            self.client = back 
            if __debug:
                print( f'cant connect serial application. Error: {err}')
            return False 

    def read_register( self, register_type: str, address: int, length: int, var_type: str ) -> None | list[ int | float ]:
        try:
            # Verifica se o cliente esta conectado 
            if self.client is None:
                if self.__debug:
                    print("Conexão Modbus não estabelecida.")       
                return None      
            # Verifica o tipo de registro e a tabela correspondente
            if register_type == 'analog_input':
                fc = 0x04 
            elif register_type == 'holding_register':
                fc = 0x03
            else:
                if self.__debug:
                    print(f"Tipo de registro inválido: '{register_type}'")                
                return None 
            # Leitura dos input registers
            response = self.client.read_registers(address, length, functioncode = fc )
            if response is None:
                if self.__debug:
                    print("Erro ao ler os registradores do dispositivo Modbus.")
                return None
            else:
                # Realize o tratamento adequado para cada tipo de dado
                values = response
                if var_type == 'FLOAT':
                    float_values = []
                    for i in range(0, len(values), 2):
                        float_values.append(struct.unpack('>f', struct.pack('>HH', values[i], values[i + 1]))[0])
                    return float_values
                else:
                    int_values = []
                    for i in range(len(values)):
                        int_values.append(values[i])
                    return int_values
        except Exception as err:
            if self.__debug:
                print(f"Erro ao ler registros do dispositivo Modbus. Erro: {err}")
            return None
    
    def read_coils(self, register_type: str, address: int, length: int ):
        try:
            # Verifica se o cliente está conectado
            if self.client is None:
                if self.__debug:
                    print("Conexão Modbus não estabelecida.")
                return None
            # Verifica o tipo de registro e a tabela correspondente
            if register_type == 'coil_register':
                fc = 0x01
            elif register_type == 'coil_input':
                fc = 0x02
            else:
                if self.__debug:
                    print(f"Tipo de registro inválido: '{register_type}'")                
                return None 
            # Consulta as bobinas no dispositivo Modbus
            response = self.client.read_bits( address, length, functioncode = fc )
            if response is None:
                if self.__debug:
                    print("Erro ao ler as bobinas do dispositivo Modbus.")
                return None
            else: 
                # Obtém os valores lidos das bobinas
                return response
        except Exception as err:
            if self.__debug:
                print(f"Erro ao ler as bobinas do dispositivo Modbus. Erro: {err}")
            return None

    def write_registers(self, address: int, values: Union[int, float, list[Union[int, float]]] ):
        try:
            # Verifica se o cliente está conectado
            if self.client is None:
                if self.__debug:
                    print("Conexão Modbus não estabelecida.")
                return False
            # Verifica o tipo de cada dado e realiza o tratamento adequado
            if isinstance(values, int):            
                response = self.client.write_register(address, values, functioncode = 0x06 )
            elif isinstance(values, float ):
                response = self.client.write_float( address, values, number_of_registers = 2 )
            elif isinstance(values, list):
                addr_count = 0x00
                regs = []
                for value in values:
                    if isinstance(value, int):
                        regs.append(value)
                        addr_count += 1 
                    if isinstance(value, float):
                        regs.extend(struct.unpack('>HH', struct.pack('>f', value)))
                        addr_count += 2 
                response = self.client.write_registers( address, regs )
            else: 
                if self.__debug:
                    print("Erro de registrador Modbus.")
                return False
            if response is None:
                if self.__debug:
                    print("Erro ao ler as bobinas do dispositivo Modbus.")
                return None
            else:
                return True 
        except Exception as err:
            if self.__debug:
                print(f"Erro ao escrever nos registradores do dispositivo Modbus. Erro: {err}")
            return False

    def write_coils(self, address: int, values: Union[bool, list[bool]]) -> bool:
        try:
            # Verifica se o cliente está conectado
            if self.client is None:
                if self.__debug:
                    print("Conexão Modbus não estabelecida.")
                return False
            # Escreve na bobina do dispositivo Modbus
            if isinstance(values, bool):
                response = self.client.write_bit(address, values, functioncode = 0x05 )
            elif isinstance(values, list) and all(isinstance(value, bool) for value in values):
                response = self.client.write_bits(address, values ) # Funtion_Code = 15 
            else:
                if self.__debug:
                    print('Tipo de registrador incompatível.')
                return False

            if response is None:
                if self.__debug:
                    print("Erro ao escrever nas bobinas do dispositivo Modbus.")
                return False
            else:
                return True
        except Exception as err:
            if self.__debug:
                print(f"Erro ao escrever nas bobinas do dispositivo Modbus. Erro: {err}")
            return False


if __name__ == '__main__':
    # Teste da classe ModbusRTU
    modbus = ModbusRTU( 0x12, 'COM5', 19200, debug = True  )
    
    # print( modbus.write_registers( 0x00, [ i/10 for i in range(10)] ))
    print(modbus.write_coils( 0x00, [True, True, False, False, True ]) )
     
    # print( modbus.read_register( 'analog_input', 0x00, 10, var_type = 'INT' )  ) 
    # print( modbus.read_register( 'holding_register', 0x00, 10, var_type = 'INT' )  ) 
    print( modbus.read_coils( 'coil_input', 0x00, 10 )  ) 
    print( modbus.read_coils( 'coil_register', 0x00, 10 )  ) 

    # print( modbus.read_register( 'analog_input', 0x00,  10, var_type = 'INT'   ) )
