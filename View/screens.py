# The screen's dictionary contains the objects of the models and controllers
# of the screens of the application.

from Model.login_model import LoginModel
from Controller.login_screen import LoginScreenController

from Model.home_model import HomeModel
from Controller.home_screen import HomeScreenController

from Model.system_model import SystemModel
from Controller.map_screen import MapScreenController

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
}