from secure import encode_object, decode_obj, get_sync_unikey 
from database import Database

import _thread
import socket
import time 
import sys
import os 

def multi_threaded_login( connection : socket.socket, __debug : bool = False ):
    ''' Realiza uma conexão segura '''  
    db = Database( os.path.dirname( __file__ ) + '/db/database.db' )
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


def listen_login_connections( IP : str, PORT : str, MAX_CLIENT_CONNECTED : int = 5, __debug : bool = False ):
    ''' Login socket connection listen '''  
    try:
        login = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        login.bind  ( ( IP, PORT ) )
        login.listen( MAX_CLIENT_CONNECTED )
        loginCount = 0 
        if __debug:
            print('Socket login is listening..')
    except socket.error as e:
        if __debug:
            print( str(e) )
        sys.exit()

    while True: 
        client, addr = login.accept()
        _thread.start_new_thread( multi_threaded_login, ( client, __debug, ) )
        loginCount += 1
        if __debug:
            print( f'Connected {addr[0]} with IP {addr[1]}' )
            print('Thread Number: ' + str(loginCount))
        time.sleep(0.001)