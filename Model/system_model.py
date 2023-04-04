from Model.base_model import BaseScreenModel

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
