from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.documents import Document

from langchain_core.prompts import ChatPromptTemplate

from core.nlp.langchain_google_connector import get_chat_model


class SummarizeAgent:
    def __init__(self):
        llm = get_chat_model()
        prompt = ChatPromptTemplate.from_messages(
            [("system", "You will be given excerpts from many files. "
                        "Your task is to write a concise summary of the those files. "
                        "Please do not focus on one topics. "
                        "\\n Please provide your summary in {language}."
                        "\\n Provide only plain text, no format."
                        "\\n Use maximum of 300 words."),
             ("human", "{context}")]
        )

        # Instantiate chain
        self.chain = create_stuff_documents_chain(llm, prompt)

    async def summarize(self, files: list[Document], language: str):
        return await self.chain.ainvoke({'context': files, 'language': language})