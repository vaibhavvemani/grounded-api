from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """<h1>Welcome to Grounded!</h1> 
    <ul>
        <li>/: homepage </li>
        <li>/pdf: RAG with a pdf </li>
        <li>/webpage: RAG with a webpage </li>
        <li>/testcase: Using RAG to build testcases </li>
        <li>/sql: Using RAG to create SQL queries </li>
    </ul>"""

@app.route('/pdf')
def pdf():
    return "pdf"

@app.route('/webpage')
def webpage():
    return "webpage"

@app.route('/testcase')
def testcase():
    return "testcase"

@app.route('/sql')
def sql():
    return "sql"
