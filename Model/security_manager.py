from libs.Security          import encode_object, decode_object, sync_unikey
from Model.params_config    import SYNC_TIMEOUT, LOGIN_PORT, SERVER_IP 
from cryptography.fernet    import Fernet 
import socket

class SecurityManager:
    # Fenet.generate_key 
    key: bytes 

    # Debug 
    debug: bool

    """ Construtor """
    def __init__(self, _debug: bool = False ):
        self.key = Fernet.generate_key()
        self.debug = _debug
    
    """ 
        Codifica o obj com a chave Fernet Gerado no Construtor 
    """
    def encode(self, obj: object ) -> bytes:
        return encode_object( obj, UNIKEY = self.key )
    
    """ 
        DECodifica os dados recebidos usando a chave gerada no Construtor 
    """
    def decode(self, data: bytes ) -> bytes:
        return decode_object(data, UNIKEY = self.key)
    
    """ 
        Realiza a troca de chaves via TCP (sync) para estabelecer a 
        conexão segura e ambas as partes terem acesso à chave simétrica
        Retorna True se a Sync ocorreu bem. False caso contrário
    """
    def sync_key(self, sock: socket.socket, server: str = SERVER_IP, port: int = LOGIN_PORT, timeout: int = 1 ) -> bool:
        return sync_unikey(sock, server, port, self.key, timeout = SYNC_TIMEOUT )
    