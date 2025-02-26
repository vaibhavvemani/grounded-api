from dotenv import load_dotenv
import getpass
load_dotenv()

import os
from langchain.vectorstores import FAISS
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import GoogleGenerativeAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

os.environ['GOOGLE_API_KEY'] = getpass.getpass('Gemini API Key:')
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def load_website(url: str):
    loader = WebBaseLoader(web_paths = [url])
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 50)
    splits = text_splitter.split_documents(docs)
    return splits

def load_pdf(path: str):
    loader = PyPDFLoader(file_path = path)
    docs = loader.load()
    text_spliiter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap=50)
    splits = text_spliiter.split_documents(docs)
    return splits

store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
        
    return store[session_id]


if __name__ == "__main__":
    website_url = "https://en.wikipedia.org/wiki/Christmas"
    pinecone_host = "https://rag-testing-m4lr6ld.svc.aped-4627-b74a.pinecone.io"
    llm_model = "models/gemini-2.0-flash-thinking-exp-01-21"
    embedding_model = "models/embedding-001"



    llm = GoogleGenerativeAI(model=llm_model, temperature=0.7, top_p=0.85)
    gemini_embeddings = GoogleGenerativeAIEmbeddings(model = embedding_model)
    docs = load_website(website_url)
    vectorstore = FAISS.from_documents(docs, gemini_embeddings)
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
        print("Select an option: \n1. Ask a question\n2. Load a pdf\n3. Load a website\n4. Exit")
        option = input("Enter your choice: ")
        if option == "1":
            while True:
                question = input("Enter your question: ")
                if question.lower() == "exit":
                    print("Exiting...")
                    break
                elif question.lower() == "pdf":
                    path = input("Enter the path to the pdf: ")
                    docs = load_pdf(path)
                elif question.lower() == "web":
                    url = input("Enter the url: ")
                    docs = load_website(url)
                
                response = final_chain.invoke(
                    {"input": question},
                    config = {
                        "configurable": {"session_id": "test"}
                    },
                )['answer']
                print(response)
        elif option == "2":
            path = input("Enter the path to the pdf: ")
            docs = load_pdf(path)
            vectorstore.add_documents(docs)
        elif option == "3":
            url = input("Enter the url: ")
            docs = load_website(url)
            vectorstore.add_documents(docs)
        elif option == "4":
            print("Exiting...")
            break
        else:
            print("Invalid option")

