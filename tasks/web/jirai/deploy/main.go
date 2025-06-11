package main

import (
	"fmt"
	"github.com/gofiber/fiber/v3"
	"github.com/gofiber/fiber/v3/middleware/logger"
	"github.com/gofiber/fiber/v3/middleware/static"
	"github.com/gofiber/template/html/v2"
	"log"
)

func main() {
	var err error
	session, err = initCassandra()
	if err != nil {
		log.Fatalf("Failed to connect to Cassandra: %v", err)
	}
	defer session.Close()

	err = setupDatabase()
	if err != nil {
		log.Fatalf("Failed to set up database: %v", err)
	}

	engine := html.New("./views", ".html")
	app := fiber.New(fiber.Config{
		Views: engine,
	})

	app.Use(logger.New())

	// Serve static files properly
	app.Get("/static/*", static.New("./static"))

	setupRoutes(app)

	fmt.Println("Jirai service starting on http://localhost:3000")
	log.Fatal(app.Listen(":3000"))
}

func setupRoutes(app *fiber.App) {
	app.Get("/", handleIndex)

	app.Get("/issues", handleListIssues)
	app.Get("/issues/new", handleNewIssueForm)
	app.Post("/issues", handleCreateIssue)
	app.Get("/issues/:id", handleGetIssue)
	app.Put("/issues/:id", handleUpdateIssue)
	app.Delete("/issues/:id", handleDeleteIssue)

	app.Get("/search", handleSearch)

	app.Get("/api/issues", handleApiListIssues)
}
