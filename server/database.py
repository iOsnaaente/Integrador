import datetime 
import sqlite3 
import json
import pytz 
import os 

class Database: 
    def __init__(self, path ) -> None:
        self.con = sqlite3.connect( path )
        self.path = path
        self.cursor = self.con.cursor()
        self.create_tables() 

    def create_tables( self ):
        # Cria tabela de gerenciador e nível de acesso
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS 
                manager (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    manager_group VARCHAR(32) NOT NULL,
                    password VARCHAR(32) NOT NULL,
                    level_access INTEGER NOT NULL
                )
            '''             
        )
        # Cria tabela de usuários
        self.cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS 
                user(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(24) NOT NULL,
                    password VARCHAR(24) NOT NULL,
                    last_access date NOT NULL,
                    name VARCHAR(24) NOT NULL,
                    photo blob,
                    manager_id integer NOT NULL,
                    FOREIGN KEY (manager_id) REFERENCES manager (id)
                )
            '''
        )
        self.con.commit() 

    def create_new_user( self, manager_group : str, manager_psd : str, username : str, psd : str, name : str, __debug : bool = False ) -> bool:
        # Primeiro verifica se o manager possui as credenciais 
        self.cursor.execute( 'SELECT id FROM manager WHERE manager_group = ? AND password = ?', (manager_group, manager_psd, ) )
        manager_id = self.cursor.fetchall() 
        if not manager_id:
            if __debug:
                print( 'Manager not found or password incorrect' )
            return False 
        else: 
            # Procura o ID de um usuário com o mesmo username 
            self.cursor.execute( 'SELECT id FROM user WHERE username = ?', ( username, ) )
            has_user = self.cursor.fetchall()
            # Se encontrar um ID então já existe usuário com esse username
            if has_user:
                if __debug:
                    print( f'Username already registered at { username }')
                return False
            # Caso contrário deve criar um novo
            else:  
                last_access = self.get_date_now() 
                manager_id = manager_id[0][0]
                self.cursor.execute( 'INSERT INTO user(username, password, last_access, name, manager_id ) VALUES (?,?,?,?,?)', ( username, psd, last_access, name, manager_id ,) )
                self.con.commit()
                if __debug:
                    print(f'Username {username} registered.')
                return True 
            
    def create_new_manager( self, group : str, password : str, level_access : int, __debug : bool = False ):
        # Procura o ID de um usuário com o mesmo username 
        self.cursor.execute( 'SELECT id FROM manager WHERE manager_group = ?', ( group, ) )
        has_manager = self.cursor.fetchall()
        # Se encontrar um ID então já existe usuário com esse username
        if has_manager:
            if __debug:
                print( f'Manager already registered like { group }' )
            return False
        # Caso contrario adionar um novo gerenciador
        else: 
            self.cursor.execute( 'INSERT INTO manager( manager_group, password, level_access ) VALUES (?,?,?)', ( group, password, level_access ,) )
            self.con.commit()
            if __debug:
                print(f'Manager {group} registered.')
            return True             

    def login( self, username: str, password: str, __debug: bool = False) -> str:
        # Pega os dados de usuário caso ele exista 
        self.cursor.execute('''
            SELECT user.*, manager.level_access 
                FROM user 
                    INNER JOIN manager ON user.manager_id = manager.id 
                WHERE user.username = ? AND user.password = ?
            ''', 
            (username, password, ) 
        )
        result = self.cursor.fetchone()
        # Verifica se foi encontrado um usuário ou não 
        if not result:
            if __debug:
                print(f"User {username} not found or password incorrect")
            return json.dumps({"error" : "User not found or password incorrect" } )

        user_dict = {
            "id": result[0],
            "username": result[1],
            "password": result[2],
            "last_access": result[3],
            "name": result[4],
            "photo": result[5].hex() if result[5] else None,
            "manager_id" : result[6],
            "level_access": result[7]
        }
        # Atualiza o ultimo acesso 
        self.set_user_last_access( username ) 

        if __debug:
            print(f"User {username} logged in successfully")
        # Retorna o Json 
        return json.dumps(user_dict)

    def get_date_now( self, utc : str = 'America/Sao_Paulo' ):
        # pytz cria um objeto timezone nos moldes do datetime 
        timezone = pytz.timezone( utc )
        # Retorna no modelo YYYY-MM-DD usado pelo sqlite3
        return datetime.datetime.now( tz = timezone ).strftime('%Y-%m-%d %H:%M:%S')
        
    def get_user_level_access( self, username : str, __debug : bool = False  ) -> int: 
        # Procura o ID do manager dentro do usuário definido 
        self.cursor.execute( 'SELECT manager_id FROM user WHERE username = ?', ( username, ) )
        manager_id =  self.cursor.fetchall()
        try:
            # Após, basta procurar o level access do manager associado 
            self.cursor.execute( 'SELECT level_access FROM manager WHERE id = ?', (manager_id[0][0],))
            level_access = self.cursor.fetchall()
            if __debug: 
                print( f'[{username}] Manager {manager_id[0][0]} has {level_access[0][0]} level access')
            return level_access[0][0]
        except:
            if __debug: 
                print( f'Error. Username not found' )
            return False 
    
    def get_user_photo( self, username : str, __debug : bool = False ) -> bytearray:
        # Procura a foto dentro do usuário definido 
        self.cursor.execute( 'SELECT photo FROM user WHERE username = ?', ( username, ) )
        photo =  self.cursor.fetchall()
        if not photo:
            if __debug: 
                print( f'{username} dont have a photo updated. Can use datebase.att_photo method.')
            return False 
        else: 
            if __debug: 
                print( f'[{username}] A photo has found')
            return photo[0][0]
         
    def set_user_photo( self, username : str, photo : bytearray, __debug : bool = False ) -> bool:
        # Apenas faz o UPDATE de photo no lugar onde há o username 
        self.cursor.execute( 'UPDATE user SET photo = ? WHERE username = ?', ( sqlite3.Binary( photo ), username, ))
        self.con.commit()
        if __debug: 
            print( f'Username {username} has a nem photo')
        return True 

    def set_user_last_access( self, username : str, __debug : bool = False ) -> bool:
        last_access = self.get_date_now() 
        self.cursor.execute( 'UPDATE user SET last_access = ? WHERE username = ? ', (username, last_access, ) ) 
        self.con.commit() 
        if __debug: 
            print( f'Username {username} updated last access: {last_access}')
        return True 

# Teste de uso 
if __name__ == '__main__':
    db = Database( os.path.dirname(__file__) + '/db/database.db') 
    db.create_new_manager( 'sup', 'sup123', 10, True )
    db.create_new_user( 'sup', 'sup123', 'iosnaaente', '1205', 'BrunoSup', True )
    db.get_user_level_access( 'iosnaaente', True )
    print( db.login( 'iosnaaente', '1205', True ) )
    
    db.create_new_manager( 'adm', 'adm123',  1, True )
    db.create_new_user( 'adm', 'adm123', 'iOsnaaenteAdm', '1205', 'BrunoAdm', True )
    db.get_user_level_access( 'iOsnaaenteAdm', True )
    print( db.login( 'iOsnaaenteAdm', '1205', True ) )