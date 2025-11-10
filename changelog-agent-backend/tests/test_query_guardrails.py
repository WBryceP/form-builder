import pytest
import json
from app.agents.database_operations import query_database


TEST_DB_PATH = "data/forms.sqlite"


@pytest.fixture
def setup_test_env(monkeypatch):
    """Set the database path for tests."""
    monkeypatch.setenv("DATABASE_PATH", TEST_DB_PATH)


@pytest.mark.asyncio
async def test_query_rejects_insert(setup_test_env):
    """Test that INSERT queries are rejected."""
    result = await query_database(
        "INSERT INTO forms (id, title) VALUES ('test', 'Test')",
        TEST_DB_PATH
    )
    
    assert "Validation error" in result
    assert "Only SELECT queries are allowed" in result


@pytest.mark.asyncio
async def test_query_rejects_update(setup_test_env):
    """Test that UPDATE queries are rejected."""
    result = await query_database(
        "UPDATE forms SET title = 'Hacked' WHERE id = 'test'",
        TEST_DB_PATH
    )
    
    assert "Validation error" in result
    assert "Only SELECT queries are allowed" in result


@pytest.mark.asyncio
async def test_query_rejects_delete(setup_test_env):
    """Test that DELETE queries are rejected."""
    result = await query_database(
        "DELETE FROM forms WHERE id = 'test'",
        TEST_DB_PATH
    )
    
    assert "Validation error" in result
    assert "Only SELECT queries are allowed" in result


@pytest.mark.asyncio
async def test_query_rejects_drop(setup_test_env):
    """Test that DROP queries are rejected."""
    result = await query_database(
        "DROP TABLE forms",
        TEST_DB_PATH
    )
    
    assert "Validation error" in result
    assert "Only SELECT queries are allowed" in result


@pytest.mark.asyncio
async def test_query_rejects_pragma(setup_test_env):
    """Test that PRAGMA queries are rejected."""
    result = await query_database(
        "PRAGMA table_info(forms)",
        TEST_DB_PATH
    )
    
    assert "Validation error" in result
    assert "Only SELECT queries are allowed" in result


@pytest.mark.asyncio
async def test_query_accepts_valid_select(setup_test_env):
    """Test that valid SELECT queries work."""
    result = await query_database(
        "SELECT id, title FROM forms LIMIT 1",
        TEST_DB_PATH
    )
    
    assert "Validation error" not in result
    parsed = json.loads(result)
    assert isinstance(parsed, list)


@pytest.mark.asyncio
async def test_query_result_truncation(setup_test_env):
    """Test that large result sets are truncated."""
    result = await query_database(
        "SELECT id FROM option_items",
        TEST_DB_PATH,
        max_results=5
    )
    
    parsed = json.loads(result)
    
    # Check if results were truncated
    if isinstance(parsed, dict) and "truncated" in parsed:
        assert parsed["truncated"] is True
        assert len(parsed["results"]) == 5
        assert "Results limited to 5 rows" in parsed["message"]
    else:
        # If not truncated, there are fewer than 6 rows
        assert isinstance(parsed, list)
        assert len(parsed) <= 5


@pytest.mark.asyncio
async def test_query_no_truncation_small_result(setup_test_env):
    """Test that small result sets are not marked as truncated."""
    result = await query_database(
        "SELECT id FROM forms LIMIT 2",
        TEST_DB_PATH,
        max_results=100
    )
    
    parsed = json.loads(result)
    
    # Should be a plain list, not truncated response
    assert isinstance(parsed, list)
    assert "truncated" not in str(result)
