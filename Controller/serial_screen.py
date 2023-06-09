import importlib

import View.SerialScreen.serial_screen

from Model.shared_data import SharedData 

# We have to manually reload the view module in order to apply the
# changes made to the code on a subsequent hot reload.
# If you no longer need a hot reload, you can delete this instruction.
importlib.reload(View.SerialScreen.serial_screen)


class SerialScreenController:
    """
    The `LoginScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """
    card_widget = None 

    __shared_data : SharedData 

    def __init__(self, model, shared_data ):
        self.model = model  # Model.login_screen.LoginScreenModel
        self.view = View.SerialScreen.serial_screen.SerialScreenView( controller = self, model = self.model )
        self.__shared_data = shared_data 
        
    def get_view(self) -> View.SerialScreen.serial_screen:
        return self.view
