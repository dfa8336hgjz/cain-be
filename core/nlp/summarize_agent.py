from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.documents import Document
from typing import *

from langchain_core.prompts import ChatPromptTemplate

from core.nlp.langchain.langchain_google_connector import get_chat_model


class SummarizeAgent:
    def __init__(self):
        llm = get_chat_model()
        prompt = ChatPromptTemplate.from_messages(
            [("system", "You will be given excerpts from many documents. "
                        "Your task is to write a concise summary of the those documents. "
                        "Please do not focus on one topics. "
                        "\\n Please provide your summary in {language}."
                        "\\n Provide only plain text, no format."
                        "\\n Use maximum of 300 words."),
             ("human", "{context}")]
        )

        # Instantiate chain
        self.chain = create_stuff_documents_chain(llm, prompt)

    async def summarize(self, documents: List[Document], language: str):
        return await self.chain.ainvoke({'context': documents, 'language': language})