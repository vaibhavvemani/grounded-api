import os
from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder  
from langchain_core.runnables.history import RunnableWithMessageHistory

from grounded_package.document_extractor import load_pdf
from grounded_package.vectorstore import upload_to_fiass
from grounded_package.prompt_templates import contextual_system_prompt
from grounded_package.prompt_templates import system_prompt

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY is None:
    raise ValueError("Please set the GOOGLE_API_KEY environment variable")


chat_store = {}
faiss_store = {}

def get_session_history(session_id: str):
    if session_id not in chat_store:
        chat_store[session_id] = ChatMessageHistory()
        
    return chat_store[session_id]

def rag_chain_pdf(file_path: str, question: str, session_id: str):
    llm = ChatGoogleGenerativeAI(model="models/gemini-2.0-flash-lite-001", temperature=0.6, top_p=0.85)
    embedding_model = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")

    if file_path not in faiss_store:
        docs = load_pdf(file_path)
        store_retriever = upload_to_fiass(docs, embedding_model)
        faiss_store[file_path] = store_retriever
    else:
        store_retriever = faiss_store[file_path]

    contextual_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextual_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ]
    )

    history_aware_retriever = create_history_aware_retriever(llm, store_retriever, contextual_prompt)


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
