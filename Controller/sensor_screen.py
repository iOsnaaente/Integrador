from Model.shared_data import SharedData
import View.SensorScreen.sensor_screen
import importlib

# We have to manually reload the view module in order to apply the
# changes made to the code on a subsequent hot reload.
# If you no longer need a hot reload, you can delete this instruction.
importlib.reload(View.SensorScreen.sensor_screen)

class SensorScreen:
    def __init__(self, model, shared_data : SharedData ):
        self.model = model  # Model.diganosticos_screen.DiganosticosScreenModel
        __shared_data = shared_data 
        self.view = View.SensorScreen.sensor_screen.SensorScreenView( controller = self, model = self.model )

    def get_view(self):
        return self.view
    
    def is_connected( self ): 
        return None if self.model.system == None else self.model.system.is_connected()

    def get_tags( self, device: int = 0x12 ):
        if self.model.system == None:
            return None 
        else: 
            return self.model.system.DB.read_tags_by_device( device )