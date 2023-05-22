import importlib

import View.LoginScreen.login_screen

from Model.shared_data import SharedData 

# We have to manually reload the view module in order to apply the
# changes made to the code on a subsequent hot reload.
# If you no longer need a hot reload, you can delete this instruction.
importlib.reload(View.LoginScreen.login_screen)


class LoginScreenController:
    """
    The `LoginScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    card_widget = None 
    __shared_data : SharedData 

    def __init__(self, model, shared_data : SharedData = None ):
        self.model = model  # Model.login_screen.LoginScreenModel
        self.view = View.LoginScreen.login_screen.LoginScreenView( controller = self, model = self.model )
        self.__shared_data = shared_data 
        
    def get_view(self) -> View.LoginScreen.login_screen:
        return self.view
    
    # Abrir o card de novo usuário 
    def raise_card( self ):
        self.card_widget = View.LoginScreen.login_screen.CardNewUser()
        self.view.add_widget( self.card_widget )

    # Fechar o card de novo usuário     
    def close_widget( self ):
        self.view.remove_widget( self.card_widget )