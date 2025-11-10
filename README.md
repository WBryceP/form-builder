# Form Management Changelog Agent

An AI-powered system that converts natural language requests into structured database operations for an enterprise form management platform.

## Overview

This project consists of two main components:
- **Backend**: OpenAI Agents SDK-based API that interprets form management requests
- **Frontend**: React + TypeScript chat interface for interacting with the agent

**Live Demo**: [https://forms-app-seven-theta.vercel.app/](https://forms-app-seven-theta.vercel.app/)

## Quick Start

### Prerequisites
- Docker and Docker Compose (for backend)
- Node.js 18+ (for frontend)
- OpenAI API key

### 1. Start Backend

```bash
cd changelog-agent-backend
docker compose up --build
```

Backend runs at `http://localhost:8000`

### 2. Start Frontend

```bash
cd changelog-agent-frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend                            │
│  - Multi-conversation UI                                     │
│  - Chat interface with tool call inspector                   │
│  - Real-time message streaming                               │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                            │
│  - Session management                                        │
│  - OpenAI Agents SDK integration                            │
│  - Tool call tracing                                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              OpenAI Agent with Tools                         │
│  - Query Tool (read database)                                │
│  - Mutation Tools (validate changes)                         │
│    • create_database_record                                  │
│    • update_database_record                                  │
│    • delete_database_record                                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   SQLite Database                            │
│  - forms.sqlite: Form management schema (11 tables)          │
│  - sessions.db: Conversation history                         │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
form-builder/
├── forms.sqlite                      # Main form management database
├── changelog-agent-backend/          # Python FastAPI backend
│   ├── app/
│   │   ├── agents/                   # Agent logic and tools
│   │   │   ├── changelog_agent.py    # Main agent definition
│   │   │   ├── database_operations.py # Core DB functions
│   │   │   ├── validators.py         # Phase 1 validation
│   │   │   ├── context.py            # Dependency injection
│   │   │   └── tool_models.py        # Pydantic models
│   │   ├── api/                      # REST endpoints
│   │   ├── models/                   # API schemas
│   │   ├── services/                 # Business logic
│   │   └── tracing/                  # Tool call tracking
│   ├── data/
│   │   ├── forms.sqlite              # Copied from root
│   │   └── sessions.db               # Session storage
│   ├── tests/                        # 30 comprehensive tests
│   ├── INSTRUCTIONS.md               # Original requirements
│   ├── PHASE1_IMPLEMENTATION.md      # Phase 1 security features
│   └── README.md                     # Backend documentation
│
└── changelog-agent-frontend/         # React TypeScript frontend
    ├── src/
    │   ├── components/               # React components
    │   ├── api/                      # Backend client
    │   └── types/                    # TypeScript definitions
    └── README.md                     # Frontend documentation
```

## Key Features

### Backend
- **Tool-Based Validation**: Every database change validated via mutation tools before returning changelog
- **Phase 1 Security**: Table name whitelist, foreign key enforcement, transaction rollback guarantees
- **Session Management**: SQLite-backed conversation history with multi-turn support
- **Structured Output**: Two-type system (changelog vs clarification)
- **Comprehensive Testing**: 30 tests covering unit, integration, validation, and security

### Frontend
- **Multi-Conversation UI**: Create, switch between, and delete conversations
- **Tool Call Inspector**: Expand to see exactly what the agent did
- **Real-Time Updates**: Optimistic UI with automatic refresh
- **TypeScript**: Fully typed API client and components

## Example Usage

### Add Option to Form

**Input:**
```
Add a Paris option to the travel form destination field
```

**Output (Changelog):**
```json
{
  "type": "changelog",
  "changes": {
    "option_items": {
      "insert": [{
        "id": "$opt_paris",
        "option_set_id": "a930a282-9b59-4099-be59-e4b16fb73ff5",
        "value": "Paris",
        "label": "Paris",
        "position": 6,
        "is_active": 1
      }]
    }
  }
}
```

### Create Conditional Logic

**Input:**
```
I want the employment-demo form to require university_name when employment_status is "Student"
```

**Output:** Structured changelog with:
- New `university_name` field (hidden by default)
- Logic rule with condition checking employment status
- Two actions: show field + mark as required

### Clarification Flow

**Input:**
```
Add an option to the form
```

**Output (Clarification):**
```json
{
  "type": "clarification",
  "clarification": "Which form and field should I add the option to?"
}
```

## Testing

### Backend Tests

```bash
cd changelog-agent-backend

# Run all tests with delays (prevents rate limiting)
./run_tests.sh

# Run specific test suite
python3 -m pytest tests/test_validators_phase1.py -v
```

**Test Coverage (30 tests):**
- 10 unit tests (database operations)
- 16 integration tests (API endpoints, changelogs, clarifications)
- 4 security tests (prompt injection, output validation)

### Frontend Development

```bash
cd changelog-agent-frontend

# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## API Reference

### Core Endpoints

- `POST /api/v1/conversations` - Create new conversation
- `GET /api/v1/conversations` - List all conversations
- `POST /api/v1/chat` - Send message to agent
- `GET /api/v1/traces/{session_id}` - Get trace for debugging
- `GET /api/v1/tool-calls/session/{session_id}` - View tool calls

See `changelog-agent-backend/README.md` for complete API documentation.

## Database Schema

The agent manages 11 tables in `forms.sqlite`:
- `forms` - Form definitions
- `form_pages` - Multi-page form structure
- `form_fields` - Field definitions with types
- `field_types` - Available field types (text, select, date, etc.)
- `option_sets` - Dropdown/radio option groups
- `option_items` - Individual options
- `form_field_bindings` - Field-to-option set relationships
- `logic_rules` - Conditional behavior rules
- `logic_conditions` - When rules should trigger
- `logic_actions` - What rules should do
- `prefill_mappings` - Auto-populate field values

## Security Features (Phase 1)

**Implemented November 9, 2025**

1. **Table Name Whitelist**: SQL injection prevention via validated table names
2. **Foreign Key Enforcement**: `PRAGMA foreign_keys = ON` prevents orphaned records
3. **Transaction Rollback**: All validation operations rolled back automatically
4. **Explicit Error Messages**: Clear constraint violation reporting

See `changelog-agent-backend/PHASE1_IMPLEMENTATION.md` for details.

## Known Issues

1. **Max Turns**: Agent uses 25 turns. Complex requests may hit limit (configurable)
2. **Model Selection**: Configured for `gpt-5` - ensure API key has access
3. **Large Database Performance**: Complex queries with hundreds of fields may be slow
4. **Session Storage**: SQLite sessions - consider Redis for production scale

## Future Enhancements

### Short Term
- Output schema validation before returning changelog
- Query optimization and caching
- Batch operations support

### Medium Term
- WebSocket streaming for real-time updates
- Multi-agent system for different domains
- Change preview with estimated impact
- Undo/rollback changelog generation

### Long Term
- Fine-tune model on successful interactions
- Visual form builder integration
- Database migration script generation
- Multi-database support (PostgreSQL, MySQL)

## Development

### Backend Development

```bash
cd changelog-agent-backend

# Make changes to app/
# Run tests
python3 -m pytest tests/ -v

# Restart container
docker compose restart
```

### Frontend Development

```bash
cd changelog-agent-frontend

# Make changes to src/
# Hot reload automatically updates browser
```

### Code Style

- **SOLID Principles**: Single responsibility, dependency injection
- **One Class Per File**: Clear separation of concerns
- **Minimal Comments**: Self-documenting code with clear variable names
- **No Extra Features**: Only implement what's requested

## Contributing

When adding features:
1. Write tests first (TDD approach)
2. Follow existing code patterns
3. Update relevant README sections
4. Verify all tests pass before committing

## License

[Your License Here]

## References

- [Original Requirements](changelog-agent-backend/INSTRUCTIONS.md)
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-sdk)
- [Sample Form App](https://forms-app-seven-theta.vercel.app/)
