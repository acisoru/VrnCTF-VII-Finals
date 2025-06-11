package main

import (
	goerrors "errors"
	"log"
	"time"

	"github.com/gocql/gocql"
	"github.com/gofiber/fiber/v3"
)

func handleIndex(c fiber.Ctx) error {
	return c.Render("index", fiber.Map{
		"Title": "Jirai - A JIRA-like Service",
	})
}

func handleListIssues(c fiber.Ctx) error {
	issues, err := listIssues()
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error": "Failed to fetch issues: " + err.Error(),
		})
	}

	return c.Render("issues", fiber.Map{
		"Title":  "All Issues",
		"Issues": issues,
	})
}

func handleApiListIssues(c fiber.Ctx) error {
	issues, err := listIssues()
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error": "Failed to fetch issues: " + err.Error(),
		})
	}

	return c.JSON(issues)
}

func handleNewIssueForm(c fiber.Ctx) error {
	return c.Render("new_issue", fiber.Map{
		"Title": "Create New Issue",
	})
}

func handleCreateIssue(c fiber.Ctx) error {
	issue, err := newIssueFromRequest(c)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": "Failed to parse issue data: " + err.Error(),
		})
	}

	if err := createIssue(issue); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error": "Failed to create issue: " + err.Error(),
		})
	}

	if c.Get("HX-Request") == "true" {
		return c.Render("partials/issue_row", fiber.Map{
			"Issue": issue,
		})
	}

	return c.Redirect().To("/issues")
}

func handleGetIssue(c fiber.Ctx) error {
	id := c.Params("id")

	issue, err := getIssueByID(id)
	if err != nil {
		if goerrors.Is(err, gocql.ErrNotFound) {
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{
				"error": "Issue not found",
			})
		}
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error": "Failed to fetch issue: " + err.Error(),
		})
	}

	return c.Render("issue_detail", fiber.Map{
		"Title": issue.Title,
		"Issue": issue,
	})
}

func handleUpdateIssue(c fiber.Ctx) error {
	id := c.Params("id")

	issue, err := getIssueByID(id)
	if err != nil {
		if goerrors.Is(err, gocql.ErrNotFound) {
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{
				"error": "Issue not found",
			})
		}
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error": "Failed to fetch issue: " + err.Error(),
		})
	}

	updates := new(Issue)
	if err := c.Bind().JSON(updates); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": "Failed to parse issue data: " + err.Error(),
		})
	}

	issue.Title = updates.Title
	issue.Description = updates.Description
	issue.Status = updates.Status
	issue.Priority = updates.Priority
	issue.Assignee = updates.Assignee
	issue.Labels = updates.Labels
	issue.Fields = updates.Fields
	issue.Updated = time.Now()

	if err := updateIssue(issue); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error": "Failed to update issue: " + err.Error(),
		})
	}

	if c.Get("HX-Request") == "true" {
		return c.Render("partials/issue_detail", fiber.Map{
			"Issue": issue,
		})
	}

	return c.Redirect().To("/issues/" + id)
}

func handleDeleteIssue(c fiber.Ctx) error {
	id := c.Params("id")

	if err := deleteIssue(id); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error": "Failed to delete issue: " + err.Error(),
		})
	}

	if c.Get("HX-Request") == "true" {
		return c.SendStatus(fiber.StatusOK)
	}

	return c.Redirect().To("/issues")
}

func handleSearch(c fiber.Ctx) error {
	filters := make(map[string]string)

	err := c.Bind().Query(filters)
	if err != nil {
		log.Printf("Failed to parse search filters: %v", err)
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": "Failed to parse search filters: " + err.Error(),
		})
	}

	issues, err := searchIssues(filters)
	if err != nil {
		log.Printf("Search failed: %v", err)
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error": "Search failed: " + err.Error(),
		})
	}

	if c.Get("HX-Request") == "true" {
		// Render partial
		return c.Render("partials/search_results", fiber.Map{
			"Issues":  issues,
			"Count":   len(issues),
			"Filters": filters,
		})
	}

	return c.Render("search", fiber.Map{
		"Title":   "Search Results",
		"Issues":  issues,
		"Count":   len(issues),
		"Filters": filters,
	})
}
