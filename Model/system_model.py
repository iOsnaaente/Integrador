from Model.base_model import BaseScreenModel

from libs.Security import encode_object, decode_object, sync_unikey
from cryptography.fernet import Fernet 

from libs.Sun           import SunPosition 
from Model.db.database  import Database
from System.tracker     import Device 
from System.Tags        import * 

from kivy.clock import Clock
from datetime import datetime 
from System.Tags import * 

import threading
import socket
import json 
import os 


PATH            = os.path.dirname( __file__ ).removesuffix( os.path.join( 'Model') )
SERVER          = '127.0.0.1'
LOGIN_PORT      = 50505
SYNC_TIMEOUT    = 1
CREATE_TIMEOUT  = 1 
PING_TIMEOUT    = 1 


class SystemModel( BaseScreenModel ):
    # Imagens do sistema 
    painel_solar        = PATH + os.path.join( 'assets', 'images', 'PainelSolar.png' ) 
    motor_vertical      = PATH + os.path.join( 'assets', 'images', 'motorVertical.png' ) 
    motor_horizontal    = PATH + os.path.join( 'assets', 'images', 'motorHorizontal.png' ) 
    sensor_motores      = PATH + os.path.join( 'assets', 'images', 'encoder.png' ) 
    background          = PATH + os.path.join( 'assets', 'images', 'background.png' ) 
    # Latitude e Longitude do Painel 
    SunData : SunPosition = SunPosition( 
        latitude = -29.71332542661317, 
        longitude = -53.71766381408064, 
        altitude = 300 
    )
    # Informações de Keep data: Keep username & password  / Keep serial connection  
    _database : Database  
    # Acesso ao sistema 
    _system: Device | None = None 
    # Informações do usuário 
    _username : str = ''
    _last_access : str = ''
    _level_access : str = '' 
    _photo : bytes = b''
    _login_index : int = 0 
    _date : str = '00:00:00 01/01/2001'
    _connected = False
    # Informações de conexão com o server 
    __login_client : socket.socket
    # View infos 
    __checkbox : str = 'normal'
    __user : str = ''
    __psd : str = ''
    # system infos 
    __login_index : int 
    __sync : bool =  False 
    # Banco de dados e cripto 
    db = Database()
    KEY = Fernet.generate_key()
    connection : bool = False 
    # Debug 
    __debug = True 
    # Informações sobre o sistema 
    SYSTEM_TABLE = {
        "INPUT_POS_GIR"       : 0.0,  "INPUT_POS_ELE"       : 0.0,
        "INPUT_AZIMUTE"       : 0.0,  "INPUT_ZENITE"        : 0.0,
        "INPUT_GENERATION" 	  : 0.0,     
        "INPUT_TEMP"          : 0.0,  "INPUT_PRESURE"       : 0.0,
        "INPUT_SENS_CONF_GIR" : 0.0,  "INPUT_SENS_CONF_ELE" : 0.0,
        "INPUT_YEAR"          : 0  ,  "INPUT_MONTH"         : 0  ,  "INPUT_DAY"           : 0  ,
        "INPUT_HOUR"          : 0  ,  "INPUT_MINUTE"        : 0  ,  "INPUT_SECOND"        : 0  ,
        
        "HR_PV_GIR"           : 0.0,  "HR_KP_GIR"           : 0.0,  "HR_KI_GIR"           : 0.0, "HR_KD_GIR"           : 0.0,  
        "HR_AZIMUTE"          : 0.0,  
        "HR_PV_ELE"           : 0.0,  "HR_KP_ELE"           : 0.0,  "HR_KI_ELE"           : 0.0, "HR_KD_ELE"           : 0.0,
        "HR_ALTITUDE"         : 0.0,  "HR_LATITUDE"         : 0.0,  "HR_LONGITUDE"        : 0.0,
        "HR_STATE"            : 0,
        "HR_YEAR"             : 0,    "HR_MONTH"            : 0,  "HR_DAY"                : 0,
        "HR_HOUR"             : 0,    "HR_MINUTE"           : 0,  "HR_SECOND"             : 0,
        
        "DISCRETE_FAIL"       : False,
        "DISCRETE_POWER"      : False,
        "DISCRETE_TIME"       : False,
        "DISCRETE_GPS"        : False,
        "DISCRETE_CONNECTED"  : False,

        "COIL_POWER"          : False, "COIL_LED"            : False,
        "COIL_M_GIR"          : False, "COIL_M_ELE"          : False,
        "COIL_LEDR"           : False, "COIL_LEDG"           : False,   "COIL_LEDB"           : False,
        "COIL_SYNC_DATE"      : False,
    } 

    # STATES 
    FAIL_STATE     = 0
    AUTOMATIC      = 1
    MANUAL         = 2
    REMOTE         = 3
    DEMO           = 4
    IDLE           = 5
    RESET          = 6
    PRE_RETURNING  = 7
    RETURNING      = 8
    SLEEPING       = 9
    
    # Valores default  
    ZEN_HOME = 30
    AZI_HOME = 40 
    
    def __init__( self, _debug: bool = False  ) -> None:
        super().__init__()
        self._debug = _debug
        self._database = Database()        
        self.username = ""
        self.email = ""

    @property 
    def database( self ):
        return self._database 
    @property 
    def system( self ):
        return self._system 
    @system.setter 
    def system( self, value ):
        self._system = value  

    def get_sys_time( self ) -> str:
        return    str(
            self.SYSTEM_TABLE['INPUT_HOUR']
        ) + ':' + str(
            self.SYSTEM_TABLE['INPUT_MINUTE']
        ) + ':' + str(
            self.SYSTEM_TABLE['INPUT_SECOND']
        )
    def get_sys_date( self ) -> str:
        return    str(
            self.SYSTEM_TABLE['INPUT_YEAR']
        ) + ':' + str(
            self.SYSTEM_TABLE['INPUT_MONTH']
        ) + ':' + str(
            self.SYSTEM_TABLE['INPUT_DAY']
        )

    def auto_connect( self ):
        return self.database.serial[0]
    
    def serial( self ): 
        return self.database.serial 
    
    def is_connected(self): 
        return self.SYSTEM_TABLE["DISCRETE_CONNECTED"]
             
    def disconnect( self ):
        try:
            self.system.close()
        except:
            pass 

    def connect_device( self, slave: int, port: str, baudrate : int, timeout : int = 1 ) -> bool:
        try:
            if type( baudrate ) != int :
                baudrate = int( baudrate ) 
            if type( timeout ) != int :
                timeout = int( timeout )
            self.system = Device( slave, port, baudrate, timeout = timeout, debug = self._debug  )
            self.connected = self.system.is_connected()
            return self.connected
        except Exception as err :
            if self._debug:
                print( 'System Model error:', err )
            self.connected = False 
            return False 

    # Retorna os valores de posição dos motores 
    def get_motor_pos( self ) -> list | None:
        if self.system is not None:
            return [ self.SYSTEM_TABLE['INPUT_POS_GIR'], self.SYSTEM_TABLE['INPUT_POS_ELE'] ]
        else:
            return None
    
    # Retorna o valor de medição do sensor LDR 
    def get_system_generation( self ) -> float: 
        return ( ( ((2**16)-1) - self.SYSTEM_TABLE['INPUT_GENERATION'] )/((2**16)-1) )*100
    
    def get_azimute_zenite_data( self ) -> list:
        return [
            self.SYSTEM_TABLE['INPUT_ZENITE'],
            self.SYSTEM_TABLE['INPUT_POS_GIR'], 
            self.SYSTEM_TABLE['INPUT_AZIMUTE'],
            self.SYSTEM_TABLE['INPUT_POS_ELE'], 
        ]

    # ---------------------------------------------------------------#
    #                   Files into Login Model                       #
    # ---------------------------------------------------------------# 
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
            self.login_index = ans['id'] 
            self.username = ans['username'] 
            self.last_access = ans['last_access'] 
            self.level_access = ans['level_access'] 
            self.photo = ans['photo']
            if self.__debug:    
                print( f'Login index {self.login_index}' ) 
            return True 
            
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


    # ---------------------------------------------------------------#
    #                   Files into Shared Data Model                 #
    # ---------------------------------------------------------------# 

    def update_date( self, dt = None ):
        self.datetime =  datetime.now().strftime("%H:%M:%S %d/%m/%Y")

    @property
    def datetime( self ): 
        return self._date 
    
    @datetime.setter
    def datetime( self, value : str ):
        self._date = value
         
    @property 
    def time(self):
        return self._date.split(' ')[0]
    
    @property
    def date(self):
        return self._date.split(' ')[1]

    @property
    def connected(self):
        return self._connected    
    
    @connected.setter
    def connected(self, value : bool ) -> None:
        self._connected = value 

    @property
    def username( self ):
            return self._username
     
    @username.setter
    def username( self, value ): 
        self._username = value 

    @property
    def last_access( self ):
        return self._last_access 
    
    @last_access.setter
    def last_access( self, value ): 
        self._last_access = value 

    @property
    def level_access( self ):
        return self._level_access 
    
    @level_access.setter
    def level_access( self, value ): 
        self._level_access = value 

    @property
    def photo( self ):
        return self._photo 
    
    @photo.setter
    def photo( self, value ): 
        self._photo = value 

    @property
    def login_index( self ):
        return self._login_index 
    
    @login_index.setter
    def login_index( self, value ): 
        self._login_index = value 
