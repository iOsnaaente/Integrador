from Model.login_model import LoginModel
from Controller.login_screen import LoginScreenController

from Model.home_model import HomeModel
from Controller.home_screen import HomeScreenController
from Controller.map_screen import MapScreenController

from Model.system_model import SystemModel
from Controller.serial_screen import SerialScreenController

screens = {
    'login screen': {
        'model': LoginModel,
        'controller': LoginScreenController,
    },
    'home screen': {
        'model': HomeModel,
        'controller': HomeScreenController,
    },
    'map screen': {
        'model': HomeModel,
        'controller': MapScreenController,
    },
    'serial screen': {
        'model': SystemModel,
        'controller': SerialScreenController,
    },
    'sensor screen': {
        'model': SystemModel,
        'controller': SerialScreenController,
    },
    
}