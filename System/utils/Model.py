from kivy.logger import Logger
import datetime
import sqlite3 
import pytz 

class ModbusDatabase: 
    """
        Implementa as funções básicas para se manipular as tags em um banco de dados
        Os atributos são: 
            >>> devices = {} 
        Os princiapais métodos são::
            - Manipulação dos devices:
                >>> create_device() -> bool
                >>> read_devices() -> dict
                >>> get_device() -> dict
            - Manipulação das tags: 
                >>> create_tag() -> bool
                >>> read_tag() -> dict
                >>> update_tag() -> bool
    """
    devices = {}

    def __init__( self, DB_PATH : str, init_registers : bool = False, debug : bool = False, **kwargs ):    
        self.db_path = DB_PATH 
        self.__debug = debug
        try: 
            self.con = sqlite3.connect( DB_PATH )
            self.cursor = self.con.cursor()
            self.create_db() 
            if init_registers:
                self.initialize_tags()
            self.read_devices() 
            if self.__debug:
                Logger.info( 'DB Modbus inicializado com sucesso.' )
        except Exception as err: 
            if self.__debug:
                Logger.warning( f'DB Exception: {err}' )

    def create_db( self ) -> None:
        # self.con.execute( "PRAGMA foreign_keys = ON")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS device (
                id INTEGER PRIMARY KEY,
                address INTEGER UNIQUE,
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
                type TEXT,
                value RAW,
                last_update TEXT,
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
                type TEXT,
                value INTEGER,
                last_update TEXT,
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
                type TEXT,
                value RAW,
                last_update TEXT,
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
                type TEXT,
                value RAW,
                last_update TEXT,
                name TEXT UNIQUE,
                description TEXT,
                read_write TEXT,
                timeout INTEGER,
                periodic INTEGER,
                FOREIGN KEY (device_address) REFERENCES device (address)
            )
        """)

        # Salva os dados de sensor de giro 
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS history_sensor_gir (
                id INTEGER PRIMARY KEY,
                tag_id INTEGER,
                value RAW,
                update_time TEXT,
                FOREIGN KEY( tag_id ) REFERENCES analog_input( id )
            );
        """)

        # Salva os dados de sensor de elevação 
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS history_sensor_ele (
                id INTEGER PRIMARY KEY,
                tag_id INTEGER,
                value RAW,
                update_time TEXT,
                FOREIGN KEY( tag_id ) REFERENCES analog_input( id )
            );
        """)

        # Salva os dados de setpoint de azimute  
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS history_azimute (
                id INTEGER PRIMARY KEY,
                tag_id INTEGER,
                value RAW,
                update_time TEXT,
                FOREIGN KEY( tag_id ) REFERENCES analog_input( id )
            );
        """)

        # Salva os dados de setpoint de zenite  
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS history_zenite (
                id INTEGER PRIMARY KEY,
                tag_id INTEGER,
                value RAW,
                update_time TEXT,
                FOREIGN KEY( tag_id ) REFERENCES analog_input( id )
            );
        """)

        # Salva os dados de setpoint de geração  
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS history_generation (
                id INTEGER PRIMARY KEY,
                tag_id INTEGER,
                value RAW,
                update_time TEXT,
                FOREIGN KEY( tag_id ) REFERENCES analog_input( id )
            );
        """)                
        self.con.commit() 

    #
    #   DEVICE STTINGS
    #
    def read_devices( self ) -> dict:
        self.devices = {}
        self.cursor.execute(""" SELECT id, address, name, description, version, status FROM device """ ) 
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
    

    def read_tags_by_device(self, device_address : int ) -> list:
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


    def create_device(self, name: str, address: int, description: str = '', version: str = '') -> None:
        self.cursor.execute(""" SELECT id FROM device WHERE name = ?""", ( name,) )
        if self.cursor.fetchone():
            if self.__debug:
                Logger.warning(f"Device '{name}' already exists!")
            return None
        else: 
            self.cursor.execute("""
                INSERT INTO device ( name, address, description, version, status )
                VALUES (?, ?, ?, ?, ?)
            """, ( name, address, description, version, False ) ) 
            self.con.commit()
            self.read_devices()
        return None 


    def get_device(self, name: str, address: int) -> dict:
        devices = self.read_devices()
        for _, device_info in devices.items():
            if device_info['name'] == name and device_info['address'] == address:
                return device_info
        if self.__debug:
            Logger.warning(f"Device '{name}' with address '{address}' does not exist!")
        return dict({})


    #
    #   TAGS STTINGS
    #
    def create_tag( self, tag_type : str,  device_address : int , address : int, length : int, var_type : str, name : str, read_write : str, description : str = '', timeout : int = 0, periodic : int = 0 ) -> None:
        self.cursor.execute("""SELECT id FROM device WHERE address = ?""", ( device_address , ) ) 
        if not self.cursor.fetchone():
            if self.__debug:
                Logger.warning(f"Device with address '{device_address}' does not exist!")
            return None
        self.cursor.execute(f"""SELECT id FROM {tag_type} WHERE address = ?""", (address,))
        if self.cursor.fetchone():
            if self.__debug:
                Logger.warning(f"Tag with address '{address}' already exists in '{tag_type}'!")
            return None
        if tag_type not in  [ 'coil_input', 'coil_register', 'holding_register', 'analog_input' ]:
            if self.__debug:
                Logger.warning(f"Invalid tag type: '{tag_type}'")
            return None

        self.cursor.execute(
            f"""
                INSERT INTO {tag_type} (device_address, address, len, type, value, last_update, name, description, read_write, timeout, periodic)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (device_address, address, length, var_type, None, datetime.datetime.now(pytz.timezone('America/Sao_Paulo')), name, description, read_write, timeout, periodic)
        )
        self.con.commit()
        self.read_devices()
        if self.__debug:
            Logger.info(f"Tag '{name}' created successfully!")
        return 


    def read_tag ( self, device_address : int, tag_type : str, addr : int ) -> dict:
        # Verifica o tipo de tag e a tabela correspondente
        if tag_type not in ['coil_input', 'coil_register', 'holding_register', 'analog_input']:        
            if self.__debug:
                Logger.warning(f"Invalid tag type: '{tag_type}'")
            return dict({})

        # Consulta a tag no banco de dados
        self.cursor.execute(f"""SELECT * FROM {tag_type} WHERE device_address = ? AND address = ?""", (device_address, addr))
        tag = self.cursor.fetchone()
        if not tag:
            if self.__debug:
                Logger.warning(f"Tag not found with address '{addr}' and type '{tag_type}'")
            return dict({})

        # Retorna as informações da tag
        tag_info = {
            'id'            : tag[ 0],
            'device_address': tag[ 1],
            'address'       : tag[ 2],
            'len'           : tag[ 3],
            'type'          : tag[ 4],
            'value'         : tag[ 5],
            'last_update'   : tag[ 6],
            'name'          : tag[ 7],
            'description'   : tag[ 8],
            'read_write'    : tag[ 9],
            'timeout'       : tag[10],
            'periodic'      : tag[11]
        }
        return tag_info


    def read_tags(self, device_address: int, tag_type: str, start_address: int, count: int) -> list[dict]:
        # Verifica o tipo de tag e a tabela correspondente
        if tag_type not in ['coil_input', 'coil_register', 'holding_register', 'analog_input']:
            if self.__debug:
                Logger.warning(f"Invalid tag type: '{tag_type}'")
            return []
        
        # Consulta as tags no banco de dados
        query = f"""SELECT * FROM {tag_type} WHERE device_address = ? AND address BETWEEN ? AND ?"""
        params = (device_address, start_address, start_address + count - 1)
        self.cursor.execute(query, params)
        tags = self.cursor.fetchall()
        # Retorna as informações das tags
        tag_list = []
        for tag in tags:
            tag_info = {
                'id': tag[0],
                'device_address': tag[1],
                'address': tag[2],
                'len': tag[3],
                'type': tag[4],
                'value': tag[5],
                'last_update': tag[6],
                'name': tag[7],
                'description': tag[8],
                'read_write': tag[9],
                'timeout': tag[10],
                'periodic': tag[11]
            }
            tag_list.append(tag_info)

        return tag_list


    def write_tag( self, device_address : int, tag_type : str, address : int, new_value ) -> bool:
        # Verifica o tipo de tag e a tabela correspondente
        if tag_type not in ['coil_input', 'coil_register', 'holding_register', 'analog_input']:
            if self.__debug:
                Logger.warning(f"Invalid tag type: '{tag_type}'")
            return False
        else: 
            # Consulta a tag no banco de dados
            self.cursor.execute(f"""SELECT id FROM {tag_type} WHERE device_address = ? AND address = ?""", (device_address, address) )
            tag_id = self.cursor.fetchone()
            if not tag_id:
                if self.__debug:
                    Logger.warning( f"Tag not found with address '{address}' and type '{tag_type}'")
                return False
            else: 
                # Atualiza as informações da tag no banco de dados
                query = f""" UPDATE {tag_type} SET value = ?, last_update = ? WHERE id = ? """
                current_time = datetime.datetime.now(pytz.timezone('America/Sao_Paulo'))

                self.cursor.execute(query, (new_value, current_time, tag_id[0] ) )
                self.con.commit()

                if self.__debug:
                    Logger.warning(f"Tag with address '{address}' and type '{tag_type}' updated successfully!")
                return True

    """
    Retorna os registros da tabela especificada cujo campo update_time está entre start_date e end_date.
    :param table_name: Nome da tabela onde buscar (ex: 'history_sensor_gir', 'history_sensor_ele', etc.)
    :param start_date: Data inicial (datetime)
    :param end_date: Data final (datetime)
    :return: Lista de tuplas com os registros encontrados.
    """
    def read_data_by_date_range(self, table_name: str, start_date: datetime.datetime, end_date: datetime.datetime) -> list:
        # Formata as datas para string no formato padrão ISO (ou no formato que você esteja utilizando)
        start_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
        end_str = end_date.strftime("%Y-%m-%d %H:%M:%S")
        query = f"""
            SELECT *
            FROM {table_name}
            WHERE update_time BETWEEN ? AND ?
        """
        self.cursor.execute(query, (start_str, end_str))
        results = self.cursor.fetchall()
        return results

    # type,  device_address, address, length, var_type,  name, read_write, description
    def initialize_tags( self ) -> None:
        # Cria o sistema caso ele não exista
        self.create_device( name = 'Tracker', address = 0x12, description = 'Sistema de rastreamento solar', version = '2.2.0' )
        # HOLDING REGISTERS
        self.create_tag( 'holding_register', 0x12, 0x00, 2, 'FLOAT' , 'HR_PV_GIR'       , 'rw', '', 100, 1000 )
        self.create_tag( 'holding_register', 0x12, 0x02, 2, 'FLOAT' , 'HR_KP_GIR'       , 'rw', '', 100, 1000 )
        self.create_tag( 'holding_register', 0x12, 0x04, 2, 'FLOAT' , 'HR_KI_GIR'       , 'rw', '', 100, 1000 )
        self.create_tag( 'holding_register', 0x12, 0x06, 2, 'FLOAT' , 'HR_KD_GIR'       , 'rw', '', 100, 1000 )
        self.create_tag( 'holding_register', 0x12, 0x08, 2, 'FLOAT' , 'HR_AZIMUTE'      , 'rw', '', 100, 1000 )
        self.create_tag( 'holding_register', 0x12, 0x0A, 2, 'FLOAT' , 'HR_PV_ELE'       , 'rw', '', 100, 1000 )
        self.create_tag( 'holding_register', 0x12, 0x0C, 2, 'FLOAT' , 'HR_KP_ELE'       , 'rw', '', 100, 1000 )
        self.create_tag( 'holding_register', 0x12, 0x0E, 2, 'FLOAT' , 'HR_KI_ELE'       , 'rw', '', 100, 1000 )
        self.create_tag( 'holding_register', 0x12, 0x10, 2, 'FLOAT' , 'HR_KD_ELE'       , 'rw', '', 100, 1000 )
        self.create_tag( 'holding_register', 0x12, 0x12, 2, 'FLOAT' , 'HR_ALTITUDE'     , 'rw', '', 100, 1000 )
        self.create_tag( 'holding_register', 0x12, 0x14, 2, 'FLOAT' , 'HR_LATITUDE'     , 'rw', '', 100, 1000 )
        self.create_tag( 'holding_register', 0x12, 0x16, 2, 'FLOAT' , 'HR_LONGITUDE'    , 'rw', '', 100, 1000 )
        self.create_tag( 'holding_register', 0x12, 0x18, 1, 'INT'   , 'HR_STATE'        , 'rw', '', 100, 1000 )
        self.create_tag( 'holding_register', 0x12, 0x19, 1, 'INT'   , 'HR_YEAR'         , 'rw', '', 100, 1000 )
        self.create_tag( 'holding_register', 0x12, 0x1A, 1, 'INT'   , 'HR_MONTH'        , 'rw', '', 100, 1000 )
        self.create_tag( 'holding_register', 0x12, 0x1B, 1, 'INT'   , 'HR_DAY'          , 'rw', '', 100, 1000 )
        self.create_tag( 'holding_register', 0x12, 0x1C, 1, 'INT'   , 'HR_HOUR'         , 'rw', '', 100, 1000 )
        self.create_tag( 'holding_register', 0x12, 0x1D, 1, 'INT'   , 'HR_MINUTE'       , 'rw', '', 100, 1000 )
        self.create_tag( 'holding_register', 0x12, 0x1E, 1, 'INT'   , 'HR_SECOND'       , 'rw', '', 100, 1000 )
        # ANALOG INPUTS
        self.create_tag( 'analog_input', 0x12, 0x00, 2, 'FLOAT', 'INPUT_POS_GIR'        , 'r', '', 100, 1000 )
        self.create_tag( 'analog_input', 0x12, 0x02, 2, 'FLOAT', 'INPUT_POS_ELE'        , 'r', '', 100, 1000 )
        self.create_tag( 'analog_input', 0x12, 0x04, 2, 'FLOAT', 'INPUT_AZIMUTE'        , 'r', '', 100, 1000 )
        self.create_tag( 'analog_input', 0x12, 0x06, 2, 'FLOAT', 'INPUT_ZENITE'         , 'r', '', 100, 1000 )
        self.create_tag( 'analog_input', 0x12, 0x08, 2, 'FLOAT', 'INPUT_GENERATION'     , 'r', '', 100, 1000 )
        self.create_tag( 'analog_input', 0x12, 0x0A, 2, 'FLOAT', 'INPUT_TEMP'           , 'r', '', 100, 1000 )
        self.create_tag( 'analog_input', 0x12, 0x0C, 2, 'FLOAT', 'INPUT_PRESURE'        , 'r', '', 100, 1000 )
        self.create_tag( 'analog_input', 0x12, 0x0E, 2, 'FLOAT', 'INPUT_SENS_CONF_GIR'  , 'r', '', 100, 1000 )
        self.create_tag( 'analog_input', 0x12, 0x10, 2, 'FLOAT', 'INPUT_SENS_CONF_ELE'  , 'r', '', 100, 1000 )
        self.create_tag( 'analog_input', 0x12, 0x12, 1, 'INT'  , 'INPUT_YEAR'           , 'r', '', 100, 1000 )
        self.create_tag( 'analog_input', 0x12, 0x13, 1, 'INT'  , 'INPUT_MONTH'          , 'r', '', 100, 1000 )
        self.create_tag( 'analog_input', 0x12, 0x14, 1, 'INT'  , 'INPUT_DAY'            , 'r', '', 100, 1000 )
        self.create_tag( 'analog_input', 0x12, 0x15, 1, 'INT'  , 'INPUT_HOUR'           , 'r', '', 100, 1000 )
        self.create_tag( 'analog_input', 0x12, 0x16, 1, 'INT'  , 'INPUT_MINUTE'         , 'r', '', 100, 1000 )
        self.create_tag( 'analog_input', 0x12, 0x17, 1, 'INT'  , 'INPUT_SECOND'         , 'r', '', 100, 1000 )
        # COIL REGISTERS
        self.create_tag( 'coil_register', 0x12, 0X00, 1, 'BIT', 'COIL_POWER'      , 'wr', '', 100, 1000 )
        self.create_tag( 'coil_register', 0x12, 0x01, 1, 'BIT', 'COIL_LED'        , 'wr', '', 100, 1000 )
        self.create_tag( 'coil_register', 0x12, 0x02, 1, 'BIT', 'COIL_M_GIR'      , 'wr', '', 100, 1000 )
        self.create_tag( 'coil_register', 0x12, 0x03, 1, 'BIT', 'COIL_M_ELE'      , 'wr', '', 100, 1000 )
        self.create_tag( 'coil_register', 0x12, 0x04, 1, 'BIT', 'COIL_LEDR'       , 'wr', '', 100, 1000 )
        self.create_tag( 'coil_register', 0x12, 0x05, 1, 'BIT', 'COIL_LEDG'       , 'wr', '', 100, 1000 )
        self.create_tag( 'coil_register', 0x12, 0x06, 1, 'BIT', 'COIL_LEDB'       , 'wr', '', 100, 1000 )
        self.create_tag( 'coil_register', 0x12, 0x07, 1, 'BIT', 'COIL_SYNC_DATE'  , 'wr', '', 100, 1000 )
        # COIL INPUTS 
        self.create_tag( 'coil_input', 0x12, 0x00, 1, 'BIT', 'DISCRETE_FAIL'       , 'r', '', 100, 1000 )
        self.create_tag( 'coil_input', 0x12, 0x01, 1, 'BIT', 'DISCRETE_POWER'      , 'r', '', 100, 1000 )
        self.create_tag( 'coil_input', 0x12, 0x02, 1, 'BIT', 'DISCRETE_TIME'       , 'r', '', 100, 1000 )
        self.create_tag( 'coil_input', 0x12, 0x03, 1, 'BIT', 'DISCRETE_GPS'        , 'r', '', 100, 1000 )
        self.create_tag( 'coil_input', 0x12, 0x04, 1, 'BIT', 'DISCRETE_CONNECTED'  , 'r', '', 100, 1000 )