import logging as l
import os
import pickle
from os.path import isdir
from typing import Optional

import torch
from numpy import array
from sentence_transformers import util

from embedding.embedding import FileEmbedder, config
from embedding.text_processor import TextProcessor


class App:
    def __init__(self):
        self.embedder = FileEmbedder(TextProcessor())
        self.embeddings: dict[str, list] = {}
        # initialise embeddings file
        try:
            with open(config.embedding_file, "rb") as file:
                self.embeddings = pickle.load(file)
        except FileNotFoundError:
            open(config.embedding_file, "a").close()
        except EOFError:
            pass

        pass

    def __get_files(self, directory: str) -> list:
        filenames = []
        for root, dirs, files in os.walk(directory):
            for pth in config.ignore_paths:
                try:
                    dirs.remove(pth)
                except ValueError:
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

    def __process_files(self, directory: str):
        l.debug("processing_files")
        embeddings: dict[str, list[float]] = {}
        for filepath in self.__get_files(directory):
            l.debug(f"filepath: {filepath}")
            embedding = self.embedder.embed_file(filepath)
            embeddings[filepath] = embedding
        return embeddings

    def __sort_search_results(self, scores: dict) -> dict:
        return {
            k: v
            for k, v in sorted(
                scores.items(), key=lambda item: item[1], reverse=True
            )
        }

    def search(self, query: str, top_k: Optional[int]):
        query_enc = torch.from_numpy(self.embedder.embed_text(query)).float()
        scores: dict[str, float] = {}
        for filename, embedding in self.embeddings.items():
            emb = torch.from_numpy(array(embedding)).float()
            score = util.pytorch_cos_sim(query_enc, emb)
            scores[filename] = score.item()
        sorted = self.__sort_search_results(scores)
        results = list(sorted.keys())
        if top_k:
            return results[: int(top_k)]
        return results

    def index(self, filepath: Optional[str]) -> None:
        l.debug("indexing")
        l.debug(f"filepath: {filepath}")
        if filepath:
            self.embeddings[filepath] = self.embedder.embed_file(filepath)
        else:
            for path in config.paths:
                l.debug(f"path: {path}")
                if isdir(path):
                    self.embeddings.update(self.__process_files(path))
        self.embedder.write_embeddings(self.embeddings, config.embedding_file)


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
