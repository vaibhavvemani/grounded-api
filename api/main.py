from flask import Flask

app = Flask(__name__)

@app.route("/", methods=['GET'])
def test():
    return "Hello fella"


if __name == '__main__':
    app.run()
