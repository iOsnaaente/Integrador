from View.base_screen       import BaseScreenView
from kivy.properties        import ObjectProperty
from kivymd.uix.card        import MDCard 
from kivy.clock             import Clock
from kivymd.uix.behaviors   import HoverBehavior 
from kivymd.theming         import ThemableBehavior

from libs.sweetalert.sweetalert import SweetAlert

import os 
IMAGE_PATH = os.path.dirname( __file__ ).removesuffix('\\View\\LoginScreen') + '/images'
KV_PATH = os.path.dirname( __file__ )


class CardNewUser( MDCard ):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# Linha para puxar a tela de login 
class SwipeLine( MDCard, ThemableBehavior, HoverBehavior ):
    HOVER_ENTER_COLOR : list = [ 0.8, 0.8, 0.8, 0.85 ] 
    HOVER_LEAVE_COLOR : list = [ 0.5, 0.5, 0.5, 0.60 ] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_enter(self, *args):
        self.md_bg_color = self.HOVER_ENTER_COLOR
        return super().on_enter()
    
    def on_leave(self, *args):
        self.md_bg_color = self.HOVER_LEAVE_COLOR
        return super().on_leave()


class LoginScreenView( BaseScreenView ):

    __debug : bool = True 

    IMAGE_PATH = os.path.dirname( __file__ ).removesuffix('\\View\\LoginScreen') + '/assets/images'

    username = ObjectProperty()
    password = ObjectProperty()

    sunrise_image =  IMAGE_PATH + '/sunrise.jpg'   
    connectivity_icon = IMAGE_PATH +  '/connectivity.png'
    green_power_icon = IMAGE_PATH +  '/green-power.png' 
    security_icon = IMAGE_PATH +  '/security.png'
    solar_icon = IMAGE_PATH +  '/smart-power.png'
    smart_sun = IMAGE_PATH +  '/smart.png'
    map_icon = IMAGE_PATH +  '/map.png'
    
    ping_pong = None 

    def __init__(self, **kw):
        super().__init__(**kw)
                

    # Tenta iniciar o socket de login
    def on_enter(self, *args):
        self.model.connect_server()
        self.ping_pong = Clock.schedule_interval( self.model.keep_connection_alive, 1 )
        if not self.model.connection_status():
            SweetAlert( ).fire( 'Servidor não conectado', type = 'warning', footer = "O sistema pode não funcionar de acordo" )
        return super().on_enter(*args)
    

    # Faz o login 
    def login ( self ):
        # Primeiro verifica o status da conexão 
        if not self.model.connection_status():
            SweetAlert( ).fire( 'Servidor não conectado', type = 'warning', footer = "Sistema de login indisponível" )
            return 
        else: 
            # Tenta executar o login 
            ans = self.model.login( self.username.text, self.password.text )
            if ans:
                if self.ids.checkbox_keep_login.state == 'down':
                    self.model.set_table( 'DOWN', self.username.text, self.password.text )
                elif self.ids.checkbox_keep_login.state == 'normal':
                    self.model.set_table( 'NORMAL', '' , '' ) 

                # Se o login foi estabelecido, entra na aplicação 
                self.manager_screens.current = 'home screen'
                Clock.unschedule( self.ping_pong )
                self.model.shared_data.connected = True
                if self.__debug: 
                    print( 'Logado com \nUsuário: {}\nSenha: {}'.format( self.username.text, self.password.text ) )
                    print( 'Keep data state : ', self.ids.checkbox_keep_login.state )
                    print( 'Data kept: ', self.model.get_table () )

            # Caso contrário, lança um erro de usuário e senha incorreto 
            else: 
                SweetAlert( timer = 0.5 ).fire( 'Usuário e senha incorretos', type = 'failure' )

    # Criar novo usuário 
    def create_new_user( self, user, password, sup, sup_psd ):
        # Primeiro verifica o status da conexão 
        if not self.model.connection_status():
            SweetAlert( ).fire( 'Servidor não conectado', type = 'warning', footer = "Sistema de registro indisponível" )
            return 
        else: 
            ans = self.model.create_new_user( user, password, sup, sup_psd )
            if ans == 'NEW USER CREATED':
                # Lançar o sweetAlert de usuário registrado com sucesso 
                SweetAlert( timer = 2 ).fire( 'Usuário registrado com sucesso', type = 'success' )
                # Salva os nomes na tela de login
                self.ids.login_user_field.text = user 
                self.ids.login_password_field.text = password
                # Fecha a janela de registro 
                self.controller.close_widget( )
                # Abre o navigationDrawer de login  
                self.ids.drawer_login.state = 'open'
            elif ans == 'ALREADY REGISTERED':
                # Lançar o erro de usuário já registrado  
                SweetAlert( timer = 2 ).fire( f'Usuário {user} já registrado\nPor favor registre outro usuário', type = 'failure' )
            else:
                # Supervisor não encontrado ou erro desconhecido
                SweetAlert( timer = 2 ).fire( 'Erro ao registrar usuário\nChame o supervisor', type = 'failure' )


    # Observador
    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """