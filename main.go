package main

import (
	"fmt"

	"github.com/abhishekghoshh/config-client/config"
)

func main() {
	_, appCtx := config.New()
	fmt.Println(appCtx.Name)
	fmt.Println(appCtx.Server)
	fmt.Println(appCtx.Config.Profiles)
	fmt.Println(appCtx.Config.Sources)
}
