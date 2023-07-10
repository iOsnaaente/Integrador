from Model.base_model import BaseScreenModel


from Model.shared_data  import SharedData 
from Model.db.database  import Database
from System.tracker     import Device 
from libs.Sun           import SunPosition 

import os 
PATH = os.path.dirname( __file__ ).removesuffix('\\Model')


class SystemModel( BaseScreenModel ):
    """
    Implements the logic of the
    :class:`~View.home_screen.HomeScreen.HomeScreenView` class.
    """
    painel_solar        = PATH + '/assets/images/PainelSolar.png'
    motor_vertical      = PATH + '/assets/images/motorVertical.png'
    motor_horizontal    = PATH + '/assets/images/motorHorizontal.png'
    sensor_motores      = PATH + '/assets/images/encoder.png'
    background          = PATH + '/assets/images/background.png'
    
    SunData : SunPosition = SunPosition( 
        latitude = -29.71332542661317, 
        longitude = -53.71766381408064, 
        altitude = 300 
    )
    
    # # Informações de acesso 
    # #     Usuário, level_access e photo
    # # 
    _shared_data : SharedData

    # # Informações de Keep data 
    # #     Keep username & password 
    # #     Keep serial connection 
    # # 
    _database : Database 

    # # Acesso ao sistema
    # # 
    _system: Device | None = None 


    def __init__( self, shared_data : SharedData ) -> None:
        self._shared_data = shared_data
        self._database = Database()
        super().__init__() 

    @property 
    def shared_data( self ):
        return self._shared_data
    @property 
    def database( self ):
        return self._database 
    @property 
    def system( self ):
        return self._system 


    def auto_connect( self ):
        return self.database.serial[0]
    
    def serial( self ): 
        return self.database.serial 
    
    def is_connected(self): 
        if self.system is None:
            return False 
        else:      
            return self.system.connected

    def connect_device( self, slave: int, port: str, baudrate : int, timeout : int = 1 ) -> bool:
        try:
            self.system.__init__( slave, port, baudrate, timeout = timeout )
            self.system.connected = True 
            return True 
        except:
            return False 
    

        
