from kivymd.uix.screenmanager import MDScreenManager
from kivy.utils import rgba, QueryDict
from kivymd.app import MDApp

import os

# Obtém o monitor primário (índice 0) ou o segundo monitor (índice 1)
from screeninfo import get_monitors
try: 
    # Pega o monitor secundário 
    monitor = get_monitors()[1] if get_monitors()[1].is_primary == False else get_monitors()[0]  
except:
    monitor = get_monitors()[0]

from kivy.core.window import Window
Window.size = ( monitor.width, monitor.height )
Window.left = monitor.x
Window.top = monitor.y + 25

# Inicia em modo Tela Cheia 
Window.fullscreen = 'auto'

# Onde as informações devem ser compartilhadas 
from Model.shared_data import SharedData 
from Model.login_model import LoginModel 
from Model.system_model import SystemModel 

class Tracker(MDApp):

    KV_DIRS = [os.path.join(os.getcwd(), "View")]
    shared_data : SharedData 
    DEBUG = 0

    colors = QueryDict() 
    # Cores 
    colors.background    = rgba( '#444444FF' )
    colors.primary       = rgba( "#FDC6BBFF" )
    colors.accent        = rgba( "#FD453BFF" )
    colors.hint          = rgba( "#F6F6F6FF" )


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_all_kv_files(self.directory)
        # This is the screen manager that will contain all the screens of your
        # application.
        self.manager_screens = MDScreenManager()
        
    def build(self) -> MDScreenManager:
        import View.screens

        self.manager_screens = MDScreenManager()
        self.shared_data = SharedData()
        self.login_model = LoginModel( shared_data = self.shared_data )
        self.system_model = SystemModel( shared_data = self.shared_data, _debug = False )

        Window.bind( on_key_down = self.on_keyboard_down)
        screens = View.screens.screens   
        for _, name_screen in enumerate(screens.keys()):
            if name_screen == 'login screen':
                controller = screens[name_screen]["controller"]( model = self.login_model, shared_data = self.shared_data)
            else:
                controller = screens[name_screen]["controller"]( model = self.system_model, shared_data = self.shared_data)
            view = controller.get_view()
            view.manager_screens = self.manager_screens
            view.name = name_screen
            self.manager_screens.add_widget(view)
        
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        # self.theme_cls.material_style = "M3"
        # self.theme_cls.primary_hue = "500"

        self.manager_screens.current = 'login screen'

        return self.manager_screens


    def on_keyboard_down(self, window, keyboard, keycode, text, modifiers) -> None:
        if "meta" in modifiers or "ctrl" in modifiers and text == "r":
            # self.rebuild()
            pass 

    def get_manager(self):
        return self.manager_screens

Tracker().run()