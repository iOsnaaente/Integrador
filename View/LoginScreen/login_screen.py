from View.base_screen   import BaseScreenView
from kivy.properties    import ObjectProperty
from kivymd.uix.card    import MDCard 

import os 
IMAGE_PATH = os.path.dirname( __file__ ).removesuffix('\\View\\LoginScreen') + '/images'
KV_PATH = os.path.dirname( __file__ )


class CardNewUser( MDCard ):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LoginScreenView( BaseScreenView ):

    __debug : bool = True 

    IMAGE_PATH = os.path.dirname( __file__ ).removesuffix('\\View\\LoginScreen') + '/images'

    username = ObjectProperty()
    password = ObjectProperty()

    sunrise_image =  IMAGE_PATH + '/sunrise.jpg'   
    connectivity_icon = IMAGE_PATH +  '/connectivity.png'
    green_power_icon = IMAGE_PATH +  '/green-power.png' 
    security_icon = IMAGE_PATH +  '/security.png'
    solar_icon = IMAGE_PATH +  '/smart-power.png'
    smart_sun = IMAGE_PATH +  '/smart.png'
    map_icon = IMAGE_PATH +  '/map.png'
    

    def __init__(self, **kw):
        super().__init__(**kw)
        

    # Tenta iniciar o socket de login
    def on_enter(self, *args):
        self.model.connect_server()
        return super().on_enter(*args)
        
    # Faz o login 
    def login ( self ):
        ans = self.model.login( self.username.text, self.password.text )
        if ans != False :
            if self.ids.checkbox_keep_login.state == 'down':
                self.model.set_table( 'DOWN', self.username.text, self.password.text )
            elif self.ids.checkbox_keep_login.state == 'normal':
                self.model.set_table( 'NORMAL', '' , '' ) 
            self.manager_screens.current = 'home screen'
            if self.__debug: 
                print( 'Logado com \nUsuário: {}\nSenha: {}'.format( self.username.text, self.password.text ) )
                print( 'Keep data state : ', self.ids.checkbox_keep_login.state )
                print( 'Data kept: ', self.model.get_table () )


    # Criar novo usuário 
    def create_new_user( self, user, password, family ):
        ans = self.model.create_new_user( user, password, family )
        if ans: 
            self.ids.login_user_field.text = user 
            self.ids.login_password_field.text = password
            self.controller.close_widget( )


    # Observador
    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
