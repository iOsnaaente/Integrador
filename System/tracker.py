import pymodbus
import sqlite3 
import serial 
import os 

DB_PATH = os.path.dirname( __file__ ) + '/tags.db' 

class Tracker( serial.Serial ):
    
    devices = {}

    def __init__(self, port: str | None = None, baudrate: int = 9600, bytesize: int = 8, parity: str = "N", stopbits: float = 1, timeout: float | None = None, xonxoff: bool = False, rtscts: bool = False, write_timeout: float | None = None, dsrdtr: bool = False, inter_byte_timeout: float | None = None, exclusive: float | None = None, __debug : bool = False) -> None:
        # Open data base 
        self.__debug = __debug
        self.con = sqlite3.connect( DB_PATH )
        self.cursor = self.con.cursor()
        self.create_tags() 
        self.read_devices() 

        # Open serial port
        try:
            super().__init__(port, baudrate, bytesize, parity, stopbits, timeout, xonxoff, rtscts, write_timeout, dsrdtr, inter_byte_timeout, exclusive) 
        except:
            print( 'cant connect serial application')

    def create_tags( self ):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS device (
                id INTEGER PRIMARY KEY,
                address INTEGER,
                name TEXT UNIQUE,
                description TEXT,
                version TEXT,
                status BOOLEAN,
                last_update DATE
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS coil_input (
                id INTEGER PRIMARY KEY,
                device_address INTEGER,
                address INTEGER,
                len INTEGER,
                name TEXT UNIQUE,
                description TEXT,
                read_write TEXT,
                timeout INTEGER,
                periodic INTEGER,
                FOREIGN KEY (device_address) REFERENCES device (address)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS coil_register (
                id INTEGER PRIMARY KEY,
                device_address INTEGER,
                address INTEGER,
                len INTEGER,
                name TEXT UNIQUE,
                description TEXT,
                read_write TEXT,
                timeout INTEGER,
                periodic INTEGER,
                FOREIGN KEY (device_address) REFERENCES device (address)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS holding_register (
                id INTEGER PRIMARY KEY,
                device_address INTEGER,
                address INTEGER,
                len INTEGER,
                name TEXT UNIQUE,
                description TEXT,
                read_write TEXT,
                timeout INTEGER,
                periodic INTEGER,
                FOREIGN KEY (device_address) REFERENCES device (address)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS analog_input (
                id INTEGER PRIMARY KEY,
                device_address INTEGER,
                address INTEGER,
                len INTEGER,
                name TEXT UNIQUE,
                description TEXT,
                read_write TEXT,
                timeout INTEGER,
                periodic INTEGER,
                FOREIGN KEY (device_address) REFERENCES device (address)
            )
        """)
        self.con.commit() 

    def read_devices(self):
        self.devices = {}
        self.cursor.execute("""
            SELECT id, address, name, description, version, status
            FROM device
        """)

        for row in self.cursor.fetchall():
            device_id, device_address, device_name, device_description, device_version, device_status = row

            # Cria um dicionário para representar o dispositivo
            device = {
                'id': device_id,
                'address': device_address,
                'name': device_name,
                'description': device_description,
                'version': device_version,
                'status': "ACTIVE" if device_status else "INACTIVE",
                'tags': []
            }

            # Obtém as tags associadas ao dispositivo
            tags = self.read_tags_by_device(device_address)
            device['tags'] = tags

            # Adiciona o dispositivo ao dicionário de dispositivos
            self.devices[device_address] = device
        return self.devices 
    
    
    def read_tags_by_device(self, device_address):
        tags = []
        self.cursor.execute("""
            SELECT address, name, read_write
            FROM coil_input
            WHERE device_address = ?
            UNION ALL
            SELECT address, name, read_write
            FROM coil_register
            WHERE device_address = ?
            UNION ALL
            SELECT address, name, read_write
            FROM holding_register
            WHERE device_address = ?
            UNION ALL
            SELECT address, name, read_write
            FROM analog_input
            WHERE device_address = ?
        """, (device_address, device_address, device_address, device_address))
        for row in self.cursor.fetchall():
            address, name, read_write = row
            tag = {'address': address, 'name': name, 'read_write': read_write}
            tags.append(tag)
        return tags

    def create_device(self, name: str, address: int, description: str = '', version: str = ''):
        self.cursor.execute(""" SELECT id FROM device WHERE name = ?""", ( name,) )
        if self.cursor.fetchone():
            if self.__debug:
                print(f"Device '{name}' already exists!")
            return None
        else: 
            self.cursor.execute("""
                INSERT INTO device ( name, address, description, version, status )
                VALUES (?, ?, ?, ?, ?)
            """, ( name, address, description, version, False ) ) 
            self.con.commit()
            self.read_devices()


    def create_tag( self, type,  device_address, address, name, read_write, description = '', timeout = 0, periodic = 0 ):
        self.cursor.execute("""SELECT id FROM device WHERE address = ?""", ( device_address , ) ) 
        if not self.cursor.fetchone():
            if self.__debug:
                print(f"Device with address '{device_address}' does not exist!")
            return None
        self.cursor.execute(f"""SELECT id FROM {type} WHERE address = ?""", (address,))
        if self.cursor.fetchone():
            if self.__debug:
                print(f"Tag with address '{address}' already exists in '{type}'!")
            return None
        if type not in  [ 'coil_input', 'coil_register', 'holding_register', 'analog_input' ]:
            if self.__debug:
                print(f"Invalid tag type: '{type}'")
            return None

        self.cursor.execute(
            f"""
                INSERT INTO {type} (device_address, address, name, description, read_write, timeout, periodic)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (device_address, address, name, description, read_write, timeout, periodic)
        )

        self.con.commit()
        self.read_devices()

        if self.__debug:
            print(f"Tag '{name}' created successfully!")



    def read_tag ( self, device_address, type, addr ):
        # Verifica o tipo de tag e a tabela correspondente
        if type not in ['coil_input', 'coil_register', 'holding_register', 'analog_input']:        
            if self.__debug:
                print(f"Invalid tag type: '{type}'")
            return None

        # Consulta a tag no banco de dados
        self.cursor.execute(f"""SELECT * FROM {type} WHERE device_address = ? AND address = ?""", (device_address, addr))
        tag = self.cursor.fetchone()
        if not tag:
            if self.__debug:
                print(f"Tag not found with address '{addr}' and type '{type}'")
            return None

        # Retorna as informações da tag
        tag_info = {
            'id': tag[0],
            'device_address': tag[1],
            'address': tag[2],
            'len': tag[3],
            'name': tag[4],
            'description': tag[5],
            'read_write': tag[6],
            'timeout': tag[7],
            'periodic': tag[8]
        }
        return tag_info


if __name__ == '__main__':
    tracker = Tracker( 'COM15', baudrate = 11560 )
    
    tracker.create_device( 
        name = 'Tracker',
        address = 0x12,
        description = 'Rastreador solar - Integrador \bDesigned by: Bruno G. F. Sampaio',
        version = '1.0.0'
    )

    # Criando uma tag do tipo coil_input para o dispositivo com endereço 1
    # tracker.create_tag('coil_input'         , 0x12, 0x10, '', 'r' , '', 100, 1000 )
    # tracker.create_tag('coil_register'      , 0x12, 0x10, '', 'rw', '', 100, 1000 )
    # tracker.create_tag('holding_register'   , 0x12, 0x05, '', 'rw', '', 50 , 1000 )
    # tracker.create_tag('analog_input'       , 0x12, 0x20, '', 'r' , '', 50 , 1000 )

    # HOLDING REGISTERS
    tracker.create_tag( 'holding_register', 0x12, 0x00, 'HR_STATE'       , 'rw', '', 100, 1000 )
    tracker.create_tag( 'holding_register', 0x12, 0x01, 'HR_AZIMUTE'     , 'rw', '', 100, 1000 )
    tracker.create_tag( 'holding_register', 0x12, 0x03, 'HR_ALTITUDE'    , 'rw', '', 100, 1000 )
    tracker.create_tag( 'holding_register', 0x12, 0x05, 'HR_PV_MOTOR_GIR', 'rw', '', 100, 1000 )
    tracker.create_tag( 'holding_register', 0x12, 0x07, 'HR_PV_MOTOR_ELE', 'rw', '', 100, 1000 )
    tracker.create_tag( 'holding_register', 0x12, 0x09, 'HR_KP_GIR'      , 'rw', '', 100, 1000 )
    tracker.create_tag( 'holding_register', 0x12, 0x0B, 'HR_KI_GIR'      , 'rw', '', 100, 1000 )
    tracker.create_tag( 'holding_register', 0x12, 0x0D, 'HR_KD_GIR'      , 'rw', '', 100, 1000 )
    tracker.create_tag( 'holding_register', 0x12, 0x0F, 'HR_KP_ELE'      , 'rw', '', 100, 1000 )
    tracker.create_tag( 'holding_register', 0x12, 0x11, 'HR_KI_ELE'      , 'rw', '', 100, 1000 )
    tracker.create_tag( 'holding_register', 0x12, 0x13, 'HR_KD_ELE'      , 'rw', '', 100, 1000 )
    tracker.create_tag( 'holding_register', 0x12, 0x15, 'HR_GIR_STEP'    , 'rw', '', 100, 1000 )
    tracker.create_tag( 'holding_register', 0x12, 0x17, 'HR_GIR_USTEP'   , 'rw', '', 100, 1000 )
    tracker.create_tag( 'holding_register', 0x12, 0x19, 'HR_GIR_RATIO'   , 'rw', '', 100, 1000 )
    tracker.create_tag( 'holding_register', 0x12, 0x1B, 'HR_ELE_STEP'    , 'rw', '', 100, 1000 )
    tracker.create_tag( 'holding_register', 0x12, 0x1D, 'HR_ELE_USTEP'   , 'rw', '', 100, 1000 )
    tracker.create_tag( 'holding_register', 0x12, 0x1F, 'HR_ELE_RATIO'   , 'rw', '', 100, 1000 )
    tracker.create_tag( 'holding_register', 0x12, 0x21, 'HR_YEAR'        , 'rw', '', 100, 1000 )
    tracker.create_tag( 'holding_register', 0x12, 0x22, 'HR_MONTH'       , 'rw', '', 100, 1000 )
    tracker.create_tag( 'holding_register', 0x12, 0x23, 'HR_DAY'         , 'rw', '', 100, 1000 )
    tracker.create_tag( 'holding_register', 0x12, 0x24, 'HR_HOUR'        , 'rw', '', 100, 1000 )
    tracker.create_tag( 'holding_register', 0x12, 0x25, 'HR_MINUTE'      , 'rw', '', 100, 1000 )
    tracker.create_tag( 'holding_register', 0x12, 0x26, 'HR_SECOND'      , 'rw', '', 100, 1000 )
    tracker.create_tag( 'holding_register', 0x12, 0x27, 'HR_POS_MGIR'    , 'rw', '', 100, 1000 )
    tracker.create_tag( 'holding_register', 0x12, 0x29, 'HR_POS_MELE'    , 'rw', '', 100, 1000 )
    tracker.create_tag( 'holding_register', 0x12, 0x31, 'HR_LATITUDE'    , 'rw', '', 100, 1000 )
    tracker.create_tag( 'holding_register', 0x12, 0x33, 'HR_LONGITUDE'   , 'rw', '', 100, 1000 )
    tracker.create_tag( 'holding_register', 0x12, 0x35, 'HR_TEMPERATURE' , 'rw', '', 100, 1000 )
    tracker.create_tag( 'holding_register', 0x12, 0x37, 'HR_PRESSURE'    , 'rw', '', 100, 1000 )
    tracker.create_tag( 'holding_register', 0x12, 0x39, 'HR_ALTURA'      , 'rw', '', 100, 1000 )
    # ANALOG INPUTS
    tracker.create_tag( 'analog_input', 0x12, 0x00, 'INPUT_SENS_GIR'     , 'r', '', 100, 1000 )
    tracker.create_tag( 'analog_input', 0x12, 0x02, 'INPUT_SENS_ELE'     , 'r', '', 100, 1000 )
    tracker.create_tag( 'analog_input', 0x12, 0x04, 'INPUT_AZIMUTE'      , 'r', '', 100, 1000 )
    tracker.create_tag( 'analog_input', 0x12, 0x06, 'INPUT_ALTITUDE'     , 'r', '', 100, 1000 )
    tracker.create_tag( 'analog_input', 0x12, 0x07, 'INPUT_YEAR'         , 'r', '', 100, 1000 )
    tracker.create_tag( 'analog_input', 0x12, 0x08, 'INPUT_MONTH'        , 'r', '', 100, 1000 )
    tracker.create_tag( 'analog_input', 0x12, 0x09, 'INPUT_DAY'          , 'r', '', 100, 1000 )
    tracker.create_tag( 'analog_input', 0x12, 0x0A, 'INPUT_HOUR'         , 'r', '', 100, 1000 )
    tracker.create_tag( 'analog_input', 0x12, 0x0B, 'INPUT_MINUTE'       , 'r', '', 100, 1000 )
    tracker.create_tag( 'analog_input', 0x12, 0x0C, 'INPUT_SECOND'       , 'r', '', 100, 1000 )
    tracker.create_tag( 'analog_input', 0x12, 0x0D, 'INPUT_SENS_CONF_GIR', 'r', '', 100, 1000 )
    tracker.create_tag( 'analog_input', 0x12, 0x0F, 'INPUT_SENS_CONF_ELE', 'r', '', 100, 1000 )
    # COIL REGISTERS
    tracker.create_tag( 'coil_register', 0x12, 0X00, 'COIL_POWER'         , 'wr', '', 100, 1000 )
    tracker.create_tag( 'coil_register', 0x12, 0x01, 'COIL_LED1_BLUE'     , 'wr', '', 100, 1000 )
    tracker.create_tag( 'coil_register', 0x12, 0x02, 'COIL_LED1_RED'      , 'wr', '', 100, 1000 )
    tracker.create_tag( 'coil_register', 0x12, 0x03, 'COIL_LED2_BLUE'     , 'wr', '', 100, 1000 )
    tracker.create_tag( 'coil_register', 0x12, 0x04, 'COIL_LED2_RED'      , 'wr', '', 100, 1000 )
    tracker.create_tag( 'coil_register', 0x12, 0x05, 'COIL_PRINT'         , 'wr', '', 100, 1000 )
    tracker.create_tag( 'coil_register', 0x12, 0x06, 'COIL_DATETIME_SYNC' , 'wr', '', 100, 1000 )
    tracker.create_tag( 'coil_register', 0x12, 0x07, 'COIL_FORCE_DATETIME', 'wr', '', 100, 1000 )
    # COIL INPUTS 
    tracker.create_tag( 'coil_input', 0x12, 0x00, 'DISCRETE_POWERC_L'   , 'r', '', 100, 1000 )
    tracker.create_tag( 'coil_input', 0x12, 0x01, 'DISCRETE_WAITING'    , 'r', '', 100, 1000 )
    tracker.create_tag( 'coil_input', 0x12, 0x02, 'DISCRETE_TIME_STATUS', 'r', '', 100, 1000 )
    tracker.create_tag( 'coil_input', 0x12, 0x03, 'DISCRETE_LEVER1_L'   , 'r', '', 100, 1000 )
    tracker.create_tag( 'coil_input', 0x12, 0x04, 'DISCRETE_LEVER1_R'   , 'r', '', 100, 1000 )
    tracker.create_tag( 'coil_input', 0x12, 0x05, 'DISCRETE_LEVER2_L'   , 'r', '', 100, 1000 )
    tracker.create_tag( 'coil_input', 0x12, 0x06, 'DISCRETE_LEVER2_R'   , 'r', '', 100, 1000 )
    
    print( tracker.read_tag( 0x12, 'holding_register', 0x31) )
    print( tracker.read_tag( 0x12, 'analog_input', 0x07) )
    print( tracker.read_tag( 0x12, 'coil_register', 0x05) )
    print( tracker.read_tag( 0x12, 'coil_input', 0x03) )