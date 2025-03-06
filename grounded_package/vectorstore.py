from langchain_community.vectorstores import FAISS

def upload_to_fiass(docs, embedding_model):
    vectorstore = FAISS.from_documents(docs, embedding_model)
    store_retriever = vectorstore.as_retriever()
    return store_retriever
