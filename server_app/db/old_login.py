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

def login(name, password):
    with open(PATH + '/bd/login.csv', 'r') as log:
        lines = log.readlines()[1:]
        print( lines )
        for line in lines:
            id, user, psw = line.replace('\n', '').split(';')
            if name == user and password == psw:
                if DEBUG: print('Find user {} with password {}'.format(name, password))
                return id 
    return False 

def new_user( user, password ):
    if not login( user, password ):
        with open( PATH + '/bd/login.csv', 'r') as log:
            log.seek(0)
            nl = len(log.readlines())
            data = str(nl) + ';' + user + ';' + password + '\n'
        with open( PATH + '/bd/login.csv', 'a') as log:
            log.write( data )
            if DEBUG: print('Criado o usuário {} com senha {} no ID {}'.format(user, password, nl))
            return str(nl)
    else:     
        return False 

def multi_threaded_client(connection):
    while True:
        data = connection.recv(2048).decode()
        if DEBUG:   print('Received: {}'.format(data))
        if not data:
            break
        else:
            try:
                NF, user, password = data.split(';')
                if DEBUG:   print('[{}] User:{}\nPassword:{}'.format(NF, user, password))
                if   NF == 'LGN':   ans = login( user, password )
                elif NF == 'NEW':   ans = new_user(user, password )
                if ans: 
                    if type(ans) == str:
                        connection.send( str.encode(ans) )
                    elif type(ans) == bytearray: 
                        connection.send( ans )
                    else: 
                        pass 
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