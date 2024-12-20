from typing import *

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever

from weaviate.collections.classes.filters import Filter
from core.nlp.langchain_google_connector import get_chat_model, get_embedding
from db.weaviate_db import get_langchain_weaviate_vectorstore

from schema.message_schema import BaseMessage
from dotenv import load_dotenv

load_dotenv()
# os.environ['GOOGLE_API_KEY'] = "AIzaSyDZGG5KFPKJhx-VSoVe0CrD64nAG5cLlV8"

class RagAgent:
    def __init__(self, file_ids: list[str]):
        self.file_ids = file_ids
        self.llm = get_chat_model()
        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is."
            "Do not include any icons in your answer."
        )

        self.contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        
        system_prompt = (
            "You are an assistant for question-answering tasks named CAIN."
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Use five sentences maximum and keep the "
            "answer concise. Do not include any special characters in your answer."
            "\n\n"
            "{context}"
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        self.question_answer_chain = create_stuff_documents_chain(self.llm, prompt)

    def parse_rag_chain(self, vectorstore):
        filter_file = Filter.by_property("file_id").contains_any(self.file_ids)
        retriever = vectorstore.as_retriever(
            search_kwargs={'filters': filter_file}
        )
        history_aware_retriever = create_history_aware_retriever(
            self.llm, retriever, self.contextualize_q_prompt
        )
        rag_chain = create_retrieval_chain(history_aware_retriever, self.question_answer_chain)
        return rag_chain


    def get_answer(self, query: str, chat_history: list[BaseMessage]):
        with get_langchain_weaviate_vectorstore(get_embedding()) as vectorstore:
            rag_chain = self.parse_rag_chain(vectorstore)
            messages = []
            for chat in chat_history:
                if chat.message_id.startswith("a"):
                    messages.append(HumanMessage(content=chat.content))
                elif chat.message_id.startswith("b"):
                    messages.append(AIMessage(content=chat.content))
            
            result = rag_chain.invoke({"input": query, "chat_history": messages})
            
            return result["answer"]
