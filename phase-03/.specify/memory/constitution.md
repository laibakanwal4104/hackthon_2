# AI-Powered Todo Chatbot Constitution

<!--
Sync Impact Report:
Version: 1.0.0 (Initial Ratification)
Modified Principles: N/A (initial version)
Added Sections: All sections (initial creation)
Removed Sections: None

Templates Status:
✅ plan-template.md - Constitution Check section aligns with principles
✅ spec-template.md - User scenarios and requirements structure compatible
✅ tasks-template.md - Task organization supports agent-first architecture
✅ Command files - Generic guidance maintained

Follow-up TODOs: None
-->

## Core Principles

### I. Agent-First Architecture

All AI functionality MUST be implemented using the OpenAI Agents SDK. The agent is the central orchestrator that:
- Receives natural language input from users
- Determines appropriate actions via reasoning
- Invokes MCP tools to execute operations
- Returns responses to users

**Rationale**: Agent-first design ensures consistent AI behavior, proper tool orchestration, and maintainable separation of concerns. Direct implementation of AI logic outside the agent framework leads to fragmented, untestable code.

### II. MCP Tool Isolation

All task operations (create, read, update, delete, list) MUST be executed exclusively through MCP (Model Context Protocol) tools. MCP tools MUST be:
- Stateless: No internal state between invocations
- Schema-defined: Input/output contracts explicitly declared
- Single-purpose: Each tool performs one clear operation
- Database-aware: Tools are the ONLY layer that accesses the database

**Rationale**: MCP tool isolation creates a clean boundary between AI reasoning and data operations, enabling independent testing, tool reusability, and clear audit trails.

### III. Database Access Boundaries (NON-NEGOTIABLE)

Agents MUST NOT access the database directly. All database operations MUST flow through MCP tools. This boundary is absolute and non-negotiable.

**Architecture Flow**:
```
UI → FastAPI Endpoint → Agent → MCP Tools → Database
                          ↓
                    (reasoning only)
```

**Rationale**: Direct database access by agents creates untraceable operations, bypasses validation, and violates the stateless principle. The MCP layer provides auditing, validation, and consistent error handling.

### IV. Stateless Chat Execution

The FastAPI chat endpoint MUST be stateless. Each request MUST:
- Load conversation context from the database
- Reconstruct agent state from persisted messages
- Execute agent reasoning with current context
- Persist new messages and state changes
- Return response without maintaining session state

**Rationale**: Stateless execution enables horizontal scaling, simplifies deployment, eliminates memory leaks, and ensures conversation consistency across restarts.

### V. Conversation Persistence & Traceability

All AI interactions MUST be persisted in Neon PostgreSQL:
- Conversations: User sessions with metadata
- Messages: User inputs and agent responses with timestamps
- Tool Invocations: Which MCP tools were called, with what parameters
- Results: Tool execution outcomes

**Rationale**: Persistence enables conversation resumption, debugging, audit trails, and analytics. Traceability is essential for understanding agent behavior and troubleshooting issues.

### VI. Security & User Isolation

User isolation from Phase-II MUST be maintained:
- Each user's todos are isolated by user_id
- Authentication required for all endpoints
- MCP tools MUST enforce user_id filtering
- No cross-user data leakage permitted

**Rationale**: Security and privacy are non-negotiable. User isolation prevents unauthorized access and ensures compliance with data protection requirements.

### VII. Natural Language Interface

Users MUST interact with the system exclusively through natural language. The agent MUST:
- Parse user intent from conversational input
- Handle ambiguous requests by asking clarifying questions
- Provide human-readable responses
- Support common todo operations (create, list, update, delete, mark complete)

**Rationale**: Natural language interface is the core value proposition. Users should not need to learn commands or syntax—the agent adapts to their communication style.

## Technology Constraints

**Language**: Python 3.11+
**AI Framework**: OpenAI Agents SDK (official)
**Tool Protocol**: MCP SDK (official Model Context Protocol implementation)
**API Framework**: FastAPI (stateless endpoints)
**Database**: Neon PostgreSQL (managed, serverless)
**Authentication**: JWT-based (Phase-II implementation)
**Deployment**: Stateless containers (horizontal scaling ready)

**Prohibited**:
- Direct database access from agent code
- Stateful session management in API layer
- Hardcoded credentials or API keys
- Manual SQL queries outside MCP tools
- Synchronous blocking operations in endpoints

## Development Workflow

### Agent Development
1. Define tool requirements (what operations needed)
2. Implement MCP tools with schemas
3. Test tools independently (unit tests)
4. Integrate tools with agent
5. Test agent reasoning with tools (integration tests)
6. Validate end-to-end user scenarios

### MCP Tool Standards
- Each tool MUST have a JSON schema defining inputs/outputs
- Tools MUST validate inputs and return structured errors
- Tools MUST log all operations for audit trails
- Tools MUST be independently testable without agent
- Tools MUST handle database errors gracefully

### Testing Requirements
- **Unit Tests**: Each MCP tool tested in isolation
- **Integration Tests**: Agent + tools tested together
- **Contract Tests**: Tool schemas validated against actual behavior
- **End-to-End Tests**: Full user scenarios via API

### Code Review Gates
- No direct database imports in agent code
- All MCP tools have schemas
- Stateless endpoint verification
- User isolation checks in tools
- Error handling coverage

## Observability & Operations

### Logging Requirements
- All agent reasoning steps logged (debug level)
- All MCP tool invocations logged (info level)
- All errors logged with context (error level)
- User actions logged for audit (info level)

### Metrics
- Agent response latency (p50, p95, p99)
- MCP tool execution time per tool
- Database query performance
- Conversation length distribution
- Error rates by type

### Monitoring
- Agent availability (health checks)
- Database connection pool status
- API endpoint response times
- Failed tool invocations
- Authentication failures

## Governance

This constitution supersedes all other development practices and guidelines. All code, architecture decisions, and implementations MUST comply with these principles.

### Amendment Process
1. Proposed changes documented with rationale
2. Impact analysis on existing code and architecture
3. Team review and approval required
4. Version bump according to semantic versioning:
   - **MAJOR**: Backward-incompatible principle changes
   - **MINOR**: New principles or significant expansions
   - **PATCH**: Clarifications, wording improvements
5. Migration plan for existing code if needed
6. Update all dependent templates and documentation

### Compliance
- All pull requests MUST verify constitution compliance
- Architecture reviews MUST reference relevant principles
- Complexity violations MUST be explicitly justified in plan.md
- Security principles are non-negotiable (no exceptions)

### Runtime Guidance
For detailed development instructions, see `CLAUDE.md` in the repository root. That file provides agent-specific execution guidance and workflow details.

**Version**: 1.0.0 | **Ratified**: 2026-02-07 | **Last Amended**: 2026-02-07
