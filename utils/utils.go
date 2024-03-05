package utils

import (
	"io"
	"log"
	"os"
	"path"

	"github.com/kirsle/configdir"
)

func CreateAppDirs() {
	configDir := configdir.LocalConfig("cartographer")
	cacheDir := configdir.LocalCache("cartographer")
	if err := configdir.MakePath(configDir); err != nil {
		log.Println(err.Error())
	}
	if err := configdir.MakePath(cacheDir); err != nil {
		log.Println(err.Error())
	}
}

func CreateFile(filePath string) error {
	_, err := os.Stat(filePath)
	if err != nil {
		log.Println(err.Error())
	}
	if os.IsNotExist(err) {
		log.Println("file ", filePath, " does not exist")
		// File does not exist, create it
		file, error := os.Create(filePath)
		if error != nil {
			return error
		}
		defer file.Close()
		return nil
	} else {
		return err
	}
}

func CreateDir(filePath string) error {
	_, err := os.Stat(filePath)
	if os.IsNotExist(err) {
		// File does not exist, create it
		error := os.Mkdir(filePath, 0o755)
		if error != nil {
			return err
		}
		return nil
	} else {
		return err
	}
}

func OpenLogFile(filename string) io.Writer {
	cacheDir := configdir.LocalCache("cartographer")
	cacheFilepath := path.Join(cacheDir, filename)
	err := CreateFile(cacheFilepath)
	if err != nil {
		log.Print(err.Error())
	}
	file, err := os.OpenFile(cacheFilepath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0o666)
	if err != nil {
		log.Print("could not open file", filename, "for logging:\n", err.Error())
	}
	return file
}
