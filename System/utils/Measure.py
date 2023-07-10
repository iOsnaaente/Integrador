import datetime
import sqlite3 
import pytz 

ano   = 2022
mes   = [ 'jan', 'fev', 'mar','abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez' ]
anual = [  6461,  5963, 4967,  3891,  2809,  2333,  2563,  3323,  3774,  4927,  6275,  6809 ] 
mean  = round( sum(anual)/len(anual) ) 

'''
    Tabela generation: 
        Armazena os dados de geração solar com as colunas 
            id (chave primária);
            timestamp (data e hora da medição);
            generation_value (valor de geração).
            
    Tabela daily_generation: 
        Armazena os dados de geração diária com as colunas:
            id (chave primária), date (data da medição);
            average_generation (média de geração solar no dia);
            peak_generation (pico de geração solar no dia);
            total_generation (total de geração solar no dia).

    Tabela monthly_generation:  
        Armazena os dados de geração mensal com as colunas 
            id (chave primária);
            month (mês da medição);
            year (ano da medição);
            average_generation (média de geração solar no mês); 
            peak_generation (pico de geração solar no mês);
            total_generation (total de geração solar no mês).

    Tabela total_generation: 
        Armazena os dados de geração total com as colunas 
        id (chave primária);
        average_generation (média de geração solar total);
        peak_generation (pico de geração solar total);
        total_generation (total de geração solar acumulado).

'''
class Measure( ): 
    def __init__( self, path: str, create_table: bool = False, debug: bool = False ) -> None: 
        self.db_path = path
        if create_table:    
            self.create_table()

    def create_table( self ) -> None: 
        conn = sqlite3.connect( self.db_path )
        c = conn.cursor()
        # Tabela 'generation'
        c.execute('''
            CREATE TABLE IF NOT EXISTS generation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                value REAL
            )
        ''')
        # Tabela 'daily_generation'
        c.execute('''
            CREATE TABLE IF NOT EXISTS daily_generation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                average_generation REAL,
                peak_generation REAL,
                total_generation REAL,
                generation_id INTEGER,
                FOREIGN KEY (generation_id) REFERENCES generation (id)
            )
        ''')
        # Tabela 'monthly_generation'
        c.execute('''
            CREATE TABLE IF NOT EXISTS monthly_generation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                month INTEGER,
                year INTEGER,
                average_generation REAL,
                peak_generation REAL,
                total_generation REAL,
                generation_id INTEGER,
                FOREIGN KEY (generation_id) REFERENCES generation (id)
            )
        ''')
        # Tabela 'total_generation'
        c.execute('''
            CREATE TABLE IF NOT EXISTS total_generation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                average_generation REAL,
                peak_generation REAL,
                total_generation REAL,
                generation_id INTEGER,
                FOREIGN KEY (generation_id) REFERENCES generation (id)
            )
        ''')
        conn.commit()
        conn.close()
    

    def save_data(self, value):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Salva o valor de geração 
        cursor.execute("INSERT INTO generation (value) VALUES (?, ?, ?, ?)", (value,) ) 
        generation_id = cursor.lastrowid
        timestamp = cursor.execute("SELECT timestamp FROM generation WHERE id = ?", (generation_id,)).fetchone()[0]
        self.save_daily_generation( cursor, generation_id, date = timestamp ) 


    def save_daily_generation( self, cursor, id, date ):
        day = date.split()[0]
        # Verificar se a data já existe na tabela 'daily_generation'
        if cursor.execute( "SELECT date FROM daily_generation WHERE date = ?", ( day, ) ).fetchone():
            cursor.execute("""
                UPDATE daily_generation
                    SET average_generation = (SELECT AVG(value) FROM generation ),
                        peak_generation = (SELECT MAX(value) FROM generation ),
                        total_generation = (SELECT SUM(value) FROM generation )
                    WHERE date = ?
            """, ( day, ) )
        else: 
            # Inserir um novo registro na tabela 'daily_generation'
            cursor.execute("""
                INSERT INTO daily_generation (
                    date, 
                    average_generation, 
                    peak_generation, 
                    total_generation, 
                    generation_id
                ) VALUES (
                    ?, 
                    ( SELECT AVG(value) FROM generation WHERE DATE(timestamp) = ? ), 
                    ( SELECT MAX(value) FROM generation WHERE DATE(timestamp) = ? ), 
                    ( SELECT SUM(value) FROM generation WHERE DATE(timestamp) = ? ), 
                    ?
                )
            """, ( date, date, date, date, id ) )    


        # Verificar se o registro mensal já existe na tabela 'monthly_generation'
        existing_month = cursor.execute("SELECT id FROM monthly_generation WHERE month = ? AND year = ?", (month, year)).fetchone()
        # Se existir, atualizar os valores na tabela 'monthly_generation'
        if existing_month:
            cursor.execute("""
                UPDATE monthly_generation
                    SET 
                        average_generation = (SELECT AVG(value) FROM generation),
                        peak_generation = (SELECT MAX(value) FROM generation),
                        total_generation = (SELECT SUM(value) FROM generation)
                    WHERE 
                        month = ? AND year = ?
            """, ( month, year ) )

        # Inserir um novo registro na tabela 'monthly_generation'
        else:
            cursor.execute("""
                INSERT INTO monthly_generation (
                    month, 
                    year, 
                    average_generation, 
                    peak_generation, 
                    total_generation, 
                    generation_id
                ) VALUES (
                    ?, 
                    ?, 
                    (SELECT AVG(value) FROM generation), 
                    (SELECT MAX(value) FROM generation), 
                    (SELECT SUM(value) FROM generation), 
                    ?
                )
            """, ( month, year, generation_id ) ) 

        # Salvar na tabela 'total_generation'
        cursor.execute("""
            INSERT INTO total_generation (generation_id)
            VALUES (?)
        """, (generation_id,))



        conn.commit()
        conn.close()
        
