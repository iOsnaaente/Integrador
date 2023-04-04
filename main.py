from kivymd.tools.hotreload.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager

# TODO: You may know an easier way to get the size of a computer display.
import importlib

# Change the values of the application window size as you need.
from kivy import Config
Config.set( "graphics", "width" , "1400" )
Config.set( "graphics", "height", "900"  )


# Place the application window on the right side of the computer screen.
from kivy.core.window import Window
Window.left = -1375
Window.top = 25


import os


class Tracker(MDApp):

    KV_DIRS = [os.path.join(os.getcwd(), "View")]
    DEBUG = 0

    def build_app(self) -> MDScreenManager:
        import View.screens

        self.manager_screens = MDScreenManager()
        Window.bind(on_key_down=self.on_keyboard_down)
        importlib.reload(View.screens)
        screens = View.screens.screens

        for i, name_screen in enumerate(screens.keys()):
            model = screens[name_screen]["model"]()
            controller = screens[name_screen]["controller"](model)
            view = controller.get_view()
            view.manager_screens = self.manager_screens
            view.name = name_screen
            self.manager_screens.add_widget(view)

        self.theme_cls.theme_style = "Dark"

        self.manager_screens.current = 'login screen'

        return self.manager_screens

    def on_keyboard_down(self, window, keyboard, keycode, text, modifiers) -> None:
        if "meta" in modifiers or "ctrl" in modifiers and text == "r":
            self.rebuild()


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
