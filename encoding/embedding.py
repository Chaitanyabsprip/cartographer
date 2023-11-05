import os
import pickle
from dataclasses import dataclass
from os.path import isdir
from re import sub
from string import punctuation

import torch
from bs4 import BeautifulSoup
from markdown import markdown
from numpy import array
from sentence_transformers import SentenceTransformer, util

from config import Config

config = Config()


class TextProcessor:
    def remove_urls(self, text: str = "") -> str:
        cleaned_text = sub(r"http\S+|www\S+", "", text or self.text)
        cleaned_text = sub(r"\[(.*?)\]\((.*?)\)", "", cleaned_text)
        self.text = cleaned_text
        return self.text

    def remove_html_tags(self, text: str = "") -> str:
        soup = BeautifulSoup(text or self.text, "html.parser")
        cleaned_text = soup.get_text(separator=" ")
        self.text = cleaned_text
        return self.text

    def remove_decorations(self, text: str = "") -> str:
        cleaned_text = sub(r"[*_~]", "", text or self.text)
        self.text = cleaned_text
        return self.text

    def remove_punctuation(self, text: str = "") -> str:
        cleaned_text = (text or self.text).translate(str.maketrans("", "", punctuation))
        self.text = cleaned_text
        return self.text

    def clean(self, text: str = "") -> str:
        self.text = text
        self.remove_urls(text)
        self.remove_html_tags()
        self.remove_decorations()
        self.remove_punctuation()
        return self.text.strip()


class Embedder:
    def __init__(self):
        self.model = SentenceTransformer(config.transformer_name)
        self.tp = TextProcessor()
        self.embeddings = {}

    def embed_text(self, text: str) -> list[float]:
        return self.model.encode([text])[0].tolist()

    def embed_file(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as file:
            markdown_content = file.read()
            html_content = markdown(markdown_content)
            cleaned_text = self.tp.clean(html_content)
            embedding = self.embed_text(cleaned_text)
            return embedding

    def write_embeddings(
        self, embeddings: dict[str, list[float]], file_path: str
    ) -> None:
        with open(f"{file_path}_bin", "wb") as file:
            pickle.dump(embeddings, file)

    def process_files(self, directory: str):
        embeddings: dict[str, list[float]] = {}
        for root, dirs, files in os.walk(directory):
            try:
                for pth in config.ignore_paths:
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
                embedding = self.embed_file(file_path)
                embeddings[file_path] = embedding
        return embeddings

    def index_files(self) -> None:
        for path in config.paths:
            if isdir(path):
                new_embeddings = self.process_files(path)
                self.embeddings.update(new_embeddings)
        self.write_embeddings(self.embeddings, config.embedding_file)


emb = Embedder()


def search(query, embeddings_file, top_k=None):
    if not emb.embeddings:
        with open(embeddings_file, "rb") as file:
            emb.embeddings = pickle.load(file)
    query_embedding = torch.from_numpy(emb.model.encode([query])[0]).float()
    scores = {}
    for filename, embedding in emb.embeddings.items():
        score = util.pytorch_cos_sim(
            query_embedding, torch.from_numpy(array(embedding)).float()
        )
        scores[filename] = score.item()
    sorted_scores = {
        k: v for k, v in sorted(scores.items(), key=lambda item: item[1], reverse=True)
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
    embeddings_file = emb.embedding_file
    results = search(query, embeddings_file, top_k=limit)
    formatted_results = format_search_results(results)
    return formatted_results
