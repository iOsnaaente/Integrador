import serial 
import glob 
import sys 

def get_serial_ports( lenght : int = 50, debug: bool = False  ):
    port_list = [] 
    if sys.platform.startswith('win'):  
        ports = ['COM%s' % (i + 1) for i in range( lenght )]
        if 'COM10' in ports: 
            ports.remove('COM10') 
        elif 'COM11' in ports:
            ports.remove('COM11')
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    else:
        if debug: 
            print("Sistema Operacional não suportado")
    for port in ports:
        try:
            s = serial.Serial( port )
            s.close()
            port_list.append(port)
            if debug:
                print( f'Port {port} found!' )
        except (OSError, serial.SerialException):
            pass
    return port_list

if __name__ == '__main__':
    ports = get_serial_ports( debug = True)
    print( ports ) 