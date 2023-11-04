from argparse import ArgumentParser

import requests
from embeding import make_search_request
from server import app


def is_server_running():
    try:
        response = requests.get("http://127.0.0.1:5000/")
        return response.ok
    except requests.exceptions.ConnectionError:
        return False


def parse_args(parser: ArgumentParser):
    parser.add_argument(
        "-d",
        "--directory",
        help="Directory path of markdown files",
    )
    parser.add_argument(
        "-e",
        "--embeddings",
        help="Embeddings file path",
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run the server as a daemon",
    )
    parser.add_argument(
        "-q",
        "--query",
        help="Query string for semantic search",
    )
    return parser.parse_args()


def main():
    parser = ArgumentParser(description="Semantic Search Program")
    args = parse_args(parser)
    if args.daemon:
        return app.run()
    if args.query:
        if not is_server_running():
            print("Server is not running. Starting the server...")
            app.run()
        print(make_search_request(args.query, 20))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
