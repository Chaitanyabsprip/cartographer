import pickle

from config import Config
from sentence_transformers import SentenceTransformer

config = Config()


class Embedder:
    def __init__(self):
        self.model = SentenceTransformer(config.transformer_name)
        self.embeddings = {}

    def embed_text(self, text: str) -> list[float]:
        return self.model.encode([text])[0].tolist()

    def write_embeddings(
        self, embeddings: dict[str, list[float]], file_path: str
    ) -> None:
        with open(file_path, "wb") as file:
            pickle.dump(embeddings, file)
