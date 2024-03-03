package embedding

import (
	"fmt"
	"os"

	"google.golang.org/protobuf/proto"

	"github.com/chaitanyabsprip/cartographer/config"
)

const host string = "http://127.0.0.1:30000"

func Save(floatMap map[string][]float64) error {
	filePath := config.Config.EmbeddingFile
	data := &FloatMap{
		Data: make(map[string]*ListOfFloats),
	}

	for key, values := range floatMap {
		data.Data[key] = &ListOfFloats{
			Data: values,
		}
	}

	encodedData, err := proto.Marshal(data)
	if err != nil {
		return err
	}

	err = os.WriteFile(filePath, encodedData, 0o644)
	if err != nil {
		return err
	}

	return nil
}

func Load(filePath string) (map[string][]float64, error) {
	data, err := os.ReadFile(filePath)
	if err != nil {
		return nil, fmt.Errorf("error reading file: %v", err)
	}
	var floatMap FloatMap
	err = proto.Unmarshal(data, &floatMap)
	if err != nil {
		return nil, fmt.Errorf("error unmarshalling data: %v", err)
	}
	result := make(map[string][]float64)
	for key, values := range floatMap.Data {
		result[key] = values.Data
	}
	return result, nil
}
