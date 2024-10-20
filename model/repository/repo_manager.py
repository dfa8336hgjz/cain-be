from core.nlp.langchain.langchain_google_connector import get_embedding
from model.repository.chunk_repo import ChunkRepository
from model.repository.chunk_vector_repo import ChunkVectorRepository


class RepositoryManager:
    def __init__(self):
        self.chunk_repo = ChunkRepository()
        self.chunk_vector_repo = ChunkVectorRepository(get_embedding())


def get_repositories():
    return RepositoryManager()