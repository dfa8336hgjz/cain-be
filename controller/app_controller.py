from controller.auth_controller import AuthController
from controller.user_controller import UserController
from controller.notebook_controller import NotebookController
from controller.file_controller import FileController
from utils.singleton import Singleton


class AppController(metaclass=Singleton):
    def __init__(self):
        self.auth_controller = AuthController()
        self.user_controller = UserController()
        self.notebook_controller = NotebookController()
        self.file_controller = FileController()
        

def get_app_controller() -> AppController:
    return AppController()