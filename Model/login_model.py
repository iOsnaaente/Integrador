from Model.base_model import BaseScreenModel

from cryptography.fernet import Fernet 
from libs.Security import encode_object, decode_object, sync_unikey
from Model.db.database import Database 
from kivy.clock import Clock

import socket
SERVER = '127.0.0.1'
LOGIN_PORT = 50505

class LoginModel(BaseScreenModel):
    """
    Implements the logic of the
    :class:`~View.login_screen.LoginScreen.LoginScreenView` class.
    """
    __login_client : socket.socket
    __debug = True 

    __checkbox = 'normal'
    __user = ''
    __psd = ''

    __login_index : int 
    __sync = False 

    db = Database()

    KEY = Fernet.generate_key()



    # sistema de login não usa nenhum tipo de criptografia de dados
    # usar um arquivo xml para isso e colocar cripto em cima 
    def login( self, user : str , psd : str ) -> bool:
        login_data = {
            'type'    : 'LOGIN',
            'username': user,
            'password': psd,
            'family'  : '' }
        try:
            data = encode_object( login_data, UNIKEY = self.KEY )
            self.__login_client.send( data ) 
            ANS = self.__login_client.recv( 1024 )
            ans = decode_object( ANS, UNIKEY = self.KEY )
        except socket.error as e:
            ans = e 
        if self.__debug:    print( f'Socket connection OK\nSend {data}\nReceived {ans}' ) 
        if ans == b'False' or type(ans) == socket.error :
            return False 
        else:
            try:
                self.__login_index = int( ans.decode() )
                if self.__debug:    print( f'Login index {self.__login_index}' ) 
            except: 
                if self.__debug:    print( 'Login index not valid' ) 
                return False
            return True 

    # Criar novo usuário 
    def create_new_user( self, user : str, password : str, family : str  ) -> bool:
        create_user_data = {
            'type'    : 'NEW USER',
            'username': user,
            'password': password,
            'family'  : family 
        }
        if user and password:
            try: 
                data = encode_object( create_user_data, UNIKEY = self.KEY )
                self.__login_client.send( data ) 
                ANS = self.__login_client.recv( 1024 )
                ans = decode_object( ANS, UNIKEY = self.KEY )        
            except socket.error as e:
                ans = e 
            if self.__debug:    print( f'Socket creat new user connection OK\nSend {data}\nReceived {ans}' ) 
            if ans == b'False' or type(ans) == socket.error :
                return False 
            else:
                return True 
        else: 
            return False 
    
    # Conectar ao servidor 
    def connect_server( self, clock_event = None ) -> bool:
        try:
            self.__login_client = socket.socket( socket.AF_INET, socket.SOCK_STREAM ) 
            self.__sync = sync_unikey( self.__login_client, SERVER, LOGIN_PORT, self.KEY, timeout = 0.1 )
            if self.__sync: 
                if self.__debug:   print( 'Server login sync' )
                return True 
            else:
                if self.__debug:   print( 'Server login not sync' )
                return False 
        except socket.error as e :
            if self.__debug:   print( e )
            Clock.schedule_once( self.connect_server, 1 )
            return False

    # Getter and Setter DB properties  
    def get_table(self):
        return self.db.get_login_table()[0]
    
    def set_table(self, state, user, psd ):
        self.db.set_login_table( state, user, psd )

    # Getter and Setter checkbox property 
    @property 
    def checkbox_keep_login_data( self ): 
        table = self.get_table()
        self.__checkbox = table[1].lower()
        if self.__checkbox == 'down':
            self.__user = table[2]
            self.__psd = table[3]
        return self.__checkbox
    @checkbox_keep_login_data.setter 
    def checkbox_keep_login_data( self, state ):
        self.__checkbox = state  

    # User ans Password model.getters 
    @property
    def user( self ):
        return self.__user 
    
    @property
    def psd( self ):
        return self.__psd 