
from langchain.document_loaders import Docx2txtLoader

class DocxReader:
    @staticmethod
    def extract_text(self, docx_path) -> list[str]:
        loader = Docx2txtLoader(docx_path)
        files = loader.load()
        doc_list = [str(doc) for doc in files]
        return doc_list