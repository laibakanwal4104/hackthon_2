# Implementation Plan: AI Chat Agent & Integration

**Branch**: `001-chat-agent-integration` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-chat-agent-integration/spec.md`

## Summary

Implement an AI-powered chat interface that enables users to manage todos through natural language conversations. The system integrates OpenAI Agents SDK with the existing FastAPI backend, using MCP tools for all todo operations. The architecture is stateless with conversation persistence in Neon PostgreSQL, maintaining Phase-II authentication and user isolation. The Chatkit frontend communicates with a new chat API endpoint that orchestrates agent reasoning and tool execution.

**Technical Approach**: Extend the existing Phase-II backend with new database models (Conversation, Message, ToolInvocation), implement a stateless `/chat` endpoint, configure OpenAI Agents SDK with MCP tool access, and integrate the Chatkit frontend to send messages and display responses.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI (existing), OpenAI Agents SDK, MCP SDK (official), SQLModel (existing), Neon PostgreSQL (existing)
**Storage**: Neon PostgreSQL (existing database, new tables for conversations/messages/tool_invocations)
**Testing**: pytest (existing test infrastructure)
**Target Platform**: Linux server (containerized deployment)
**Project Type**: Web application (backend + frontend)
**Performance Goals**: <5s response time (p95), support 10+ concurrent users, agent reasoning <3s
**Constraints**: Stateless execution, no direct DB access from agent, all operations via MCP tools, maintain Phase-II auth
**Scale/Scope**: Hackathon demo (10-50 users), 3 user stories, 5 MCP tools, single conversation per user session

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Agent-First Architecture ✅
- **Requirement**: All AI functionality via OpenAI Agents SDK
- **Compliance**: Agent will be initialized with OpenAI Agents SDK and configured with MCP tools
- **Status**: PASS - Design uses OpenAI Agents SDK as central orchestrator

### Principle II: MCP Tool Isolation ✅
- **Requirement**: All task operations via stateless, schema-defined MCP tools
- **Compliance**: Five MCP tools (create_todo, list_todos, update_todo, delete_todo, mark_complete) with JSON schemas
- **Status**: PASS - MCP tools are the only interface to todo operations

### Principle III: Database Access Boundaries (NON-NEGOTIABLE) ✅
- **Requirement**: Agents MUST NOT access database directly
- **Compliance**: Agent only invokes MCP tools; tools access database via SQLModel
- **Status**: PASS - Clear separation: Agent → MCP Tools → Database

### Principle IV: Stateless Chat Execution ✅
- **Requirement**: Chat endpoint stateless, context rebuilt from database
- **Compliance**: `/chat` endpoint loads conversation history, reconstructs agent state, persists new messages
- **Status**: PASS - No session state maintained in API layer

### Principle V: Conversation Persistence & Traceability ✅
- **Requirement**: All interactions persisted (conversations, messages, tool invocations)
- **Compliance**: Three new database models with full audit trail
- **Status**: PASS - Complete persistence and traceability

### Principle VI: Security & User Isolation ✅
- **Requirement**: Maintain Phase-II auth and user isolation
- **Compliance**: JWT auth required, user_id filtering in all queries, MCP tools enforce isolation
- **Status**: PASS - Existing auth extended to chat endpoint

### Principle VII: Natural Language Interface ✅
- **Requirement**: Users interact via natural language
- **Compliance**: Agent parses conversational input, handles ambiguity, provides human-readable responses
- **Status**: PASS - Core feature requirement

**Overall Status**: ✅ ALL PRINCIPLES SATISFIED - No violations, proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/001-chat-agent-integration/
├── plan.md              # This file
├── research.md          # Phase 0: OpenAI Agents SDK, MCP SDK research
├── data-model.md        # Phase 1: Conversation, Message, ToolInvocation models
├── quickstart.md        # Phase 1: Setup and testing guide
├── contracts/           # Phase 1: Chat API contract
│   └── chat-api.yaml    # OpenAPI spec for /chat endpoint
└── tasks.md             # Phase 2: Implementation tasks (created by /sp.tasks)
```

### Source Code (repository root)

```text
phase-02/
├── backend/
│   ├── src/
│   │   ├── models/
│   │   │   ├── user.py              # Existing
│   │   │   ├── task.py              # Existing
│   │   │   ├── conversation.py      # NEW: Conversation model
│   │   │   ├── message.py           # NEW: Message model
│   │   │   └── tool_invocation.py   # NEW: ToolInvocation model
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── auth.py          # Existing
│   │   │   │   ├── tasks.py         # Existing
│   │   │   │   └── chat.py          # NEW: Chat endpoint
│   │   │   └── schemas/
│   │   │       └── chat.py          # NEW: Chat request/response schemas
│   │   ├── services/
│   │   │   ├── auth_service.py      # Existing
│   │   │   └── agent_service.py     # NEW: Agent orchestration
│   │   ├── agent/
│   │   │   ├── __init__.py          # NEW: Agent module
│   │   │   ├── config.py            # NEW: Agent configuration
│   │   │   └── prompts.py           # NEW: System prompts
│   │   ├── mcp/
│   │   │   ├── __init__.py          # NEW: MCP tools module
│   │   │   ├── tools.py             # NEW: MCP tool definitions
│   │   │   └── schemas.py           # NEW: Tool input/output schemas
│   │   └── main.py                  # Modified: Add chat route
│   ├── alembic/
│   │   └── versions/
│   │       └── 005_add_chat_tables.py  # NEW: Migration for chat tables
│   └── tests/
│       ├── test_chat_api.py         # NEW: Chat endpoint tests
│       ├── test_agent_service.py    # NEW: Agent service tests
│       └── test_mcp_tools.py        # NEW: MCP tool tests
│
└── full_stack_todo_frontend/
    └── src/
        ├── app/
        │   └── chat/
        │       └── page.tsx         # NEW: Chat page (Chatkit integration)
        ├── components/
        │   └── chat/
        │       ├── ChatInterface.tsx    # NEW: Chat UI component
        │       ├── MessageList.tsx      # NEW: Message display
        │       └── MessageInput.tsx     # NEW: Input component
        └── lib/
            └── api/
                └── chat.ts          # NEW: Chat API client
```

**Structure Decision**: Web application structure (Option 2) selected. Existing Phase-II backend and frontend will be extended with new modules for chat functionality. Backend adds agent/, mcp/, and new models. Frontend adds chat page and components. This maintains separation of concerns while leveraging existing infrastructure.

## Complexity Tracking

> No constitution violations - this section is empty.

## Phase 0: Research & Technology Validation

### Research Areas

1. **OpenAI Agents SDK Integration**
   - SDK initialization and configuration
   - Agent prompt engineering best practices
   - Tool registration and invocation patterns
   - Error handling and retry strategies
   - Conversation context management

2. **MCP SDK Implementation**
   - Official MCP SDK usage patterns
   - Tool schema definition (JSON Schema)
   - Stateless tool design patterns
   - Database integration within tools
   - Error propagation to agent

3. **Stateless Chat Architecture**
   - Conversation context reconstruction
   - Message ordering and pagination
   - Concurrent request handling
   - Database transaction patterns
   - Performance optimization strategies

4. **Frontend Integration**
   - Chatkit library usage (if applicable)
   - WebSocket vs HTTP polling vs simple POST
   - Message rendering patterns
   - Loading states and error handling
   - Authentication token passing

### Research Outputs

Research findings will be documented in `research.md` with:
- Decision: Technology/pattern chosen
- Rationale: Why this approach
- Alternatives: What else was considered
- Implementation notes: Key details for Phase 1

## Phase 1: Design & Contracts

### Data Model Design

Three new entities to be defined in `data-model.md`:

1. **Conversation**
   - Fields: id (UUID), user_id (UUID, FK to User), status (enum), created_at, updated_at
   - Relationships: One-to-many with Message
   - Indexes: user_id, created_at
   - Validation: User must exist, status must be valid enum

2. **Message**
   - Fields: id (UUID), conversation_id (UUID, FK), role (enum: user/agent), content (text), sequence_number (int), created_at
   - Relationships: Many-to-one with Conversation, one-to-many with ToolInvocation
   - Indexes: conversation_id, sequence_number, created_at
   - Validation: Content not empty, role must be valid, sequence unique per conversation

3. **ToolInvocation**
   - Fields: id (UUID), message_id (UUID, FK), tool_name (str), input_params (JSON), output_result (JSON), status (enum), executed_at
   - Relationships: Many-to-one with Message
   - Indexes: message_id, tool_name, executed_at
   - Validation: Tool name must be valid, JSON fields must be valid JSON

### API Contracts

Chat API endpoint to be defined in `contracts/chat-api.yaml`:

**POST /chat**
- Request: `{ "message": "string", "conversation_id": "uuid?" }`
- Response: `{ "response": "string", "conversation_id": "uuid", "message_id": "uuid", "tool_calls": [...] }`
- Auth: JWT required (existing Phase-II auth)
- Errors: 401 (unauthorized), 400 (invalid input), 500 (agent error)

### Quickstart Guide

`quickstart.md` will include:
- Environment setup (OpenAI API key, MCP configuration)
- Database migration steps
- Agent configuration and testing
- Frontend integration steps
- End-to-end testing scenarios

## Phase 2: Implementation Tasks

Tasks will be generated by `/sp.tasks` command and organized by user story:
- **Setup**: Database migrations, dependencies, configuration
- **Foundational**: MCP tools, agent service, database models
- **User Story 1 (P1)**: Chat API endpoint, basic agent integration, frontend connection
- **User Story 2 (P2)**: Natural language todo operations, tool invocation, confirmations
- **User Story 3 (P3)**: Conversation persistence, context reconstruction, resumption

## Key Architectural Decisions

### Decision 1: OpenAI Agents SDK vs Custom Agent Implementation
- **Chosen**: OpenAI Agents SDK
- **Rationale**: Constitution mandates agent-first architecture, SDK provides robust tool orchestration, reduces custom code
- **Trade-offs**: Dependency on OpenAI, less control over agent internals, requires API key

### Decision 2: MCP Tool Granularity
- **Chosen**: Five single-purpose tools (create, list, update, delete, mark_complete)
- **Rationale**: Aligns with MCP Tool Isolation principle, easier to test, clear audit trail
- **Trade-offs**: More tools to maintain, agent must choose correct tool, potential for multiple calls

### Decision 3: Conversation Context Strategy
- **Chosen**: Load full conversation history on each request
- **Rationale**: Stateless execution requirement, ensures consistency, simple implementation
- **Trade-offs**: Database load increases with conversation length, may need pagination for long conversations

### Decision 4: Frontend Integration Approach
- **Chosen**: Simple HTTP POST to /chat endpoint
- **Rationale**: Simplest for hackathon demo, no streaming requirement, works with existing auth
- **Trade-offs**: No real-time updates, user waits for full response, no typing indicators

## Risk Analysis

### Risk 1: Agent Response Latency
- **Impact**: User experience degraded if responses take >5s
- **Mitigation**: Optimize MCP tool queries, implement timeout handling, show loading indicators
- **Contingency**: Add response time monitoring, implement caching for common queries

### Risk 2: MCP Tool Errors
- **Impact**: Agent cannot complete operations, user sees error messages
- **Mitigation**: Comprehensive error handling in tools, graceful degradation, clear error messages to agent
- **Contingency**: Implement retry logic, fallback responses, detailed logging

### Risk 3: Conversation Context Size
- **Impact**: Long conversations may cause performance issues or token limits
- **Mitigation**: Implement message pagination, summarize old messages, set conversation length limits
- **Contingency**: Archive old conversations, implement conversation reset, warn users

## Success Metrics

- All 7 constitution principles satisfied ✅
- 3 user stories independently testable
- <5s response time for 90% of queries
- Zero cross-user data leakage in testing
- Agent correctly interprets 90%+ of standard commands
- Conversation persistence across restarts verified

## Next Steps

1. ✅ Complete Phase 0: Research OpenAI Agents SDK and MCP SDK patterns
2. ✅ Complete Phase 1: Design data models and API contracts
3. Run `/sp.tasks` to generate implementation tasks
4. Execute tasks by user story priority (P1 → P2 → P3)
5. Validate end-to-end flow with hackathon reviewers
