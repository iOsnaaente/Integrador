import sqlite3 

class Database: 
    def __init__(self, path ) -> None:
        self.con = sqlite3.connect( path )
        self.path = path
        self.cursor = self.con.cursor()
        self.create_tables() 

    def create_tables( self ): 
        self.cursor.execute( '''CREATE TABLE IF NOT EXISTS 
        users( 
            id integer PRIMARY_KEY_AUTOINCREMENT, 
            user varchar(24) NOT NULL, 
            password varchar(50) NOT NULL, 
            family varchar(50) 
            )''' 
                            )
        self.cursor.execute( '''CREATE TABLE IF NOT EXISTS 
        family( 
            id integer PRIMARY_KEY_AUTOINCREMENT, 
            family_name varchar(50) NOT NULL, 
            renda double NOT NULL 
            )'''
                            )
        self.con.commit() 

    def create_user( self, user : str, password : str, family : str ) -> str:
        self.cursor.execute( 'SELECT * FROM users')
        users = self.cursor.fetchall()
        nl = len(users)
        for usr in users:
            if usr[1] == user:
                return 'False' 
        self.cursor.execute('''INSERT INTO users( id, user, password, family ) VALUES(?,?,?,?)''', (nl, user, password, family) )
        self.con.commit()
        return str(nl) 

    def login( self, user : str, password : str, DEBUG : bool = False ) -> str:
        users = self.cursor.execute( 'SELECT * FROM users').fetchall()
        for usr in users:
            if DEBUG:   print( usr )
            if usr[1] == user and usr[2] == password:
                if DEBUG:   print( 'User find. [{}]: {} / {} / {}'.format(*usr) )
                return str(usr[0])
        return 'False' 


if __name__ == '__main__':
    db = Database('db\\database.db') 
    # db.create_user( 'ios', '123', 'iOsnaaente')
    print( db.login( 'ios', '123' ) ) 
