from cryptography.fernet import Fernet

import hashlib
import socket
import pickle
import hmac

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