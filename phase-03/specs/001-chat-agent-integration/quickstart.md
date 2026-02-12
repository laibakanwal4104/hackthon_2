# Quickstart Guide: AI Chat Agent & Integration

**Feature**: 001-chat-agent-integration
**Date**: 2026-02-09
**Audience**: Developers and hackathon reviewers

## Overview

This guide walks through setting up and testing the AI-powered chat interface for natural language todo management. Follow these steps to get the system running locally.

## Prerequisites

- Python 3.11+ installed
- Node.js 18+ installed (for frontend)
- PostgreSQL database (Neon Serverless) from Phase-II
- OpenAI API key (with GPT-4 Turbo access)
- Phase-II backend and frontend working

## Step 1: Environment Setup

### 1.1 Install Backend Dependencies

```bash
cd phase-02/backend

# Install all dependencies from requirements.txt
pip install -r requirements.txt

# Verify OpenAI SDK installation
python -c "import openai; print(openai.__version__)"
```

### 1.2 Configure Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `phase-02/backend/.env`:

```bash
# Database Configuration (Neon PostgreSQL)
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require

# JWT Authentication
JWT_SECRET=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=15

# OpenAI Configuration (REQUIRED for chat agent)
OPENAI_API_KEY=sk-...your-key-here...

# Application
DEBUG=true
LOG_LEVEL=info
```

**Optional agent tuning** (via environment variables):

```bash
# These override defaults in src/agent/config.py
AGENT_MODEL=gpt-4-turbo-preview    # Default: gpt-4-turbo-preview
AGENT_TEMPERATURE=0.7               # Default: 0.7
AGENT_MAX_TOKENS=1000               # Default: 1000
AGENT_TIMEOUT=30                     # Default: 30 seconds
```

### 1.3 Verify OpenAI API Key

```bash
python -c "
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
response = client.chat.completions.create(
    model='gpt-3.5-turbo',
    messages=[{'role': 'user', 'content': 'Hello'}],
    max_tokens=10
)
print('OpenAI API working:', response.choices[0].message.content)
"
```

## Step 2: Database Setup

Database tables are **automatically created** on application startup via `SQLModel.metadata.create_all()`. No manual migration is needed.

The following tables are created automatically:
- `conversation` - Chat sessions per user
- `message` - Individual messages within conversations
- `tool_invocation` - MCP tool call audit trail

**Note**: A migration file exists at `alembic/versions/versions/005_add_chat_tables.py` for reference, but the app uses auto-creation.

## Step 3: Start the Application

### 3.1 Start Backend Server

```bash
cd phase-02/backend

# Start with hot-reload for development
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Verify server started
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# View API docs
# Open: http://localhost:8000/docs
```

### 3.2 Start Frontend

```bash
cd phase-02/full_stack_todo_frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Frontend starts on http://localhost:3000
```

## Step 4: Test Chat API

### 4.1 Get Authentication Token

```bash
# Sign up a new user
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'

# Or sign in with existing user
curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'

# Save the access_token from the response
export TOKEN="eyJ..."
```

### 4.2 Test Chat Endpoint

```bash
# Send first message (auto-creates conversation)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message": "Hello, what can you help me with?"}'

# Expected response:
# {
#   "response": "Hello! I'm your AI assistant...",
#   "conversation_id": "550e8400-...",
#   "message_id": "660e8400-...",
#   "tool_calls": []
# }

# Save conversation_id for subsequent messages
export CONV_ID="550e8400-..."
```

### 4.3 Test Todo Operations via Chat

```bash
# Create a todo via natural language
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"message\": \"Add a task to buy groceries\", \"conversation_id\": \"$CONV_ID\"}"

# List todos
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"message\": \"Show me my tasks\", \"conversation_id\": \"$CONV_ID\"}"

# Mark complete
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"message\": \"Mark the grocery task as complete\", \"conversation_id\": \"$CONV_ID\"}"
```

### 4.4 Test Conversation History

```bash
# Get conversation history (most recent 50 messages)
curl -X GET "http://localhost:8000/chat/history?conversation_id=$CONV_ID&limit=50" \
  -H "Authorization: Bearer $TOKEN"

# Expected: { "conversation_id": "...", "messages": [...] }
```

## Step 5: Frontend Chat Interface

### 5.1 Access Chat Page

1. Open browser to `http://localhost:3000`
2. Sign in with your credentials
3. Navigate to `/chat`
4. Start chatting with the AI assistant

### 5.2 Frontend Features

- **Message input**: Type messages, press Enter to send (Shift+Enter for newline)
- **Role-based styling**: User messages (blue, right), Agent messages (gray, left)
- **Tool call indicators**: Shows which MCP tools were invoked with success/error status
- **Loading state**: Animated "Agent is thinking..." indicator
- **Conversation persistence**: Messages survive browser refresh
- **New Conversation**: Button to start a fresh conversation
- **Error handling**: Displays errors with retry capability
- **Character limit**: 2000 characters per message

## Step 6: End-to-End Testing Scenarios

### Scenario 1: Basic Chat (User Story 1)

1. Open `/chat` page
2. Send: "Hello"
3. Verify: Agent responds with greeting and capability description
4. Verify: Response time < 5 seconds
5. Verify: User message (blue, right) and agent message (gray, left)

### Scenario 2: Todo Operations (User Story 2)

1. Send: "Add a task to buy groceries"
2. Verify: Agent confirms creation, tool call indicator shows "Created task"
3. Send: "Show me my tasks"
4. Verify: Agent lists tasks
5. Send: "Mark the grocery task as complete"
6. Verify: Agent confirms completion
7. Send: "Delete the grocery task"
8. Verify: Agent confirms deletion

### Scenario 3: Ambiguous Request Handling (User Story 2)

1. Create 2+ tasks with similar names
2. Send: "Update the task" (ambiguous)
3. Verify: Agent asks which task you mean with specific options

### Scenario 4: Conversation Persistence (User Story 3)

1. Have a conversation with 3-4 messages
2. Refresh the browser page (F5)
3. Verify: All messages still visible
4. Send a new message
5. Verify: Conversation continues with full context
6. Click "New Conversation" button
7. Verify: Messages cleared, fresh conversation starts

### Scenario 5: Error Handling

1. Send an empty message (should be blocked by validation)
2. If OpenAI API is down, verify graceful error message
3. Verify tool errors show helpful messages (not raw errors)

## Architecture Overview

```
Frontend (Next.js)          Backend (FastAPI)           External
┌──────────────┐           ┌──────────────────┐        ┌─────────┐
│ ChatInterface├──POST────>│ /chat endpoint   │───────>│ OpenAI  │
│ MessageList  │  /chat    │   ├─ Auth (JWT)  │        │ GPT-4   │
│ MessageInput │           │   ├─ AgentService│<───────│ Turbo   │
│              │<─JSON─────│   │  ├─ MCP Tools│        └─────────┘
│              │           │   │  │  ├─ create│
│ chat.ts API  ├──GET─────>│   │  │  ├─ list  │        ┌─────────┐
│  client      │ /history  │   │  │  ├─ update│───────>│ Neon    │
└──────────────┘           │   │  │  ├─ delete│        │ Postgres│
                           │   │  │  └─ mark  │<───────│         │
                           └───┴──┴───────────┘        └─────────┘
```

## Verify Constitution Compliance

- **Principle I** - Agent-First: OpenAI Agents SDK orchestrates all AI interactions
- **Principle II** - MCP Tool Isolation: 5 stateless tools with JSON schemas
- **Principle III** - Database Boundaries: Agent never touches DB directly
- **Principle IV** - Stateless Execution: Context rebuilt from DB each request
- **Principle V** - Persistence: Conversations, messages, tool invocations all stored
- **Principle VI** - User Isolation: JWT auth + user_id filtering everywhere
- **Principle VII** - Natural Language: Conversational interface for all todo ops

## Troubleshooting

### OpenAI API Error (500)
- Verify `OPENAI_API_KEY` is set in `.env`
- Check API key has GPT-4 Turbo access
- Verify internet connectivity
- Check OpenAI status page

### Chat Returns Empty Response
- Check backend logs for errors
- Verify the system prompt loads correctly
- Ensure MCP tools are registered in `src/mcp/__init__.py`

### Conversation Not Persisting
- Verify `DATABASE_URL` is correct
- Check database connectivity
- Ensure tables were auto-created (check backend startup logs)

### Frontend Can't Connect
- Verify backend runs on port 8000
- Check CORS middleware allows frontend origin
- Verify `NEXT_PUBLIC_API_URL` points to correct backend URL
- Check browser console for network errors

## Performance Expectations

| Metric | Target | Notes |
|--------|--------|-------|
| Chat response | 2-5s (p95) | Includes OpenAI API latency |
| DB query | <100ms | Indexed queries |
| Agent reasoning | 1-3s | GPT-4 Turbo |
| Tool execution | <500ms | Direct DB operations |
| Frontend render | <100ms | React client-side |
