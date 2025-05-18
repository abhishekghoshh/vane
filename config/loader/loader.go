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
		val := config.Get(key)
		evaluatedVal := evaluate(val)
		config.Set(key, evaluatedVal)
	}
	return config
}

func evaluate(val any) any {
	if strVal, ok := val.(string); ok {
		return evalualteString(strVal)
	} else if listVal, ok := val.([]any); ok {
		return evaluateList(listVal)
	} else if mapVal, ok := val.(map[string]any); ok {
		return evaluateMap(mapVal)
	}
	return val
}
func evalualteString(val string) string {
	re := regexp.MustCompile(`\$\{([^}:]+)(:([^}]+))?\}`)
	return re.ReplaceAllStringFunc(val, func(match string) string {
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

func evaluateList(listVal []any) any {
	for i, val := range listVal {
		listVal[i] = evaluate(val)
	}
	return listVal
}

func evaluateMap(mapVal map[string]any) any {
	for key, val := range mapVal {
		mapVal[key] = evaluate(val)
	}
	return mapVal
}
