# Testing Guide

This directory contains unit and integration tests for the Form Management Changelog Agent.

## Test Structure

- `test_database_operations.py` - Unit tests for core database functions
- `test_api_integration.py` - Integration tests for API endpoints

## Running Tests

### Prerequisites

Ensure the Docker container is running:
```bash
docker compose up
```

### Run All Tests

```bash
# Run all tests (unit + integration)
python3 -m pytest tests/ -v

# Run with coverage
python3 -m pytest tests/ --cov=app --cov-report=html
```

### Run Unit Tests Only

```bash
# Unit tests run without requiring the API server
python3 -m pytest tests/test_database_operations.py -v
```

### Run Integration Tests Only

```bash
# Integration tests require the API server to be running
python3 -m pytest tests/test_api_integration.py -v

# Or using markers
python3 -m pytest -m integration -v
```

### Run Specific Tests

```bash
# Single test
python3 -m pytest tests/test_api_integration.py::test_add_single_option -v

# Multiple specific tests
python3 -m pytest tests/test_api_integration.py::test_add_single_option tests/test_api_integration.py::test_vague_request_clarification -v

# All tests matching a pattern
python3 -m pytest tests/test_api_integration.py -k "clarification" -v
```

## Integration Test Coverage

The integration tests verify:

### Changelog Generation
- ✅ Add single option to form
- ✅ Add and update options simultaneously
- ✅ Create conditional logic (fields + rules + conditions + actions)
- ✅ Create complete new form from scratch
- ✅ Delete form
- ✅ Update form properties
- ✅ Complex multi-table operations

### Clarification Flow
- ✅ Vague requests trigger clarification
- ✅ Ambiguous requests trigger clarification

### API Endpoints
- ✅ Health check endpoint
- ✅ Chat endpoint with session management
- ✅ Trace endpoint for debugging
- ✅ Multi-turn conversations

### Response Validation
Each test validates:
- Correct response type (`changelog` or `clarification`)
- Proper JSON structure
- Expected tables present in changes
- Placeholder IDs for inserts (`$` prefix)
- Real IDs for updates/deletes
- Required fields included

## Test Output Examples

### Successful Test Run
```
tests/test_api_integration.py::test_add_single_option PASSED                  [ 50%]
tests/test_api_integration.py::test_vague_request_clarification PASSED        [100%]

==================== 2 passed in 79.54s ====================
```

### Failed Test Example
```
FAILED tests/test_api_integration.py::test_add_single_option - AssertionError: Expected changelog type
```

## Debugging Failed Tests

1. **Check server is running:**
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

2. **View trace for a failed test:**
   ```bash
   # Get session_id from test
   curl http://localhost:8000/api/v1/traces/{session_id}
   # Visit the trace_url to see tool calls
   ```

3. **Run with verbose output:**
   ```bash
   python3 -m pytest tests/test_api_integration.py::test_name -vv
   ```

4. **Check Docker logs:**
   ```bash
   docker compose logs --tail 50
   ```

## Writing New Tests

### Unit Test Template
```python
@pytest.mark.asyncio
async def test_new_feature(setup_test_env):
    """Test description."""
    result = await your_function(params)
    assert expected_condition
```

### Integration Test Template
```python
@pytest.mark.integration
def test_new_endpoint(client):
    """Test description."""
    request_data = {
        "message": "Your test query",
        "session_id": "test_session"
    }
    
    response = client.post("/api/v1/chat", json=request_data)
    
    assert response.status_code == 200
    # Add your assertions
```

## Continuous Integration

To run these tests in CI/CD:

```yaml
# Example GitHub Actions workflow
- name: Start services
  run: docker compose up -d

- name: Wait for API
  run: |
    timeout 30 bash -c 'until curl -f http://localhost:8000/api/v1/health; do sleep 1; done'

- name: Run tests
  run: python3 -m pytest tests/ -v

- name: Stop services
  run: docker compose down
```

## Performance Notes

- Unit tests: ~1 second total
- Integration tests: ~10-80 seconds per test (depends on agent complexity)
- Full test suite: ~5-10 minutes

Integration tests are slower because they:
1. Make actual API calls
2. Run OpenAI agent with multiple tool calls
3. Query the database multiple times
4. Generate complex responses

## Known Test Limitations

1. **API Quota**: Integration tests consume OpenAI API credits
2. **Timing**: Tests may timeout if agent exceeds max_turns
3. **Non-deterministic**: Agent responses may vary slightly between runs
4. **Database State**: Tests assume specific forms exist in the database

## Troubleshooting

### "Connection refused" errors
- Ensure Docker container is running: `docker compose ps`
- Check health endpoint: `curl http://localhost:8000/api/v1/health`

### "Max turns exceeded" errors
- Increase `max_turns` in `agent_service.py`
- Simplify the test query

### "Insufficient quota" errors
- Check OpenAI API key has credits
- Use a different model (gpt-4o-mini)

### Inconsistent test results
- Agent responses may vary due to LLM non-determinism
- Adjust assertions to be more flexible if needed
