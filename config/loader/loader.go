package loader

import (
	"fmt"
	"os"
	"regexp"

	"github.com/spf13/viper"
)

func LoadConfig(resourcesDir string, configName string) *viper.Viper {
	config := viper.New()
	config.SetConfigName(configName)
	config.SetConfigType("yaml")
	config.AddConfigPath(resourcesDir)
	err := config.ReadInConfig()
	if err != nil {
		panic(fmt.Errorf("fatal error config file: %w", err))
	}
	keys := config.AllKeys()
	for _, key := range keys {
		val := get(config, key)
		config.Set(key, val)
	}
	return config
}

func get(config *viper.Viper, key string) any {
	val := config.Get(key)
	return getEvalualtedValue(val)
}

func getEvalualtedValue(val any) string {
	strVal, ok := val.(string)
	if !ok {
		return fmt.Sprintf("%v", val)
	}
	re := regexp.MustCompile(`\$\{([^}:]+)(:([^}]+))?\}`)
	return re.ReplaceAllStringFunc(strVal, func(match string) string {
		groups := re.FindStringSubmatch(match)
		envKey := groups[1]
		defaultVal := ""
		if len(groups) > 3 {
			defaultVal = groups[3]
		}
		envVal := os.Getenv(envKey)
		if envVal != "" {
			return envVal
		}
		if defaultVal == "" {
			panic(fmt.Sprintf("no default value for key %s, no environment variable set for %s", match, envKey))
		}
		return defaultVal
	})
}
