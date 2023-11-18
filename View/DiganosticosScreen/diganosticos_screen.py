from View.Widgets.SideBar.side_bar import SideBar
from View.base_screen import BaseScreenView


class DiganosticosScreenView(BaseScreenView):
    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
    
    def on_kv_post (self, *args):
        return super().on_kv_post(*args)


    # Callback para entrar na tela
    def on_enter(self, *args):
        # Coloca o side bar no lugar 
        self.side_bar = SideBar( model = self.model) 
        self.ids.float_content.add_widget( self.side_bar )
        return super().on_enter(*args)

    # Callback qundo sair da tela
    def on_leave( self, *args ):
        self.ids.float_content.remove_widget( self.side_bar )
        return super().on_leave(*args)