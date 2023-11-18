from Tracker.Sensor.myAS5600   import AS5600
from Tracker.Time.myDatetime   import DS3231
from Tracker.Serial.myModbus   import Modbus
from Tracker.Sun.mySunposition import compute 
from L298N import Motor

from constants import * 
from pinout import *

import machine
import time 

machine.freq()          # get the current frequency of the CPU
machine.freq(240000000) # set the CPU frequency to 240 MHz

generation = machine.ADC(26)
power_gen = generation.read_u16()

''' Watchdog de 5000ms '''
#wdt = machine.WDT( timeout = 8000 )

print( f'Motor de giro: INA={MOTOR_GIR_INA} / INB={MOTOR_GIR_INB} / ENB={MOTOR_GIR_ENB}')
print( f'Motor de elevação: INA={MOTOR_ELE_INA} / INB={MOTOR_ELE_INB} / ENB={MOTOR_ELE_ENB}')
GIR = Motor( machine.Pin( MOTOR_GIR_INA, machine.Pin.OUT ), machine.Pin( MOTOR_GIR_INB, machine.Pin.OUT ), machine.PWM( machine.Pin( MOTOR_GIR_ENB, machine.Pin.OUT ) ) )
ELE = Motor( machine.Pin( MOTOR_ELE_INA, machine.Pin.OUT ), machine.Pin( MOTOR_ELE_INB, machine.Pin.OUT ), machine.PWM( machine.Pin( MOTOR_ELE_ENB, machine.Pin.OUT ) ) )


''' Prevent a long loop to reset'''
#wdt.feed() 
print( 'Iniciando o barramento I2C' ) 
I2C0 = machine.I2C ( 0, freq = 100000, sda = machine.Pin( I2C_SDA0 ), scl = machine.Pin( I2C_SCL0 ) )
I2C1 = machine.I2C ( 1, freq = 100000, sda = machine.Pin( I2C_SDA1 ), scl = machine.Pin( I2C_SCL1 ) ) 
print( f"Barramento I2C0: {I2C0} Endereços no barramento: {I2C0.scan()}\n" )
print( f"Barramento I2C1: {I2C1} Endereços no barramento: {I2C1.scan()}\n" ) 


''' Prevent a long loop to reset'''
#wdt.feed() 
print( 'Iniciando o sensor angular AS5600 de ELEVAÇÃO' )
print( 'Iniciando o sensor angular AS5600 de GIRO' )
SELE = AS5600( I2C1 ) 
SGIR = AS5600( I2C0 )
   
   
''' Prevent a long loop to reset'''
#wdt.feed() 
print( f'Iniciando RTC DS3231: {I2C0.scan()}' )
DS = DS3231( I2C0 )


''' Prevent a long loop to reset'''
#wdt.feed() 
print( f'Iniciando Modbus na UART {UART_NUM} com o baudrate {UART_BAUD} no endereço {MODBUS_ID}' )
MODBUS = Modbus( UART_NUM, UART_BAUD, 0x12, tx  = machine.Pin( UART_TXD0 ) , rx  = machine.Pin( UART_RXD0 ) )
MODBUS.set_registers( DISCRETES, COILS, INPUTS, HOLDINGS )

print( MODBUS.myUART ,'\nSLAVE ADDRESS: ', MODBUS.ADDR_SLAVE, "\nFunction code available: ", Modbus.FUNCTIONS_CODE_AVAILABLE )
print( 'Registradores cadastrados\n' )
print( 'Holdings  - Type: {} Len: {} {}'.format( MODBUS.HOLDINGS.TYPE , MODBUS.HOLDINGS.REGS , MODBUS.HOLDINGS.STACK  )  )
print( 'Inputs    - Type: {} Len: {} {}'.format( MODBUS.INPUTS.TYPE   , MODBUS.INPUTS.REGS   , MODBUS.INPUTS.STACK    )  )
print( 'Coils     - Type: {} Len: {} {}'.format( MODBUS.COILS.TYPE    , MODBUS.COILS.REGS    , MODBUS.COILS.STACK     )  )
print( 'Discretes - Type: {} Len: {} {}'.format( MODBUS.DISCRETES.TYPE, MODBUS.DISCRETES.REGS, MODBUS.DISCRETES.STACK )  , end = '\n\n' )
    
print( 'Atualizando os COILS registers' ) 
POWER_MOTOR   = machine.Pin( POWER_MOTOR, machine.Pin.OUT )
POWER_LED = machine.Pin( POWER_LED  , machine.Pin.OUT )

print( 'Atualizando os DISCRETE registers' ) 
LED_FAIL = machine.Pin( LED_BUILTIN, machine.Pin.OUT )


''' Prevent a long loop to reset'''
#wdt.feed()

while True:
    loop_time = time.ticks_ms()
    
    print( 'Atualizando os INPUTS registers' ) 
    AZIMUTE, ALTITUDE = compute( LOCALIZATION,  DS.get_datetime() )
    print( 'DS.get_datetime()=', DS.get_datetime() ) 
    INPUTS.set_regs( INPUT_YEAR, DS.get_datetime() )
    print( 'DS.get_temperature()=', DS.get_temperature() ) 
    INPUTS.set_reg_float ( INPUT_TEMP, DS.get_temperature() ) 
    print( 'SGIR.degAngle()=', SGIR.degAngle() ) 
    INPUTS.set_reg_float ( INPUT_POS_GIR, SGIR.degAngle() ) 
    print( 'SELE.degAngle()=', SELE.degAngle() ) 
    INPUTS.set_reg_float ( INPUT_POS_ELE, SELE.degAngle() ) 
    print( 'compute( LOCALIZATION,  TIME )=', AZIMUTE, ALTITUDE )
    power_gen = generation.read_u16()
    INPUTS.set_reg_float ( INPUT_GENERATION,  power_gen )
    print( 'Generation =', power_gen )
    INPUTS.set_reg_float ( INPUT_AZIMUTE, AZIMUTE ) 
    INPUTS.set_reg_float ( INPUT_ZENITE, ALTITUDE ) 
    
    
    print( 'Atualizando os DISCRETES registers' )
    DISCRETES.set_reg_bool( DISCRETE_FAIL, False )
    DISCRETES.set_reg_bool( DISCRETE_POWER, COILS.get_reg_bool( COIL_POWER ) )
    DISCRETES.set_reg_bool( DISCRETE_TIME, False )
    DISCRETES.set_reg_bool( DISCRETE_GPS, False )
    
    
    print( 'Atualizando os COILS registers' )
    POWER_LED.value( COILS.get_reg_bool( COIL_LED ) )
    POWER_MOTOR.value( COILS.get_reg_bool( COIL_POWER ) )
    if COILS.get_reg_bool( COIL_M_GIR ):
        GIR.move( HOLDINGS.get_reg_float( HR_PV_GIR) )
    else:
        GIR.break_motor()
    if COILS.get_reg_bool( COIL_M_ELE ):
        ELE.move( HOLDINGS.get_reg_float( HR_PV_ELE) )
    else:
        ELE.break_motor()
    if COILS.get_reg_bool( COIL_SYNC_DATE ):
        print( 'Atualizando a hora do sistema' )
        DS.set_datetime( HOLDINGS.get_reg( HR_YEAR ), HOLDINGS.get_reg( HR_MONTH ), HOLDINGS.get_reg( HR_DAY ), HOLDINGS.get_reg( HR_HOUR ), HOLDINGS.get_reg( HR_MINUTE ), HOLDINGS.get_reg( HR_SECOND ), 3 )
    
    LED_FAIL.value( True if HOLDINGS.get_reg( HR_STATE ) == FAIL_STATE else False )
    
    # Mantem o sincronismo de 1s para a rotina de atualização dos dados
    time.sleep_ms( 1000 - (time.ticks_ms()-loop_time) if (time.ticks_ms()-loop_time) < 1000 else 0 )
    
    ''' Watchdog reset prevent'''
    #wdt.feed()
    
    
    

