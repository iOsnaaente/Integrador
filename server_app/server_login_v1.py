from database import Database
from _thread import *
import socket 
import time
import os 

PATH = os.path.dirname( __file__ )

server = socket.socket()
ThreadCount = 0

IP, PORT = '127.0.0.1', 50505
DEBUG = True 

try:
    server.bind((IP, PORT))
except socket.error as e:
    print(str(e))
print('Socket is listening..')

server.listen(5)
ThreadCount = 0 


def multi_threaded_client(connection):
    db = Database( PATH + '\\db\\database.db' )
    while True:
        data = connection.recv(2048).decode()
        if DEBUG:       
            print('Received: {}'.format(data))
        if not data:    
            break
        else:
            try:
                NF, user, password, family = data.split(';')
                if DEBUG:           
                    print('[{}] User:{} \ Password:{} \ From family: {}'.format(NF, user, password, family))                
        
                if   NF == 'LGN':   
                    ans = db.login( user, password )
                elif NF == 'NEW':   
                    ans = db.create_user( user, password, family )
                
                if ans: 
                    if type(ans) == str:            connection.send( ans.encode() )
                    elif type(ans) == int:          connection.send( str(ans).encode() )
                    elif type(ans) == bytearray:    connection.send( ans )
                    else:                           pass 
                
                if DEBUG:           
                    print( 'Resposta: ', ans )
            except:
                pass 
    connection.close()

while True: 
    client, (cltIP, cltPORT) = server.accept()
    print( 'Connected {} with IP {} '.format(cltIP, cltPORT))
    start_new_thread( multi_threaded_client, (client, ) )
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))
    time.sleep(0.001)

server.close()