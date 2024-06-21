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

    def __init__( self, shared_data : SharedData | None = None ): 
        self.__shared_data = shared_data 

    ''' 
                    ~~ Conectar ao servidor ~~ 
        Para realizar a conexão com o servidor, primeiro o sistema 
        inicia uma conexão socket TCP com o IP e PORTA. Após criada 
        a conexão, é trocada uma chave de acesso única entre os sistemas.
        Essa chave é usada como criptografia de forma que somente a 
        conexão entre sistema/servidor seja feita utilizando essa 
        chave de criptografia.   
    '''
    def connect_server( self, clock_event = None ) -> bool:
        try:
            # Cria a conexão TCP 
            self.__login_client = socket.socket( socket.AF_INET, socket.SOCK_STREAM ) 
            # Realiza a troca das chaves de criptografia
            self.__sync = sync_unikey( self.__login_client, SERVER, LOGIN_PORT, self.KEY, timeout = SYNC_TIMEOUT )
            # Verifica se o Servidor recebeu/reconheceu a chave 
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
        # Tratamento de erros 
        except socket.error as e :
            if self.__debug:   print( e )
            self.connection = False 
            return False

    '''
                    ~~ Thread keep_alive ~~ 
        Essa thread usa o timer periodico do kivy para comunicar 
        com o servidor de forma periodica, para não perder o vínculo 
        com o sistema. 
    '''
    def keep_connection_alive( self, d_time = None ):
        thr = threading.Thread( target = self.__keep_connection_alive, args = () )
        thr.start() 
    def __keep_connection_alive( self ):
        # Se não estiver conectado, estabelece uma conexão 
        if not self.connection:
            self.connect_server()
        # Caso conectado, envia uma mensagem contendo PING e espera uma resposta PONG
        else:
            ans = None
            try: 
                ping_pong_data = { 'type' : 'PING' }
                # Seta o timeout da conexão 
                self.__login_client.settimeout( PING_TIMEOUT )
                # Criptografa a mensagem e envia 
                data = encode_object( ping_pong_data, UNIKEY = self.KEY )
                self.__login_client.send( data ) 
                # Aguarda resposta e descriptografa
                ANS = self.__login_client.recv( 1024 )
                ans = decode_object( ANS, UNIKEY = self.KEY )
            except Exception as e :
                if self.__debug:
                    print( e )
                ans = None  
            finally:
                # Verifica se a mensagem recebida é um PONG 
                if ans == b'PONG':
                    self.connection = True 
                    if self.__debug:
                        print( "Servidor CONECTADO!!" )
                # Caso contrário, o servidor não esta respondendo de acordo
                else: 
                    if self.__debug:
                        print( "Conexão com o servidor PERDIDA!!" )
                    self.connection = False 

    '''
                    ~~ Login ~~ 
        Essa é a função que realiza o login do sistema 
        com usuário e senha 
    '''
    def login( self, user : str , psd : str ) -> bool:
        # Pega as credencias recebidas da interface do sistema `View`
        login_data = { 'type' : 'LOGIN', 'username': user, 'password': psd }
        # Tenta conectar com o servidor atrás de um usuário válido 
        try:
            # Encriptografa a mensage, envia e aguarda resposta
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

        # Se não, a conexão foi estabelecida com algum valor
        if self.__debug:    
            print( f'Socket connection OK\nSend {data}\nReceived {ans} of type {type(ans)}' ) 
        # Mas pode estar correta ou não 
        if ans == b'UNKNOW' or 'error' in ans.decode():
            return False 
        # Caso a mensagem contenha um usuário válido 
        else:
            try:
                # Decodifica a mensagem enviada como json 
                ans = json.loads( ans.decode() )
            except: 
                # Caso não tenha recebido um json 
                print( ans, ans.decode() ) 
                return False 
            # Carrega os valores do usuário dentro de Shared_data 
            if self.shared_data is not None:
                self.shared_data.login_index = ans['id'] 
                self.shared_data.username = ans['username'] 
                self.shared_data.last_access = ans['last_access'] 
                self.shared_data.level_access = ans['level_access'] 
                self.shared_data.photo = ans['photo']
                if self.__debug:    
                    print( f'Login index {self.shared_data.login_index}' ) 
                return True 
            else: 
                return False 

    '''
                        ~~ Criar novo usuário ~~ 
        Essa é a função que cria um novo usuário dentro do menu de login 
    '''
    def create_new_user( self, user : str, password : str, manager_group : str, manager_psd : str  ) -> str:
        # Cria a mensagem de novo usuário para enviar ao servidor 
        create_user_data = {'type' : 'NEW_USER', 'username': user, 'password': password, 'manager_group' : manager_group, 'manager_psd' : manager_psd    }
        # Se for uma mensagem válida, prossegue 
        if user and password:
            try: 
                # Encriptografa a mensage, envia e aguarda resposta
                data = encode_object( create_user_data, UNIKEY = self.KEY )
                self.__login_client.send( data ) 
                self.__login_client.settimeout(CREATE_TIMEOUT)
                ANS = self.__login_client.recv( 1024 )
                ans = decode_object( ANS, UNIKEY = self.KEY )        
            # Se houver exeção, aborta 
            except socket.error as e:
                ans = e 
            if self.__debug:    
                print( f'Socket creat new user connection OK\nSend {create_user_data}\nReceived {ans}' )
            # Processa o tipo de resposta recebido  
            if type(ans) == socket.error :
                return 'FAIL' 
            elif ans == b'ALREADY REGISTERED':
                return 'ALREADY REGISTERED' 
            elif ans == b'MANAGER NOT FOUND': 
                return 'MANAGER NOT FOUND' 
            elif ans == b'NEW USER CREATED':
                return 'NEW USER CREATED'
            else:
                return 'FAIL'
        else: 
            return 'FAIL' 


    '''
                ~~ Funções de Getter e Setter ~~ 
        As funções abaixo tem a intenção de facilitar o código 
        e servem de apoio ao sistema de login. 
    '''


    ''' Getter and Setter DB properties '''  
    def get_table(self) -> list:
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