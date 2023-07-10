from kivy_garden.mapview import MapMarkerPopup
from kivy_garden.mapview import MapView

from kivymd.uix.button import MDFlatButton


class MapSystem( MapView ):
    map_view : MapView 
    markers = [ 
        MapMarkerPopup( lat=-29.71332542661317, lon=-53.71766381408064, source = '/assets/images/panel.png' ) 
    ]
    markers[0].add_widget(
        MDFlatButton(
            text=f'Informações do sistema\nlat={markers[0].lat}\nlon={markers[0].lon}\nNot connected',
            md_bg_color='gray' 
        ) 
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def init_map_view(
        self,
        lat=-29.71332542661317,
        lon=-53.71766381408064,
        zoom=18,
        pos_hint={'center_x': 0.50, 'center_y': 0.5 },
        size_hint = [1,1]
    ):
        self.map_view = MapView(
            lat = lat, 
            lon = lon,  
            zoom = zoom,  
            pos_hint=pos_hint,
            size_hint=size_hint
        )

        self.map_view.add_widget( self.markers )

    def get(self):
        return self.map_view 
    
    def get_markers(self):
        return self.markers 

