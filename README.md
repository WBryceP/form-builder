# Form Management Changelog Agent

An AI-powered system that converts natural language requests into structured database operations for an enterprise form management platform.

## Overview

This project consists of two main components:
- **Backend**: OpenAI Agents SDK-based API that interprets form management requests
- **Frontend**: React + TypeScript chat interface for interacting with the agent

How I approached the problem:
I wanted to ensure that the agent had as many guard rails in place as possible. I started by seeing what an agent was capable of doing on its own and slowly started to add tools. These tools allowed the agent to verify that its actions weren't going to have unintended actions to the database. This whole process involved a lot of experimentation such as choosing different models and testing different staged approaches.

Many decisions made were done so with the time constraint. If there was more time I would have allowed all tools to work within the same transaction and have more verification on db actions. However, I still wanted to address the dangers of giving the LLM access to the db. As such, transactions were used and checks are done on the db queries from the agent. There is also a strict output format for the agent.

I tracked performance through a few different means. The first was seeing which tools the agent used and when. Initially the agent did not even use the db mutation tools and instead relied on its own ability to create the JSON output. This was unintended behavior so the tools were tweaked. I also tested varrying difficulties of questions. Its important to note that tests were performed numerous times to ensure stability in responses. The number of tool calls and progression were checked in addition to the similarity of the answers.

For evaluating success, I tried a few difficult questions and tested them repeatedly to ensure that the answers were stable. I also checked if they made sense. With more time, I'd build an evaluation layer that takes that final JSON output and runs those operations against a copy of the db and checks if it worked, then have a smarter model evaluate the final form against the query.


## Quick Start

### Prerequisites
- Docker and Docker Compose (for backend)
- Node.js 18+ (for frontend)
- OpenAI API key

### 1. Setup Backend

**Create `.env` file** in `changelog-agent-backend/` directory:

```bash
cd changelog-agent-backend
cat > .env << EOF
OPENAI_API_KEY=your-openai-api-key-here
ENVIRONMENT=development
DATABASE_PATH=/app/data/forms.sqlite
PORT=8000
EOF
```

**Or manually create** `changelog-agent-backend/.env`:

```env
OPENAI_API_KEY=your-openai-api-key-here
ENVIRONMENT=development
DATABASE_PATH=/app/data/forms.sqlite
PORT=8000
```

**Start the backend:**

```bash
# Build and start Docker container
docker compose up --build

# Or run in detached mode
docker compose up -d --build

# View logs
docker compose logs -f

# Stop the backend
docker compose down
```

Backend runs at `http://localhost:8000`

Verify it's running:
```bash
curl http://localhost:8000/api/v1/health
# Should return: {"status":"healthy"}
```

### 2. Setup Frontend

```bash
cd changelog-agent-frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
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
│   │   │   ├── validators.py         # Validation functions
│   │   │   ├── context.py            # Dependency injection
│   │   │   └── tool_models.py        # Pydantic models
│   │   ├── api/                      # REST endpoints
│   │   ├── models/                   # API schemas
│   │   ├── services/                 # Business logic
│   │   └── tracing/                  # Tool call tracking
│   ├── data/
│   │   ├── forms.sqlite              # Copied from root
│   │   └── sessions.db               # Session storage
│   └── tests/                        # 30+ comprehensive tests
│
└── changelog-agent-frontend/         # React TypeScript frontend
    ├── src/
    │   ├── components/               # React components
    │   ├── api/                      # Backend client
    │   └── types/                    # TypeScript definitions
    ├── package.json
    └── vite.config.ts
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

# Run specific test suite
python3 -m pytest tests/test_validators.py -v

# Run all unit tests (no API calls)
python3 -m pytest tests/test_database_operations.py tests/test_validators.py tests/test_column_validation.py tests/test_query_guardrails.py -v

# Run all tests including integration tests (may hit rate limits)
python3 -m pytest tests/ -v

# Run with coverage report
python3 -m pytest tests/ --cov=app --cov-report=html
```

**Test Coverage (30+ tests):**
- 10 unit tests (database operations)
- 7 validation tests (security, constraints, SQL injection)
- 6 column validation tests
- 9 query guardrail tests
- 4 structured output guardrail tests (prompt injection resistance)

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
- `GET /api/v1/conversations/{session_id}/messages` - Get conversation messages
- `DELETE /api/v1/conversations/{session_id}` - Delete conversation
- `POST /api/v1/chat` - Send message to agent
- `GET /api/v1/traces/{session_id}` - Get trace for debugging
- `GET /api/v1/tool-calls/session/{session_id}` - View tool calls
- `GET /api/v1/health` - Health check

Visit `http://localhost:8000/docs` for interactive API documentation.

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

## Security Features

1. **Table Name Whitelist**: SQL injection prevention via validated table names
2. **Transaction Rollback**: All validation operations rolled back automatically
3. **Structured Output Validation**: Outputs will be consistent (either a clarification or the final result)

## Known Issues

1. **Max Turns**: Agent uses 25 turns. Complex requests may hit limit (configurable)
2. **Model Selection**: Configured for `gpt-5` - ensure API key has access

## Future Enhancements

### Short Term
- Query optimization and caching
- Batch operations support
- Multiple instances of an agent to reduce 500 errors

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

## Troubleshooting

### Backend Issues

**"Connection refused" or "Cannot connect to Docker daemon"**
```bash
# Ensure Docker is running
docker --version

# Restart Docker Desktop (macOS)
# Or restart Docker service (Linux)
sudo systemctl restart docker
```

**"OPENAI_API_KEY not found"**
```bash
# Check .env file exists
cat changelog-agent-backend/.env

# Verify it contains your API key
# Restart container after creating/updating .env
cd changelog-agent-backend
docker compose down
docker compose up --build
```

**Backend not responding**
```bash
# Check container status
docker compose ps

# View logs
cd changelog-agent-backend
docker compose logs -f

# Restart container
docker compose restart

# Or rebuild completely
docker compose down
docker compose up --build
```

**Database locked errors**
```bash
# Stop all containers
cd changelog-agent-backend
docker compose down

# Remove WAL files
rm data/sessions.db-wal data/sessions.db-shm

# Restart
docker compose up
```

### Frontend Issues

**"Cannot find module" errors**
```bash
cd changelog-agent-frontend

# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Frontend can't connect to backend**
```bash
# Verify backend is running
curl http://localhost:8000/api/v1/health

# Check API base URL in frontend
# Should be http://localhost:8000/api/v1
```

**Port 5173 already in use**
```bash
# Vite will automatically try the next available port
# Or specify a different port
npm run dev -- --port 3000
```

### Test Issues

**Rate limiting errors during integration tests**
```bash
# Run tests one at a time with delays between them
python3 -m pytest tests/test_api_integration.py::test_add_single_option -v
sleep 2
python3 -m pytest tests/test_api_integration.py::test_create_conditional_logic -v
# etc.

# Or run only unit tests (no API calls, no rate limits)
python3 -m pytest tests/test_database_operations.py tests/test_validators.py tests/test_column_validation.py tests/test_query_guardrails.py -v
```

**"Insufficient quota" errors**
```bash
# Check your OpenAI API credits
# Visit: https://platform.openai.com/usage

# Consider switching to a cheaper model
# Edit app/agents/changelog_agent.py
# Change model from "gpt-5" to "gpt-4o-mini"
```

## Development

### Backend Development

```bash
cd changelog-agent-backend

# Make changes to app/
# Run tests
python3 -m pytest tests/ -v

# Restart container
docker compose restart

# View logs
docker compose logs -f
```

### Frontend Development

```bash
cd changelog-agent-frontend

# Make changes to src/
# Hot reload automatically updates browser

# Type check
npm run type-check

# Lint
npm run lint
```