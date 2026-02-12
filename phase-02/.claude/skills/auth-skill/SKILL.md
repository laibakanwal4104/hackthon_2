---
name: auth-skill
description: Implement secure authentication systems including signup, signin, password hashing, tokens, and Better Auth integration.
---

# Authentication Skill

## Instructions

1. **User Signup**
   - Validate user input (email, password)
   - Hash passwords before storing
   - Prevent duplicate accounts
   - Return success or error response

2. **User Signin**
   - Verify user credentials
   - Compare hashed passwords
   - Generate authentication tokens
   - Handle invalid login attempts securely

3. **Password Security**
   - Use strong hashing algorithms (bcrypt, argon2)
   - Apply salting
   - Never store plain-text passwords

4. **Token Management**
   - Generate JWT or session tokens
   - Set token expiration
   - Secure tokens using HTTP-only cookies or headers
   - Implement refresh token strategy

5. **Better Auth Integration**
   - Configure Better Auth provider
   - Connect with database adapter
   - Enable email/password authentication
   - Support OAuth providers if needed

## Best Practices
- Always hash passwords before saving
- Use environment variables for secrets
- Implement rate limiting on auth routes
- Return generic error messages (avoid leaking info)
- Protect routes with authentication middleware
- Follow OWASP authentication guidelines

## Example Structure
```js
// Signup example
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";

export async function signup(req, res) {
  const { email, password } = req.body;

  const hashedPassword = await bcrypt.hash(password, 10);

  const user = await db.user.create({
    data: { email, password: hashedPassword }
  });

  res.status(201).json({ message: "User created successfully" });
}

// Signin example
export async function signin(req, res) {
  const { email, password } = req.body;

  const user = await db.user.findUnique({ where: { email } });
  if (!user) return res.status(401).json({ error: "Invalid credentials" });

  const isValid = await bcrypt.compare(password, user.password);
  if (!isValid) return res.status(401).json({ error: "Invalid credentials" });

  const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET, {
    expiresIn: "7d",
  });

  res.json({ token });
}
