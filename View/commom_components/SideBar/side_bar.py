from kivy.properties import ObjectProperty
from kivy.clock import Clock 

from kivymd.uix.boxlayout import MDBoxLayout 
from kivymd.uix.behaviors import HoverBehavior
from kivymd.theming import ThemableBehavior 
from kivymd.uix.card import MDCard
from kivymd.app import MDApp

import os 
PATH = os.path.dirname( __file__ ).removesuffix('\\View\\commom_components\\SideBar')
IMAGES = PATH + '/images/'
APP = MDApp.get_running_app()

imgs = [ 'smart.png'          ,
         'map.png'            ,  
         'connectivity.png'   ,
         'smart-power.png'    ,
         'security.png'       , 
        ]
lbls = [ 'Home'               ,
         'Mapa'               ,  
         'Atuador'            ,
         'Sensor'             ,
         'Diagnos.'           ,
        ] 
lnks = [ 'home screen'        ,
         'map screen'         ,  
         'serial screen'    ,
         'sensor screen'      ,
         'diagnosticos screen', 
        ]
    

class MyCardMenu( MDCard, ThemableBehavior, HoverBehavior ):    
    card_title = ObjectProperty()
    card_image = ObjectProperty()
    
    def __init__(self, text, image, body_size, screen_link = '', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.card_title.text = text 
        self.card_image.source = image
        self.size_hint = body_size
        self.screen_link = screen_link 

    def on_press(self):
        manager_screen = APP.manager_screens
        current = manager_screen.current 
        try: 
            print('Link to screen: ', self.screen_link  )
            manager_screen.current = self.screen_link 
        except: 
            manager_screen.current = current 
        return super().on_press()
    
    def on_enter(self):
        self.md_bg_color  = [ 1, 1, 1, 0.25 ]
        return super().on_enter()

    def on_leave(self):
        self.md_bg_color = self.theme_cls.bg_darkest
        return super().on_leave()



    
class SideBar( MDBoxLayout ):

    user_photo = ObjectProperty()
    username = ObjectProperty()
    user_level_access = ObjectProperty()

    home_side_bar = ObjectProperty() 

    model = ''

    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model 
        Clock.schedule_once( self.build, 0.1 )

    def build( self, clock_event ):
        self.user_level_access.text = self.model.get_user_level_access
        self.user_photo.source = self.model.get_user_photo 
        self.username.text = self.model.get_username

        for img, label, link in zip( imgs, lbls, lnks ):
            self.home_side_bar.add_widget(  MyCardMenu(
                                                text = label,
                                                image = IMAGES + img, 
                                                body_size = [ 1, 1/(len(imgs)+1) ],
                                                screen_link = link
                                            ) )
    
