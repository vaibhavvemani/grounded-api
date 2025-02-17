from dotenv import load_dotenv
load_dotenv()

import os
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from pinecone import Pinecone as pc

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

pinecone_client = pc(api_key = PINECONE_API_KEY)
def pinecone_init(embedding_model, host):
    index = pinecone_client.Index(host = host)
    vectorstore = PineconeVectorStore(embedding = embedding_model, index = index)
    return vectorstore

def load_website(vectorstore, url: str):
    loader = WebBaseLoader(web_paths = [url])
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 50)
    splits = text_splitter.split_documents(docs)
    vectorstore.add_documents(splits)

def load_pdf(vectorstore, path: str):
    loader = PyPDFLoader(file_path = path)
    docs = loader.load()
    text_spliiter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap=50)
    splits = text_spliiter.split_documents(docs)
    vectorstore.add_documents(splits)

store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
        
    return store[session_id]

    

if __name__ == "__main__":
    website_url = "https://en.wikipedia.org/wiki/Mahabrahma"
    pinecone_host = "https://rag-testing-m4lr6ld.svc.aped-4627-b74a.pinecone.io"
    llm_model = "models/gemini-2.0-flash-thinking-exp-01-21"
    embedding_model = "models/embedding-001"

    llm = GoogleGenerativeAI(model=llm_model, temperature=0.4, top_p=0.85)
    gemini_embeddings = GoogleGenerativeAIEmbeddings(model = embedding_model)
    vectorstore = pinecone_init(gemini_embeddings, pinecone_host)
    store_retriever = vectorstore.as_retriever()

    contextual_system_prompt = """Given a chat history and the latest user query which might 
    reference context in the history, generate a standalone question which can be understood without
    the chat history. Do NOT answer the question, just generate it if needed otherwise return it
    as is."""

    contextual_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextual_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ]
    )

    histry_aware_retriever = create_history_aware_retriever(llm, store_retriever, contextual_prompt)

    system_prompt = """You are an assistant for question answering tasks.
    Use only the given context to answer the question.
    If you don't know the answer just say I don't know.
    Use a maximum of 3 sentences to answer the question.

    Context: {context}
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ]
    )

    qa_chain = create_stuff_documents_chain(llm , prompt)
    rag_chain = create_retrieval_chain(histry_aware_retriever, qa_chain)
    
    final_chain = RunnableWithMessageHistory(
        rag_chain, 
        get_session_history, 
        input_messages_key="input", 
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

    while True:
        question = input("Enter your question: ")
        if question.lower() == "exit":
            print("Exiting...")
            break
        elif question.lower() == "pdf":
            path = input("Enter the path to the pdf: ")
            docs = load_pdf(vectorstore, path)
        elif question.lower() == "web":
            url = input("Enter the url: ")
            docs = load_website(vectorstore, url)
        
        result = final_chain.invoke(
            {"input": question},
            config = {
                "configurable": {"session_id": "test"}
            },
        )['answer']
        print(result)


