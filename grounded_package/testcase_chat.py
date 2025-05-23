import os 
from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")


def parse_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    return content

def test_chat():

    chat = ChatGoogleGenerativeAI(
        temperature=0.2,
        model="chat-bison",
        max_output_tokens=1024,
        top_k=40,
        top_p=0.95,
        stop_sequences=["\n"],
    )


