from Model.base_model import BaseScreenModel
from Model.shared_data import SharedData 
from libs.Sun import SunPosition 
from libs.Uart import UART 

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
    
    __shared_data : SharedData 
    __serial : UART

    def __init__( self, shared_data : SharedData = None ) -> None:
        self.__shared_data = shared_data 
        self.__serial = None 
        super().__init__() 

    @property 
    def shared_data( self ):
        return self.__shared_data