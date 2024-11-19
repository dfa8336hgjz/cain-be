from langchain.document_loaders import PyPDFLoader

class PDFReader:
    @staticmethod
    def extract_text(self, pdf_path):
        loader = PyPDFLoader(pdf_path)
        files = loader.load()
        for i, file in enumerate(files):
            print(f"Page {i+1} content:\n{file.page_content}\n")