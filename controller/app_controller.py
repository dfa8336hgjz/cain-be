from controller.auth_controller import AuthController
from controller.chunk_controller import ChunkController
from controller.user_controller import UserController
from controller.notebook_controller import NotebookController
from controller.file_controller import FileController


class AppController:
    __instance = None

    def __init__(self):
        self.auth_controller = AuthController(self)
        self.user_controller = UserController(self)
        self.notebook_controller = NotebookController(self)
        self.file_controller = FileController(self)
        self.chunk_controller = ChunkController(self)

    @staticmethod
    def get_instance():
        if AppController.__instance is None:
            AppController.__instance = AppController()
        return AppController.__instance
    
controller = AppController.get_instance()