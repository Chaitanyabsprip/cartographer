from dataclasses import dataclass
import yaml


class Config:
    def __init__(self):
        with open("./config.yml", "r") as file:
            config = yaml.safe_load(file)

        # TODO: This should be in cache path
        self.embedding_file = config.get("embeddings_file", ".embeddings_bin")
        self.transformer_name = config.get(
            "transformer_name", "msmarco-distilbert-base-v4"
        )
        self.paths = config.get("paths", [])
        self.ignore_paths = config.get("ignore_paths", [])
        self.extensions = config.get("extensions", [])
        self.blacklist_extensions = config.get(
            "blacklist_extensions", not self.extensions
        )
