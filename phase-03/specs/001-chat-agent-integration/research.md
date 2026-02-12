# Research: AI Chat Agent & Integration

**Feature**: 001-chat-agent-integration
**Date**: 2026-02-07
**Phase**: Phase 0 - Technology Research & Validation

## Overview

This document captures research findings for integrating OpenAI Agents SDK with the existing FastAPI backend, implementing MCP tools, and creating a stateless chat architecture.

## 1. OpenAI Agents SDK Integration

### Decision
Use OpenAI Agents SDK (official Python SDK) with function calling capabilities for tool orchestration.

### Rationale
- **Constitution Compliance**: Principle I mandates agent-first architecture using OpenAI Agents SDK
- **Robust Tool Orchestration**: SDK handles tool selection, parameter extraction, and result processing
- **Conversation Management**: Built-in support for message history and context
- **Error Handling**: Structured error responses and retry mechanisms
- **Community Support**: Well-documented, actively maintained, production-ready

### Alternatives Considered
1. **Custom Agent Implementation**: Rejected - violates constitution, requires significant development effort
2. **LangChain Agents**: Rejected - constitution specifically requires OpenAI Agents SDK
3. **Anthropic Claude with Tools**: Rejected - constitution mandates OpenAI

### Implementation Notes

**SDK Installation**:
```bash
pip install openai>=1.0.0
```

**Agent Initialization Pattern**:
```python
from openai import OpenAI

client = OpenAI(api_key=settings.openai_api_key)

# Agent configuration
agent_config = {
    "model": "gpt-4-turbo-preview",  # or gpt-4, gpt-3.5-turbo
    "temperature": 0.7,
    "max_tokens": 1000,
    "tools": [...]  # MCP tools registered here
}
```

**Conversation Context Reconstruction**:
```python
# Load messages from database
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "Previous user message"},
    {"role": "assistant", "content": "Previous agent response"},
    {"role": "user", "content": "Current user message"}
]

response = client.chat.completions.create(
    model=agent_config["model"],
    messages=messages,
    tools=agent_config["tools"]
)
```

**Tool Invocation Handling**:
- Agent returns `tool_calls` in response
- Extract tool name and arguments
- Execute MCP tool with arguments
- Return result to agent for final response
- May require multiple rounds (agent → tool → agent)

**Key Configuration Parameters**:
- `model`: gpt-4-turbo-preview (best reasoning) or gpt-3.5-turbo (faster, cheaper)
- `temperature`: 0.7 (balanced creativity and consistency)
- `max_tokens`: 1000 (sufficient for responses with tool calls)
- `timeout`: 30s (prevent hanging requests)

## 2. MCP SDK Implementation

### Decision
Implement MCP tools as Python functions with JSON Schema definitions, following official MCP SDK patterns.

### Rationale
- **Constitution Compliance**: Principle II requires stateless, schema-defined MCP tools
- **Type Safety**: JSON Schema provides input/output validation
- **Discoverability**: Agent can understand tool capabilities from schemas
- **Testability**: Tools can be tested independently of agent
- **Audit Trail**: Clear logging of tool invocations and results

### Alternatives Considered
1. **Direct Database Access from Agent**: Rejected - violates Principle III (NON-NEGOTIABLE)
2. **REST API Calls**: Rejected - adds network overhead, unnecessary complexity
3. **Custom Tool Protocol**: Rejected - MCP SDK is standard and well-supported

### Implementation Notes

**MCP Tool Structure**:
```python
# mcp/schemas.py
CREATE_TODO_SCHEMA = {
    "type": "function",
    "function": {
        "name": "create_todo",
        "description": "Create a new todo task for the user",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The title of the todo task"
                },
                "description": {
                    "type": "string",
                    "description": "Optional description of the task"
                }
            },
            "required": ["title"]
        }
    }
}

# mcp/tools.py
async def create_todo(user_id: UUID, title: str, description: str = None) -> dict:
    """Create a new todo task."""
    try:
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            is_completed=False
        )
        session.add(task)
        session.commit()

        return {
            "success": True,
            "task_id": str(task.id),
            "message": f"Created todo: {title}"
        }
    except Exception as e:
        logger.error(f"Error creating todo: {e}")
        return {
            "success": False,
            "error": str(e)
        }
```

**Five MCP Tools Required**:
1. `create_todo(title, description?)` - Create new task
2. `list_todos(filter?)` - List user's tasks (all, completed, pending)
3. `update_todo(task_id, title?, description?)` - Update task details
4. `delete_todo(task_id)` - Delete a task
5. `mark_todo_complete(task_id, completed)` - Toggle completion status

**Tool Design Principles**:
- **Stateless**: No internal state between calls
- **User Isolation**: Always filter by user_id (passed from endpoint)
- **Error Handling**: Return structured errors, never raise exceptions to agent
- **Logging**: Log all invocations with parameters and results
- **Validation**: Validate inputs before database operations

**Tool Registration**:
```python
TOOLS = [
    CREATE_TODO_SCHEMA,
    LIST_TODOS_SCHEMA,
    UPDATE_TODO_SCHEMA,
    DELETE_TODO_SCHEMA,
    MARK_TODO_COMPLETE_SCHEMA
]

# Pass to OpenAI client
response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=messages,
    tools=TOOLS
)
```

## 3. Stateless Chat Architecture

### Decision
Implement stateless `/chat` endpoint that reconstructs conversation context from database on each request.

### Rationale
- **Constitution Compliance**: Principle IV mandates stateless execution
- **Horizontal Scaling**: No session affinity required, any server can handle any request
- **Reliability**: No memory leaks, server restarts don't lose conversations
- **Simplicity**: No session management, caching, or state synchronization
- **Consistency**: Database is single source of truth

### Alternatives Considered
1. **In-Memory Session State**: Rejected - violates stateless principle, doesn't scale
2. **Redis Session Store**: Rejected - adds complexity, still requires state management
3. **WebSocket Connections**: Rejected - not required for hackathon demo, adds complexity

### Implementation Notes

**Request Flow**:
```
1. User sends message to POST /chat
2. Endpoint authenticates user (JWT)
3. Load or create conversation for user
4. Load all messages in conversation (ordered by sequence_number)
5. Reconstruct message history for agent
6. Call OpenAI agent with full context
7. Handle tool calls if present
8. Persist user message and agent response
9. Return response to user
```

**Database Query Pattern**:
```python
# Get or create conversation
conversation = session.query(Conversation).filter_by(
    user_id=user_id,
    status="active"
).first()

if not conversation:
    conversation = Conversation(user_id=user_id, status="active")
    session.add(conversation)
    session.commit()

# Load message history
messages = session.query(Message).filter_by(
    conversation_id=conversation.id
).order_by(Message.sequence_number).all()

# Convert to OpenAI format
message_history = [
    {"role": msg.role, "content": msg.content}
    for msg in messages
]
```

**Performance Optimization**:
- Index on `conversation_id` and `sequence_number`
- Limit message history to last 50 messages (pagination)
- Use database connection pooling (existing in Phase-II)
- Consider caching system prompt (doesn't change per request)

**Concurrency Handling**:
- Use database transactions for message persistence
- Sequence numbers prevent message ordering issues
- Optimistic locking on conversation updates

## 4. Frontend Integration

### Decision
Use simple HTTP POST requests from frontend to `/chat` endpoint with JWT authentication.

### Rationale
- **Simplicity**: Easiest to implement for hackathon demo
- **Existing Auth**: Leverages Phase-II JWT authentication
- **No Streaming Required**: Spec explicitly excludes streaming responses
- **Browser Compatibility**: Works in all browsers without special setup
- **Testable**: Easy to test with curl or Postman

### Alternatives Considered
1. **WebSocket Connection**: Rejected - not required, adds complexity, spec excludes streaming
2. **Server-Sent Events (SSE)**: Rejected - not needed for non-streaming responses
3. **GraphQL Subscription**: Rejected - overkill for simple chat interface

### Implementation Notes

**Frontend API Client** (TypeScript):
```typescript
// lib/api/chat.ts
export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  message_id: string;
  tool_calls?: ToolCall[];
}

export async function sendChatMessage(
  message: string,
  conversationId?: string
): Promise<ChatResponse> {
  const token = getAuthToken(); // From existing Phase-II auth

  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      message,
      conversation_id: conversationId
    })
  });

  if (!response.ok) {
    throw new Error('Chat request failed');
  }

  return response.json();
}
```

**Chat Component Structure**:
- `ChatInterface.tsx`: Main container, manages state
- `MessageList.tsx`: Displays conversation history
- `MessageInput.tsx`: Input field and send button

**State Management**:
```typescript
const [messages, setMessages] = useState<Message[]>([]);
const [conversationId, setConversationId] = useState<string | null>(null);
const [isLoading, setIsLoading] = useState(false);

const handleSendMessage = async (text: string) => {
  setIsLoading(true);

  // Add user message to UI immediately
  setMessages(prev => [...prev, { role: 'user', content: text }]);

  try {
    const response = await sendChatMessage(text, conversationId);

    // Update conversation ID if new
    if (!conversationId) {
      setConversationId(response.conversation_id);
    }

    // Add agent response to UI
    setMessages(prev => [...prev, {
      role: 'agent',
      content: response.response
    }]);
  } catch (error) {
    // Show error message
    console.error('Chat error:', error);
  } finally {
    setIsLoading(false);
  }
};
```

**Loading States**:
- Show spinner or "typing..." indicator while waiting for response
- Disable input during request to prevent duplicate sends
- Show error message if request fails

**Authentication Integration**:
- Reuse existing Phase-II JWT token from auth context
- Redirect to login if token expired
- Include token in Authorization header

## 5. System Prompt Design

### Decision
Create a focused system prompt that defines agent behavior, capabilities, and response format.

### Rationale
- Guides agent to use tools correctly
- Sets tone and personality
- Defines error handling behavior
- Ensures consistent responses

### System Prompt Template
```
You are a helpful AI assistant that helps users manage their todo tasks through natural conversation.

CAPABILITIES:
- Create new todo tasks
- List existing tasks (all, completed, or pending)
- Update task details
- Mark tasks as complete or incomplete
- Delete tasks

TOOLS AVAILABLE:
You have access to the following tools:
- create_todo: Create a new task
- list_todos: List user's tasks
- update_todo: Update task details
- delete_todo: Delete a task
- mark_todo_complete: Toggle task completion

BEHAVIOR:
- Always confirm actions taken (e.g., "I've created a task called 'Buy groceries'")
- If a request is ambiguous, ask clarifying questions
- Be conversational and friendly
- If a task doesn't exist, explain clearly
- Provide helpful suggestions when appropriate

RESPONSE FORMAT:
- Keep responses concise and clear
- Use natural language, not technical jargon
- Confirm tool results in user-friendly terms
```

## Summary of Key Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| Agent Framework | OpenAI Agents SDK | Constitution mandate, robust tool support |
| Tool Protocol | MCP with JSON Schema | Stateless, type-safe, testable |
| Architecture | Stateless endpoint | Scalable, reliable, constitution compliant |
| Frontend | HTTP POST | Simple, works with existing auth |
| Model | GPT-4 Turbo | Best reasoning for tool selection |

## Implementation Readiness

✅ All research areas completed
✅ Technology choices validated
✅ Implementation patterns documented
✅ No blockers identified
✅ Ready for Phase 1 (Design & Contracts)
