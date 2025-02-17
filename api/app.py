from flask import Flask
from waitress import serve

app = Flask(__name__)

@app.route("/")
def main():
    return "Hello fella"


if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=12112)