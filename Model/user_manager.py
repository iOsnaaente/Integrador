class UserManager:
    """
    Gerencia os dados do usuário no sistema.
    A classe encapsula as informações do usuário, como:
    - username: Nome do usuário.
    - last_access: Data/hora do último acesso.
    - level_access: Nível de acesso do usuário (adm ou opr).
    - photo: Imagem do usuário (em bytes).
    - login_index: Índice ou identificador do login.
    """

    _username: str 
    _password: str
    _checkbox: str
    _last_access: str
    _level_access: str 
    _login_index: int 
    _photo: bytes
    _debug: bool 

    def __init__( self, debug: bool = False ):
        self._username = ""
        self._last_access = ""
        self._level_access = ""
        self._photo = b""
        self._login_index = 0
        self._debug = debug


    """ Nome do usuário.""" 
    @property
    def username(self) -> str:
        return self._username
    @username.setter
    def username(self, value: str) -> None:
        self._username = value

    """ Password de login do usuário.""" 
    @property
    def password(self) -> str:
        return self._password
    @password.setter
    def password(self, value: str) -> None:
        self._password = value

    """ Índice do login do usuário.""" 
    @property
    def checkbox_state(self) -> str:
        return self._checkbox
    @checkbox_state.setter
    def checkbox_state(self, value: str) -> None:
        self._checkbox = value

    """ Data/hora do último acesso.""" 
    @property
    def last_access(self) -> str:
        return self._last_access
    @last_access.setter
    def last_access(self, value: str) -> None:
        self._last_access = value

    """ Nível de acesso do usuário.""" 
    @property
    def level_access(self) -> str:
        return self._level_access
    @level_access.setter
    def level_access(self, value: str) -> None:
        self._level_access = value

    """ Foto do usuário em bytes.""" 
    @property
    def photo(self) -> bytes:
        return self._photo
    @photo.setter
    def photo(self, value: bytes) -> None:
        self._photo = value

    """ Índice do login do usuário.""" 
    @property
    def login_index(self) -> int:
        return self._login_index
    @login_index.setter
    def login_index(self, value: int) -> None:
        self._login_index = value