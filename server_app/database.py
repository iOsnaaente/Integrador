import sqlite3 

class Database: 
    def __init__(self, path ) -> None:
        self.con = sqlite3.connect( path )
        self.path = path
        self.cursor = self.con.cursor()
        self.create_tables() 

    def create_tables( self ): 
        # Cria tabela de familia 
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS 
                family( 
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(24) NOT NULL
                )
            ''')
        # Cria tabela de membros
        self.cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS 
                members(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(24) NOT NULL,
                    username VARCHAR(24) NOT NULL,
                    password VARCHAR(24) NOT NULL,
                    family_id INTEGER NOT NULL,
                    profit float,
                    photo blob,
                    FOREIGN KEY (family_id) REFERENCES family (id)
                )
            '''
        )
        # Cria tabela Gasto
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS 
                spendings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cat VARCHAR(50) NOT NULL,
                    value FLOAT NOT NULL,
                    date_buy DATE NOT NULL,
                    member_id INTEGER NOT NULL,
                    FOREIGN KEY (member_id) REFERENCES members (id)
                )
            '''
        )
        self.con.commit() 


    def create_user( self, name : str, user : str, password : str, family_name : str, __debug : bool = False ) -> bool:
        # Procura o ID de um usuário com o mesmo username 
        self.cursor.execute( 'SELECT id FROM members WHERE username = ?', ( user, ) )
        has_user = self.cursor.fetchall()
        # Se encontrar um ID então já existe usuário com esse username
        if has_user:
            if __debug:
                print( f'Username already registered at {user}')
            return False
        # Caso contrário deve criar um novo
        else:  
            # Pega o ID da familia se ela existir 
            self.cursor.execute( "SELECT id FROM family WHERE name = ?", ( family_name, ) )
            family_id = self.cursor.fetchone() 
            # Se não existe então cria uma nova familia 
            if not family_id: 
                if __debug:
                    print(f'Family dont exist. Creating {family_name} family.')
                self.cursor.execute( 'INSERT INTO family(name) VALUES (?)', (family_name, ) )
                self.con.commit() 
            # Pega o novo ID da familia 
            self.cursor.execute( "SELECT id FROM family WHERE name = ?", ( family_name, ) )
            family_id = self.cursor.fetchone() 
            # Adiciona o novo membro dentro da tabela
            self.cursor.execute( 'INSERT INTO members( name, username, password, family_id ) VALUES(?,?,?,?)', ( name, user, password, family_id[0]) )
            self.con.commit()
            if __debug:
                print(f'Username {user} registered.')
        return True


    def login( self, user : str, password : str, __debug : bool = False ) -> bool:
        # Procura a senha do usuário cadastrado com o username 
        self.cursor.execute( 'SELECT password FROM members WHERE username = ?', ( user, ) )
        user_data = self.cursor.fetchall()
        # Se não há nenhum usuário cadastrado, não retorna nada 
        if not user_data: 
            if __debug:
                print( f'Não possui nenhum usuário cadastrado como {user}')
            return False 
        # Se não, basta comparar as senhas
        if user_data[0][0] == password:
            if __debug:   
                print( f'Username {user} found and psd check' )
            return True 
        else:
            if __debug:
                print( f'Username {user} and psd dont check')
            return False


    def add_spending( self, username : str, value : float, type : str, date_buy : str, __debug : bool = False ) -> bool:
        # Pega o ID do usuário 
        self.cursor.execute( 'SELECT id FROM members WHERE username = ?', ( username, ) )
        user_id = self.cursor.fetchall()
        if not user_id: 
            return False 
        else: 
            # Seleciona o valor dentro da lista 
            user_id = user_id[0][0]
            # Adiciona o gasto na lista de usuário
            self.cursor.execute( 'INSERT INTO spendings( cat, value, data_buy, member_id ) VALUES (?,?,?,?)', ( type, value, date_buy, user_id ) )
            self.con.commit() 
            if __debug:
                print( f'Spending registered: [{type}] R${value} at {date_buy}')
            return True
         

    def get_family_profit( self, family_name : str, __debug : bool = False ) -> float:
        # Inicia pegando o valor do ID da familia 
        self.cursor.execute( 'SELECT id FROM family WHERE name = ? ', ( family_name, ) )
        family_id = self.cursor.fetchall() 
        # Se não existir familia, retorna false 
        if not family_id:
            if __debug:
                print( f'{family_name} id not found')
            return False 
        else: 
            # Se não, pega todos os salários dos membros da familia
            family_id = family_id[0][0]
            self.cursor.execute( 'SELECT profit FROM members WHERE family_id = ?', ( family_id, ) ) 
            profits = self.cursor.fetchall() 
            # Realiza a soma dos salários 
            profit_sum = 0 
            for profit in profits:
                if profit[0]:
                    profit_sum += profit[0]
                else: 
                    continue
            return profit_sum
    
    def get_total_family_spending( self, family_name : str, start_date : str = '', end_date : str = '', __debug : bool = False ) -> float:
        # Inicia pegando o valor do ID da familia 
        self.cursor.execute( 'SELECT id FROM family WHERE name = ? ', ( family_name, ) )
        family_id = self.cursor.fetchall() 
        # Se não existir familia, retorna false 
        if not family_id:
            if __debug:
                print( f'{family_name} id not found')
            return False 
        else: 
            # Se não, pega todos os IDs dos membros da familia
            self.cursor.execute( 'SELECT id FROM members WHERE family_id = ?', ( family_id[0][0], ) ) 
            members_ids = self.cursor.fetchall() 
            spendings_sum = 0 
            for member in members_ids:
                # Realiza a soma dos gastos de cada membro da familia SEM delimitação de datas 
                if not start_date:
                    self.cursor.execute( 'SELECT value FROM spendings WHERE member_id = ?', (member[0], ) )
                # Realiza a soma dos gastos de cada membro da familia COM delimitação de datas 
                else: 
                    self.cursor.execute( 'SELECT value FROM spendings WHERE date_buy BETWEEN ? AND ? AND member_id = ?', (start_date, end_date, member[0], ) )
                spendings = self.cursor.fetchall() 
                for spending in spendings:
                    spendings_sum += spending[0] 
            return spendings_sum 
        

    def get_member_spending( self, username : str, start_date : str = '', end_date : str = '', __debug : bool = False ) -> float:
        self.cursor.execute( 'SELECT id FROM members WHERE username = ?', ( username,  ) )
        member_id = self.cursor.fetchall() 
        if not member_id:
            if __debug:
                print( f'{username} id not found')
            return False 
        else: 
            spendings_sum = 0
            # Realiza a soma dos gastos do usuário SEM delimitação de datas 
            if not start_date:
                self.cursor.execute( 'SELECT value FROM spendings WHERE member_id = ?', ( member_id[0], ) ) 
            # Realiza a soma dos gastos do usuário COM delimitação de datas 
            else: 
                self.cursor.execute( 'SELECT value FROM spendings WHERE date_buy BETWEEN ? AND ? AND member_id = ?', (start_date, end_date, member_id[0], ) ) 
            for spending in self.cursor.fetchall():
                spendings_sum += spending[0]
            return spendings_sum 
        
    def get_photo( self, username : str, __debug : bool = False ) -> bytearray:
        try: 
            self.cursor.execute( 'SELECT photo FROM members WHERE username = ?', ( username, ) )
            photo =  self.cursor.fetchall()[0]
            if __debug: 
                print( f'[{username}] A photo has found')
            return photo
        except:
            print( f'{username} dont have a photo updated. Can use datebase.att_photo method.')
            return False 
        

    def att_profit( self, username : str, value : float, __debug : bool = False ) -> bool:
        try: 
            # Apenas faz o UPDATE do profit no lugar onde há o username 
            self.cursor.execute( 'UPDATE members SET profit = ? WHERE username = ?', ( value, username, ))
            self.con.commit()
            if __debug: 
                print( f'Username {username} has the nem profit {value}')
            return True 
        except:
            if __debug: 
                print( f'Not found the username {username}')
            return False 
        

    def att_photo( self, username : str, photo : bytearray, __debug : bool = False ) -> bool:
        try: 
            # Apenas faz o UPDATE de photo no lugar onde há o username 
            self.cursor.execute( 'UPDATE members SET photo = ? WHERE username = ?', ( photo, username, ))
            self.con.commit()
            if __debug: 
                print( f'Username {username} has a nem photo')
            return True 
        except:
            if __debug: 
                print( f'Not found the username {username}')
            return False 


if __name__ == '__main__':
    db = Database('db\\database_2.db') 
    print( db.create_user( 'Bruno', 'ios', '123', 'Sampaio', True))
    print( db.login( 'iosnaaente', '123' ) ) 
    print( db.add_spending('iosnaaente', 150, 'food', '12/05/1999' )  )
    db.att_profit( 'iosnaaente', 1500 )
    print( db.get_family_profit( 'Sampaio', True ) )  