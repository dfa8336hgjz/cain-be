from typing import List
from langchain.document_loaders import Docx2txtLoader

class DocxReader:
    @staticmethod
    def extract_text(self, docx_path) -> List[str]:
        loader = Docx2txtLoader(docx_path)
        documents = loader.load()
        doc_list = [str(doc) for doc in documents]
        return doc_list