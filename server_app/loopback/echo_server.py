import _thread
import socket

IP = '127.0.0.1'
LOGIN_PORT = 50505 
APLICATION_PORT =  50506
MAX_CONNECTION = 1


def listen_socket( sock : socket.socket, sock_name : str ): 
    print( f'Init socket echo named: {sock_name}')
    while True: 
        connection, addr = sock.accept()
        print( f'[{sock_name}]Connected {addr[0]} with IP {addr[1]}' )
        while True:
            data = connection.recv( 10240 )        
            if not data:
                break 
            else: 
                print( data )
                connection.send( data )


if __name__ == '__main__':
    echo_app = socket.socket(  socket.AF_INET, socket.SOCK_STREAM )
    echo_app.bind( (IP, APLICATION_PORT) ) 
    echo_app.listen( MAX_CONNECTION )
    _thread.start_new_thread( listen_socket, ( echo_app, 'ECHO APP', ) )

    echo_login = socket.socket(  socket.AF_INET, socket.SOCK_STREAM )
    echo_login.bind( (IP, LOGIN_PORT) ) 
    echo_login.listen( MAX_CONNECTION )
    listen_socket( echo_login, 'ECHO LOGIN' )