# Imports do Kivy e systema 
from Model.base_model import BaseScreenModel
from datetime   import datetime 
from kivy.clock import Clock

# Import de Libs Root 
from libs.Sun           import SunPosition 
from System.utils.Model import ModbusDatabase 
from Model.db.database  import Database
from System.tracker     import Device 
from System.Tags        import * 

# Import de Libs de Gerenciamento e config. 
from Model.server_manager import ServerManager
from Model.system_manager import SystemManager
from Model.user_manager   import UserManager 
from Model.params_config  import * 

import threading
import os 


""" 
    Classe de gerenciamento de acesso a dados do sistema
    - O Model deve armazenar as informações do sistema não 
    só de forma segura mas tambémd e forma que seja possível 
    se escalonar o sistema de forma modular 
    - Tentei na medida do possível     
"""
class SystemModel( BaseScreenModel ):
    # Imagens presentes em na tela de login  
    sunrise_image       = IMAGE_PATHS[ "sunrise_image"      ]
    connectivity_icon   = IMAGE_PATHS[ "connectivity_icon"  ]
    green_power_icon    = IMAGE_PATHS[ "green_power_icon"   ]
    security_icon       = IMAGE_PATHS[ "security_icon"      ]
    solar_icon          = IMAGE_PATHS[ "solar_icon"         ]
    smart_sun           = IMAGE_PATHS[ "smart_sun"          ]
    map_icon            = IMAGE_PATHS[ "map_icon"           ]
    # Imagens do sistema 
    painel_solar        = IMAGE_PATHS[ "painel_solar"       ]
    motor_vertical      = IMAGE_PATHS[ "motor_vertical"     ]
    motor_horizontal    = IMAGE_PATHS[ "motor_horizontal"   ]
    sensor_motores      = IMAGE_PATHS[ "sensor_motores"     ]
    background          = IMAGE_PATHS[ "background"         ]

    # Latitude e Longitude do Painel 
    SunData : SunPosition = SunPosition( 
        latitude = -29.71332542661317, 
        longitude = -53.71766381408064, 
        altitude = 300 
    )    

    # Gerenciadores de acesso 
    database_manager: Database 
    server_manager: ServerManager 
    system_manager: SystemManager 
    user_manager: UserManager 

    # Parametros do modelo 
    _connected: bool = False
    _debug: bool = True 
    _datetime: str = ''
    _date: str = ''
    _time: str = ''

    _db_locker: threading.Lock 


    def __init__( self, _debug: bool = False  ) -> None:
        super().__init__()
        self.database_manager = Database( )
        self.db_lock = threading.Lock()
        
        self.server_manager = ServerManager( debug = _debug )         
        self.system_manager = SystemManager( self.db_lock, debug = _debug )
        self.user_manager = UserManager( debug = _debug )
        self._debug = _debug

        # Outras propriedades de controle
        self._date = '00:00:00 01/01/2001'
        self._connected = False        


    # ---------------------------------------------------------------#
    #                   Properties Definitions                       #
    # ---------------------------------------------------------------#      
    @property 
    def database( self ) -> Database:
        return self.database_manager
    @property 
    def server( self ) -> ServerManager | None:
        return self.server_manager
    
    # @property 
    # def user( self ) -> UserManager:
    #     return self.user_manager

    @property
    def system_database( self ) -> ModbusDatabase:
        return self.system_manager.database
    
    @property 
    def system( self ) -> SystemManager | None:
        return self.system_manager
    @property
    def SYSTEM_TABLE( self ) -> dict:
        return self.system_manager.SYSTEM_TABLE
    @property
    def system_state( self ) -> SystemManager:
        return self.system_manager
    @property
    def datetime( self ) -> str: 
        return self._datetime 
    @property 
    def time(self) -> str:
        return self._date
    @property
    def date(self) -> str:
        return self._date
    @property
    def connected(self) -> bool:
        return self._connected    
    @connected.setter
    def connected(self, value : bool ) -> None:
        self._connected = value 
    @property 
    def checkbox_keep_login_data( self ) -> str: 
        table = self.get_table()
        self.user_manager.checkbox_state = table[1].lower()
        if self.user_manager.checkbox_state == 'down':
            self.user_manager.username = table[2]
            self.user_manager.password = table[3]
        return self.user_manager.checkbox_state
    
    @checkbox_keep_login_data.setter 
    def checkbox_keep_login_data( self, state ):
        self.user_manager.checkbox_state = state  


    # ---------------------------------------------------------------#
    #                   Database Manager Functions                   #
    # ---------------------------------------------------------------#  
    def update_date( self, dt = None ):
        self._datetime =  datetime.now().strftime("%H:%M:%S %d/%m/%Y")
        self._time = self.datetime.split(' ')[0]
        self._date = self.datetime.split(' ')[1]

    def get_table(self) -> list:
        return self.database_manager.login[0]
    
    def set_table(self, state, user, psd ):
        self.database_manager.set_login( state, user, psd )
        
    def connection_status( self ) -> bool:
        return self.connected 
    
    def auto_connect( self ):
        if isinstance( self.database_manager, Database ):
            return self.database_manager.serial[0]
        else: 
            return None 
        
    def serial( self ): 
        if isinstance( self.database_manager, Database ):
            return self.database_manager.serial 
        else: 
            return None 
    
    def disconnect( self ):
        try:
            if isinstance( self.system, Database ):
                self.system.close()
            else: 
                pass
        except:
            pass 

    # ---------------------------------------------------------------#
    #                   System Manager Functions                     #
    # ---------------------------------------------------------------# 
    def get_sys_time( self ) -> str:
        return self.system_manager.get_sys_time()
    
    def get_sys_date( self ) -> str:
        return self.system_manager.get_sys_date() 

    def update( self, new_data: dict ) -> None:
        self.system_manager.update( new_data = new_data )
    
    def get_motor_pos( self ) -> list | None:
        if self.system is not None:
            return self.system_manager.get_motor_pos()
        else:
            return None
    
    def get_system_generation( self ) -> float: 
        return self.system_manager.get_system_generation() 

    def get_azimute_zenite_data( self ) -> list:
        return self.system_manager.get_azimute_zenite_data() 

    def is_connected(self): 
        return self.system_manager.is_connected()


    # ---------------------------------------------------------------#
    #                   User Manager Functions                       # 
    # ---------------------------------------------------------------# 
    def connect_device( self, slave: int, port: str, baudrate : int, timeout : int = 1 ) -> bool:
        return self.system_manager.connect_device_RTU( slave, port, baudrate, timeout = timeout )

    ''' User ans Password model.getters '''
    @property
    def user( self ) -> str:
        return self.user_manager.username     
    @property
    def psd( self ) -> str:
        return self.user_manager.password 

    @property
    def username( self ) -> str:
        return self.user_manager.username
    
    @username.setter
    def username( self, value ): 
        self.user_manager.username = value 

    @property
    def last_access( self ) -> str:
        return self.user_manager.last_access 
    
    @last_access.setter
    def last_access( self, value ): 
        self.user_manager.last_access = value 

    @property
    def level_access( self ) -> str:
        return self.user_manager.level_access 
    
    @level_access.setter
    def level_access( self, value ): 
        self.user_manager.level_access = value 

    @property
    def photo( self ) -> bytes:
        return self.user_manager.photo 
    
    @photo.setter
    def photo( self, value ): 
        self.user_manager.photo = value 

    @property
    def login_index( self ) -> int:
        return self.user_manager.login_index 
    
    @login_index.setter
    def login_index( self, value ): 
        self.user_manager.login_index = value 
