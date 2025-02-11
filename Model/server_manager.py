from Model.params_config import SERVER_IP, LOGIN_PORT, SYNC_TIMEOUT, PING_TIMEOUT, CREATE_TIMEOUT
from Model.security_manager import SecurityManager 
from kivy.logger import Logger

import threading
import socket
import json


class ServerManager:
    # Socket de conexão com Servidor 
    __socket: socket.socket | None 
    # Security Manager para criptografia 
    security_manager: SecurityManager 
    connection: bool 
    debug: bool 

    
    def __init__(self, security_manager: SecurityManager | None = None, debug: bool = False):
        if security_manager == None: 
            self.security_manager = SecurityManager( debug )
        else: 
            self.security_manager = security_manager
        self.connection = False
        self.__socket = None
        self.debug = debug


    """
        Estabelece a conexão TCP com o servidor e realiza a troca de chaves simétricas .
    """
    def connect_server(self, clock_event = None ) -> bool:
        try:
            # Sincroniza a chave usando o SecurityManager
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.security_manager.sync_key(self.__socket, SERVER_IP, LOGIN_PORT, SYNC_TIMEOUT):
                if self.debug:
                    Logger.info('Server login sync')
                self.connection = True
                return True
            else:
                if self.debug:
                    Logger.info('Server login not sync')
                self.connection = False
                return False
        # Caso algum erro ocorra
        except socket.error as e:
            if self.debug:
                Logger.warning( f"{e}" )
            self.connection = False
            return False


    """
        Inicia uma thread para manter a conexão ativa com o servidor 
        enviando um comando de PING periodicamente.
    """
    def keep_connection_alive(self, dt = None ):
        thr = threading.Thread( target = self.__keep_connection_alive, args = () )
        thr.start()


    """
        Callback da Thread de Keep Alive:
        1. Se não estiver conectado, tenta conectar 
        2. Se estiver, envia 'PING' e espera a resposta 'PONG'
    """
    def __keep_connection_alive(self):
        if not self.connection:
            self.connect_server()
        else:
            ans = None
            try:
                # Garante que __socket foi instanciado corretamente 
                if isinstance( self.__socket, socket.socket ):
                    ping_data = {'type': 'PING'}
                    # Define o timeout
                    self.__socket.settimeout(PING_TIMEOUT)
                    # Codifica e envia a mensagem
                    data = self.security_manager.encode(ping_data)
                    self.__socket.send(data)
                    # Aguarda resposta
                    raw_ans = self.__socket.recv(1024)
                    ans = self.security_manager.decode(raw_ans)
            # Caso encontre algum erro na conexão  
            except Exception as e:
                if self.debug:
                    Logger.warning( f"{e}" )
                ans = None
            finally:
                if ans == b'PONG':
                    self.connection = True
                    if self.debug:
                        Logger.info("Servidor CONECTADO!!")
                else:
                    if self.debug:
                        Logger.info("Conexão com o servidor PERDIDA!!")
                    self.connection = False


    """
        Realiza o Login com um Usuário e Senha.
        Retorna um dicionário com os dados do usuário se o login for bem-sucedido ou False caso contrário.
    """
    def login(self, user: str, psd: str):
        login_data = {'type': 'LOGIN', 'username': user, 'password': psd}
        try:
            if isinstance( self.__socket, socket.socket ):
                data = self.security_manager.encode(login_data)
                self.__socket.send(data)
                raw_ans = self.__socket.recv(1024)
                ans = self.security_manager.decode(raw_ans)
        # Caso encontre algum erro na conexão 
        except Exception as e:
            if self.debug:
                Logger.warning( f"{e}" )
            return False
        if self.debug:
            Logger.info(f'Socket connection OK\nSend: {data}\nReceived: {ans} of type {type(ans)}')

        # Verifica se houve erro no login
        if ans == b'UNKNOW' or 'error' in ans.decode():
            return False
        else:
            try:
                ans = json.loads(ans.decode())
            except Exception as e:
                if self.debug:
                    Logger.warning( f"{e}" )
                return False
            return ans


    """
        Cria um novo usuário e retorna uma string indicando o status da operação.
    """
    def create_new_user(self, user: str, password: str, manager_group: str, manager_psd: str) -> str:
        create_user_data = {
            'type': 'NEW_USER',
            'username': user,
            'password': password,
            'manager_group': manager_group,
            'manager_psd': manager_psd
        }
        if user and password:
            try:
                if isinstance( self.__socket, socket.socket ):
                    data = self.security_manager.encode(create_user_data)
                    self.__socket.send(data)
                    self.__socket.settimeout(CREATE_TIMEOUT)
                    raw_ans = self.__socket.recv(1024)
                    ans = self.security_manager.decode(raw_ans)
            # Caso encontre algum erro na conexão 
            except socket.error as e:
                if self.debug:
                    Logger.warning( f"{e}" )
                return 'FAIL'
            
            if self.debug:
                Logger.info(f'Socket create new user connection OK\nSend: {create_user_data}\nReceived: {ans}')

            # Retorna o valor recebido pela requisição
            if isinstance(ans, socket.error):
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


    """
        Fecha a conexão do socket
        - Se aberta
    """
    def close(self):
        if isinstance( self.__socket, socket.socket ) and self.__socket:
            self.__socket.close()
            self.__socket = None 
            self.connection = False
