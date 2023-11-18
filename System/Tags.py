# MODBUS INPUTS REGISTER ADDRESSES
INPUT_POS_GIR       = 0x00
INPUT_POS_ELE       = 0x02
INPUT_AZIMUTE       = 0x04    
INPUT_ZENITE        = 0x06
INPUT_GENERATION 	= 0x08     
INPUT_TEMP          = 0x0A
INPUT_PRESURE       = 0x0C
INPUT_SENS_CONF_GIR = 0x0E
INPUT_SENS_CONF_ELE = 0x10
INPUT_YEAR          = 0x12
INPUT_MONTH         = 0x13
INPUT_DAY           = 0x14
INPUT_HOUR          = 0x15
INPUT_MINUTE        = 0x16
INPUT_SECOND        = 0x17

# MODBUS HOLDING REGISTER ADDRESSES
HR_PV_GIR           = 0x00
HR_KP_GIR           = 0x02
HR_KI_GIR           = 0x04
HR_KD_GIR           = 0x06
HR_AZIMUTE          = 0x08
HR_PV_ELE           = 0x0A
HR_KP_ELE           = 0x0C
HR_KI_ELE           = 0x0E
HR_KD_ELE           = 0x10
HR_ALTITUDE         = 0x12
HR_LATITUDE         = 0x14
HR_LONGITUDE        = 0x16
HR_STATE            = 0x18
HR_YEAR             = 0x19
HR_MONTH            = 0x1A
HR_DAY              = 0x1B
HR_HOUR             = 0x1C
HR_MINUTE           = 0x1D
HR_SECOND           = 0x1E

# MODBUS DISCRETES REGISTER ADDRESSES
DISCRETE_FAIL       = 0x00
DISCRETE_POWER      = 0x01
DISCRETE_TIME       = 0x02
DISCRETE_GPS        = 0x03

# MODBUS COILS REGISTER ADDRESSES
COIL_POWER          = 0x00   
COIL_LED            = 0x01
COIL_M_GIR          = 0x02 
COIL_M_ELE          = 0x03
COIL_LEDR           = 0x04  
COIL_LEDG           = 0x05  
COIL_LEDB           = 0x06
COIL_SYNC_DATE      = 0x07
