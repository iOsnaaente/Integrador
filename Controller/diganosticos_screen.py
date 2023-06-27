import View.DiganosticosScreen.diganosticos_screen
from Model.shared_data import SharedData
import importlib

importlib.reload(View.DiganosticosScreen.diganosticos_screen)

class DiganosticosScreenController:
    def __init__(self, model, shared_data : SharedData ):
        self.model = model  
        __shared_data = shared_data 
        self.view = View.DiganosticosScreen.diganosticos_screen.DiganosticosScreenView( controller = self, model = self.model )

    def get_view(self):
        return self.view
