---
name: database-schema-design
description: Design relational database schemas with tables, migrations, and best practices. Use for scalable backend systems.
---

# Database Schema & Migrations

## Instructions

1. **Schema design**
   - Identify core entities
   - Define relationships (1–1, 1–many, many–many)
   - Normalize data (avoid redundancy)

2. **Table creation**
   - Use meaningful table and column names
   - Define primary keys and foreign keys
   - Choose appropriate data types

3. **Migrations**
   - Create versioned migration files
   - Support up and down migrations
   - Keep migrations atomic and reversible

## Best Practices
- Follow naming conventions (snake_case or camelCase consistently)
- Always use primary keys
- Index frequently queried columns
- Avoid premature optimization
- Document schema changes

## Example Structure
```sql
-- users table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(150) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- posts table
CREATE TABLE posts (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  title VARCHAR(200),
  body TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
