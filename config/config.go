package config

import (
	"log"
	"os"
	"os/user"
	"path/filepath"

	"github.com/kirsle/configdir"
	yaml "gopkg.in/yaml.v3"
)

// Configuration represents the configuration structure
type Configuration struct {
	EmbeddingFile       string   `yaml:"embeddings_file"`
	TransformerName     string   `yaml:"transformer"`
	Paths               []string `yaml:"paths"`
	IgnorePaths         []string `yaml:"ignore_paths"`
	Extensions          []string `yaml:"extensions"`
	BlacklistExtensions bool     `yaml:"blacklist_extensions"`
	PythonInterpreter   string   `yaml:"python_interpreter"`
}

var Config Configuration

func Initialise() {
	Config = readConfig()
}

func readConfig() Configuration {
	log.Println("created dirs")
	configFilePath := filepath.Join(configdir.LocalConfig("cartographer"), "config.yml")
	cacheFilePath := configdir.LocalCache("cartographer")
	config := Configuration{
		EmbeddingFile:       filepath.Join(cacheFilePath, "embeddings.pb"),
		TransformerName:     "msmarco-distilbert-base-v4",
		BlacklistExtensions: false,
		PythonInterpreter:   "python3",
	}

	log.Println(configFilePath)
	if _, err := os.Stat(configFilePath); os.IsNotExist(err) {
		return config
	}

	log.Println("Config file exists, reading")
	file, err := os.ReadFile(configFilePath)
	if err != nil {
		log.Println("Error reading config file:", err)
		return config
	}

	if err := yaml.Unmarshal(file, &config); err != nil {
		log.Println("Error unmarshalling YAML:", err)
	}

	config.Paths = expandUser(config.Paths)
	log.Println("Config loaded: ", config)

	return config
}

func expandUser(paths []string) []string {
	var expandedPaths []string
	for _, p := range paths {
		expandedPaths = append(expandedPaths, expand(p))
	}
	return expandedPaths
}

func expand(path string) string {
	if len(path) == 0 || path[0] != '~' {
		return path
	}

	usr, _ := user.Current()
	return filepath.Join(usr.HomeDir, path[1:])
}
