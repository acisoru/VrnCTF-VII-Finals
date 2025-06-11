package main

import (
	"fmt"
	"github.com/gofiber/fiber/v2"
	"log"
	"maps"
	"os"
	"os/signal"
	"slices"
	"strconv"
)

type HandlerContext struct {
	Users map[int]SomeUser `json:"users"`
}

type SomeUser struct {
	Name string `json:"name"`
	Desc string `json:"desc"`
}

func main() {
	fmt.Println("Starting...")
	ctx := &HandlerContext{
		Users: map[int]SomeUser{
			0: {
				Name: "Пётр",
				Desc: "Великий",
			},
			1: {
				Name: "Александр",
				Desc: "Меншиков",
			},
			2: {
				Name: "Фёдор",
				Desc: "Апраксин",
			},
			3: {
				Name: "Борис",
				Desc: "Шереметев",
			},
			4: {
				Name: "Иван",
				Desc: "vrnctf{w3ll_d0n3_1n_tls_j0urn3y}",
			},
			5: {
				Name: "Яков",
				Desc: "Брюс",
			},
		},
	}

	app := fiber.New()

	// Routes
	app.Get("/user/:id", ctx.getByIdHandler)
	app.Get("/users", ctx.getListHandler)

	// Start server in a goroutine
	go func() {
		if err := app.Listen(":8088"); err != nil {
			log.Fatal("Failed to start server: ", err)
		}
	}()

	// Wait for interrupt signal
	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt)
	<-c

	// Graceful shutdown
	if err := app.Shutdown(); err != nil {
		log.Fatal("Error during server shutdown: ", err)
	}
}

func (ctx *HandlerContext) getByIdHandler(c *fiber.Ctx) error {
	presentApp := c.Get("App-ID")
	if presentApp == "" {
		return c.SendStatus(fiber.StatusBadRequest)
	}

	presentBearer := c.Get("Authorization")
	if presentBearer == "" {
		return c.SendStatus(fiber.StatusBadRequest)
	}

	id, err := strconv.Atoi(c.Params("id"))
	if err != nil {
		return c.SendStatus(fiber.StatusBadRequest)
	}

	valInMap, ok := ctx.Users[id]
	if !ok {
		return c.SendStatus(fiber.StatusNotFound)
	}

	return c.JSON(valInMap)
}

func (ctx *HandlerContext) getListHandler(c *fiber.Ctx) error {
	presentApp := c.Get("App-ID")
	if presentApp == "" {
		return c.SendStatus(fiber.StatusBadRequest)
	}

	presentBearer := c.Get("Authorization")
	if presentBearer == "" {
		return c.SendStatus(fiber.StatusBadRequest)
	}

	return c.JSON(slices.Collect(maps.Keys(ctx.Users)))
}
