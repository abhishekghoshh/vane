package config

import (
	"errors"
	"log"
	"os"

	"github.com/abhishekghoshh/config-client/config/loader"
	"github.com/mitchellh/mapstructure"
	"github.com/spf13/viper"
)

const (
	RESOURCES_DIR = "resources"
	ROOT_CONFIG   = "app.yaml"
)

type Config struct {
	*viper.Viper
}

func New() (*Config, *ApplicationContext) {
	workingDir, _ := os.Getwd()
	resourcesDir := workingDir + "/" + RESOURCES_DIR
	config := &Config{
		Viper: loader.LoadConfig(resourcesDir, ROOT_CONFIG),
	}
	appCtx := &ApplicationContext{}
	config.Decode("application", appCtx)
	return config, appCtx
}

func (*Config) FromEnv(key string) string {
	return os.Getenv(key)
}

func (*Config) FromEnvOrDefault(key, defaultVal string) string {
	val := os.Getenv(key)
	if val != "" {
		return val
	}
	return defaultVal
}
func (config *Config) FromEnvOrConfig(envKey, configKey string) string {
	val := os.Getenv(envKey)
	if val != "" {
		return val
	}
	return config.GetString(configKey)
}

func (config *Config) decode(key string, data any) error {
	innerConfig := config.Get(key)
	if innerConfig == nil {
		return errors.New("unable to find key in the config, " + key)
	}
	err := mapstructure.Decode(innerConfig, data)
	if err != nil {
		log.Printf("Error unmarshaling config: %v", err)
		return errors.New("error in loading config for the key, " + key)
	}
	return nil
}

func (config *Config) Decode(key string, data any) {
	if err := config.decode(key, data); err != nil {
		panic(err.Error())
	}
}
