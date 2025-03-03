from kivymd.uix.screenmanager import MDScreenManager
from Model.system_model import SystemModel 
from kivy.utils import rgba, QueryDict
from kivy.logger import Logger 
from kivymd.app import MDApp
import logging 
import os


# Obtém o monitor primário (índice 0) ou o segundo monitor (índice 1)
from screeninfo import get_monitors
try: 
    # Tenta iniciar no monitor secundário 
    monitor = get_monitors()[1] if get_monitors()[1].is_primary == False else get_monitors()[0]  
except:
    # Caso não consiga, inicia no monitor primário
    monitor = get_monitors()[0]


# Define o tamanho da janela
from kivy.core.window import Window
Window.size = ( monitor.width, monitor.height )
Window.left = monitor.x
Window.top = monitor.y + 25

# Inicia em modo Tela Cheia 
Window.fullscreen = 'auto'


# FileHandler para gravar os logs do programa dentro de App.log
file_handler = logging.FileHandler( "App.log", encoding = "utf-8" )
file_handler.setLevel( logging.INFO ) 
formatter = logging.Formatter( "%(asctime)s - %(name)s - %(levelname)s - %(message)s" )
file_handler.setFormatter( formatter )

# Adiciona o handler para usar o Logger do Kivy
Logger.addHandler(file_handler)

# Define o nível do Logger para:
# logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL
Logger.setLevel(logging.DEBUG)


class Tracker( MDApp ):
    KV_DIRS = [os.path.join(os.getcwd(), "View")]
    DEBUG = False

    # Cores do Aplicativo 
    colors = QueryDict() 
    colors.background    = rgba( '#444444FF' )
    colors.primary       = rgba( "#FDC6BBFF" )
    colors.accent        = rgba( "#FD453BFF" )
    colors.hint          = rgba( "#F6F6F6FF" )


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_all_kv_files(self.directory)
        self.manager_screens = MDScreenManager()
        

    def build(self) -> MDScreenManager:
        import View.screens

        self.manager_screens = MDScreenManager()
        self.system_model = SystemModel( _debug = False )

        screens = View.screens.screens   
        for _, name_screen in enumerate(screens.keys()):
            if name_screen == 'login screen':
                controller = screens[name_screen]["controller"]( model = self.system_model )
            else:
                controller = screens[name_screen]["controller"]( model = self.system_model )
            view = controller.get_view()
            view.manager_screens = self.manager_screens
            view.name = name_screen
            self.manager_screens.add_widget(view)
        
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        self.theme_cls.material_style = "M3"
        self.theme_cls.primary_hue = "500"

        self.manager_screens.current = 'home screen'
        return self.manager_screens

    def get_manager(self):
        return self.manager_screens

Tracker().run()