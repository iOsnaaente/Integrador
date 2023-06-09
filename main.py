from kivymd.uix.screenmanager import MDScreenManager
from kivymd.tools.hotreload.app import MDApp
from kivy.utils import rgba, QueryDict

import importlib

# Obtém o monitor primário (índice 0) ou o segundo monitor (índice 1)
from screeninfo import get_monitors
try: 
    monitor = get_monitors()[1]
except:
    monitor = get_monitors()[0]

from kivy.core.window import Window
Window.size = ( monitor.width, monitor.height )
Window.left = monitor.x
Window.top = monitor.y + 25

# Inicia em modo Tela Cheia 
Window.fullscreen = 'auto'

# Debug 
LOAD_SCREEN = 'login screen'
#

# Onde as informações devem ser compartilhadas 
from Model.shared_data import SharedData 
from Model.login_model import LoginModel 
from Model.system_model import SystemModel 

# from System.tracker import Tracker as TrackerSerial

import os
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


    def build_app(self) -> MDScreenManager:
        import View.screens

        self.manager_screens = MDScreenManager()
        self.shared_data = SharedData()
        self.login_model = LoginModel( shared_data = self.shared_data )
        self.system_model = SystemModel( shared_data = self.shared_data )

        Window.bind( on_key_down = self.on_keyboard_down)

        importlib.reload(View.screens)
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
        self.theme_cls.material_style = "M3"
        self.theme_cls.primary_hue = "500"
        self.manager_screens.current = LOAD_SCREEN
        return self.manager_screens

    def on_keyboard_down(self, window, keyboard, keycode, text, modifiers) -> None:
        if "meta" in modifiers or "ctrl" in modifiers and text == "r":
            self.rebuild()

    def get_manager(self):
        return self.manager_screens
    

Tracker().run()

# After you finish the project, remove the above code and uncomment the below
# code to test the application normally without hot reloading.

# """
# The entry point to the application.
# 
# The application uses the MVC template. Adhering to the principles of clean
# architecture means ensuring that your application is easy to test, maintain,
# and modernize.
# 
# You can read more about this template at the links below:
# 
# https://github.com/HeaTTheatR/LoginAppMVC
# https://en.wikipedia.org/wiki/Model–view–controller
# """
# 
# from kivymd.app import MDApp
# from kivymd.uix.screenmanager import MDScreenManager
# 
# from View.screens import screens
# 
# 
# class Tracker(MDApp):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.load_all_kv_files(self.directory)
#         # This is the screen manager that will contain all the screens of your
#         # application.
#         self.manager_screens = MDScreenManager()
#         
#     def build(self) -> MDScreenManager:
#         self.generate_application_screens()
#         return self.manager_screens
# 
#     def generate_application_screens(self) -> None:
#         """
#         Creating and adding screens to the screen manager.
#         You should not change this cycle unnecessarily. He is self-sufficient.
# 
#         If you need to add any screen, open the `View.screens.py` module and
#         see how new screens are added according to the given application
#         architecture.
#         """
# 
#         for i, name_screen in enumerate(screens.keys()):
#             model = screens[name_screen]["model"]()
#             controller = screens[name_screen]["controller"](model)
#             view = controller.get_view()
#             view.manager_screens = self.manager_screens
#             view.name = name_screen
#             self.manager_screens.add_widget(view)
# 
# 
# Tracker().run()
