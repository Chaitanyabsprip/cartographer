import logging as l
import os
import sys

import uvicorn
from fastapi import APIRouter, FastAPI, HTTPException, Query, Request

from cartographer.app import FileEmbedder

home = os.environ.get("HOME", "")
l.basicConfig(
    format="PY %(asctime)s %(levelname)s: %(message)s",
    filename=f"{home}/.local/cache/cartographer/debug.log",
    encoding="utf-8",
    filemode="a",
    level=l.DEBUG,
)


app = FastAPI()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    req_body = await request.body()
    l.info(f"{request.url} {req_body}")
    return await call_next(request)


class Server:
    def __init__(self, embedder: FileEmbedder):
        self.embedder = embedder
        self.router = APIRouter()
        self.router.add_api_route("/health", self.healthcheck, methods=["GET"])
        self.router.add_api_route("/embed", self.embed_get, methods=["GET"])
        self.router.add_api_route("/embed", self.embed_post, methods=["POST"])

    async def embed_get(self, filepath: str = Query(None)):
        if filepath is None:
            raise HTTPException(
                status_code=400, detail="Missing filepath query parameter"
            )
        embedding = self.embedder.embed_file(filepath)
        return {"embedding": embedding}

    async def embed_post(self, request: Request):
        data = await request.body()
        embedding = self.embedder.embed_text(str(data))
        return embedding.tolist()

    async def healthcheck(self):
        return {"status": {"healthy": "wealthy"}}


def main():
    model_name = sys.argv[1]
    l.debug(f"starting daemon with model {model_name}")
    embedder = FileEmbedder(model_name)
    server = Server(embedder)
    app.include_router(server.router)
    uvicorn.run(app, port=30000, host="0.0.0.0")
    l.debug("closing daemon")


if __name__ == "__main__":
    main()
