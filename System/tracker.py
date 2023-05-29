from serial import Serial 

class Tracker( Serial ):
    
    def __init__(self, port: str | None = None, baudrate: int = 9600, bytesize: int = 8, parity: str = "N", stopbits: float = 1, timeout: float | None = None, xonxoff: bool = False, rtscts: bool = False, write_timeout: float | None = None, dsrdtr: bool = False, inter_byte_timeout: float | None = None, exclusive: float | None = None) -> None:
        super().__init__(port, baudrate, bytesize, parity, stopbits, timeout, xonxoff, rtscts, write_timeout, dsrdtr, inter_byte_timeout, exclusive) 
    



if __name__ == '__main__':

    tracker = Tracker( 'COM14', baudrate = 11560 )
    