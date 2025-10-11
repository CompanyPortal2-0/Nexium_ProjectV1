package main

import (
	"fmt"
	"server/modeles"
)

func main() {
	u := modeles.User{Name: "Alice", Age: 30}
	fmt.Println(u.ToStringUser())
}
