from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_website(url: str):
    loader = WebBaseLoader(web_paths = [url])
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 200, chunk_overlap = 50)
    splits = text_splitter.split_documents(docs)
    return splits

def load_pdf(file):
    loader = PyPDFLoader(file)
    docs = loader.load()
    text_spliiter = RecursiveCharacterTextSplitter(chunk_size = 200, chunk_overlap=50)
    splits = text_spliiter.split_documents(docs)
    return splits
