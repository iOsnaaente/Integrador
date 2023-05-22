from Model.base_model import BaseScreenModel

from libs.Security import encode_object, decode_object, sync_unikey
from cryptography.fernet import Fernet 
from Model.db.database import Database 
from Model.shared_data import SharedData

import threading
import socket
import json 

SERVER = '127.0.0.1'
LOGIN_PORT = 50505

SYNC_TIMEOUT = 1
CREATE_TIMEOUT = 1 
PING_TIMEOUT = 1 

class LoginModel( BaseScreenModel ):
    """
        Implements the logic of the
        :class:`~View.login_screen.LoginScreen.LoginScreenView` class.
    """
    __login_client : socket.socket
    __debug = True 

    __checkbox : str = 'normal'
    __user : str = ''
    __psd : str = ''

    __login_index : int 
    __sync : bool =  False 

    db = Database()
    KEY = Fernet.generate_key()
    connection : bool = False 

    def __init__( self, shared_data : SharedData = None ): 
        self.__shared_data = shared_data 

    ''' Conectar ao servidor '''
    def connect_server( self, clock_event = None ) -> bool:
        try:
            self.__login_client = socket.socket( socket.AF_INET, socket.SOCK_STREAM ) 
            self.__sync = sync_unikey( self.__login_client, SERVER, LOGIN_PORT, self.KEY, timeout = SYNC_TIMEOUT )
            if self.__sync: 
                if self.__debug:   
                    print( 'Server login sync' )
                self.connection = True 
                return True 
            else:
                if self.__debug:   
                    print( 'Server login not sync' )
                self.connection = False
                return False 
            
        except socket.error as e :
            if self.__debug:   print( e )
            self.connection = False 
            return False

    def keep_connection_alive( self, d_time : int = None ):
        thr = threading.Thread( target = self.__keep_connection_alive, args = () )
        thr.start() 
    
    def __keep_connection_alive( self ):
        if not self.connection:
            self.connect_server()
        else:
            try: 
                ping_pong_data = { 'type' : 'PING' }
                self.__login_client.settimeout( PING_TIMEOUT )
                data = encode_object( ping_pong_data, UNIKEY = self.KEY )
                self.__login_client.send( data ) 
                ANS = self.__login_client.recv( 1024 )
                ans = decode_object( ANS, UNIKEY = self.KEY )
                if self.__debug:
                    print( ans )
            except Exception as e :
                if self.__debug:
                    print( e )
                ans = None  
            finally:
                if ans == b'PONG':
                    self.connection = True 
                else: 
                    self.connection = False 


    def login( self, user : str , psd : str ) -> bool:
        login_data = { 'type' : 'LOGIN', 'username': user, 'password': psd }
        try:
            data = encode_object( login_data, UNIKEY = self.KEY )
            self.__login_client.send( data ) 
            ANS = self.__login_client.recv( 1024 )
            ans = decode_object( ANS, UNIKEY = self.KEY )

        # Se houver alguma execção no caminho significa que houve algum erro 
        except Exception as e:
            ans = e 
            if self.__debug:
                print( e )
            return False 

        # Se não, a conexão foi estabelecida
        if self.__debug:    
            print( f'Socket connection OK\nSend {data}\nReceived {ans} of type {type(ans)}' ) 
        # Mas pode estar correta ou não 
        if ans == b'UNKNOW' or 'error' in ans.decode():
            return False 
        else:
            try:
                ans = json.loads( ans.decode() )
            except: 
                print( ans, ans.decode() ) 
                return False 
            self.shared_data.login_index = ans['id'] 
            self.shared_data.username = ans['username'] 
            self.shared_data.last_access = ans['last_access'] 
            self.shared_data.level_access = ans['level_access'] 
            self.shared_data.photo = ans['photo']
            if self.__debug:    
                print( f'Login index {self.shared_data.login_index}' ) 
            return True 

    # Criar novo usuário 
    def create_new_user( self, user : str, password : str, manager_group : str, manager_psd : str  ) -> bool:
        '''
            Estrutura do login esta nessa linha
            se o servidor mudar, deve ser mudado aqui também 
        '''
        create_user_data = {'type' : 'NEW_USER', 'username': user, 'password': password, 'manager_group' : manager_group, 'manager_psd' : manager_psd    }
        
        if user and password:
            try: 
                data = encode_object( create_user_data, UNIKEY = self.KEY )
                self.__login_client.send( data ) 
                self.__login_client.settimeout(CREATE_TIMEOUT)
                ANS = self.__login_client.recv( 1024 )
                ans = decode_object( ANS, UNIKEY = self.KEY )        
            except socket.error as e:
                ans = e 

            if self.__debug:    
                print( f'Socket creat new user connection OK\nSend {data}\nReceived {ans}' ) 
            
            if ans == b'FAILED' or type(ans) == socket.error :
                return False 
            elif ans == b'SUCCESS': 
                return True 
            else:
                return False

    ''' Getter and Setter DB properties '''  
    def get_table(self):
        return self.db.login[0]
    
    def set_table(self, state, user, psd ):
        self.db.set_login( state, user, psd )

    ''' Estado da conexão com o servidor'''
    def connection_status( self ):
        return self.connection 

    ''' Getter and Setter checkbox property '''
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

    ''' User ans Password model.getters '''
    @property
    def user( self ):
        return self.__user 
    
    @property
    def psd( self ):
        return self.__psd 
    
    @property
    def shared_data( self ):
        return self.__shared_data 