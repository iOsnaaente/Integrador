from kivy.properties import ObjectProperty
from kivy.clock import Clock 

from kivymd.uix.boxlayout import MDBoxLayout 
from kivy.animation import Animation 
from kivymd.uix.card import MDCard
from kivymd.app import MDApp


import os 
PATH = os.path.dirname( __file__ ).removesuffix('\\View\\Widgets\\SideBar')
IMAGES = PATH + '/assets/images/'
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
         'serial screen'      ,
         'sensor screen'      ,
         'diagnosticos screen', 
        ]
    

class MyCardMenu( MDCard ):    
    card_title = ObjectProperty()
    card_image = ObjectProperty()
    
    def __init__(self, text, image, body_size, screen_link = '', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.card_title.text = text 
        self.card_image.source = image
        self.size_hint = body_size
        self.screen_link = screen_link 

    def click(self):
        manager_screen = APP.manager_screens
        current = manager_screen.current 
        try: 
            print('Link to screen: ', self.screen_link  )
            manager_screen.current = self.screen_link 
            print('OK - Current screen: ', manager_screen.current )
        except: 
            manager_screen.current = current 
            print( 'Exception change screen ')
        return super().on_press()

    def hover_in(self):
        self.md_bg_color  = [ 1, 1, 1, 0.25 ]

    def hover_out(self):
        self.md_bg_color = self.theme_cls.bg_darkest
    
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
        
        self.user_level_access.text = str(self.model.shared_data.level_access) 
        print( self.model.shared_data.username )

        if self.model.shared_data.photo: 
            self.user_photo.source = self.model.shared_data.photo
        else: 
            self.user_photo.source = PATH.removesuffix('\\View\\commom_components\\SideBar') + '/assets/images/usernophoto.png'
            
        self.username.text = str(self.model.shared_data.username)

        for img, label, link in zip( imgs, lbls, lnks ):
            self.home_side_bar.add_widget(  
                MyCardMenu(
                    text = label,
                    image = IMAGES + img, 
                    body_size = [ 1, 1/(len(imgs)+1) ],
                    screen_link = link
                ) 
            )

    def hover_image_in( self ):
        print( 'hover_image_in' )

    def hover_image_out( self ):
        print( 'hover_image_out' )

    def change_image( self ):
        print( 'change_image' )
