from machine import Pin , soft_reset
from machine import I2C , SoftI2C 

import struct
import time 


'''
DS3231 // Classe destinada para o uso do módulo DS3231, um RTC que utiliza o protocolo I2C de comunicação. 
O códulo DS3231 possui também, um EEPROM de 32kbi ( 4k Bytes ) anexa a placa, utilizando dos mesmos meios
de comunicação. Por padrão o endereço do DS3231 é 0x68 e o endereço do EEPROM anexo é 0x57. 
'''
class DS3231: 
    days_of_week: list[str]  = [ "Domingo", "Segunda-feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira" , "Sexta-Feira", "Sábado" ]
    actual_day_of_week: int = 7
    wrong_datetime: bool = False
    raw_datetime: list = [ 2020, 12, 25, 3, 6, 30, 0, 7 ]
    temperature: float = 0.0
    
    '''
    Construtor da classe DS3231 ::
        >>> NUM : int -> (0 ou 1) depende qual dos dois I2C iremos usar ( Olhar o pinout do Rasp )
        >>> SDA : Pin -> Pino Serial DAta (SDA)  
        >>> SCL : Pin -> Pino Serial CLock ( SCL )
        >>> addrs : bytes(2) -> Endereços do DS3231 e AT24C32 ( Utilizar somente se forem alterados os valores em hardware)
        >>> pages : int -> Número de páginas do EEPROM ( O AT24C32 possui por padrão 128 páginas ) 
        >>> len_pages : int -> Número de bytes por página da EEPROM ( O AT24C32 possui por padrão 32 bytes por página )
    '''
    def __init__(self, i2c, addrs : list = [0x68, 0x57], pages : int = 128, len_pages : int = 32 ):
        self.DS_I2C    = i2c
        self.ADDR_DS   = addrs[0]
        self.ADDR_EE   = addrs[1]
        self.len_pages = len_pages
        self.num_pages = pages
        self.time_not_sync = True 
        
        
    ''' Função de baixo nível para escrita no DS. Aceita tanto I2C quanto SoftI2C.
    É necessário que o dados estejam em um buffer de bytes do tipo::
        >>> buff = b'cafe'
        >>> type( buff ) -> <class 'bytes'>
    >>> Caso a função retorne -1 é porque algum erro aconteceu e a escrita
    não pode ser concluida
    >>> Se algum erro for detectado, não irá interromper o fluxo 
    '''
    def _write( self, addr_dev : int, addr_mem : int, buffer : bytes ) -> bool:
        try: 
            if type( self.DS_I2C ) == I2C:        
                self.DS_I2C.writeto_mem( addr_dev, addr_mem, buffer)
            elif type( self.DS_I2C ) == SoftI2C:  
                self.DS_I2C.writeto( addr_dev, buffer, addr_mem )
            else:
                return False 
            return True
        except:
            return False 
            

    ''' Função de baixo nível para leitura no DS. Aceita tanto I2C quanto SoftI2C.
    os dados de saída terão uma estrutura de buffer de bytes do tipo::
        >>> buff = _read( addr_mem, num_bytes : N ) -> b'cafe' 
        >>> type( buff ) -> <class 'bytes'>
        >>> len( buff ) -> N
    >>> Caso a função retorne -1 é porque algum erro aconteceu e a escrita
    não pode ser concluida
    >>> Se algum erro for detectado, não irá interromper o fluxo 
    '''      
    def _read( self, addr_dev : int, addr_mem : int, num_bytes : int = 2 ) -> list | None :
        try:
            if type( self.DS_I2C ) == I2C:        
                return self.DS_I2C.readfrom_mem( addr_dev, addr_mem, num_bytes )
            elif type( self.DS_I2C ) == SoftI2C:  
                return self.DS_I2C.readfrom( addr_dev, num_bytes, addr_mem )
            else:
                return None
        except:
            return None 
            
            
    '''Seta os parametros de data e hora::
            >>> y  : byte -> Year 
            >>> m  : byte -> Month  
            >>> d  : byte -> Day
            >>> hh : byte -> Hour 
            >>> mm : byte -> Minute 
            >>> ss : byte -> Second
        >>> Retorna 1 caso a data tenha sido trocada
        >>> Retorna -1 em caso de erro 
    '''
    def set_time(self, y : int, m : int, d : int, hh : int, mm : int, ss : int ) -> bool: 
        dow = self.get_day_of_week_index( int(y), int(m), int(d) )
        buff = struct.pack( 'bbbbbb', self.dec2bcd(ss), self.dec2bcd(mm), self.dec2bcd(hh), self.dec2bcd(dow), self.dec2bcd(d), self.dec2bcd(m), self.dec2bcd(y) )
        status = self._write(  self.ADDR_DS, 0x00, buff )
        if status == -1:
            return False
        else: 
            return True
        

    ''' Recebe os parametros de data e hora do momento da chamada::
            >>> Retorna um array de bytes com datetime de 7 bytes 
            >>> Caso retorne -1, a data não pode ser lida do DS3231 
    '''
    def now( self ) -> list | None:
        time = self._read( self.ADDR_DS, 0x00, 7 )
        if time == None:
            return None 
        else: 
            time = [ self.bcd2dec( time[i] ) for i in range(len(time)-1,-1,-1) if i != 3 ]
            time.append( 3 )
            self.raw_datetime = time
            return time
    
    def get_raw_datetime(self):
        to_send = b''
        if isinstance( self.raw_datetime, list ):
            for i in self.raw_datetime:
                to_send += bytes(i)
        return to_send
    
    
    ''' Executa a leitura de temperatura do sensor interno do DS3231. O sensor
        de temperuta esta localizado no endereço 0x11 e possui precisão de 0.5º
            >>> Retorna um valor positivo caso a leitura tenha sido bem sucedida
            >>> Retorna -1 caso não tenha executado a leitura da temperatura. 
    '''
    def get_temperature( self ) -> float | None :
        temp = self._read( self.ADDR_DS, 0x11, 2)
        if temp == None :
            return None 
        else: 
            self.temp = temp[0] + ((temp[1] and 0xC0)>>6)/4
            return self.temp 
        

    ''' Retorna a hora, mais o parâmetro de wrong_datetime::
            >>> Se self.wrong_datetime == True::
                >>> Precisa-se solicitar uma correção de datetime para o supervisório
            >>> Se self.wrong_datetime == False::
                >>> A hora esta sincronizada com a hora do supervisório
    '''
    def get_datetime(self):
        return self.now()


    ''' Retorna o dia da semana de 0 a 6 sendo::
        >>> 0 = Segunda-feira
        >>> .....
        >>> 6 = Domingo
    '''
    def get_day_of_week_index(self, year : int, month : int, day : int) -> int :
        year  = year if year < 99 else year & 0x63 
        y_key = ((year//4 + year%7) % 7)-1 
        m_key = [ 1, 4, 4, 0, 2, 5, 0, 3, 6, 1, 4, 6 ] 
        DoW   = ( day + m_key[month-1] + y_key )
        DoW   = DoW if DoW < 7 else DoW // 7 
        self.actual_day_of_week = DoW if DoW >= 0 else 7
        return self.actual_day_of_week 


    ''' Retorna o dia da semana por extenso.
        >>> 'Segunda-feira', 'Terça-feira' .... 'Domingo' 
    '''
    def get_day_of_week_name( self ) -> str:
        return self.days_of_week[ self.actual_day_of_week ]


    ''' Conversão dos bytes em formato Decimal apartir do formato BCD '''
    def bcd2dec(self, bcd : bytes ) -> int: 
        return int(( int(bcd) >> 4 )*10 + ( int(bcd) & 0b1111 ))  


    ''' Conversão dos bytes em formato BCD apartir do formato Decimal '''
    def dec2bcd(self, dec : int ) -> bytes:
        return bytes( ((dec//10)<<4) + (dec % 10) ) 
    

    def scan( self, dec : bool = True ) -> list:
        if dec :
            return self.DS_I2C.scan()
        else:
            return [ hex(add) for add in self.DS_I2C.scan() ] 
        

    def get_parameters(self) -> list:
        return self.DS_I2C


    '''
    Read é o método que irá ler um byte da EEPROM AT24C32 do DS3231 ::
        >>> addr : int -> Endereço de leitura da EEPROM 
        >>> nbytes : int ->  Quantidade de bytes para serem lidos 
    nbytes é número de bytes que queremos ler apartir do endereço passa como parâmetro.
    >>> Retorna a leitura do endereço passado como parametro
    >>> Caso retorne None, não foi possível executar a leitura dos parametros 
    '''
    def read_eeprom( self, addr : int, nbytes : int ) -> bytearray | None:
        # Calcula o índice da página inicial e o offset dentro da página
        page_index = addr // self.len_pages
        offset = addr % self.len_pages
        # Determina quantas páginas serão necessárias para cobrir (offset + nbytes)
        pages_needed = (offset + nbytes + self.len_pages - 1) // self.len_pages
        data = bytearray()
        # Lê cada página necessária
        for i in range(pages_needed):
            page_addr = (page_index + i) * self.len_pages
            page_data = self._read(self.ADDR_EE, page_addr, self.len_pages)
            if page_data is None:
                return None
            # Se o _read retornar uma lista de objetos bytes, os concatena
            if isinstance(page_data, list):
                for part in page_data:
                    data.extend(part)
            else:
                data.extend(page_data)
        # Retorna os nbytes solicitados, a partir do offset inicial
        return data[offset:offset + nbytes]     


    ''' 
    Write é o método de escrita na EEPROM AT24C32 do DS3231 ::
        >>> addr : int -> Endereço de escrita de 1 byte 
        >>> buff : bytearray -> dados a serem escritos na EEPROM
    O Buff começa a ser escrito a partir do primeiro endereço passado como parâmetro 
    na variável addr e vai sendo escrito na medida que é necessário.
    '''

def write_eeprom(self, addr: int, buff: bytes) -> bool:
    # Se o buffer tiver apenas 1 byte, escreve diretamente
    if len(buff) == 1:
        self._write(self.ADDR_EE, addr, buff)
        return True

    # Calcula o bloco atual e o offset dentro da página
    block_len = addr // self.len_pages
    block = self._read(self.ADDR_EE, block_len, self.len_pages)
    offset = addr % self.len_pages

    # Concatena o conteúdo do bloco lido em um bytearray
    empty = b''
    if isinstance(block, list):
        for data in block:
            empty += data
        
        # Atualiza o buffer conforme o tamanho da página
        if len(buff) > self.len_pages:
            buff = empty[:offset] + buff
        else:
            buff = empty[:offset] + buff + empty[offset + len(buff):]

        # Separa a escrita em vários blocos, se necessário
        blocks = []
        if len(buff) > self.len_pages:
            # Divide o buff em blocos do tamanho da página
            for init in range((len(buff) // self.len_pages) + 1):
                data = b''
                for piece in buff[init * self.len_pages : (init + 1) * self.len_pages]:
                    data += struct.pack('B', piece)
                blocks.append(data)
        else:
            data = b''
            for piece in buff:
                data += struct.pack('B', piece)
            blocks = [data]
        
        # Escreve cada bloco na respectiva página
        for bloco, buffer in enumerate(blocks):
            # Cálculo do endereço para escrita – ajuste conforme a organização da sua EEPROM
            write_addr = (block_len + bloco) * self.len_pages
            self._write(self.ADDR_EE, write_addr, buffer)
            time.sleep_ms(1)
        return True
    else:
        return False  
        


if __name__ == "__main__":
    SDA_DS = 16 
    SCL_DS = 17
    isc0   = I2C ( 0,  sda = Pin( SDA_DS  ), scl = Pin( SCL_DS  ) )
    if 104 in isc0.scan():
        print( isc0.scan())
        Time   = DS3231( isc0  )
        #Time.set_time( 22, 1, 20, 15, 44, 50 )
        print( Time.get_time(), Time.get_temperature() )
    print( Time.get_raw_datetime()) 
    
    #Time.write_eeprom( 0,  b'Bruno Gabriel Flores Sampaio' ) 
    # estoura
    #Time.write_eeprom( 32, b'E eu estou desenvolvendo o Trac' ) 
    # não estoura    
    #Time.write_eeprom( 0, b'Meu nome eh Bruno' )
    #print( Time.read_eeprom( 0, 32) )
    #print( Time.now())