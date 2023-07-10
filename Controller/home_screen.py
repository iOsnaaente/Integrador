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

    def __init__(self, model, shared_data : SharedData ):
        self.model = model  # Model.home_screen.HomeScreenModel
        __shared_data = shared_data 
        self.view = View.HomeScreen.home_screen.HomeScreenView( controller = self, model = self.model )

    def get_view(self) -> MDScreen:
        return self.view

    def system_connected( self ):
        return self.model.is_connected()
    
    def auto_connect(self):
        return self.model.auto_connect()
    
        if self.model.auto_connect():
            try: 
                keep, _, comp, baudrate, timeout = self.model.serial()[0]
                print( 'Serial confi', keep, comp, baudrate, timeout )
                status = self.model.connect_device( 0x12, comp, baudrate, timeout )
                return status 
            except Exception as err: 
                print( 'init_system error:', err  )
                return False
            

    def already_connected( self ):
        print( 'already connected in home.controller')
        return False 
    
    def connect_system( self ): 
        print( 'Connect system in home.controller')
        return True 