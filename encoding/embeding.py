from dataclasses import dataclass
from json import dump
from json import load as jLoad
from os import environ, path, walk
from re import sub
from string import punctuation

import torch
from bs4 import BeautifulSoup
from markdown import markdown
from numpy import array
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("msmarco-distilbert-base-v4")


@dataclass
class Config:
    directory: str
    embeddings_file: str
    embeddings: dict | None


notespath = environ["NOTESPATH"]  # this is unsafe, use a config file instead
config = Config(
    directory=notespath,
    embeddings_file=f"{notespath}/.embeddings",
    embeddings={},
)


def remove_urls(text: str) -> str:
    cleaned_text = sub(r"http\S+|www\S+", "", text)
    cleaned_text = sub(r"\[(.*?)\]\((.*?)\)", "", cleaned_text)
    return cleaned_text


def remove_html_tags(text: str) -> str:
    soup = BeautifulSoup(text, "html.parser")
    cleaned_text = soup.get_text(separator=" ")
    return cleaned_text


def remove_decorations(text: str) -> str:
    cleaned_text = sub(r"[*_~]", "", text)
    return cleaned_text


def remove_punctuation(text: str) -> str:
    cleaned_text = text.translate(str.maketrans("", "", punctuation))
    return cleaned_text


def clean_text(text: str) -> str:
    cleaned_text = remove_punctuation(
        remove_decorations(remove_html_tags(remove_urls(text)))
    )
    return cleaned_text.strip()


def embed_text(text: str) -> list[float]:
    return model.encode([text])[0].tolist()


def embed_file(file_path: str):
    with open(file_path, "r", encoding="utf-8") as file:
        markdown_content = file.read()
        html_content = markdown(markdown_content)
        cleaned_text = clean_text(html_content)
        embedding = embed_text(cleaned_text)
        return embedding


def write_embeddings(
    embeddings: dict[str, list[float]], file_path: str
) -> None:
    with open(file_path, "w", encoding="utf-8") as file:
        dump(embeddings, file, indent=4)


def process_files(directory: str):
    embeddings: dict[str, list[float]] = {}
    for root, _, files in walk(directory):
        for filename in files:
            if filename.endswith(".md"):
                file_path = path.abspath(path.join(root, filename))
                embedding = embed_file(file_path)
                embeddings[file_path] = embedding
    return embeddings


def index_files(fpath: str, embeddings_file: str) -> None:
    embeddings = config.embeddings or {}
    if path.isfile(fpath):
        abs_file_path = path.abspath(fpath)
        embedding = embed_file(abs_file_path)
        embeddings[abs_file_path] = embedding
    elif path.isdir(fpath):
        new_embeddings = process_files(fpath)
        embeddings.update(new_embeddings)
    else:
        return print("Invalid file or directory path.")
    write_embeddings(embeddings, embeddings_file)


def search(query, embeddings_file, top_k=None):
    if not config.embeddings:
        with open(embeddings_file, "r", encoding="utf-8") as file:
            config.embeddings = jLoad(file)
    query_embedding = torch.from_numpy(model.encode([query])[0]).float()
    scores = {}
    for filename, embedding in config.embeddings.items():
        score = util.pytorch_cos_sim(
            query_embedding, torch.from_numpy(array(embedding)).float()
        )
        scores[filename] = score.item()
    sorted_scores = {
        k: v
        for k, v in sorted(
            scores.items(), key=lambda item: item[1], reverse=True
        )
    }
    results = list(sorted_scores.keys())
    if top_k:
        results = list(sorted_scores.keys())[: int(top_k)]
    return results


def format_search_results(results):
    formatted_results = []
    for result in results:
        result_dict = {
            "filename": result,
            "display_filename": result.split("/")[-1],
            "directory": "/".join(result.split("/")[:-1]),
        }
        formatted_results.append(result_dict)
    return formatted_results


def make_search_request(query, limit):
    embeddings_file = config.embeddings_file
    results = search(query, embeddings_file, top_k=limit)
    formatted_results = format_search_results(results)
    return formatted_results
