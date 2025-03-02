from Tracker.Sensor.myAS5600   import AS5600
from Tracker.Time.myDatetime   import DS3231
from Tracker.Serial.myModbus   import Modbus
from Tracker.Sun.mySunposition import compute
from Tracker.Controle.myPID    import PID 
from L298N import Motor

from constants import * 
from pinout import *

import machine
import math 
import time 


machine.freq()          # get the current frequency of the CPU
machine.freq(240000000) # set the CPU frequency to 240 MHz


generation = machine.ADC(26)
power_gen = generation.read_u16()


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
DS.set_time( 25, 2, 11, 12, 30, 12 )

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


print( "Iniciando os controladores PID" )
pid_azimuth = PID( setpoint = 0.0, Kp = 0.75, Ki = 0.55, Kd = 0.10, tol = 0.25 ) 
pid_zenith  = PID( setpoint = 0.0, Kp = 0.75, Ki = 0.55, Kd = 0.10, tol = 0.25 ) 


loop_time = time.ticks_ms()
while True:
    
    # Atualiza as posições do sol 
    AZIMUTE, ALTITUDE = compute( LOCALIZATION,  DS.get_datetime() )
    INPUTS.set_reg_float ( INPUT_AZIMUTE, AZIMUTE ) 
    INPUTS.set_reg_float ( INPUT_ZENITE, ALTITUDE ) 
    
    # Atualiza a geração solar 
    power_gen = generation.read_u16()
    INPUTS.set_reg_float ( INPUT_GENERATION,  power_gen )
    
    # Atualiza a hora do relógio e temperatura 
    INPUTS.set_regs( INPUT_YEAR, DS.get_datetime() )
    INPUTS.set_reg_float ( INPUT_TEMP, DS.get_temperature() )
    
    # Lê as posições dos motores 
    pos_az = SGIR.read_angle( accumulate = True )
    pos_ze = SELE.read_angle( accumulate = True )
    INPUTS.set_reg_float(INPUT_POS_GIR, pos_az)
    INPUTS.set_reg_float(INPUT_POS_ELE, pos_ze)

    # Atualiza o Set Point do sistema 
    state = HOLDINGS.get_reg( HR_STATE ) 
    if  state == REMOTE:
        setpoint_az = HOLDINGS.get_reg_float(HR_PV_GIR)
        setpoint_ze = HOLDINGS.get_reg_float(HR_PV_ELE) 
    elif state == AUTOMATIC: 
        setpoint_az = AZIMUTE
        setpoint_ze = ALTITUDE
    elif state == FAIL_STATE:
        setpoint_az = 0.0
        setpoint_ze = 0.0
    else: 
        setpoint_az = 0.0
        setpoint_ze = 0.0
        DISCRETES.set_reg_bool( DISCRETE_FAIL, True )

    # Atualiza o INPUT com o valor adotado 
    INPUTS.set_reg_float(INPUT_AZIMUTE, setpoint_az)
    INPUTS.set_reg_float(INPUT_ZENITE, setpoint_ze)

    # Atualiza o SetPoint 
    pid_azimuth.set_setpoint( setpoint = setpoint_az )
    pid_zenith.set_setpoint( setpoint = setpoint_ze )
    
    # Calcula a malha de controle PID
    pid_output_az = pid_azimuth.update(pos_az)
    pid_output_ze = pid_zenith.update(pos_ze)

    # Limita entre -100 e 100 
    pid_output_az = min(max( -100, pid_output_az ), 100 )
    pid_output_ze = min(max( -100, pid_output_ze ), 100 )

    
    '''	Para mover os motores, COIL_M_GIR/ELE deve ser ON '''
    if state in [ REMOTE, AUTOMATIC ]:
        if math.fabs(pid_azimuth.error) < pid_azimuth.tol:
            pid_azimuth.reset()
            GIR.break_motor() 
        else:   
            GIR.move( pid_output_az/100 )  

        if math.fabs( pid_zenith.error) < pid_zenith.tol:
            pid_zenith.reset()
            ELE.break_motor()
        else:
            ELE.move( pid_output_ze/100 ) 
    else: 
        GIR.break_motor() 
        ELE.break_motor() 
    

    ''' Para Atualizar a hora do sistema '''   
    if COILS.get_reg_bool( COIL_SYNC_DATE ):
        try:
            DS.set_time( 
                HOLDINGS.get_reg( HR_YEAR ), 
                HOLDINGS.get_reg( HR_MONTH ), 
                HOLDINGS.get_reg( HR_DAY ), 
                HOLDINGS.get_reg( HR_HOUR ), 
                HOLDINGS.get_reg( HR_MINUTE ), 
                HOLDINGS.get_reg( HR_SECOND )
            )
        except:
            pass 
    
    ''' Se acontecer um FAIL STATE  '''
    LED_FAIL.value( True if HOLDINGS.get_reg( HR_STATE ) == FAIL_STATE else False )
    
    """ Atualiza os valores de COILS """
    POWER_LED.value( True if HOLDINGS.get_reg( HR_STATE ) == FAIL_STATE else False )
    POWER_MOTOR.value( COILS.get_reg_bool( COIL_POWER ) )

    """ Atualiza o relé de acionamento """    
    DISCRETES.set_reg_bool( DISCRETE_POWER, COILS.get_reg_bool( COIL_POWER ) )
    
    """ Informações de data e hora sincronizados """ 
    DISCRETES.set_reg_bool( DISCRETE_TIME, False )
    DISCRETES.set_reg_bool( DISCRETE_GPS, False )


    ''' 
        Loop de Debug do sistema a cada 1s  
    '''      
    if (time.ticks_ms()-loop_time) > 100: 
        print( 'Atualizando os INPUTS registers' ) 
        print( 'DS.get_datetime()=', DS.get_datetime() ) 
        print( 'DS.get_temperature()=', DS.get_temperature() ) 
        print( 'OP MODE=', HOLDINGS.get_reg( HR_STATE ) ) 
        print( 'SGIR.read_angle( accumulate = True )=', SGIR.read_angle( accumulate = True ) ) 
        print( 'SELE.read_angle( accumulate = True )=', SELE.read_angle( accumulate = True ) ) 
        print( 'GIR SP =', INPUTS.get_reg_float ( INPUT_AZIMUTE ) ) 
        print( 'ELE SP =', INPUTS.get_reg_float ( INPUT_ZENITE ) ) 
        print( 'compute( LOCALIZATION,  TIME )=', AZIMUTE, ALTITUDE )
        print( 'Generation =', power_gen )
        loop_time = time.ticks_ms()
    
    ''' Watchdog reset prevent'''
    #wdt.feed()
    
    
    
