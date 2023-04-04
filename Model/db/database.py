import sqlite3 
import os 

PATH = os.path.dirname( __file__ )

class Database: 
    def __init__( self ) -> None:
        self.con = sqlite3.connect( PATH + '/db_keeper.db' )
        self.cursor = self.con.cursor()
        self.create_login_table() 

    def create_login_table( self ): 
        self.cursor.execute( '''CREATE TABLE IF NOT EXISTS 
        login( 
            id integer PRIMARY_KEY_AUTOINCREMENT, 
            state VARCHAR(5), 
            user VARCHAR(32),  
            password VARCHAR(32)
            )''' 
                            )
      
        if self.cursor.execute('SELECT * FROM login ').fetchall() == []:
            self.cursor.execute( '''INSERT INTO login ( id, state, user, password) VALUES (?,?,?,?)''', (0, 'NORMAL', '', '' ) )
            self.con.commit() 
        
    def set_login_table(self, state = 'NORMAL', user = None, psd = None ): 
        self.cursor.execute( ''' UPDATE login SET state=?, user=?, password=? WHERE id = 0 ''', ( state, user, psd ) )
        self.con.commit()

    def get_login_table( self ):
        return self.cursor.execute( 'SELECT * FROM login').fetchall()

