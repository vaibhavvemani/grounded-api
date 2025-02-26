import os
from dotenv import load_dotenv
load_dotenv()

from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder  
from langchain_core.runnables.history import RunnableWithMessageHistory

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY is None:
    raise ValueError("Please set the GOOGLE_API_KEY environment variable")

def load_website(file):
    loader = PyPDFLoader(file)
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 50)
    splits = text_splitter.split_documents(docs)
    return splits

def upload_to_fiass(docs, embedding_model):
    vectorstore = FAISS.from_documents(docs, embedding_model)
    store_retriever = vectorstore.as_retriever()
    return store_retriever

store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
        
    return store[session_id]

def rag_chain(website_url: str, question: str, session_id: str):
    llm = ChatGoogleGenerativeAI(model="models/gemini-2.0-flash-lite-001", temperature=0.7, top_p=0.85)
    embedding_model = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
    docs = load_website(website_url)
    store_retriever = upload_to_fiass(docs, embedding_model)

    contextual_system_prompt = """Given a chat history and the latest user query which might reference
    context in the history, generate a standalone question which can be understood without
    the chat history. Do NOT answer the question, just generate it if needed otherwise return it as is."""

    contextual_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextual_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ]
    )

    history_aware_retriever = create_history_aware_retriever(llm, store_retriever, contextual_prompt)

    system_prompt = """You are an assistant for question answering tasks.
    Use only the given context to answer the question. Do not use any external information.
    If you don't konw the answer just say I don't know.
    Context: {context}"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ]
    )

    qa_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, qa_chain)

    final_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer"
    )

    response = final_chain.invoke(
        {"input": question},
        config = {
            "configurable": {
                "session_id": session_id
            }
        }
    )['answer']

    return response

