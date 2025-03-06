import os
from flask import Flask, request, jsonify
from grounded_package.web_chat import rag_chain

app = Flask(__name__)

folder = "uploads"
os.makedirs(folder, exists_ok = True)
app.config["upload_folder"] = folder

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

@app.route('/pdf', methods=["POST"])
def pdf():
    if "file" not in request.files:
        return jsonify({"error": "File not found"})

    file = request.files["file"]
    question = request.form.get("question")

    if file.filename == "":
        return jsonify({"error": "File not selected"})
    
    filepath = os.path.join(app.config["upload_folder"], file.filename)

    file.save(filepath)

    print(file.filename, filepath, question)




@app.route('/webpage', methods=['POST'])
def webpage():
    try: 
        data = request.get_json()
        web_url = data['url']
        question = data['question']
        session_id = data['url']
    except Exception:
        return jsonify({"error": "Invalid input"})

    reply = rag_chain(web_url, question, session_id)

    return jsonify(reply)

@app.route('/testcase')
def testcase():
    return "testcase"

@app.route('/sql')
def sql():
    return "sql"
