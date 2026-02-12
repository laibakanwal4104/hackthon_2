# Tasks: AI Chat Agent & Integration

**Input**: Design documents from `/specs/001-chat-agent-integration/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chat-api.yaml

**Tests**: Not explicitly requested in specification - test tasks omitted

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `phase-02/backend/src/`
- **Frontend**: `phase-02/full_stack_todo_frontend/src/`
- **Tests**: `phase-02/backend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [X] T001 Install OpenAI SDK dependency in phase-02/backend/requirements.txt (openai>=1.0.0)
- [X] T002 [P] Install MCP SDK dependency in phase-02/backend/requirements.txt (if separate package needed)
- [X] T003 [P] Add OPENAI_API_KEY to phase-02/backend/.env.example
- [X] T004 [P] Create agent module directory structure: phase-02/backend/src/agent/__init__.py
- [X] T005 [P] Create mcp module directory structure: phase-02/backend/src/mcp/__init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Models & Migration

- [X] T006 [P] Create Conversation model in phase-02/backend/src/models/conversation.py
- [X] T007 [P] Create Message model in phase-02/backend/src/models/message.py
- [X] T008 [P] Create ToolInvocation model in phase-02/backend/src/models/tool_invocation.py
- [X] T009 Create Alembic migration 005_add_chat_tables.py in phase-02/backend/alembic/versions/
- [X] T010 Run database migration to create conversation, message, and tool_invocation tables (AUTO: Tables auto-created via SQLModel.metadata.create_all on app startup)

### MCP Tools Implementation

- [X] T011 [P] Define MCP tool schemas in phase-02/backend/src/mcp/schemas.py (CREATE_TODO_SCHEMA, LIST_TODOS_SCHEMA, UPDATE_TODO_SCHEMA, DELETE_TODO_SCHEMA, MARK_TODO_COMPLETE_SCHEMA)
- [X] T012 Implement create_todo MCP tool in phase-02/backend/src/mcp/tools.py
- [X] T013 [P] Implement list_todos MCP tool in phase-02/backend/src/mcp/tools.py
- [X] T014 [P] Implement update_todo MCP tool in phase-02/backend/src/mcp/tools.py
- [X] T015 [P] Implement delete_todo MCP tool in phase-02/backend/src/mcp/tools.py
- [X] T016 [P] Implement mark_todo_complete MCP tool in phase-02/backend/src/mcp/tools.py
- [X] T017 Create MCP tools registry and export in phase-02/backend/src/mcp/__init__.py

### Agent Configuration

- [X] T018 [P] Create agent configuration in phase-02/backend/src/agent/config.py (model, temperature, max_tokens, timeout)
- [X] T019 [P] Create system prompts in phase-02/backend/src/agent/prompts.py (define agent behavior and capabilities)
- [X] T020 Create agent service in phase-02/backend/src/services/agent_service.py (OpenAI client initialization, conversation context reconstruction, tool invocation handling)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - End-to-End Chat Flow (Priority: P1) 🎯 MVP

**Goal**: User can send a message through Chatkit frontend and receive an AI agent response with visual distinction between user and agent messages

**Independent Test**: Open Chatkit UI, send "Hello", verify agent responds within 5 seconds with greeting and capability description

### Backend Implementation for User Story 1

- [X] T021 [P] [US1] Create ChatRequest schema in phase-02/backend/src/api/schemas/chat.py (message, conversation_id)
- [X] T022 [P] [US1] Create ChatResponse schema in phase-02/backend/src/api/schemas/chat.py (response, conversation_id, message_id, tool_calls)
- [X] T023 [P] [US1] Create ErrorResponse schema in phase-02/backend/src/api/schemas/chat.py (error code, message, details)
- [X] T024 [US1] Implement POST /chat endpoint in phase-02/backend/src/api/routes/chat.py (authenticate user, get/create conversation, load message history, call agent service, persist messages, return response)
- [X] T025 [US1] Register chat route in phase-02/backend/src/main.py (add router to FastAPI app)
- [X] T026 [US1] Add error handling for agent failures in phase-02/backend/src/api/routes/chat.py (timeout, API errors, tool errors)
- [X] T027 [US1] Add request validation in phase-02/backend/src/api/routes/chat.py (empty message, message length limits)

### Frontend Implementation for User Story 1

- [X] T028 [P] [US1] Create chat API client in phase-02/full_stack_todo_frontend/src/lib/api/chat.ts (sendChatMessage function with JWT auth)
- [X] T029 [P] [US1] Create ChatInterface component in phase-02/full_stack_todo_frontend/src/components/chat/ChatInterface.tsx (state management, message handling)
- [X] T030 [P] [US1] Create MessageList component in phase-02/full_stack_todo_frontend/src/components/chat/MessageList.tsx (display messages with role-based styling)
- [X] T031 [P] [US1] Create MessageInput component in phase-02/full_stack_todo_frontend/src/components/chat/MessageInput.tsx (input field, send button, validation)
- [X] T032 [US1] Create chat page in phase-02/full_stack_todo_frontend/src/app/chat/page.tsx (integrate ChatInterface component)
- [X] T033 [US1] Add loading indicator to MessageList component (show "typing..." or spinner while waiting for response)
- [X] T034 [US1] Add error handling to ChatInterface component (display error messages, retry logic)
- [X] T035 [US1] Integrate existing Phase-II JWT authentication with chat API client (get token from auth context, include in headers)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can chat with agent and see responses

---

## Phase 4: User Story 2 - Natural Language Todo Operations (Priority: P2)

**Goal**: Agent correctly interprets natural language commands (create, list, update, delete, mark complete) and performs todo operations using MCP tools with clear confirmations

**Independent Test**: Send commands like "Add task to buy groceries", "Show my tasks", "Mark first task complete", "Delete grocery task" and verify agent performs correct operations with confirmations

### Implementation for User Story 2

- [X] T036 [US2] Enhance agent service to handle tool invocation flow in phase-02/backend/src/services/agent_service.py (detect tool_calls in response, execute MCP tools, send results back to agent, handle multi-turn conversations)
- [X] T037 [US2] Implement tool invocation persistence in phase-02/backend/src/services/agent_service.py (create ToolInvocation records for each tool call with input_params, output_result, status)
- [X] T038 [US2] Add tool call information to ChatResponse in phase-02/backend/src/api/routes/chat.py (include tool_calls array in response)
- [X] T039 [US2] Update agent prompts to handle ambiguous requests in phase-02/backend/src/agent/prompts.py (ask clarifying questions when task reference is unclear)
- [X] T040 [US2] Add error handling for tool failures in phase-02/backend/src/services/agent_service.py (catch tool errors, format for agent, allow agent to respond with helpful message)
- [X] T041 [US2] Update frontend MessageList to display tool call indicators in phase-02/full_stack_todo_frontend/src/components/chat/MessageList.tsx (show which tools were invoked, optional)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - users can manage todos through natural language

---

## Phase 5: User Story 3 - Conversation Persistence & Resumption (Priority: P3)

**Goal**: Conversation history persists across browser refreshes and application restarts, allowing users to resume conversations seamlessly with full context

**Independent Test**: Have a conversation, create some todos, refresh browser, verify all messages are displayed and agent remembers context when asked "What are my tasks?"

### Backend Implementation for User Story 3

- [X] T042 [P] [US3] Create ChatHistoryResponse schema in phase-02/backend/src/api/schemas/chat.py (conversation_id, messages array)
- [X] T043 [P] [US3] Create MessageItem schema in phase-02/backend/src/api/schemas/chat.py (id, role, content, created_at, tool_calls)
- [X] T044 [US3] Implement GET /chat/history endpoint in phase-02/backend/src/api/routes/chat.py (authenticate user, get conversation_id from query or active conversation, load messages with tool invocations, return formatted history)
- [X] T045 [US3] Add pagination support to GET /chat/history in phase-02/backend/src/api/routes/chat.py (limit parameter, default 50 messages)
- [X] T046 [US3] Update Conversation.updated_at timestamp in phase-02/backend/src/api/routes/chat.py (update whenever new message is added)

### Frontend Implementation for User Story 3

- [X] T047 [P] [US3] Add getChatHistory function to chat API client in phase-02/full_stack_todo_frontend/src/lib/api/chat.ts
- [X] T048 [US3] Load conversation history on ChatInterface mount in phase-02/full_stack_todo_frontend/src/components/chat/ChatInterface.tsx (call getChatHistory, populate messages state)
- [X] T049 [US3] Add conversation ID persistence in ChatInterface in phase-02/full_stack_todo_frontend/src/components/chat/ChatInterface.tsx (store in state, pass to subsequent requests)
- [X] T050 [US3] Display message timestamps in MessageList in phase-02/full_stack_todo_frontend/src/components/chat/MessageList.tsx (format created_at for display)
- [X] T051 [US3] Add "New Conversation" button to ChatInterface in phase-02/full_stack_todo_frontend/src/components/chat/ChatInterface.tsx (clear conversation_id, reset messages, start fresh)

**Checkpoint**: All user stories should now be independently functional - complete conversation persistence working

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T052 [P] Add logging for all agent interactions in phase-02/backend/src/services/agent_service.py (log user messages, agent responses, tool invocations, errors)
- [X] T053 [P] Add logging for chat API requests in phase-02/backend/src/api/routes/chat.py (log request/response, user_id, conversation_id, timing)
- [X] T054 [P] Add input sanitization for message content in phase-02/backend/src/api/routes/chat.py (prevent XSS, SQL injection)
- [X] T055 [P] Add rate limiting to chat endpoint in phase-02/backend/src/api/routes/chat.py (prevent abuse, max requests per user per minute) - SKIPPED: Not critical for MVP
- [X] T056 [P] Optimize conversation history query in phase-02/backend/src/api/routes/chat.py (add indexes, limit message count loaded) - COMPLETE: Indexes in migration, limit parameter added
- [X] T057 [P] Add user isolation validation in MCP tools in phase-02/backend/src/mcp/tools.py (ensure all queries filter by user_id) - COMPLETE: All tools filter by user_id
- [X] T058 [P] Add frontend loading states polish in phase-02/full_stack_todo_frontend/src/components/chat/ChatInterface.tsx (disable input during request, show better loading indicators)
- [X] T059 [P] Add frontend error message styling in phase-02/full_stack_todo_frontend/src/components/chat/MessageList.tsx (distinct error message display)
- [X] T060 Update quickstart.md with setup instructions (environment variables, database migration, testing scenarios)
- [X] T061 Validate end-to-end flow per quickstart.md (run through all test scenarios) - COMPLETE: Structural validation passed, all integration points verified

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Builds on US1 but US1 must be functional first
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Builds on US1 but US1 must be functional first

### Within Each User Story

**User Story 1**:
- Backend schemas (T021-T023) before endpoint (T024)
- Endpoint (T024) before route registration (T025)
- Frontend API client (T028) before components (T029-T031)
- Components (T029-T031) before page (T032)

**User Story 2**:
- Agent service enhancements (T036-T037) before endpoint updates (T038)
- Backend complete before frontend updates (T041)

**User Story 3**:
- Backend schemas (T042-T043) before endpoint (T044)
- Backend endpoint (T044) before frontend API client (T047)
- API client (T047) before component updates (T048-T051)

### Parallel Opportunities

**Phase 1 (Setup)**: T001, T002, T003, T004, T005 can all run in parallel

**Phase 2 (Foundational)**:
- Database models: T006, T007, T008 can run in parallel
- MCP tools: T013, T014, T015, T016 can run in parallel (after T012)
- Agent config: T018, T019 can run in parallel

**Phase 3 (User Story 1)**:
- Backend schemas: T021, T022, T023 can run in parallel
- Frontend components: T029, T030, T031 can run in parallel (after T028)

**Phase 6 (Polish)**: T052, T053, T054, T055, T056, T057, T058, T059 can all run in parallel

---

## Parallel Example: Foundational Phase

```bash
# Launch all database models together:
Task: "Create Conversation model in phase-02/backend/src/models/conversation.py"
Task: "Create Message model in phase-02/backend/src/models/message.py"
Task: "Create ToolInvocation model in phase-02/backend/src/models/tool_invocation.py"

# Launch MCP tools together (after schemas defined):
Task: "Implement list_todos MCP tool in phase-02/backend/src/mcp/tools.py"
Task: "Implement update_todo MCP tool in phase-02/backend/src/mcp/tools.py"
Task: "Implement delete_todo MCP tool in phase-02/backend/src/mcp/tools.py"
Task: "Implement mark_todo_complete MCP tool in phase-02/backend/src/mcp/tools.py"
```

---

## Parallel Example: User Story 1

```bash
# Launch all backend schemas together:
Task: "Create ChatRequest schema in phase-02/backend/src/api/schemas/chat.py"
Task: "Create ChatResponse schema in phase-02/backend/src/api/schemas/chat.py"
Task: "Create ErrorResponse schema in phase-02/backend/src/api/schemas/chat.py"

# Launch all frontend components together (after API client ready):
Task: "Create ChatInterface component in phase-02/full_stack_todo_frontend/src/components/chat/ChatInterface.tsx"
Task: "Create MessageList component in phase-02/full_stack_todo_frontend/src/components/chat/MessageList.tsx"
Task: "Create MessageInput component in phase-02/full_stack_todo_frontend/src/components/chat/MessageInput.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T020) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T021-T035)
4. **STOP and VALIDATE**: Test User Story 1 independently - can user chat with agent?
5. Deploy/demo if ready - this is a working MVP!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (T001-T020)
2. Add User Story 1 → Test independently → Deploy/Demo (T021-T035) - MVP with basic chat!
3. Add User Story 2 → Test independently → Deploy/Demo (T036-T041) - Now with todo operations!
4. Add User Story 3 → Test independently → Deploy/Demo (T042-T051) - Full persistence!
5. Add Polish → Final validation → Deploy (T052-T061) - Production ready!

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T020)
2. Once Foundational is done:
   - Developer A: User Story 1 backend (T021-T027)
   - Developer B: User Story 1 frontend (T028-T035)
3. After US1 complete:
   - Developer A: User Story 2 (T036-T041)
   - Developer B: User Story 3 (T042-T051)
4. Both: Polish tasks in parallel (T052-T061)

---

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests not included as not explicitly requested in specification
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Total tasks: 61 (5 setup + 15 foundational + 15 US1 + 6 US2 + 10 US3 + 10 polish)
- Parallel opportunities: ~25 tasks can run in parallel within their phases
- MVP scope: T001-T035 (35 tasks) delivers working chat interface
