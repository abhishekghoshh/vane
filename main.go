package main

import (
	"fmt"

	"github.com/abhishekghoshh/config-client/config"
)

func main() {
	cfg, appCtx := config.New()
	fmt.Println(cfg.Get("app.name"))
	fmt.Println(appCtx)
}
