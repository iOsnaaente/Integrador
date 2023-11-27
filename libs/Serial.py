import serial 
import glob 
import sys 

def get_serial_ports( lenght : int = 25, debug: bool = False  ):
    portList = [] 
    if sys.platform.startswith('win'):  
        ports = ['COM%s' % (i + 1) for i in range( lenght )]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    else:
        if debug: 
            print("Sistema Operacional não suportado")
    for port in ports:
        try:
            s = serial.Serial( port )
            s.close()
            portList.append(port)
            if debug:
                print( f'Port {port} found!' )
        except (OSError, serial.SerialException):
            pass
    return portList