import os
import pickle
from os.path import isdir

import torch
from embedding import Embedder, config
from markdown import markdown
from numpy import array
from sentence_transformers import util
from text_processor import TextProcessor

emb = Embedder()
tp = TextProcessor()


def get_clean_text(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        markdown_content = file.read()
        html_content = markdown(markdown_content)
        cleaned_text = tp.clean(html_content)
        return cleaned_text


def embed_file(file_path: str):
    cleaned_text = get_clean_text(file_path)
    embedding = emb.embed_text(cleaned_text)
    return embedding


def get_files(directory: str) -> list[str]:
    filenames = []
    for root, dirs, files in os.walk(directory):
        for pth in config.ignore_paths:
            try:
                dirs.remove(pth)
            except:
                pass
        for filename in files:
            if not (
                (os.path.splitext(filename)[1] in config.extensions)
                ^ config.blacklist_extensions
            ):
                continue
            file_path = os.path.abspath(os.path.join(root, filename))
            filenames.append(file_path)
    return filenames


def process_files(directory: str):
    embeddings: dict[str, list[float]] = {}
    for file_path in get_files(directory):
        embedding = embed_file(file_path)
        embeddings[file_path] = embedding
    return embeddings


def index_files(filepath: str = "") -> None:
    if filepath:
        emb.embeddings[filepath] = embed_file(filepath)
    else:
        for path in config.paths:
            if isdir(path):
                new_embeddings = process_files(path)
                emb.embeddings.update(new_embeddings)
    emb.write_embeddings(emb.embeddings, config.embedding_file)


def search(query, embeddings_file, top_k=None):
    if not emb.embeddings:
        with open(embeddings_file, "rb") as file:
            try:
                emb.embeddings = pickle.load(file)
            except:
                pass

    query_embedding = torch.from_numpy(emb.model.encode([query])[0]).float()
    scores = {}
    for filename, embedding in emb.embeddings.items():
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
    embeddings_file = config.embedding_file
    results = search(query, embeddings_file, top_k=limit)
    formatted_results = format_search_results(results)
    return formatted_results
