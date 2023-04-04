from cryptography.fernet import Fernet
from _thread import *
import hashlib
import socket
import pickle
import hmac

UNIKEY = Fernet.generate_key() 

# Codifica os dados para um byte-array contendo o HASH e os dados binários 
def encode_object( obj : object, encrypted : bool = True, UNIKEY : bytearray = b'', __debug : bool = False ) -> bytes: 
    data = pickle.dumps( obj )
    digest = hmac.new( UNIKEY, data, hashlib.blake2b ).hexdigest()
    if encrypted:
        if UNIKEY != b'':
            f = Fernet( UNIKEY )
            encrypt = f.encrypt( digest.encode() + data )
    if __debug:
        print( f'Encoded {data} with key {UNIKEY}. Hash {digest}' )
        if encrypted:
            print( f'Encrypted { encrypt }' )
    if not encrypted:
        return digest.encode() + data
    else: 
        return encrypt

# Verifica recebimento dos dados 
def decode_object( data : bytearray, signature_len : int = 128, encrypted : bool = True, UNIKEY : bytearray = b'', __debug : bool = False ) -> object:
    if encrypted:
        if UNIKEY != b'':
            f = Fernet( UNIKEY )
            data = f.decrypt( data )
    digest, data = data[:signature_len], data[signature_len:]
    import secrets
    expected_digest = hmac.new( UNIKEY, data, hashlib.blake2b ).hexdigest()
    if not secrets.compare_digest( digest, expected_digest.encode() ):
        if __debug: 
            print('Invalid signature')
        return False 
    else: 
        if __debug:
            print( 'Right signatures')
        return pickle.loads( data )

# Sincroniza a chave de criptografia 
def sync_unikey( sock : socket.socket, IP : str, LOGIN_PORT : int , UNIKEY : bytearray, timeout : float = 1, __debug : bool = False ):
    if __debug: 
        print( 'Unique key based in Fernet', UNIKEY, type(UNIKEY), len(UNIKEY) )
    sock.settimeout( timeout )
    try: 
        sock.connect( (IP, LOGIN_PORT) )
        if __debug:     
            print( f'Client connected at {IP}:{LOGIN_PORT}\nSync unique key session with key {UNIKEY}')
        sock.send( UNIKEY )
        DATA = sock.recv( 1024 )   
        data = decode_object( DATA, UNIKEY = UNIKEY ) 
        if __debug: 
            print( f'sock.recv {DATA}\nDecrypted:{data}' )
        if data == b'SYNC':
            return True 
        else:     
            return False 
    except socket.error as e:
        if __debug: 
            print( 'Socket error:', e )
        return False 
    

if __name__ == '__main__':
    # 1º Cria o soquete 
    client = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    # 2º Cria uma UNIQUE KEY 
    KEY = Fernet.generate_key()
    # 3º Sincroniza a Unique Key com o servidor 
    IP = '127.0.0.1'
    PORT = 50505
    sync = sync_unikey( client, IP, PORT, UNIKEY = KEY, __debug = True )
    print( 'Sync state: ', sync )
    # 4º Pegar ou gerar os dados a serem transmitidos 
    # db = Database( PATH + '\\db\\database.db' )
    login_struct = {
        'tyse'    : 'LOGIN',
        'username': 'Bruno',
        'password': '12051999',
        'family'  : ''
    }
    # 4º Faz o encode do objeto que será transmitido e habilite a criptografia 
    data = encode_object( login_struct, encrypted = True, UNIKEY = KEY )
    # 5º Envie ou salve o byte-array 
    client.sendall( data )
    # 6º Receba o byte-array
    recv = client.recv(15000)
    # 7º Cheque se ele esta de correto 
    obj = decode_object( recv, UNIKEY = KEY )
    # 8º Se estiver, então pode usar o objeto normalmente com as mesmas propriedades 
    print( obj )