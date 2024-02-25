import logging as l
import os
import sys

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Request

from cartographer.app import FileEmbedder

home = os.environ.get("HOME", "")
l.basicConfig(
    format="PY %(asctime)s %(levelname)s: %(message)s",
    filename=f"{home}/.local/cache/cartographer/debug.log",
    encoding="utf-8",
    filemode="a",
    level=l.DEBUG,
)


class Server:
    server = FastAPI()

    def __init__(self, embedder: FileEmbedder):
        self.embedder = embedder

    @server.middleware("http")
    async def log_requests(self, request: Request, call_next):
        req_body = await request.body()
        l.info(f"{request.url} {req_body}")
        return await call_next(request)

    @server.get("/embed")
    async def embed_get(self, filepath: str = Query(None)):
        if filepath is None:
            raise HTTPException(
                status_code=400, detail="Missing filepath query parameter"
            )
        embedding = self.embedder.embed_file(filepath)
        return {"embedding": embedding}

    @server.post("/embed")
    async def embed_post(self, request: Request):
        data = await request.body()
        embedding = self.embedder.embed_text(str(data))
        return embedding.tolist()

    @server.get("/health")
    async def healthcheck():
        return {"status": {"healthy": "wealthy"}}


def main():
    model_name = sys.argv[1]
    l.debug(f"starting daemon with model {model_name}")
    embedder = FileEmbedder(model_name)
    uvicorn.run(Server(embedder).server, port=30000, host="0.0.0.0")
    l.debug("closing daemon")


if __name__ == "__main__":
    main()
