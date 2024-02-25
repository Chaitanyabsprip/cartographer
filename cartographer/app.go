package cartographer

import (
	"errors"
	"log"
	"os"
	"path/filepath"
	"sort"

	"github.com/khaibin/go-cosinesimilarity"

	"github.com/chaitanyabsprip/cartographer/config"
	"github.com/chaitanyabsprip/cartographer/embedding"
	"github.com/chaitanyabsprip/cartographer/utils"
)

var embeddings map[string][]float64

func Initialise() {
	config.Initialise()
	embeddings = make(map[string][]float64)
	_, err := os.Stat(config.Config.EmbeddingFile)
	if errors.Is(err, os.ErrNotExist) {
		utils.CreateFile(config.Config.EmbeddingFile)
	} else {
		embeddings, err = embedding.Load(config.Config.EmbeddingFile)
	}
	if err != nil {
		log.Println(err)
		Index("")
	}
}

func contains(value string, array []string) bool {
	for _, v := range array {
		if value == v {
			return true
		}
	}
	return false
}

func shouldConsiderFile(filename string) bool {
	ext := filepath.Ext(filename)
	isInExtensions := contains(ext, config.Config.Extensions)
	isBlacklistExtensions := config.Config.BlacklistExtensions
	return (isInExtensions && !isBlacklistExtensions) ||
		(!isInExtensions && isBlacklistExtensions)
}

func getFiles(directory string) ([]string, error) {
	var filenames []string

	err := filepath.Walk(directory, func(root string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if contains(info.Name(), config.Config.IgnorePaths) {
			return filepath.SkipDir
		}

		if !info.IsDir() {
			filename := info.Name()

			if shouldConsiderFile(filename) {
				absPath, err := filepath.Abs(filepath.Join(root, filename))
				if err != nil {
					return err
				}
				filenames = append(filenames, absPath)
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
	log.Println("processing files")
	results := make(map[string][]float64)
	files, _ := getFiles(directory)
	for _, file := range files {
		log.Println("filepath:", file)
		e, _ := embedding.EmbedFile(file)
		results[file] = e
	}
	return results
}

func sortSearchResults(results map[string]float64) []string {
	keys := make([]string, len(results))
	i := 0
	for k := range results {
		keys[i] = k
		i++
	}
	sort.SliceStable(keys, func(i, j int) bool {
		ival, iok := results[keys[i]]
		jval, jok := results[keys[j]]
		return iok && jok && ival < jval
	})
	return keys
}

func Search(query string, limit int) ([]string, error) {
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
	if filepath != "" {
		embedding.EmbedFile(filepath)
		return nil
	}
	log.Println(config.Config.Paths)
	for _, path := range config.Config.Paths {
		log.Println("path:", path)
		if isDirectory(path) {
			embeddings = update(embeddings, processFiles(path))
		}
	}
	err := embedding.Save(embeddings)
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
