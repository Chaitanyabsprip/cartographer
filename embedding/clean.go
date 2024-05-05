// Package embedding provides embedding  
package embedding

import (
	"log"
	"regexp"
	"strings"

	"github.com/PuerkitoBio/goquery"
)

// RemoveUrls function  
func RemoveUrls(text string) string {
	re := regexp.MustCompile(`http\S+|www\S+`)
	return re.ReplaceAllString(text, "")
}

// RemoveHTMLTags function  
func RemoveHTMLTags(text string) string {
	doc, err := goquery.NewDocumentFromReader(strings.NewReader(text))
	if err != nil {
		log.Fatal(err)
	}
	return doc.Text()
}

// RemoveDecorations function  
func RemoveDecorations(text string) string {
	re := regexp.MustCompile(`[*_~]`)
	return re.ReplaceAllString(text, "")
}

// RemovePunctuation function  
func RemovePunctuation(text string) string {
	return strings.Map(func(r rune) rune {
		if strings.ContainsRune("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~", r) {
			return -1
		}
		return r
	}, text)
}

// Clean function  
func Clean(text string) string {
	text = RemoveHTMLTags(text)
	text = RemoveUrls(text)
	text = RemoveDecorations(text)
	text = RemovePunctuation(text)
	return strings.TrimSpace(text)
}
