import logging as l
import os
import sys
from argparse import ArgumentParser

from app import App, format_search_results

# from daemon.server import server
import daemon.fserver as fserv

home = os.environ.get("HOME", "")
l.basicConfig(
    format="PY %(asctime)s %(levelname)s: %(message)s",
    filename=f"{home}/.cache/cartographer/debug.log",
    encoding="utf-8",
    filemode="a",
    level=l.DEBUG,
)


# def is_server_running():
#     try:
#         response = requests.get("http://127.0.0.1:30000/")
#         l.debug("server is running")
#         return response.ok
#     except requests.exceptions.ConnectionError:
#         l.debug("server is not running")
#         return False


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
    if "-l" in sys.argv or "--limit" in sys.argv:
        parser.add_argument(
            "-l",
            "--limit",
            help="Limit the number of results",
        )
    parser.add_argument(
        "-i",
        "--index",
        action="store_true",
        help="(Re)index documents",
    )
    if "-i" in sys.argv or "--index" in sys.argv:
        parser.add_argument(
            "-f",
            "--filepath",
            help="Path to file to be indexed, if not passed, all documents will be (re)indexed",
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
    app = App()
    if args.daemon:
        l.debug("starting daemon")
        # return server.run(host="0.0.0.0", port=30000)
        return fserv.main()
    if args.index:
        l.debug(f"[CLI] indexing: {args.filepath}")
        return app.index(args.filepath)
    if args.query:
        return print(format_search_results(app.search(args.query, 20)), end="")
    parser.print_help()


if __name__ == "__main__":
    main()
