from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

app = Flask(__name__)

@app.route("/message/<name>")
@cross_origin()
def hello_world(name: str):
    return jsonify({"message": f"hello {name}"})