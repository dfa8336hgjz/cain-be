from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

# embedding creator
def get_embedding():
    return GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# chat model
def get_chat_model():
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
