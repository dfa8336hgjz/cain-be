from langchain.document_loaders import PyPDFLoader

class PDFReader:
    @staticmethod
    def extract_text(self, pdf_path):
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        for i, document in enumerate(documents):
            print(f"Page {i+1} content:\n{document.page_content}\n")