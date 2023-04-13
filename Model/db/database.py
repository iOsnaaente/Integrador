import sqlite3 
import os 

PATH = os.path.dirname( __file__ )

class Database: 
    def __init__( self ) -> None:
        self.con = sqlite3.connect( PATH + '/db_keeper.db' )
        self.cursor = self.con.cursor()
        self.create_login_table() 

    def create_login_table( self ): 
        self.cursor.execute( 
            '''CREATE TABLE IF NOT EXISTS 
                login( 
                    id integer PRIMARY KEY AUTOINCREMENT, 
                    state VARCHAR(5), 
                    user VARCHAR(32),  
                    password VARCHAR(32)
                )
            ''' 
        )
        self.cursor.execute(
            '''
                CREATE TABLE IF NOT EXISTS
                    serial(
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        state VARCHAR(1),
                        comport TEXT, 
                        baudrate TEXT, 
                        timeout TEXT
                    )
            '''
        )
      
        if self.cursor.execute('SELECT * FROM login ').fetchall() == []:
            self.cursor.execute( '''INSERT INTO login ( id, state, user, password) VALUES (?,?,?,?)''', (0, 'NORMAL', '', '' ) )
        if self.cursor.execute('SELECT * FROM serial' ).fetchall() == []:
            self.cursor.execute('''INSERT INTO serial ( state, comport, baudrate, timeout) VALUES (?,?,?,?)''', ( 'F', 'COM3', '9600', '1' ) )
        self.con.commit() 
        
    @property
    def login( self ):
        return self.cursor.execute( 'SELECT * FROM login WHERE id = 0').fetchall()
    
    def set_login(self, state = 'NORMAL', user = None, psd = None ): 
        self.cursor.execute( ''' UPDATE login SET state=?, user=?, password=? WHERE id = 0 ''', ( state, user, psd ) )
        self.con.commit()
    
    @property 
    def serial( self ):
        return self.cursor.execute( 'SELECT * FROM serial WHERE id = 1').fetchall()
    
    def set_serial( self, state : str, comport : str, baudrate : str, timeout : str ):
        self.cursor.execute( '''UPDATE serial SET state=?, comport=?, baudrate=?, timeout=? WHERE id = 1''', (state, comport, baudrate, timeout))
        self.con.commit() 
    
    def close( self ):
        self.con.close() 

