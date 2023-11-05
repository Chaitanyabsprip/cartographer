import time
from os import getpid

from embedding import emb, make_search_request
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/")
def hello():
    help_data = """
    Welcome to the Semantic Search Server!

    Available endpoints:
    - /search?query=<your_query> - Perform a semantic search with the specified query.
    - /index - Index the markdown files and generate embeddings.

    For more details, please refer to the API documentation.
    """
    return help_data


@app.route("/info", methods=["GET"])
def info():
    return jsonify({"pid": getpid()})


@app.route("/index", methods=["GET"])
def index():
    start = time.time()
    emb.index_files()
    print((time.time() - start) * 10**3)
    return "Indexing Completed\n"


@app.route("/search", methods=["GET"])
def perform_search():
    query = request.args.get("query")
    limit = request.args.get("limit")
    results = make_search_request(query, limit)
    return jsonify(results)
