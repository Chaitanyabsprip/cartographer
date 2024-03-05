package embedding

import (
	"errors"
	"fmt"
	"log"
	"os"

	p3 "github.com/sublime-security/cpy3"
)

var oModule *p3.PyObject

func Initialize(transformerName string) {
	log.Println(transformerName)
	pyCodeGo := fmt.Sprintf(`
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

model = SentenceTransformer("%s")

def embed_text(text: str) -> list[float]:
	clean_text = clean(markdown(text))
	return model.encode([clean_text])[0]
`, transformerName)

	p3.Py_Initialize()
	p3.PyRun_SimpleString(pyCodeGo)
	oModule = p3.PyImport_AddModule("__main__")
}

func EmbedText(text string) ([]float64, error) {
	pText := p3.PyUnicode_FromString(text)
	args := p3.PyTuple_New(1)
	p3.PyTuple_SetItem(args, 0, pText)
	embedStringFunc := oModule.GetAttrString("embed_text")
	if embedStringFunc == nil || !p3.PyCallable_Check(embedStringFunc) {
		return nil, errors.New("could not find embed_text function in python runtime")
	}
	result := embedStringFunc.CallObject(args)
	if result == nil {
		p3.PyErr_Print()
		return nil, errors.New("Failure in calling python function")
	}
	// defer pText.DecRef()
	// defer args.DecRef()
	return goSliceFromPyList(result)
}

func EmbedFile(filepath string) ([]float64, error) {
	content, err := os.ReadFile(filepath)
	if err != nil {
		return nil, err
	}
	return EmbedText(string(content))
}

func goSliceFromPyList(pyList *p3.PyObject) ([]float64, error) {
	defer pyList.DecRef()
	seq := pyList.GetIter()
	defer seq.DecRef()
	tNext := seq.GetAttrString("__next__")
	defer tNext.DecRef()
	length := pyList.Length()
	if length == -1 {
		return nil, errors.New("Failed to get list size")
	}
	arr := make([]float64, length)
	for i := 0; i < length; i++ {
		item := tNext.CallObject(nil)
		if item == nil && !p3.PyFloat_Check(item) {
			return nil, errors.New("List contains non float element")
		}
		arr[i] = p3.PyFloat_AsDouble(item)
		item.DecRef()
	}
	return arr, nil
}
