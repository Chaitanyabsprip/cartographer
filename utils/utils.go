// Package utils provides utils  
package utils

import (
	"io"
	"log"
	"os"
	"path"

	"github.com/kirsle/configdir"
)

// CreateAppDirs function  
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

// CreateFile function creates a file if it doesn't exist. Does nothing if the file does exist.
func CreateFile(filePath string) error {
	_, err := os.Stat(filePath)
	if os.IsNotExist(err) {
		var file *os.File
		file, err = os.Create(filePath)
		if err != nil {
			return err
		}
		defer file.Close()
		return nil
	}
	return err
}

// CreateDir function  
func CreateDir(filePath string) error {
	_, err := os.Stat(filePath)
	if os.IsNotExist(err) {
		// File does not exist, create it
		err = os.Mkdir(filePath, 0o755)
		if err != nil {
			return err
		}
		return nil
	}
	return err
}

// OpenLogFile function  
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
