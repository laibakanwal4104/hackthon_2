---
name: backend-api-core
description: Build backend APIs by generating routes, handling requests/responses, and connecting to databases.
---

# Backend API Development

## Instructions

1. **Route generation**
   - Define RESTful routes (GET, POST, PUT, DELETE)
   - Organize routes by feature/module
   - Use clear and consistent URL naming

2. **Request & response handling**
   - Validate incoming request data
   - Handle query params, route params, and body
   - Send proper HTTP status codes
   - Return structured JSON responses

3. **Database connection**
   - Connect to a database (SQL or NoSQL)
   - Use environment variables for credentials
   - Perform CRUD operations
   - Handle connection and query errors safely

## Best Practices
- Keep controllers thin and focused
- Separate routes, controllers, and services
- Use async/await with proper error handling
- Never expose sensitive data in responses
- Use middleware for auth, logging, and validation

## Example Structure
```js
// routes/user.routes.js
import express from "express";
import { getUsers, createUser } from "../controllers/user.controller.js";

const router = express.Router();

router.get("/", getUsers);
router.post("/", createUser);

export default router;
