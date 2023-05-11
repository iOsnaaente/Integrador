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
        '''Recebe uma mensagem criptografada'''
        data = connection.recv(2048).decode()
        if __debug:
            print( 'Received encrypted data' )
        if data:
            try:
                obj = decode_obj( data, UNIKEY = UNIKEY_SESION, __debug = __debug )
                if type(obj) == dict:
                    if __debug:
                        print( f'Data received: {obj} of type {type(obj)}' )            
                    

                        ''' Sistema de login OK '''
                    if obj['type'] == 'LOGIN': 
                        ans = db.login( obj['username'], obj['password'], True )
                    

                        ''' Sistema de criação de novo usuário OK '''
                    elif obj['type'] == 'NEW_USER':
                        ans = db.create_new_user( obj['manager_group'], obj['manager_psd'], obj['username'], obj['password'], True)
                        if ans:     ans = db.login( obj['username'], obj['password'], True )
                        else:       ans = 'FAILED'
                    
                    
                    elif obj['type'] == 'NEW_MAN': 
                        # ans = db.create_new_manager() 
                        ans = 'UNKONW'
                    elif obj['type'] == 'CHANGE': 
                        ans = 'UNKNOW'                    
                    else:
                        ans = 'UNKNOW'
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