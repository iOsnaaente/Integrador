from server_login import listen_login_connections 
from server_app import listen_app_connections 
import _thread 

IP = '127.0.0.1'

MAX_LOGIN_CONNECTED = 5
LOGIN_PORT = 50505 
_thread.start_new_thread( listen_login_connections, ( IP, LOGIN_PORT, MAX_LOGIN_CONNECTED, True, ) ) 

MAX_APP_CONNECTED  = 10 
APP_PORT = 50506
_thread.start_new_thread( listen_app_connections, ( IP, APP_PORT, MAX_APP_CONNECTED, True, ) )

input('Para encerrar a execução pressione enter.')