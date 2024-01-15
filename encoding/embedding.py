import pickle

from markdown import markdown
from sentence_transformers import SentenceTransformer

from cartographer.config import Config
from encoding.text_processor import TextProcessor

config = Config()


class Embedder:
    def __init__(self):
        self.model = SentenceTransformer(config.transformer_name)

    def embed_text(self, text: str):
        return self.model.encode([text])[0]

    def write_embeddings(
        self, embeddings: dict[str, list[float]], file_path: str
    ) -> None:
        with open(file_path, "wb") as file:
            pickle.dump(embeddings, file)


class FileEmbedder(Embedder):
    def __init__(self, text_proc: TextProcessor):
        super().__init__()
        self.__text_proc: TextProcessor = text_proc

    def __get_sanitized_text(self, filepath: str):
        with open(filepath, "r", encoding="utf-8") as file:
            return self.__text_proc.clean(markdown(file.read()))

    def embed_file(self, filepath: str):
        cleaned_text = self.__get_sanitized_text(filepath)
        return self.embed_text(cleaned_text).tolist()
