from Model.login_model              import LoginModel
from Model.system_model             import SystemModel

from Controller.login_screen        import LoginScreenController
from Controller.home_screen         import HomeScreenController
from Controller.map_screen          import MapScreenController
from Controller.serial_screen       import SerialScreenController
from Controller.sensor_screen       import SensorScreen 
from Controller.diganosticos_screen import DiganosticosScreenController

screens = {
    'login screen': {
        'model': LoginModel,
        'controller': LoginScreenController,
    },
    'home screen': {
        'model': SystemModel,
        'controller': HomeScreenController,
    },
    'map screen': {
        'model': SystemModel,
        'controller': MapScreenController,
    },
    'serial screen': {
        'model': SystemModel,
        'controller': SerialScreenController,
    },
    'sensor screen': {
        'model': SystemModel,
        'controller': SensorScreen,
    },
    'diagnosticos screen': {
        'model': SystemModel,
        'controller': DiganosticosScreenController,
    },   
}
