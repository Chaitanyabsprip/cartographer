import logging as l
from http import HTTPStatus
from os import getpid

from flask import Flask, Response, json, jsonify, request
from werkzeug.exceptions import HTTPException

from cartographer.app import App, format_search_results

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
    filepath = request.args.get("filepath")
    app.index(filepath)
    return "Indexing Completed\n"


@server.route("/search", methods=["GET"])
def perform_search():
    query = request.args.get("query", "", type=str)
    limit = request.args.get("limit", type=int)
    results = format_search_results(app.search(query, limit))
    return jsonify(results)


@server.route("/embed", methods=["POST", "GET"])
def embed():
    if request.method == "GET":
        filepath = request.args.get("filepath")
        if filepath is None:
            return Response(
                "The response body goes here", status=HTTPStatus.BAD_REQUEST
            )
        return jsonify(app.embedder.embed_file(filepath))
    if request.method == "POST":
        data = str(request.data)
        l.debug(data)
        return jsonify(app.embedder.embed_text(data).tolist())
    return Response("Invalid HTTP METHOD", status=HTTPStatus.BAD_REQUEST)


@server.route("/health", methods=["GET"])
def healthcheck():
    return "I'm healthier"


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


@server.route("/site-map", methods=["GET"])
def site_map():
    links = []
    for rule in server.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = rule.rule
            # url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))
    # links is now a list of url, endpoint tuples
    return links
