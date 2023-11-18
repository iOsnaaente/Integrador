from Model.shared_data import SharedData 
from kivymd.uix.screen import MDScreen 
import View.HomeScreen.home_screen
import importlib

# We have to manually reload the view module in order to apply the
# changes made to the code on a subsequent hot reload.
# If you no longer need a hot reload, you can delete this instruction.
importlib.reload(View.HomeScreen.home_screen)


class HomeScreenController:
    """
    The `HomeScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    last_pos : list = [0,0]
    motor_vel : list = [0,0]
    generation: float = 0.0
    sudently_disconected: bool = False 

    def __init__(self, model, shared_data : SharedData ):
        self.model = model  # Model.home_screen.HomeScreenModel
        __shared_data = shared_data 
        self.view = View.HomeScreen.home_screen.HomeScreenView( controller = self, model = self.model )

    def get_view(self) -> MDScreen:
        return self.view
    
    def auto_connect(self):
        if self.model.auto_connect():
            try: 
                keep, _, comp, baudrate, timeout = self.model.serial()[0]
                # print( 'Serial confi', keep, comp, baudrate, timeout )
                status = self.model.connect_device( 0x12, comp, baudrate, timeout )
                return status 
            except Exception as err: 
                print( 'init_system error:', err  )
                return False

    def get_motor_pos( self ):
        try:
            actual_pos = self.model.get_motor_pos()
            if actual_pos == [ None, None ]:
                self.model.disconnect()
                self.sudently_disconected = True
                return [0, 0] 
            else:
                self.motor_vel = [ 
                    actual_pos[0] - self.last_pos[0],
                    actual_pos[1] - self.last_pos[1] 
                ]
                self.last_pos = actual_pos 
                self.sudently_disconected = False 
                return actual_pos  
        except:
            self.model.disconnect( )
            self.sudently_disconected = True
            return [0, 0]
        
    def get_motor_vel( self ):
        return self.motor_vel 

    def get_generation( self ):
        return self.model.get_system_generation() 

    def get_status( self ):
        return self.model.is_connected() 