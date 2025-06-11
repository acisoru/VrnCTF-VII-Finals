package main

import (
	"github.com/gocql/gocql"
	"github.com/gofiber/fiber/v3"
	"github.com/google/uuid"
	"time"
)

func newIssueFromRequest(c fiber.Ctx) (Issue, error) {
	issue := new(Issue)

	if err := c.Bind().JSON(issue); err != nil {
		return Issue{}, err
	}

	if issue.ID == "" {
		issue.ID = uuid.NewString()
	}

	now := time.Now()
	issue.Created = now
	issue.Updated = now

	if issue.Labels == nil {
		issue.Labels = []string{}
	}

	if issue.Fields == nil {
		issue.Fields = make(map[string]string)
	}

	return *issue, nil
}

func secureSearchIssues(filters map[string]string) ([]Issue, error) {
	var issues []Issue

	query := "SELECT id, title, description, status, priority, assignee, creator, labels, created, updated, fields FROM issues"

	var params []interface{}

	if len(filters) > 0 {
		query += " WHERE "
		first := true

		for key, value := range filters {
			if value == "" {
				continue
			}

			if !first {
				query += " AND "
			}

			if key == "title" {
				query += "title CONTAINS ?"
				params = append(params, value)
			} else if key == "status" || key == "priority" || key == "assignee" || key == "creator" {
				query += key + " = ?"
				params = append(params, value)
			}

			first = false
		}
	}

	var iter *gocql.Iter
	if len(params) > 0 {
		iter = session.Query(query, params...).Iter()
	} else {
		iter = session.Query(query).Iter()
	}

	var issue Issue
	var labels []string
	var fields map[string]string

	for iter.Scan(&issue.ID, &issue.Title, &issue.Description, &issue.Status, &issue.Priority,
		&issue.Assignee, &issue.Creator, &labels, &issue.Created, &issue.Updated, &fields) {

		issue.Labels = labels
		issue.Fields = fields

		issues = append(issues, issue)
	}

	if err := iter.Close(); err != nil {
		return nil, err
	}

	return issues, nil
}
