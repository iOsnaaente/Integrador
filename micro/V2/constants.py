from Tracker.Serial.myRegisters import Registers

# MODBUS INPUTS REGISTER ADDRESSES
INPUT_YEAR          = 0x00
INPUT_MONTH         = 0x01
INPUT_DAY           = 0x02
INPUT_HOUR          = 0x03
INPUT_MINUTE        = 0x04
INPUT_SECOND        = 0x05     
INPUT_TEMP          = 0x06
INPUT_PRESURE       = 0x08    
INPUT_POS_GIR       = 0x09    
INPUT_POS_ELE       = 0x0B    
INPUTS              = Registers( 0xFF, int )
# |    0x00 |    0x01 | 0x02 |    0x03 |   0x04 |   0x05 | 
# |    YEAR |   MONTH |  DAY |    HOUR | MINUTE | SECOND | 
# |    0x06 |    0x08 | 0x09 |    0x0B |
# | POS_GIR | POS_ELE | TEMP | PRESURE |


# MODBUS HOLDING REGISTER ADDRESSES
HR_PV_GIR       = 0x00
HR_KP_GIR       = 0x02
HR_KI_GIR       = 0x04
HR_KD_GIR       = 0x06
HR_AZIMUTE      = 0x08
HR_PV_ELE       = 0x0A
HR_KP_ELE       = 0x0C
HR_KI_ELE       = 0x0E
HR_KD_ELE       = 0x10
HR_ALTITUDE     = 0x12
HR_STATE        = 0x13
HR_YEAR         = 0x14
HR_MONTH        = 0x15
HR_DAY          = 0x16
HR_HOUR         = 0x17
HR_MINUTE       = 0x18
HR_SECOND       = 0x19
HR_LATITUDE     = 0x1A
HR_LONGITUDE    = 0x1C
HOLDINGS        = Registers( 0xFF, int )
# |     0x00 |     0x02 |    0x04 |   0x06 |    0x08  |         
# |   PV_GIR |   KP_GIR |  KI_GIR | KD_GIR | AZIMUTE  | 
# |     0x0A |     0x0C |    0x0E |   0x10 |     0x12 |
# |   PV_ELE |   KP_ELE |  KI_ELE | KD_ELE | ALTITUDE |
# |     0x13 |     0x14 |    0x15 |   0x16 |     0x17 |   0x18 |   0x19 | 
# |    STATE |     YEAR |   MONTH |    DAY |     HOUR | MINUTE | SECOND |          
# |    0x1A  |     0x1C | 
# | LATITUDE |LONGITUDE |  


# MODBUS DISCRETES REGISTER ADDRESSES
DISCRETE_POWER  = 0x00
DISCRETE_TIME   = 0x01
DISCRETE_GPS    = 0x02
DISCRETES       = Registers( 0x0F, bool )
# |  0x00 | 0x01 | 0x02 |
# | POWER | TIME |  GPS | 


# MODBUS COILS REGISTER ADDRESSES
COIL_POWER      = 0x00   
COIL_WAITING    = 0x01      
COIL_LEDR       = 0x02  
COIL_LEDG       = 0x03  
COIL_LEDB       = 0x04  
COILS           = Registers( 0x0F, bool ) 
# |  0x00 |     0x01 | 0x02 | 0x03 | 0x04 | 
# | POWER | WAITING  | LEDR | LEDG | LEDB | 


# STATES 
FAIL_STATE     = 0
AUTOMATIC      = 1
MANUAL         = 2
REMOTE         = 3
DEMO           = 4
IDLE           = 5
RESET          = 6
PRE_RETURNING  = 7
RETURNING      = 8
SLEEPING       = 9 


# CONFIGURAÇÕES DE RASTREAMENTO 
LATITUDE        = -29.713446689602126
LONGITUDE       = -53.717545975250545
TEMPERATURE     =  298.5
PRESSURE        =  101.0
LOCALIZATION    = [ LATITUDE, LONGITUDE, TEMPERATURE, PRESSURE ]

import machine 
LED_BUILTIN = machine.Pin( 25, machine.Pin.OUT )