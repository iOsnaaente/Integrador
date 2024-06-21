from Model.base_model import BaseScreenModel
from Model.shared_data  import SharedData 
from Model.db.database  import Database

from System.tracker     import Device 
from System.Tags        import * 

from libs.Sun           import SunPosition 

import os 
PATH = os.path.dirname( __file__ ).removesuffix( os.path.join( 'Model') )



class SystemModel( BaseScreenModel ):
    """
    Implements the logic of the
    :class:`~View.home_screen.HomeScreen.HomeScreenView` class.
    """
    # Imagens do sistema 
    painel_solar        = PATH + os.path.join( 'assets', 'images', 'PainelSolar.png' ) 
    motor_vertical      = PATH + os.path.join( 'assets', 'images', 'motorVertical.png' ) 
    motor_horizontal    = PATH + os.path.join( 'assets', 'images', 'motorHorizontal.png' ) 
    sensor_motores      = PATH + os.path.join( 'assets', 'images', 'encoder.png' ) 
    background          = PATH + os.path.join( 'assets', 'images', 'background.png' ) 
    
    # Latitude e Longitude do Painel 
    SunData : SunPosition = SunPosition( 
        latitude = -29.71332542661317, 
        longitude = -53.71766381408064, 
        altitude = 300 
    )
    
    # Informações de acesso: Usuário, level_access e photo
    _shared_data : SharedData

    # Informações de Keep data: Keep username & password  / Keep serial connection  
    _database : Database  

    # Acesso ao sistema 
    _system: Device | None = None 

    def __init__( self, shared_data : SharedData, _debug: bool = False  ) -> None:
        super().__init__()
        self._debug = _debug 
        self._shared_data = shared_data
        self._database = Database()

    @property 
    def shared_data( self ):
        return self._shared_data
    @property 
    def database( self ):
        return self._database 
    @property 
    def system( self ):
        return self._system 
    @system.setter 
    def system( self, value ):
        self._system = value  

    def get_sys_time( self ) -> str:
        return    str(
            self.shared_data.SYSTEM_TABLE['INPUT_HOUR']
        ) + ':' + str(
            self.shared_data.SYSTEM_TABLE['INPUT_MINUTE']
        ) + ':' + str(
            self.shared_data.SYSTEM_TABLE['INPUT_SECOND']
        )
    def get_sys_date( self ) -> str:
        return    str(
            self.shared_data.SYSTEM_TABLE['INPUT_YEAR']
        ) + ':' + str(
            self.shared_data.SYSTEM_TABLE['INPUT_MONTH']
        ) + ':' + str(
            self.shared_data.SYSTEM_TABLE['INPUT_DAY']
        )

    def auto_connect( self ):
        return self.database.serial[0]
    
    def serial( self ): 
        return self.database.serial 
    
    def is_connected(self): 
        return self.shared_data.SYSTEM_TABLE["DISCRETE_CONNECTED"]
             
    def disconnect( self ):
        try:
            self.system.close()
        except:
            pass 

    def connect_device( self, slave: int, port: str, baudrate : int, timeout : int = 1 ) -> bool:
        try:
            self.system = Device( slave, port, baudrate, timeout = timeout, debug = self._debug  )
            self.shared_data.connected = self.system.is_connected()
            return self.shared_data.connected
        except Exception as err :
            if self._debug:
                print( 'System Model error:', err )
            self.shared_data.connected = False 
            return False 

    # Retorna os valores de posição dos motores 
    def get_motor_pos( self ) -> list | None:
        if self.system is not None:
            return [ self.shared_data.SYSTEM_TABLE['INPUT_POS_GIR'], self.shared_data.SYSTEM_TABLE['INPUT_POS_ELE'] ]
        else:
            return None
    
    # Retorna o valor de medição do sensor LDR 
    def get_system_generation( self ) -> float: 
        return ( ( ((2**16)-1) - self.shared_data.SYSTEM_TABLE['INPUT_GENERATION'] )/((2**16)-1) )*100
    
    def get_azimute_zenite_data( self ) -> list:
        return [
            self.shared_data.SYSTEM_TABLE['INPUT_POS_GIR'], 
            self.shared_data.SYSTEM_TABLE['INPUT_AZIMUTE'],
            self.shared_data.SYSTEM_TABLE['INPUT_POS_ELE'], 
            self.shared_data.SYSTEM_TABLE['INPUT_ZENITE']
        ]