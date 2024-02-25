import logging as l
import os

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Request

from cartographer.app import App

server = FastAPI()
app = App()

# home = os.environ.get("HOME", "")
# cache_filepath = f"{home}/.cache/cartographer/debug.log"
# l.basicConfig(
#     format="PY %(asctime)s %(levelname)s: %(message)s",
#     filename=cache_filepath,
#     encoding="utf-8",
#     filemode="a",
#     level=l.DEBUG,
# )


@server.middleware("http")
async def log_requests(request: Request, call_next):
    req_body = await request.body()
    l.info(f"{request.url} {req_body}")
    return await call_next(request)


@server.get("/embed")
async def embed_get(filepath: str = Query(None)):
    if filepath is None:
        raise HTTPException(status_code=400, detail="Missing filepath query parameter")
    embedding = app.embedder.embed_file(filepath)
    return {"embedding": embedding}


@server.post("/embed")
async def embed_post(request: Request):
    data = await request.body()
    embedding = app.embedder.embed_text(str(data))
    return embedding.tolist()


@server.get("/health")
async def healthcheck():
    return {"status": {"healthy": "wealthy"}}


def main():
    l.debug("starting server")
    uvicorn.run(server, port=30000, host="0.0.0.0")
    l.debug("server started")


if __name__ == "__main__":
    main()
