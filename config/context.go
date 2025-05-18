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
	Sources  []ConfigSource `mapstructure:"sources"`
}

type ConfigSource struct {
	Path   string `mapstructure:"path,omitempty"`
	Dir    string `mapstructure:"dir,omitempty"`
	Git    string `mapstructure:"git,omitempty"`
	Branch string `mapstructure:"branch,omitempty"`
	Link   string `mapstructure:"link,omitempty"`
}
