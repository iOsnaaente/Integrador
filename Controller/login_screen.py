from Model.shared_data import SharedData 
import View.LoginScreen.login_screen


"""
    O controlador `LoginScreenController` implementa o 
    padrão de estratégia do sistema de `LoginScreen`. Ele 
    coordena o trabalho da `View` com o `Model` e o controlador 
    se conecta a `View` para controlar suas ações.
"""
class LoginScreenController:

    card_widget = None 
    __shared_data : SharedData | None 

    def __init__(self, model, shared_data : SharedData | None = None ):
        # Seta o Modelo de LoginScreen -> Model.login_screen.LoginScreenModel
        self.model = model  
        # Seta a View de LoginScreen -> View.LoginScreen.login_screen.LoginScreenView
        self.view = View.LoginScreen.login_screen.LoginScreenView( controller = self, model = self.model )
        # Set o SharedData 
        self.__shared_data = shared_data 

    # Retorna a View de LoginScreen -> View.LoginScreen.login_screen.LoginScreenView 
    def get_view(self) -> View.LoginScreen.login_screen.LoginScreenView:
        return self.view

    # Abre o card de novo usuário 
    def raise_card( self ):
        self.card_widget = View.LoginScreen.login_screen.CardNewUser()
        self.view.add_widget( self.card_widget )

    # Fecha o card de novo usuário     
    def close_widget( self ):
        self.view.remove_widget( self.card_widget )
    
    # Hover das imagens de LoginScreen 
    def hover_item_in( self, object = None  ):
        if object:
            object.size_hint = [ 0.2, 1 ]
    def hover_item_out( self, object = None ):
        if object:
            object.size_hint = [ 0.2, 0.8 ]