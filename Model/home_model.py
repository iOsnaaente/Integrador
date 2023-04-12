from Model.base_model import BaseScreenModel
from shared_data import SharedData 
from libs.Model import SunPosition 

import os 
PATH = os.path.dirname( __file__ )

class HomeModel(BaseScreenModel):
    """
    Implements the logic of the
    :class:`~View.home_screen.HomeScreen.HomeScreenView` class.
    """

    SunData = SunPosition( latitude = -29.71332542661317, longitude = -53.71766381408064, altitude = 300 )

    __shared_data : SharedData 

    def __init__( self, shared_data : SharedData = None ) -> None:
        self.__shared_data = shared_data 
        super().__init__()
    
    @property 
    def shared_data(self):
        return self.__shared_data