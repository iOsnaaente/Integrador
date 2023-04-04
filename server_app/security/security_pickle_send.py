from cryptography.fernet import Fernet
import hashlib
import pickle
import hmac
import os 

PATH = os.path.dirname( __file__ )
UNIKEY = Fernet.generate_key() 

MAX_CLIENT_CONNECTED = 5
LOGIN_PORT = 50505 
IP = '127.0.0.1'
DEBUG = True 


# Codifica os dados para um byte-array contendo o HASH e os dados binários 
def encode_object( obj : object, encrypted : bool = True, __debug : bool = False ) -> bytes: 
    data = pickle.dumps( obj )
    digest = hmac.new( UNIKEY, data, hashlib.blake2b ).hexdigest()
    if encrypted:
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
def check_recv( data : bytearray, signature_len : int = 128, encrypted : bool = True, __debug : bool = False ) -> object:
    if encrypted:
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
    
    

  

if __name__ == '__main__':

    # Dummy class para exemplos
    class Dummy:
        def __str__(self) -> str:
            print('Dammy class for examples')
      
    # 1º Pegar ou gerar os dados a serem transmitidos
    obj_to_send = Dummy()

    # 2º Faz o encode do objeto que será transmitido e habilite a criptografia ou não 
    data = encode_object( obj_to_send,  encrypted = True, __debug = True )
    
    # 3º Salvar ou enviar o byte-array 
    with open( PATH + '/temp.bin', 'wb') as output:
        output.write( data )

    # Lado Cliente 
    # ---------------------------------------------------------------------#
    # Lado Servidor 

    # 4º Pegar os dados binários 
    with open( PATH + '/temp.bin', 'rb') as file:
        data = file.read()
    
    # 5º Cheque se ele esta de correto 
    obj = check_recv( data,  __debug = True )
    
    # 6º Se estiver, então pode usar o objeto normalmente com as mesmas propriedades 
    print( obj.__str__() )