package cartographer_test

import (
	"testing"

	"github.com/chaitanyabsprip/cartographer/cartographer"
)

func TestRemoveUrls(t *testing.T) {
	input := "Visit us at http://example.com"
	expected := "Visit us at "
	result := cartographer.RemoveUrls(input)
	if result != expected {
		t.Errorf("removeUrls: expected '%s', got '%s'", expected, result)
	}
}

func TestRemoveHTMLTags(t *testing.T) {
	input := "<p>Hello <b>World</b>!</p>"
	expected := "Hello World!"
	result := cartographer.RemoveHTMLTags(input)
	if result != expected {
		t.Errorf("removeHTMLTags: expected '%s', got '%s'", expected, result)
	}
}

func TestRemoveDecorations(t *testing.T) {
	input := "Hello *World* _of_ ~Golang~"
	expected := "Hello World of Golang"
	result := cartographer.RemoveDecorations(input)
	if result != expected {
		t.Errorf("removeDecorations: expected '%s', got '%s'", expected, result)
	}
}

func TestRemovePunctuation(t *testing.T) {
	input := "Hello! How are you?"
	expected := "Hello How are you"
	result := cartographer.RemovePunctuation(input)
	if result != expected {
		t.Errorf("removePunctuation: expected '%s', got '%s'", expected, result)
	}
}

func TestClean(t *testing.T) {
	input := "Visit us at <a href='http://example.com'>example.com</a>! *Click here* ~now~!"
	expected := "Visit us at examplecom Click here now"
	result := cartographer.Clean(input)
	if result != expected {
		t.Errorf("clean: expected '%s', got '%s'", expected, result)
	}
}
