package cartographer

import (
	"log"
	"os"
	"path/filepath"
	"slices"
	"sort"

	"github.com/khaibin/go-cosinesimilarity"

	"github.com/chaitanyabsprip/cartographer/embedding"
)

var embeddings map[string][]float64

func Initialise() {
	initConfig()
	embeddings = make(map[string][]float64)
	_, err := os.Stat(Config.EmbeddingFile)
	if err == nil {
		embeddings, err = embedding.Load(Config.EmbeddingFile)
		if err == nil {
			return
		}
	}
	f, err := os.Create(Config.EmbeddingFile)
	if err != nil {
		log.Fatal(err.Error())
	}
	defer f.Close()
	Index("")
}

func shouldConsiderFile(filename string) bool {
	ext := filepath.Ext(filename)
	isInExtensions := slices.Contains(Config.Extensions, ext)
	isBlacklistExtensions := Config.BlacklistExtensions
	return (isInExtensions && !isBlacklistExtensions) ||
		(!isInExtensions && isBlacklistExtensions)
}

func getFiles(directory string) ([]string, error) {
	var filenames []string

	err := filepath.Walk(directory, func(root string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if slices.Contains(Config.IgnorePaths, info.Name()) {
			return filepath.SkipDir
		}

		if !info.IsDir() {
			if shouldConsiderFile(root) {
				filenames = append(filenames, root)
			}
		}
		return nil
	})
	if err != nil {
		return nil, err
	}

	return filenames, nil
}

func processFiles(directory string) map[string][]float64 {
	log.Print("processing files in ", directory, "\n")
	results := make(map[string][]float64)
	files, _ := getFiles(directory)
	for _, file := range files {
		content, err := os.ReadFile(file)
		if err != nil {
			log.Print("Error reading file ", file, "\n", err.Error(), "\n")
			continue
		}
		if len(content) == 0 {
			log.Print("File ", file, "is empty\n")
			continue
		}
		e, _ := embedding.EmbedText(string(content))
		results[file] = e
	}
	return results
}

type SearchResult struct {
	Score    float64 `json:"score"`
	Filepath string  `json:"filepath"`
}

func sortSearchResults(results map[string]float64) []SearchResult {
	sorted := make([]SearchResult, len(results))
	i := 0
	for k := range results {
		sorted[i] = SearchResult{Score: results[k], Filepath: k}
		i++
	}
	sort.SliceStable(sorted, func(i, j int) bool {
		ival, iok := results[sorted[i].Filepath]
		jval, jok := results[sorted[j].Filepath]
		return iok && jok && ival > jval
	})
	return sorted
}

func Search(query string, limit int) ([]SearchResult, error) {
	queryEnc, err := embedding.EmbedText(query)
	if err != nil {
		return nil, err
	}
	scores := make(map[string]float64)
	for file, embedding := range embeddings {
		scores[file] = cosinesimilarity.Compute([][]float64{queryEnc}, [][]float64{embedding})[0][0]
	}
	results := sortSearchResults(scores)
	return results[:min(limit, len(results))], nil
}

func Index(filepath string) error {
	log.Print("Indexing ")
	if filepath != "" {
		embedding.EmbedFile(filepath)
		return nil
	}
	log.Println(Config.Paths)
	for _, path := range Config.Paths {
		log.Println("path:", path, isDirectory(path))
		if isDirectory(path) {
			embeddings = update(embeddings, processFiles(path))
		}
	}
	err := embedding.Save(Config.EmbeddingFile, embeddings)
	if err != nil {
		return err
	}
	return nil
}

func update[K comparable, V any](data, with map[K]V) map[K]V {
	for k, v := range with {
		data[k] = v
	}
	return data
}

func isDirectory(path string) bool {
	fileInfo, err := os.Stat(path)
	if err != nil {
		return false
	}
	return fileInfo.IsDir()
}

func FormatSearchResults(results []string) []map[string]string {
	mapped := make([]map[string]string, len(results))
	for i, e := range results {
		mapped[i] = map[string]string{
			"filename":         e,
			"display_filename": filepath.Base(e),
			"directory":        filepath.Dir(e),
		}
	}
	return mapped
}
