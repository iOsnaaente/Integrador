from Model.base_model import BaseScreenModel

from libs.Model import SunPosition 

import os 
PATH = os.path.dirname( __file__ )

class HomeModel(BaseScreenModel):
    """
    Implements the logic of the
    :class:`~View.home_screen.HomeScreen.HomeScreenView` class.
    """

    get_user_level_access = 'Administrador'
    get_user_photo = PATH.removesuffix('\\Model') + '/images/me.png'
    get_username = 'Brunosvaldo Sampaio' 

    SunData = SunPosition( latitude = -29.71332542661317, longitude = -53.71766381408064, altitude = 300 )