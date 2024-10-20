from typing import *

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever

from weaviate.collections.classes.filters import Filter
from core.nlp.langchain.langchain_google_connector import get_chat_model, get_embedding
from db.weaviate_db import get_langchain_weaviate_vectorstore

from schema.message_schema import BaseMessage


class RagAgent:
    def __init__(self, document_ids: List[str]):
        self.document_ids = document_ids
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
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Use three sentences maximum and keep the "
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
        """
        Create a RAG chain using the given vectorstore. The RAG chain is a
        retrieval-based chain that takes a query and a chat history as input.
        It first uses the vectorstore to retrieve the top N documents that
        match the query. Then it uses the contextualize_q_prompt to generate
        a standalone question from the query and the chat history. Finally it
        uses the question_answer_chain to answer the generated question based
        on the retrieved documents.

        Args:
            vectorstore (LangchainVectorStore): The vectorstore to use for retrieval

        Returns:
            RAGChain: The RAG chain that can be used to answer questions
        """
        filter_file = Filter.by_property("file_id").contains_any(self.document_ids)
        retriever = vectorstore.as_retriever(
            search_kwargs={'filters': filter_file}
        )
        history_aware_retriever = create_history_aware_retriever(
            self.llm, retriever, self.contextualize_q_prompt
        )
        rag_chain = create_retrieval_chain(history_aware_retriever, self.question_answer_chain)
        return rag_chain


    def stream_answer(self, query: str, chat_history: List[BaseMessage]):
        """
        This function takes a query and a chat history as input and returns an
        iterator over the answer chunks. The function first creates a RAG
        chain using the given vectorstore. The RAG chain is a retrieval-based
        chain that takes a query and a chat history as input. It first uses
        the vectorstore to retrieve the top N documents that match the query.
        Then it uses the contextualize_q_prompt to generate a standalone
        question from the query and the chat history. Finally it uses the
        question_answer_chain to answer the generated question based on the
        retrieved documents.

        The function then streams the answer chunks from the RAG chain. The
        chunks are yielded one by one.

        Args:
            query (str): The query to answer
            chat_history (List[BaseMessage]): The chat history

        Yields:
            str: The answer chunks
        """
        with get_langchain_weaviate_vectorstore(get_embedding()) as vectorstore:
            rag_chain = self.parse_rag_chain(vectorstore)
            messages = []
            for chat in chat_history:
                if chat.message_id.startswith("u"):
                    messages.append(HumanMessage(content=chat.content))
                elif chat.message_id.startswith("b"):
                    messages.append(AIMessage(content=chat.content))
            for chunk in rag_chain.stream({
                "input": query,
                "chat_history": messages,
            }):
                yield chunk
