from time import ticks_ms, ticks_diff

class PID:
    
    current_time: float = 0.0 
    last_time: float    = 0.0 

    last_error: float   = 0.0 
    error: float        = 0.0 
    
    setpoint:float      = 0.0 
    output: float       = 0.0 
    
    derivative: float   = 0.0 
    integral: float     = 0.0 
    tol: float          = 0.0 
    
    Kp: float           = 0.0 
    Ki: float           = 0.0 
    Kd: float           = 0.0 

    """
        :param setpoint: Valor desejado (PV) a ser mantido.
        :param Kp: Ganho proporcional.
        :param Ki: Ganho integral.
        :param Kd: Ganho derivativo.
        :param tol: Tolerância para considerar o erro como zero.
    """
    def __init__(self, setpoint: float, Kp: float, Ki: float, Kd: float, tol: float = 0.25):
        self.setpoint = setpoint
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.tol = tol
        
        self.integral = 0.0
        self.last_error = 0.0
        self.last_time = ticks_ms()


    """
        Atualiza o controle PID com a medição atual e retorna a saída.
        :param measurement: Valor medido atualmente.
        :return: Valor de controle calculado pelo PID.
    """
    def update(self, measurement: float) -> float:
        current_time = ticks_ms()
        dt_ms = ticks_diff(current_time, self.last_time)
        dt = dt_ms / 1000.0  # converte para segundos
        # Evita divisão por zero em dt
        if dt <= 0:
            dt = 1e-3
        # Calcula o erro
        self.error = self.setpoint - measurement
        # Se o erro estiver abaixo da tolerância, trata como zero
        if abs(self.error) < self.tol:
            self.error = 0.0
        # Integração do erro ao longo do tempo
        self.integral += self.error * dt
        # Cálculo da derivada
        self.derivative = (self.error - self.last_error) / dt
        # Cálculo da saída PID
        self.output = (self.Kp * self.error) + (self.Ki * self.integral) + (self.Kd * self.derivative)
        # Atualiza o último erro e tempo
        self.last_error = self.error
        self.last_time = current_time
        return self.output


    """ Reseta os termos integral e último erro """
    def reset(self):
        self.integral = 0.0
        self.last_error = 0.0
        self.last_time = ticks_ms()


    """ Atualiza o valor desejado (setpoint) e reseta os acumuladores """
    def set_setpoint(self, setpoint: float):
        self.setpoint = setpoint
        self.reset()


    """ Retorna os parâmetros do controlador """
    def get_params(self) -> dict:
        return {
            'setpoint': self.setpoint,
            'Kp': self.Kp,
            'Ki': self.Ki,
            'Kd': self.Kd,
            'tolerance': self.tol
        }
