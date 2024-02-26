package utils

import (
	"log"
	"os"
)

func CreateFile(filePath string) error {
	_, err := os.Stat(filePath)
	log.Println(err.Error())
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
