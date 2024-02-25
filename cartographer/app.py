import pickle
from re import sub
from string import punctuation

from bs4 import BeautifulSoup
from markdown import markdown
from sentence_transformers import SentenceTransformer


def __remove_urls(text: str = "") -> str:
    cleaned_text = sub(r"http\S+|www\S+", "", text)
    return sub(r"\[(.*?)\]\((.*?)\)", "", cleaned_text)


def __remove_html_tags(text: str = "") -> str:
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(separator=" ")


def __remove_decorations(text: str = "") -> str:
    return sub(r"[*_~]", "", text)


def __remove_punctuation(text: str = "") -> str:
    return text.translate(str.maketrans("", "", punctuation))


def clean(text: str = "") -> str:
    text = __remove_urls(text)
    text = __remove_html_tags(text)
    text = __remove_decorations(text)
    text = __remove_punctuation(text)
    return text.strip()


class Embedder:
    def __init__(self, transformer_name: str):
        self.model = SentenceTransformer(transformer_name)

    def embed_text(self, text: str):
        return self.model.encode([text])[0]

    def write_embeddings(
        self, embeddings: dict[str, list[float]], file_path: str
    ) -> None:
        with open(file_path, "wb") as file:
            pickle.dump(embeddings, file)


class FileEmbedder(Embedder):
    def __init__(self, transformer_name: str):
        super().__init__(transformer_name)

    def __get_sanitized_text(self, filepath: str):
        with open(filepath, "r", encoding="utf-8") as file:
            return clean(markdown(file.read()))

    def embed_file(self, filepath: str):
        cleaned_text = self.__get_sanitized_text(filepath)
        return self.embed_text(cleaned_text).tolist()
