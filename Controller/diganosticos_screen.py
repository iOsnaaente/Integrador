import View.DiganosticosScreen.diganosticos_screen
import importlib

importlib.reload(View.DiganosticosScreen.diganosticos_screen)

class DiganosticosScreenController:
    def __init__(self, model ):
        self.model = model  
        self.view = View.DiganosticosScreen.diganosticos_screen.DiganosticosScreenView( controller = self, model = self.model )

    def get_view(self) -> View.DiganosticosScreen.diganosticos_screen.DiganosticosScreenView:
        return self.view
