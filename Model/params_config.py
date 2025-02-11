import os

BASE_PATH = os.path.dirname(__file__).removesuffix(os.path.join('Model'))

SERVER_IP   = '127.0.0.1'
LOGIN_PORT  = 50505
SYSTEM_PORT = 50506

SYNC_TIMEOUT    = 1
CREATE_TIMEOUT  = 1
PING_TIMEOUT    = 1



""" 
    Diretório para as imagens de uso geral do sistema
    - Se for adicionar uma imagem no sistema, adicione aqui
""" 
IMAGE_PATHS = {
    "painel_solar":     os.path.join( BASE_PATH, 'assets', 'images', 'PainelSolar.png'),
    "motor_vertical":   os.path.join( BASE_PATH, 'assets', 'images', 'motorVertical.png'),
    "motor_horizontal": os.path.join( BASE_PATH, 'assets', 'images', 'motorHorizontal.png'),
    "sensor_motores":   os.path.join( BASE_PATH, 'assets', 'images', 'encoder.png'),
    "background":       os.path.join( BASE_PATH, 'assets', 'images', 'background.png'),
    "sunrise_image":    os.path.join( BASE_PATH, 'assets', 'images', 'sunrise.jpg'),
    "connectivity_icon":os.path.join( BASE_PATH, 'assets', 'images', 'connectivity.png'),
    "green_power_icon": os.path.join( BASE_PATH, 'assets', 'images', 'green-power.png'),
    "security_icon":    os.path.join( BASE_PATH, 'assets', 'images', 'security.png'),
    "solar_icon":       os.path.join( BASE_PATH, 'assets', 'images', 'smart-power.png'),
    "smart_sun":        os.path.join( BASE_PATH, 'assets', 'images', 'smart.png'),
    "map_icon":         os.path.join( BASE_PATH, 'assets', 'images', 'map.png'),    
}

