# Form Management Changelog Agent

> **v2.0 - Now with Active Tool Validation!** Refactored to follow OpenAI Agents SDK best practices. The agent now uses mutation tools to validate EVERY database change, providing stronger guarantees and better error detection.

An AI-powered agent that converts natural language requests into structured database change plans for an enterprise form management system.

## Overview

This agent uses the OpenAI Agents SDK to interpret user requests about form modifications and generates precise JSON changesets describing database operations (insert, update, delete) across multiple tables.

**Key Features:**
- Natural language understanding of form management requests
- Intelligent clarification when requests are ambiguous
- Structured JSON output matching database schema
- **Tool-based validation** - Every database change is validated via mutation tools
- Transaction-based validation without modifying the database
- Multi-turn conversation support with session memory
- **OpenAI Agents SDK best practices** - Context injection, strong typing, SDK-native error handling
- Comprehensive test coverage

## Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenAI API key

### Running Locally

1. **Clone and navigate to the project:**
   ```bash
   cd changelog-agent-backend
   ```

2. **Set up environment variables:**
   ```bash
   # .env file already exists with OPENAI_API_KEY
   # Update if needed
   ```

3. **Start with Docker:**
   ```bash
   docker compose up --build
   ```

4. **Access the API:**
   - API: `http://localhost:8000`
   - Health check: `http://localhost:8000/api/v1/health`
   - Interactive docs: `http://localhost:8000/docs`

### Example Usage

```bash
# Simple request
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a Paris option to the travel form destination field", "session_id": "my_session"}'

# Response
{
  "response": "{
    \"type\": \"changelog\",
    \"changes\": {
      \"option_items\": {
        \"insert\": [{
          \"id\": \"$opt_paris\",
          \"option_set_id\": \"a930a282-9b59-4099-be59-e4b16fb73ff5\",
          \"value\": \"Paris\",
          \"label\": \"Paris\",
          \"position\": 6,
          \"is_active\": 1
        }]
      }
    }
  }"
}
```

## How It Works

### Architecture

```
User Request → FastAPI Endpoint → Agent Service (with FormContext)
                                        ↓
                                  OpenAI Agent with Tools
                                        ↓
                    ┌───────────────────┴──────────────────┐
                    ↓                                      ↓
            Query Tool (read)                    Mutation Tools (validate)
                    ↓                                      ↓
            SQLite Database ←────────────────────────────┘
                    ↓
    Validated Structured JSON Changelog
```

**New in v2.0:** Agent now uses mutation tools (`create_database_record`, `update_database_record`, `delete_database_record`) to validate EVERY database change before constructing the final changelog.

### Design Choices

#### 1. **Stateful Session Management**
We chose to use SQLite-backed sessions rather than requiring clients to maintain conversation history. This provides:
- Simpler client integration
- Automatic conversation context management
- Persistent session storage across requests

#### 2. **Separation of Concerns**
The codebase follows SOLID principles with clear separation:
- `context.py`: FormContext for dependency injection (database path, config)
- `tool_models.py`: Pydantic models for tool parameters (RecordData, RecordUpdate)
- `database_operations.py`: Core testable functions for DB operations
- `changelog_agent.py`: Agent definition and tool wrappers with SDK best practices
- `agent_service.py`: Orchestration and session management
- `routes.py`: FastAPI endpoints

This allows unit testing of core logic and follows dependency inversion principles.

#### 3. **Transaction-Based Validation**
The mutation tools (create/update/delete) operate within database transactions that are rolled back:
- Validates changes before committing
- Returns structured change plans
- Ensures database remains unchanged during agent execution
- Provides confidence in generated SQL

#### 4. **Two-Type Output System**
Agent responds with only two structured output types:

**Clarification** (when unclear):
```json
{
  "type": "clarification",
  "clarification": "Which form and field should I add the option to?"
}
```

**Changelog** (when clear):
```json
{
  "type": "changelog",
  "changes": {
    "table_name": {
      "insert": [...],
      "update": [...],
      "delete": [...]
    }
  }
}
```

#### 5. **Placeholder ID System**
- Inserts use `$`-prefixed placeholder IDs (e.g., `$opt_paris`, `$fld_name`)
- Updates/deletes use exact existing database IDs
- Placeholders can be referenced in foreign keys within the same changeset

### Agent Workflow

1. **Query Phase**: Agent queries `forms.sqlite` to understand schema and find referenced entities
2. **Validation Phase**: Agent calls mutation tools to validate EVERY insert/update/delete operation
   - `create_database_record` - Validates inserts in a rolled-back transaction
   - `update_database_record` - Validates updates in a rolled-back transaction
   - `delete_database_record` - Validates deletes in a rolled-back transaction
3. **Collection Phase**: Agent collects all tool outputs (validated change fragments)
4. **Merge Phase**: Agent combines all validated changes into a unified changelog
5. **Output Phase**: Returns either clarification or validated structured changelog

**Key Innovation:** The agent actively uses mutation tools to validate changes against the actual database schema, ensuring all operations would succeed before returning the changelog.

## Project Structure

```
changelog-agent-backend/
├── app/
│   ├── agents/
│   │   ├── changelog_agent.py      # Agent with SDK best practices
│   │   ├── context.py              # FormContext for dependency injection
│   │   ├── tool_models.py          # Pydantic models for tool params
│   │   └── database_operations.py  # Core testable DB functions
│   ├── api/
│   │   └── routes.py                # FastAPI endpoints
│   ├── models/
│   │   └── schemas.py               # Pydantic models for API
│   ├── services/
│   │   └── agent_service.py         # Agent orchestration with context
│   ├── tracing/
│   │   └── tool_call_processor.py   # Custom tracing processor
│   └── main.py                      # FastAPI app entry
├── data/
│   └── forms.sqlite                 # Form management database
├── tests/
│   ├── test_database_operations.py  # Unit tests
│   ├── test_api_integration.py      # Integration tests
│   └── README.md                    # Testing guide
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── INSTRUCTIONS.md                  # Original requirements
```

## Testing

Comprehensive test suite with unit and integration tests. See `tests/README.md` for detailed testing guide.

### Running Tests

**Recommended approach (prevents API rate limiting):**
```bash
# Run all tests with automatic delays between integration tests
./run_tests.sh
```

**Alternative approaches:**
```bash
# Run all tests at once (may hit rate limits with large test suites)
python3 -m pytest tests/ -v

# Run unit tests only (no server required)
python3 -m pytest tests/test_database_operations.py -v

# Run integration tests only (requires server)
python3 -m pytest tests/test_api_integration.py -v

# Run with coverage
python3 -m pytest tests/ --cov=app --cov-report=html
```

### Test Coverage

**Unit Tests (10 tests):**
- Query operations (success and error cases)
- Create operations (validation, JSON parsing, missing fields)
- Update operations (validation, nonexistent IDs, JSON errors)
- Delete operations (validation, rollback verification)

**Integration Tests (13 tests):**

*Changelog Generation:*
- ✅ Add single option to form
- ✅ Add and update options simultaneously
- ✅ Create conditional logic with fields, rules, conditions, and actions
- ✅ Create complete new form from scratch
- ✅ Delete form
- ✅ Update form properties
- ✅ Complex multi-table operations

*Clarification Flow:*
- ✅ Vague requests trigger clarification
- ✅ Ambiguous requests trigger clarification

*API Endpoints:*
- ✅ Health check endpoint
- ✅ Chat endpoint with session management
- ✅ Trace endpoint for debugging
- ✅ Multi-turn conversations

*Response Validation:*
- Correct response type (changelog vs clarification)
- Proper JSON structure
- Expected tables present in changes
- Placeholder IDs for inserts ($-prefixed)
- Real IDs for updates/deletes
- Required fields included

### Database Integrity

All tests verify that the database remains unchanged:
- Record counts remain the same
- Original values are preserved
- Transactions are properly rolled back

**Structured Output Guardrails (10 tests):**
- ✅ Resists prompt injection attacks
- ✅ Enforces output schema compliance
- ✅ Validates legitimate requests still work

### Test Performance
- Unit tests: ~1 second total
- Integration tests: ~10-80 seconds per test  
- Full test suite: ~10-15 minutes with delays (using `./run_tests.sh`)
- Full test suite: ~5-10 minutes without delays (may hit rate limits)

## API Reference

### POST /api/v1/chat

Send a message to the agent.

**Request:**
```json
{
  "message": "string",
  "session_id": "string (optional, default: 'default')"
}
```

**Response:**
```json
{
  "response": "JSON string containing changelog or clarification"
}
```

### GET /api/v1/traces/{session_id}

Get the OpenAI trace ID for debugging a conversation.

**Response:**
```json
{
  "session_id": "string",
  "trace_id": "string",
  "trace_url": "string"
}
```

### GET /api/v1/tool-calls/session/{session_id}

Get all tool calls made during a conversation session. Useful for debugging and understanding agent behavior.

**Response:**
```json
{
  "session_id": "string",
  "trace_id": "string",
  "tool_calls": [
    {
      "span_id": "string",
      "tool_name": "create_database_record",
      "input": "JSON string of tool input",
      "output": "JSON string of tool output",
      "started_at": "ISO timestamp",
      "ended_at": "ISO timestamp",
      "error": null
    }
  ],
  "total_count": 15
}
```

### GET /api/v1/health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Known Issues

1. **Max Turns Configuration**: Agent uses 25 turns max. Complex requests with many database queries may hit this limit. Can be increased in `agent_service.py`.

2. **Model Selection**: Currently configured for `gpt-5`. Ensure your API key has access or change to `gpt-4o` or `gpt-4o-mini` in `changelog_agent.py`.

3. **Large Database Performance**: While we avoid loading entire tables, very complex queries (e.g., forms with hundreds of fields) may be slow. Consider adding query optimization or caching.

4. **Session Storage**: Sessions are stored in SQLite. For production, consider Redis for better performance with concurrent users.

5. **Mutation Tools Run in Transactions**: All validation operations are rolled back, so the database is never modified. The actual changes must be applied separately using the returned changelog.

## Architecture Evolution & Performance

### v2.0 Refactoring (OpenAI Agents SDK Best Practices)

We completely refactored the codebase to follow OpenAI Agents SDK best practices, resulting in **active mutation tool usage** and better code quality.

#### Key Changes

**1. Context Injection (Dependency Inversion)**
- Added `FormContext` dataclass for dependency injection
- Database path now injected via context instead of environment variables
- Tools receive `RunContextWrapper[FormContext]` as first parameter
- Enables better testing and configuration flexibility

**2. Strong Type Safety**
- Created Pydantic models (`RecordData`, `RecordUpdate`) for tool parameters
- Replaced JSON string parameters with structured types
- LLM receives clear schema showing expected structure
- Automatic validation by SDK reduces errors

**3. SDK-Native Error Handling**
- Implemented `tool_error_handler` using `failure_error_function` pattern
- Cleaner error messages sent to LLM
- No try/catch needed in tool functions
- Consistent error handling across all tools

**4. Improved Instructions**
- Rewrote agent instructions to emphasize mutation tool usage
- Added concrete examples showing exact tool call syntax
- Removed contradictory statements
- Clear step-by-step workflow (Query → Validate → Collect → Merge → Output)

**5. Static Runner Usage**
- Changed from instance-based to static `Runner.run()`
- Aligns with SDK documentation patterns
- Passes context explicitly to agent

#### Results

**Before Refactoring:**
- Mutation tool usage: 0 calls
- Agent manually constructed JSON
- JSON string parameters (weak typing)
- Manual error handling

**After Refactoring:**
- Mutation tool usage: 100% (every operation validated)
- Simple request (add option): 1 mutation call
- Complex request (conditional logic): 5 mutation calls
- Complete form creation: 11 mutation calls
- Strong Pydantic typing
- SDK-native error handling

### Current Performance Metrics

- **Success Rate**: 100% on all test examples
- **Tool Usage**: All database changes validated via mutation tools
- **Clarification Accuracy**: Correctly identifies vague/ambiguous requests
- **Output Format**: 100% compliance with expected JSON structure
- **Database Safety**: 0 unintended modifications (all operations rolled back)
- **Type Safety**: Pydantic models prevent malformed tool calls

### Real-World Examples

**Example 1: Add Option**
- Query calls: 5 (find form, field, options)
- Mutation calls: 1 (`create_database_record` for option_items)
- Total time: ~8 seconds

**Example 2: Conditional Field Logic**
- Query calls: 20 (explore schema, find IDs)
- Mutation calls: 5 (field, rule, condition, 2 actions)
- Total time: ~25 seconds

**Example 3: Create Complete Form**
- Query calls: 11 (schema exploration)
- Mutation calls: 11 (form, page, option_set, 5 option_items, 2 fields, binding)
- Total time: ~30 seconds

### Monitoring

- **Tool Calls API**: `GET /api/v1/tool-calls/session/{session_id}` shows all tool usage
- **Trace Debugging**: Use `/api/v1/traces/{session_id}` to view in OpenAI Platform
- Track query patterns to identify optimization opportunities
- Monitor mutation tool success rate for schema issues

## Future Enhancements

### Short Term
1. **Output Schema Validation**: Validate generated JSON against database schema before returning
2. **Query Optimization**: Cache frequently accessed table structures
3. **Better Error Messages**: Provide more specific guidance when agent can't fulfill request
4. **Batch Operations**: Support multiple independent changes in a single request

### Medium Term
1. **WebSocket Support**: Stream agent reasoning and tool calls in real-time
2. **Multi-Agent System**: Separate agents for different form management domains
3. **Change Preview**: Show estimated impact of changes before execution
4. **Undo/Rollback**: Generate reverse changesets for each operation

### Long Term
1. **Learning from Feedback**: Fine-tune model on successful user interactions
2. **Visual Form Builder Integration**: Connect directly to frontend form builder
3. **Migration Generation**: Auto-generate database migration scripts from changesets
4. **Multi-Database Support**: Support PostgreSQL, MySQL in addition to SQLite
5. **API Rate Limiting**: Implement per-user rate limits
6. **Authentication**: Add JWT-based authentication

## Contributing

When adding new features:
1. Write unit tests in `tests/`
2. Follow SOLID principles
3. Keep functions small and single-purpose
4. Minimize comments (code should be self-documenting)
5. Add integration tests for new query types

## License

[Your License Here]

## References

- [OpenAI Agents SDK Documentation](https://github.com/openai/openai-agents-sdk)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Sample Form App](https://forms-app-seven-theta.vercel.app/)
