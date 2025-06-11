package main

import (
	"github.com/gocql/gocql"
	"os"
	"strings"
	"time"
)

type Issue struct {
	ID          string            `json:"id"`
	Title       string            `json:"title"`
	Description string            `json:"description"`
	Status      string            `json:"status"`
	Priority    string            `json:"priority"`
	Assignee    string            `json:"assignee"`
	Creator     string            `json:"creator"`
	Labels      []string          `json:"labels"`
	Created     time.Time         `json:"created"`
	Updated     time.Time         `json:"updated"`
	Comments    []Comment         `json:"comments"`
	Fields      map[string]string `json:"fields"`
	Hidden      bool              `json:"hidden"`
}

type Comment struct {
	ID      string    `json:"id"`
	IssueID string    `json:"issue_id"`
	Author  string    `json:"author"`
	Content string    `json:"content"`
	Created time.Time `json:"created"`
}

var session *gocql.Session

func initCassandra() (*gocql.Session, error) {
	cassandraHost := os.Getenv("CASSANDRA_HOST")
	if cassandraHost == "" {
		cassandraHost = "127.0.0.1"
	}

	cassandraPort := os.Getenv("CASSANDRA_PORT")
	if cassandraPort == "" {
		cassandraPort = "9042"
	}

	cassandraKeyspace := os.Getenv("CASSANDRA_KEYSPACE")
	if cassandraKeyspace == "" {
		cassandraKeyspace = "jirai"
	}

	cassandraUser := os.Getenv("CASSANDRA_USER")
	if cassandraUser == "" {
		cassandraUser = "cassandra"
	}

	cassandraPassword := os.Getenv("CASSANDRA_PASSWORD")
	if cassandraPassword == "" {
		cassandraPassword = "cassandra"
	}

	cluster := gocql.NewCluster(cassandraHost)
	cluster.Keyspace = cassandraKeyspace
	cluster.Consistency = gocql.Quorum
	cluster.Timeout = time.Second * 5
	cluster.Authenticator = gocql.PasswordAuthenticator{Username: cassandraUser, Password: cassandraPassword}

	println("Connecting to Cassandra cluster at", cassandraHost, "port", cassandraPort, "keyspace", cassandraKeyspace)

	var err error
	session, err = cluster.CreateSession()
	return session, err
}

func setupDatabase() error {
	if err := session.Query(`
		CREATE TABLE IF NOT EXISTS issues (
			id TEXT PRIMARY KEY,
			title TEXT,
			description TEXT,
			status TEXT,
			priority TEXT,
			assignee TEXT,
			creator TEXT,
			labels LIST<TEXT>,
			created TIMESTAMP,
			updated TIMESTAMP,
			fields MAP<TEXT, TEXT>,
			hidden BOOLEAN
		)
	`).Exec(); err != nil {
		return err
	}

	if err := session.Query(`
		CREATE TABLE IF NOT EXISTS comments (
			id TEXT,
			issue_id TEXT,
			author TEXT,
			content TEXT,
			created TIMESTAMP,
			PRIMARY KEY (issue_id, id)
		)
	`).Exec(); err != nil {
		return err
	}

	return nil
}

func getIssueByID(id string) (Issue, error) {
	var issue Issue
	var labels []string
	var fields map[string]string

	// First try to get the issue regardless of hidden status (for NoSQL injection demo)
	if err := session.Query(`
		SELECT id, title, description, status, priority, assignee, creator, labels, created, updated, fields, hidden
		FROM issues
		WHERE id = ?
		ALLOW FILTERING
	`, id).Scan(&issue.ID, &issue.Title, &issue.Description, &issue.Status, &issue.Priority,
		&issue.Assignee, &issue.Creator, &labels, &issue.Created, &issue.Updated, &fields, &issue.Hidden); err != nil {
		return Issue{}, err
	}

	issue.Labels = labels
	issue.Fields = fields

	var comments []Comment
	iter := session.Query(`
		SELECT id, issue_id, author, content, created
		FROM comments
		WHERE issue_id = ?
	`, id).Iter()

	var comment Comment
	for iter.Scan(&comment.ID, &comment.IssueID, &comment.Author, &comment.Content, &comment.Created) {
		comments = append(comments, comment)
	}
	if err := iter.Close(); err != nil {
		return Issue{}, err
	}

	issue.Comments = comments
	return issue, nil
}

func createIssue(issue Issue) error {
	return session.Query(`
		INSERT INTO issues (id, title, description, status, priority, assignee, creator, labels, created, updated, fields, hidden)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
	`, issue.ID, issue.Title, issue.Description, issue.Status, issue.Priority,
		issue.Assignee, issue.Creator, issue.Labels, issue.Created, issue.Updated, issue.Fields, issue.Hidden).Exec()
}

func updateIssue(issue Issue) error {
	return session.Query(`
		UPDATE issues
		SET title = ?, description = ?, status = ?, priority = ?, assignee = ?, labels = ?, updated = ?, fields = ?, hidden = ?
		WHERE id = ? AND hidden = false
		ALLOW FILTERING
	`, issue.Title, issue.Description, issue.Status, issue.Priority,
		issue.Assignee, issue.Labels, issue.Updated, issue.Fields, issue.Hidden, issue.ID).Exec()
}

func deleteIssue(id string) error {
	if err := session.Query(`DELETE FROM comments WHERE issue_id = ? AND hidden = false ALLOW FILTERING`, id).Exec(); err != nil {
		return err
	}

	return session.Query(`DELETE FROM issues WHERE id = ? AND hidden = false ALLOW FILTERING`, id).Exec()
}

func searchIssues(filters map[string]string) ([]Issue, error) {
	var issues []Issue

	// Check if raw_query exists, if so, use it directly for NoSQL injection
	if rawQuery, ok := filters["raw_query"]; ok && rawQuery != "" {
		// Direct injection - simply use the raw query with minimal processing
		query := "SELECT id, title, description, status, priority, assignee, creator, labels, created, updated, fields, hidden FROM issues"

		// Clean up raw_query slightly
		rawQuery = strings.TrimSpace(rawQuery)

		// Add WHERE clause and the raw query directly
		query += " WHERE " + rawQuery + " ALLOW FILTERING"

		// Log the query for debugging
		println("Executing CQL query:", query)

		iter := session.Query(query).Iter()

		var issue Issue
		var labels []string
		var fields map[string]string

		for iter.Scan(&issue.ID, &issue.Title, &issue.Description, &issue.Status, &issue.Priority,
			&issue.Assignee, &issue.Creator, &labels, &issue.Created, &issue.Updated, &fields, &issue.Hidden) {

			issue.Labels = labels
			issue.Fields = fields
			issues = append(issues, issue)
		}

		if err := iter.Close(); err != nil {
			return nil, err
		}

		return issues, nil
	}

	// Regular search (without NoSQL injection)
	query := "SELECT id, title, description, status, priority, assignee, creator, labels, created, updated, fields, hidden FROM issues"

	// Collect valid conditions
	var conditions []string

	// By default filter hidden issues
	conditions = append(conditions, "hidden = false")

	// Add other filters
	for key, value := range filters {
		if value == "" || key == "raw_query" {
			continue
		}

		if strings.HasPrefix(key, "fields[") && strings.HasSuffix(key, "]") {
			fieldName := key[7 : len(key)-1]
			conditions = append(conditions, "fields['"+fieldName+"'] = '"+value+"'")
		} else {
			conditions = append(conditions, key+" = '"+value+"'")
		}
	}

	// Add WHERE clause
	if len(conditions) > 0 {
		query += " WHERE " + strings.Join(conditions, " AND ")
	}

	// Always add ALLOW FILTERING
	query += " ALLOW FILTERING"

	// Log the query for debugging
	println("Executing CQL query:", query)

	iter := session.Query(query).Iter()

	var issue Issue
	var labels []string
	var fields map[string]string

	for iter.Scan(&issue.ID, &issue.Title, &issue.Description, &issue.Status, &issue.Priority,
		&issue.Assignee, &issue.Creator, &labels, &issue.Created, &issue.Updated, &fields, &issue.Hidden) {

		issue.Labels = labels
		issue.Fields = fields
		issues = append(issues, issue)
	}

	if err := iter.Close(); err != nil {
		return nil, err
	}

	return issues, nil
}

func listIssues() ([]Issue, error) {
	var issues []Issue

	iter := session.Query(`
		SELECT id, title, description, status, priority, assignee, creator, labels, created, updated, fields, hidden
		FROM issues
		WHERE hidden = false
		ALLOW FILTERING
	`).Iter()

	var issue Issue
	var labels []string
	var fields map[string]string

	for iter.Scan(&issue.ID, &issue.Title, &issue.Description, &issue.Status, &issue.Priority,
		&issue.Assignee, &issue.Creator, &labels, &issue.Created, &issue.Updated, &fields, &issue.Hidden) {

		issue.Labels = labels
		issue.Fields = fields
		issues = append(issues, issue)
	}

	if err := iter.Close(); err != nil {
		return nil, err
	}

	return issues, nil
}
