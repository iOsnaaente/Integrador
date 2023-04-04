from cryptography.fernet import Fernet
from database import Database

import _thread 
import hashlib
import socket
import pickle
import hmac
import time 
import sys
import os 

PATH = os.path.dirname( __file__ )

MAX_CLIENT_CONNECTED = 5
DEBUG = True 

IP = '127.0.0.1'
LOGIN_PORT = 50505 


# Verifica recebimento dos dados 
def decode_obj( data : bytearray, signature_len : int = 128, encrypted : bool = True, UNIKEY : bytearray = b'', __debug : bool = False ) -> object:
    if encrypted:
        if UNIKEY != b'':
            f = Fernet( UNIKEY )
            data = f.decrypt( data )
            if __debug: 
                print( f'Data decrypted received {data}')
        else:         
            if __debug: 
                print( f'UNIQUE KEY not set [{UNIKEY}]' )
            return False 
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


# Codifica os dados para um byte-array contendo o HASH e os dados binários 
def encode_object( obj : object, encrypted : bool = True, UNIKEY : bytearray = b'', __debug : bool = False ) -> bytes: 
    data = pickle.dumps( obj )
    digest = hmac.new( UNIKEY, data, hashlib.blake2b ).hexdigest()
    to_send = digest.encode() + data
    if encrypted:
        encrypt = to_send 
        try:
            f = Fernet( UNIKEY )
            encrypt = f.encrypt( to_send )
        except:
            if __debug:
                print( 'UNIQUE KEY is not valid\nNot encrypted data' )
    if __debug:
        print( f'Encoded {data} with key {UNIKEY}. Hash {digest}' )
        if encrypted and UNIKEY != b'':
            print( f'Encrypted { encrypt }' )
    if not encrypted:
        return to_send
    else: 
        return encrypt
    

# Sincroniza a chave de criptografia para a conexão
def get_sync_unikey( connection : socket.socket, __debug : bool = False ):
    if __debug: 
        print( 'Waiting for a key...' )
    try: 
        data = connection.recv( 1024 )    
        ans  = encode_object( b'SYNC', UNIKEY = data )
        connection.send( ans )
        if __debug: 
            print( f"UNIQUE KEY set at: {data}\nAnswered b'SYNC' with encrypt: {ans}" )
        return data 
    except socket.error as e:
        if __debug: 
            print( 'Socket error:', e )
        return False 


# Realiza uma conexão segura 
def multi_threaded_login( connection : socket.socket, __debug : bool = False ):
    db = Database( PATH + '\\db\\database.db' )
    UNIKEY_SESION = get_sync_unikey( connection, __debug = __debug )
    while True:
        data = connection.recv(2048).decode()
        if __debug:
            print('Received: {}'.format(data))
        if data:
            '''Recebe uma mensagem criptografada'''
            try:
                obj = decode_obj( data, UNIKEY = UNIKEY_SESION, __debug = __debug )
                if type(obj) == dict:
                    if __debug:
                        # obj must be like login_struct
                        if 'type' in obj and 'username' in obj and 'password' in obj and 'family' in obj:         
                            print( f'Object received: type:{obj["type"]}\nusername:{obj["username"]}\npassword:{obj["password"]}\nfamily:{obj["family"]}' )            
                    if 'type' in obj:
                        if obj['type'] == 'LOGIN':
                            ans = db.login( user = obj['username'], password = obj['password'], DEBUG = __debug )
                        elif obj['type'] == 'NEW USER':
                            ans = db.create_user( user = obj['username'], password = obj['password'], family = obj['family'] )
                    else:
                        ans = 'UNKNOW'
                    ans = encode_object( ans.encode(), UNIKEY = UNIKEY_SESION, __debug = __debug )
                    connection.send( ans )
            except:
                if __debug:
                    print( 'Object wasnt in login_struct format or invalid content' ) 
                break
        else:
            if __debug:
                print( 'Socket connection closed' ) 
            break
    connection.close()


# Listen de login socket connection 
def listen_login_connections():
    try:
        login = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        login.bind  ( ( IP, LOGIN_PORT ) )
        login.listen( MAX_CLIENT_CONNECTED )
        loginCount = 0 
        print('Socket login is listening..')
    except socket.error as e:
        print( str(e) )
        sys.exit()

    while True: 
        client, addr = login.accept()
        _thread.start_new_thread( multi_threaded_login, (client, True, ) )
        print( f'Connected {addr[0]} with IP {addr[1]}' )
        loginCount += 1
        print('Thread Number: ' + str(loginCount))
        time.sleep(0.001)


if __name__ == '__main__':
    listen_login_connections()