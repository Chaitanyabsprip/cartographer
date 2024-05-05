package embedding

import (
	"errors"
	"fmt"
	"log"
	"os"

	p3 "github.com/sublime-security/cpy3"
)

var oModule *p3.PyObject

// Initialize function  
func Initialize(transformerName string) {
	log.Println(transformerName)
	pyCodeGo := fmt.Sprintf(`
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("%s")

def embed_text(text: str) -> list[float]:
	return model.encode([text])[0]
`, transformerName)

	p3.Py_Initialize()
	p3.PyRun_SimpleString(pyCodeGo)
	oModule = p3.PyImport_AddModule("__main__")
}

// EmbedText function  
func EmbedText(text string) ([]float64, error) {
	pText := p3.PyUnicode_FromString(Clean(text))
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
	// decreffing the following causes segmentation fault, need to understand
	// why. This can be a possible memory leak
	// defer pText.DecRef()
	// defer args.DecRef()
	return goSliceFromPyList(result)
}

// EmbedFile function  
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
