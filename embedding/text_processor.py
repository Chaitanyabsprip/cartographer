from re import sub
from string import punctuation

from bs4 import BeautifulSoup


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
