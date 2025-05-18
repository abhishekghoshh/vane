package config

type ApplicationContext struct {
	Name   string         `mapstructure:"name"`
	Server *ServerContext `mapstructure:"server"`
	Config *ConfigContext `mapstructure:"config"`
}
type ServerContext struct {
	Host string `mapstructure:"host"`
	Port string `mapstructure:"port"`
}

type ConfigContext struct {
	Profiles string         `mapstructure:"profiles"`
	Source   []ConfigSource `mapstructure:"source"`
}

type ConfigSource struct {
	// Path string `mapstructure:"path"`
	// Dir    string `mapstructure:"dir"`
	// Git    string `mapstructure:"git"`
	// Branch string `mapstructure:"branch"`
}
