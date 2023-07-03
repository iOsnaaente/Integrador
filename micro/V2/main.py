# importações de repositórios locais
import Tracker.Sun.mySunposition    as sun 
import Tracker.Serial.myModbus      as mmb
import Tracker.Time.myDatetime      as dt

from constants import *
from pinout    import *

import machine 
import time
import sys 

__debug = True

UART_NUM    = 0 
UART_BAUD   = 115200
MASTER_ID   = 0x12      # DEC 18 


# Inicializando o protocolo de comunicação Modbus
Modbus = mmb.myModbusCommunication( UART_NUM, UART_BAUD, MASTER_ID, tx = machine.Pin(UART_TX) , rx  = machine.Pin(UART_RX) )
if __debug:
    print( 'Utilizando modo de comunicação Modbus:  ')
    print( f'{Modbus.myUART}\nSLAVE ADDRESS: {Modbus.ADDR_SLAVE}\nFunction code available: {Modbus.FUNCTIONS_CODE_AVAILABLE}' )


# Cadastro dos registradores 
Modbus.set_registers( DISCRETES, COILS, INPUTS, HOLDINGS )
if __debug:
    print(  'Registradores cadastrados\n' )
    print( f'Holdings  - Type: {Modbus.HOLDINGS.TYPE } Len: {Modbus.HOLDINGS.REGS } {Modbus.HOLDINGS.STACK }'               )
    print( f'Inputs    - Type: {Modbus.INPUTS.TYPE   } Len: {Modbus.INPUTS.REGS   } {Modbus.INPUTS.STACK   }'               )
    print( f'Coils     - Type: {Modbus.COILS.TYPE    } Len: {Modbus.COILS.REGS    } {Modbus.COILS.STACK    }'               )
    print( f'Discretes - Type: {Modbus.DISCRETES.TYPE} Len: {Modbus.DISCRETES.REGS} {Modbus.DISCRETES.STACK}', end = '\n\n' )
     

# Criação dos barramentos i2c usados para DS3231 
I2C0 = machine.I2C ( 0, freq = 100000, sda = machine.Pin( I2C_SDA0 ), scl = machine.Pin( I2C_SCL0 ) ) 
I2C1 = machine.I2C ( 1, freq = 100000, sda = machine.Pin( I2C_SDA1 ), scl = machine.Pin( I2C_SCL1 ) ) 
if __debug:
    print( f"Barramento I2C0: {I2C0} Endereços no barramento: {I2C0.scan()}\n" )
    print( f"Barramento I2C1: {I2C1} Endereços no barramento: {I2C1.scan()}\n" ) 


# Inicia o relógio 
if 80 in I2C0.scan():
    Time = dt.Datetime( I2C0  )
    INPUTS.set_regs      ( INPUT_YEAR, Time.DS.get_datetime()[:-1] )
    HOLDINGS.set_regs    ( HR_YEAR   , Time.RTC.get_datetime()     )
else: 
    Time = None

# Seta um valor arbitrário para PV, KP, KI e KD 
HOLDINGS.set_regs_float( HR_KP_GIR, [ 0.55, 0.25, 0.15 ] ) 
HOLDINGS.set_regs_float( HR_KP_ELE, [ 0.55, 0.25, 0.15 ] )
if __debug:
    print( f"PID do motor de GIR configurado: Kd Ki Kp: {HOLDINGS.get_regs_float(HR_KP_GIR, 3)} - PV_gir: {HOLDINGS.get_reg_float(HR_PV_GIR)}  " )
    print( f"PID do motor de ELE configurado: Kd Ki Kp: {HOLDINGS.get_regs_float(HR_KP_ELE, 3)} - PV_ele: {HOLDINGS.get_reg_float(HR_PV_ELE)}\n" )


'''# --------------------------------------- INICIO DO LOOP ---------------------------------------------------------------------------#'''
loop_time  = time.ticks_ms()
print_time = time.ticks_ms()

POS_ELE    = 0.0 
POS_GIR    = 0.0 

import math 
while True:
    loop_time = time.ticks_ms()
    LED_BUILTIN.on()
    
    # SETAR OS REGISTRADORES DE INPUTS
    SENS_GIR = 180*(1 + math.cos( (30*60/1000)*loop_time ) )
    SENS_ELE =  90*(1 + math.sin( (30*60/1000)*loop_time ) )
    INPUTS.set_reg_float( INPUT_POS_GIR, SENS_GIR )
    INPUTS.set_reg_float( INPUT_POS_ELE, SENS_ELE )
    

    if Time != None:
        TIME, TIME_STATUS = Time.get_datetime()
        INPUTS.set_regs        ( INPUT_YEAR   , TIME[:-1]   )
        DISCRETES.set_reg_bool ( DISCRETE_TIME, TIME_STATUS )
    else: 
        TIME = [ 99, 5, 12, 6, 30, 12, 3 ]
        INPUTS.set_regs( INPUT_YEAR   , TIME[:-1]   )
        
    # SETA O AZIMUTE E ALTITUDE DE INPUT COM O VALOR CALCULADO
    AZIMUTE, ALTITUDE = sun.compute( LOCALIZATION,  TIME )
    INPUTS.set_reg_float ( INPUT_POS_GIR, AZIMUTE  )
    INPUTS.set_reg_float ( INPUT_POS_ELE, ALTITUDE )
    

    # Confere se foi recebido alguma mensagem para atualização das variáveis  
    if Modbus.has_message == True:
        Modbus.has_message = False 
        if __debug:
            print( 'Modbus recebeu mensagem:' )

    if time.ticks_ms() - print_time > 1000:
        print( 'INPUTS: ', INPUTS.__str__()    ) 
        print( 'HOLDINGS: ', HOLDINGS.__str__()  )
        print( 'DISCRETES: ', DISCRETES.__str__() )
        print( 'COILS: ', COILS.__str__()     )
        print_time = time.ticks_ms()
    
    
    LED_BUILTIN.off()
    # Tempo de looping do Pico
    dt = (time.ticks_ms() - loop_time )
    if dt <= 25:
        time.sleep_ms( 25 - dt )
