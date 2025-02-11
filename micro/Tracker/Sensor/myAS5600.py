import machine
import struct 
import time 

MD_CHECK = 1
MH_CHECK = 2
ML_CHECK = 3 

class AS5600: 
  ##  FIGURE 21 - DATASHEET available in https://ams.com/documents/20143/36005/AS5600_DS000365_5-00.pdf
  ## Configuration registers 
  ZMCO      = 0x0 
  ZPOS      = 0x1
  MPOS      = 0x3
  MANG      = 0x5
  CONF      = 0x7
  ## Output Registers
  RAWANGLE  = 0x0C
  ANGLE     = 0x0E
  ## Status Registers
  STATUS    = 0x0B
  AGC       = 0x1A
  MAGNITUDE = 0x1B 
  ## Burn Commands 
  BURN      = 0xff

  # Magnetic sensor stuffs 
  Status     = 0       # Status register (MD, ML, MH)
  ADDRESS    = 0x36    # By default 

  start_angle: float = 0.0  # Offset de angulo 
  prev_angle:  float = 0.0  # Salva o angulo anterior 
  total_angle: float = 0.0  # Angulo absoluto total acumulado
  total_turns: int   = 0    # Contagem de voltas
  
  ## Constructor 
  def __init__( self, I2C : machine.I2C , addr : int = 0x36, start_angle : float = 0.0  ): 
    self.ADDRESS      = addr 
    self.AS5600       = I2C 
    self.start_angle  = start_angle
    self.last_angle   = start_angle
    self.ERRORS       = 0 
    
      
  ## To write in the I2C we need a buffer struct like b'a21@\x02' 
  def _write( self, addr_mem : int, buffer : bytes ) -> bool:
    try:
        if type( self.AS5600 ) == machine.I2C: 
          self.AS5600.writeto_mem( self.ADDRESS, addr_mem, buffer )
        elif type( self.AS5600 ) == machine.SoftI2C:
          self.AS5600.writeto( self.ADDRESS, buffer, addr_mem )
        return True 
    except:
        self.ERRORS += 1 
        return False 
    
  ## to read, we start at addr_mem and we read num_bytes from addr_mem 
  def _read( self, addr_mem : int, num_bytes : int = 2 ) -> list | None:
    try:
        if type( self.AS5600 ) == machine.I2C: 
          return self.AS5600.readfrom_mem( self.ADDRESS, addr_mem, num_bytes )
        elif type( self.AS5600 ) == machine.SoftI2C:
          return self.AS5600.readfrom( self.ADDRESS, num_bytes, addr_mem )
    except:
        self.ERRORS += 1 
        return None

  ## read the unscaled angle and unmodified angle
  def read_raw_angle( self ) -> int:
    try:
      raw_angle = self._read( self.ANGLE, 2 )
      if isinstance( raw_angle, bytes ):
        HIGH_BYTE = raw_angle[0]    #  RAW ANGLE(11:8) on 0x0C address 
        LOW_BYTE  = raw_angle[1]    #  RAW ANGLE(7:0) on 0X0D address 
        raw_angle = ( (HIGH_BYTE << 8) | LOW_BYTE ) 
        return raw_angle
      else: 
        return -1
    except: 
        self.ERRORS += 1
        if self.ERRORS > 10:
            self.set_config()
        return -1  

  def gain(self) -> int:
    self.GAIN = self._read( self.AGC , 1 )
    if isinstance( self.GAIN, bytes ):
      return self.GAIN[0]
    else: 
      return -1

  # Read total angle accumulate 
  def read_angle( self, accumulate: bool = False ) -> float: 
    """ 
      Para calcular o valor de angulo em Graus
      1. Lê o angulo em bits 
      2. Divide 360º pelos 12bits (0x0fff) 
      3. Vezes o valor do angulo do sensor
      angle = rawAngle * 360/4096 = rawAngle * 0.087890625
    """ 
    raw_angle = self.read_raw_angle()
    if raw_angle == -1: 
      return False
    
    """ Converta para angulos """
    angle = raw_angle * ( 360.0 / 0x0fff )
    
    """ Normaliz para o multi voltas """
    if (angle - self.start_angle) >= 0:
      angle = angle - self.start_angle 
    else: 
      angle = (angle - self.start_angle) + 360.0 

    """ Normaliza os angulos contando os pulsos """
    delta_angle = angle - self.prev_angle 
    self.prev_angle = angle 
    if delta_angle < -180:
      self.total_turns -= 1
    elif delta_angle > 180:
      self.total_turns += 1 
    
    self.total_angle = angle + ( self.total_turns * 360.0 )
    if ( not accumulate ):
      return angle 
    else:
      return self.total_angle 

  ## Verify the status of the magnetic range 
  ### The status be in the 0x0B address in the 5:3 bits
  #  
  ## MH [3] AGC minimum gain overflow, magnet too strong  
  ## ML [4] AGC maximum gain overflow, magnet too weak
  ## MD [5] Magnet was detected
  #
  ## To operate properly, the MD have to be set and the MH and ML have to be 0 
  def check_status( self ) -> int: 
    status = self._read( self.STATUS, 1 )
    if isinstance( status, bytes ):
      self.MH = status[0] >> 3 and 1
      self.ML = status[0] >> 4 and 1
      self.MD = status[0] >> 5 and 1
      # Imã está presente  
      if self.MD:
        return MD_CHECK
      else: 
        # Imã esta Forte 
        if self.MH:
          return MH_CHECK
        # Imã esta Fraco 
        if self.ML:
          return  ML_CHECK
        # Sem erros 
        return 0
    # Não pode ler o endereço 
    else: 
      return -1


  def print_diagnosis(self) -> None:
    print( self._read( 0, 11 ) )


  def get_config( self ) -> list :
    try:
      ret = self._read( 0, 11 )
      if isinstance( ret, bytes ):
        config = [ struct.unpack('B', val)[0] for val in ret ]
        return config
      else:
        return []
    except:
      return []


  def set_config( self ) -> bool:
    for i in range( 9 ):
      status = self._write( i, bytes(0) )
      if status == False:
        self.ERRORS += 1
        return False
    return True 

  # Número de erros registrados 
  def get_error_count(self) -> int:
    return self.ERRORS
    
  def reset_errros_count(self) -> int:
    self.ERRORS = 0
    return self.ERRORS
