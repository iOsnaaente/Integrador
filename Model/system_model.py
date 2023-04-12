from Model.base_model import BaseScreenModel
from shared_data import SharedData

import os 
PATH = os.path.dirname( __file__ )


class SystemModel(BaseScreenModel):
    """
    Implements the logic of the
    :class:`~View.map_screen.MapScreen.MapScreenView` class.
    """    
    
    get_user_level_access = 'Administrador'
    get_user_photo = PATH.removesuffix('\\Model') + '/images/me.png'
    get_username = 'Brunosvaldo Sampaio' 
    __shared_data : SharedData

    def __init__(self, shared_data : SharedData = None ) -> None:
        super().__init__()
        self.__shared_data = shared_data 
    
    @property 
    def shared_data( self ):
        return self.__shared_data 