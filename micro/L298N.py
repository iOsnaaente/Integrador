import machine
import time 

class Motor:
    
    def __init__( self, INA : machine.Pin, INB : machine.Pin, PWM : machine.PWM  ) -> None:
        self.INA = INA
        self.INB = INB
        self.VEL = PWM

        self.VEL.init( freq = 5000 )
        
        
    def set_velocity( self, vel : float ):
        ''' Normalize the velocity '''
        if vel > 1:    vel = 65536
        elif vel <= 0:  vel = 0
        else:          vel = 65536*vel
        self.VEL.duty_u16( int(vel) )
        
    def break_motor( self ):
        self.set_velocity( 0 )
        self.INA.high()
        self.INB.high()
    
    def stop_motor( self ):
        self.set_velocity( 0 )
        self.INA.low()
        self.INB.low()
    
    def backward( self ):
        self.INA.low()
        self.INB.high()
    
    def forward( self ):
        self.INA.high()
        self.INB.low()
    
    def move( self, vel : float ) -> str:
        if vel < 0:
            self.set_velocity( vel*(-1) )
            self.backward()
            return "BACKWRD"
        elif vel > 0:
            self.set_velocity( vel )
            self.forward()
            return "FORWARD"
        else:
            self.stop_motor()
            return "STOP"
        
        
