package embedding

import (
	"fmt"
	"os"

	"google.golang.org/protobuf/proto"
)

// Save function  
func Save(filepath string, floatMap map[string][]float64) error {
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

	err = os.WriteFile(filepath, encodedData, 0o644)
	if err != nil {
		return err
	}

	return nil
}

// Load function  
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
