import os
from flask import Flask, request, jsonify
from grounded_package.web_chat import rag_chain_web
from grounded_package.pdf_chat import rag_chain_pdf

app = Flask(__name__)

folder = "uploads"
os.makedirs(folder, exist_ok=True)
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
        return jsonify({"error": "Send the file dummy"})

    file = request.files["file"]
    question = request.form.get("question")

    if file.filename == "":
        return jsonify({"error": "Select a file idiot"})

    filepath = os.path.join(app.config["upload_folder"], file.filename)
    file.save(filepath)
    reply = rag_chain_pdf(filepath, question, file.filename)

    return jsonify(reply)

@app.route('/webpage', methods=['POST'])
def webpage():
    try: 
        data = request.get_json()
        web_url = data['url']
        question = data['question']
        session_id = data['url']
    except Exception:
        return jsonify({"error": "Oops there seems to be an error contact the pro man"})

    reply = rag_chain_web(web_url, question, session_id)

    return jsonify(reply)

@app.route('/testcase', methods=["POST"])
def testcase():
    try:
        if "file" not in request.files:
            return jsonify({"error": "Yo send the file bro"})

        file = request.files["code"]
        code_file = file.read().decode("utf-8") 
        function_name = file.form.get('function')
        user_desc = file.form.get('description')

        return jsonify({"message": "I recieved the code thanks"})
    except Exception:
        return jsonify({"error": "Oops there seems to be an error contact Mr. Vaibhav Vemani"})

@app.route('/sql')
def sql():
    return "sql"
