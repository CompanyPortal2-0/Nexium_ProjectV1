package modeles

import "strconv"

type User struct {
	Name string
	Age  int
}

func (u User) ToStringUser() string {
	return u.Name + strconv.Itoa(u.Age)
}
