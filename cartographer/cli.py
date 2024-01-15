import logging as l
from argparse import ArgumentParser

import requests
from app import App, format_search_results

from daemon.server import server

l.basicConfig(
    filename="/Users/chaitanyasharma/projects/cartographer/debug.log",
    encoding="utf-8",
    level=l.ERROR,
)


def is_server_running():
    try:
        response = requests.get("http://127.0.0.1:80/")
        l.debug("server is running")
        return response.ok
    except requests.exceptions.ConnectionError:
        l.debug("server is not running")
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
        "-D",
        "--daemon",
        action="store_true",
        help="Run the server as a daemon",
    )
    parser.add_argument(
        "-q",
        "--query",
        help="Query string for semantic search",
    )
    parser.add_argument(
        "-c",
        "--config",
        help="Use provided config file",
    )
    return parser.parse_args()


def main():
    parser = ArgumentParser(description="Semantic Search Program")
    args = parse_args(parser)
    if args.daemon:
        return server.run(host="0.0.0.0", port=80)
    if args.query:
        if not is_server_running():
            print("Server is not running. Starting the server...")
            server.run(debug=True)
        print(format_search_results(App().search(args.query, 20)))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
