-- Create keyspace if it doesn't exist
CREATE KEYSPACE IF NOT EXISTS jirai WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

-- Switch to jirai keyspace
USE jirai;

-- Create issues table
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
);

-- Create comments table
CREATE TABLE IF NOT EXISTS comments (
    id TEXT,
    issue_id TEXT,
    author TEXT,
    content TEXT,
    created TIMESTAMP,
    PRIMARY KEY (issue_id, id)
);

-- Insert some sample data
INSERT INTO issues (id, title, description, status, priority, assignee, creator, labels, created, updated, fields, hidden)
VALUES (
    '1234-5678-9abc-def0',
    'Implement login page',
    'Create a responsive login page with username/password fields and "remember me" option.',
    'in_progress',
    'high',
    'Alex Chen',
    'Sarah Johnson',
    ['frontend', 'ui', 'authentication'],
    toTimestamp(now()),
    toTimestamp(now()),
    {'estimated_hours': '8', 'component': 'web-ui'},
    false
);

INSERT INTO issues (id, title, description, status, priority, assignee, creator, labels, created, updated, fields, hidden)
VALUES (
    '2345-6789-abcd-ef01',
    'Fix database connection leak',
    'There appears to be a connection leak when querying user profiles. Need to ensure all connections are properly closed.',
    'todo',
    'critical',
    'Miguel Rodriguez',
    'Sarah Johnson',
    ['backend', 'database', 'bug'],
    toTimestamp(now()),
    toTimestamp(now()),
    {'estimated_hours': '4', 'component': 'data-layer', 'affects_version': '1.2.0'},
    false
);

INSERT INTO issues (id, title, description, status, priority, assignee, creator, labels, created, updated, fields, hidden)
VALUES (
    '3456-789a-bcde-f012',
    'Update documentation for API v2',
    'The API documentation needs to be updated to reflect the changes in v2.',
    'review',
    'medium',
    'Jordan Taylor',
    'Miguel Rodriguez',
    ['documentation', 'api'],
    toTimestamp(now()),
    toTimestamp(now()),
    {'estimated_hours': '6', 'component': 'docs', 'affects_version': '2.0.0'},
    false
);

INSERT INTO issues (id, title, description, status, priority, assignee, creator, labels, created, updated, fields, hidden)
VALUES (
    '4567-89ab-cdef-0123',
    'Implement dark mode',
    'Add a dark mode theme option throughout the application.',
    'todo',
    'low',
    'Sarah Johnson',
    'Alex Chen',
    ['frontend', 'ui', 'enhancement'],
    toTimestamp(now()),
    toTimestamp(now()),
    {'estimated_hours': '12', 'component': 'web-ui', 'target_version': '2.1.0'},
    false
);

INSERT INTO issues (id, title, description, status, priority, assignee, creator, labels, created, updated, fields, hidden)
VALUES (
    '1',
    'Setup Authentication Module',
    'Implement user authentication using JWT tokens',
    'todo',
    'high',
    'john.doe',
    'admin',
    ['backend', 'security'],
    toTimestamp(now()),
    toTimestamp(now()),
    {'estimated_hours': '20', 'complexity': 'medium'},
    false
);

INSERT INTO issues (id, title, description, status, priority, assignee, creator, labels, created, updated, fields, hidden)
VALUES (
    'flag-issue-9876',
    'SECRET: Flag Storage System',
    'Congratulations on finding this hidden issue through NoSQL injection!
    
    The flag is: vrnctf{n0sql1_1s_un1qu3}
    
    This issue is marked as hidden=true and cannot be accessed through normal application functionality.
    
    You have successfully exploited the NoSQL injection vulnerability in the search functionality.',
    'completed',
    'critical',
    'security-team',
    'admin',
    ['security', 'confidential', 'flag'],
    toTimestamp(now()),
    toTimestamp(now()),
    {'visibility': 'restricted', 'security_level': 'maximum', 'flag': 'TRUE'},
    true
);

-- Insert some sample comments
INSERT INTO comments (id, issue_id, author, content, created)
VALUES (
    'comment-1',
    '1234-5678-9abc-def0',
    'Sarah Johnson',
    'I''ve started working on this. Should have a prototype by tomorrow.',
    toTimestamp(now())
);

INSERT INTO comments (id, issue_id, author, content, created)
VALUES (
    'comment-2',
    '1234-5678-9abc-def0',
    'Alex Chen',
    'Great! Make sure to use our new UI component library.',
    toTimestamp(now())
);

INSERT INTO comments (id, issue_id, author, content, created)
VALUES (
    'comment-1',
    '2345-6789-abcd-ef01',
    'Miguel Rodriguez',
    'This is likely due to not closing the connection in the try-finally block. Will investigate.',
    toTimestamp(now())
);

-- The following role creation statements were causing unauthorized errors
-- Commented out to fix initialization issues
CREATE ROLE IF NOT EXISTS readonly_user WITH PASSWORD = 'readonly_password' AND LOGIN = true;
-- CREATE ROLE IF NOT EXISTS admin_user WITH PASSWORD = 'omegaomegaomegaomega' AND LOGIN = true;

-- Grant statements are also commented out since they reference roles that no longer exist
GRANT SELECT ON KEYSPACE jirai TO readonly_user;
-- GRANT ALL ON KEYSPACE jirai TO admin_user;

-- Verify permissions (optional)
-- LIST ALL PERMISSIONS OF readonly_user;
