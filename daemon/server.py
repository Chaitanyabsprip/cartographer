import time
from os import getpid

from flask import Flask, json, jsonify, request
from werkzeug.exceptions import HTTPException

from encoding.app import App

server = Flask(__name__)
app = App()


@server.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps(
        {
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }
    )
    response.content_type = "application/json"
    return response


@server.route("/")
def hello():
    help_data = """
    Welcome to the Semantic Search Server!

    Available endpoints:
    - /search?query=<your_query> - Perform a semantic search with the specified
      query.
    - /index - Index the markdown files and generate embeddings.

    For more details, please refer to the API documentation.
    """
    return help_data


@server.route("/info", methods=["GET"])
def info():
    return jsonify({"pid": getpid()})


@server.route("/index", methods=["GET"])
def index():
    start = time.time()
    filepath = request.args.get("filepath")
    app.index(filepath)
    print((time.time() - start) * 10**3)
    return "Indexing Completed\n"


@server.route("/search", methods=["GET"])
def perform_search():
    query = request.args.get("query", "", type=str)
    limit = request.args.get("limit", type=int)
    results = app.search(query, limit)
    return jsonify(results)


@server.route("/health", methods=["GET"])
def healthcheck():
    return "I'm healthier"
