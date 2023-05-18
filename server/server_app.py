from secure import encode_object, decode_obj, get_sync_unikey
from database import Database

import _thread 
import socket 
import time
import sys 
import os 

# Modelo de requisição do cliente 
app_model = {
    'code' : '',
    'data' : {}
}
# Modelo de resposta do servidor
app_answere = {
    'code' : '',
    'answere' : {}
}

def multi_threaded_app( connection : socket.socket, __debug : bool = False ): 
    ''' Servidor da aplicação. Gerencia as requisições do app'''  
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
                        if 'code' in obj and 'data' in obj:         
                            print( f'Object received with code:{obj["code"]}\ndata:{obj["data"]}' )            
                    #
                    # 
                    if 'code' in obj:
                        if obj['code'] == 'TEST': 
                            print('Code test received') 
                    #
                    #
                    else:
                        ans = 'UNKNOW'
                    ans = encode_object( ans.encode(), UNIKEY = UNIKEY_SESION, __debug = __debug )
                    connection.send( ans )
            except:
                if __debug:
                    print( 'Object wasnt in app_struct format or invalid content' ) 
                break
        else:
            if __debug:
                print( 'Socket connection closed' ) 
            break
    connection.close()    

def listen_app_connections( IP : str, PORT : str, MAX_CLIENT_CONNECTED : int = 5, __debug : bool = False ):
    ''' Listen de login socket connection '''  
    try:
        app = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        app.bind  ( ( IP, PORT ) )
        app.listen( MAX_CLIENT_CONNECTED )
        loginCount = 0 
        if __debug:
            print('Socket app is listening..')
    except socket.error as e:
        if __debug:
            print( str(e) )
        sys.exit()

    while True: 
        client, addr = app.accept()
        _thread.start_new_thread( multi_threaded_app, ( client, __debug, ) )
        loginCount += 1
        if __debug:
            print( f'Connected {addr[0]} with IP {addr[1]}' )
            print( f'Thread Number: {str(loginCount)}' )
        time.sleep(0.001)