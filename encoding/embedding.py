import pickle
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


@dataclass
class Config:
    directory: str
    embeddings_file: str
    embeddings: dict


notespath = environ["NOTESPATH"]  # this is unsafe, use a config file instead


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
        cleaned_text = (text or self.text).translate(
            str.maketrans("", "", punctuation)
        )
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
    def __init__(self, directory, embedding_file):
        self.model = SentenceTransformer("msmarco-distilbert-base-v4")
        self.tp = TextProcessor()
        self.directory = directory
        self.embedding_file = embedding_file
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
            # file.write(pickle.dumps(embeddings))
        # with open(file_path, "w", encoding="utf-8") as file:
        #     dump(embeddings, file, indent=4)

    def process_files(self, directory: str):
        embeddings: dict[str, list[float]] = {}
        for root, dirs, files in walk(directory):
            try:
                dirs.remove(".git")
                dirs.remove(".obsidian")
            except:
                pass
            for filename in files:
                if not filename.endswith(".md"):
                    continue
                file_path = path.abspath(path.join(root, filename))
                embedding = self.embed_file(file_path)
                embeddings[file_path] = embedding
        return embeddings

    def index_files(self, fpath: str = "") -> None:
        embeddings = self.embeddings or {}
        if path.isfile(fpath):
            print("here")
            abs_file_path = path.abspath(fpath)
            embedding = self.embed_file(abs_file_path)
            embeddings[abs_file_path] = embedding
        elif path.isdir(fpath or self.directory):
            new_embeddings = self.process_files(fpath or self.directory)
            embeddings.update(new_embeddings)
        else:
            return print("Invalid file or directory path.")
        self.write_embeddings(embeddings, self.embedding_file)


emb = Embedder(
    directory=notespath,
    embedding_file=f"{notespath}/.embeddings",
)


def search(query, embeddings_file, top_k=None):
    if not emb.embeddings:
        with open(embeddings_file, "rb") as file:
            emb.embeddings = pickle.load(file)
        # with open(embeddings_file, "r", encoding="utf-8") as file:
        #     emb.embeddings = jLoad(file)
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
    embeddings_file = emb.embedding_file
    results = search(query, embeddings_file, top_k=limit)
    formatted_results = format_search_results(results)
    return formatted_results
