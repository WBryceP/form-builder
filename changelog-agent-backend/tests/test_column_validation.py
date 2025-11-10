import pytest
import json
from app.agents.database_operations import create_record, update_record
from app.agents.validators import validate_columns, ValidationError


TEST_DB_PATH = "data/forms.sqlite"


@pytest.fixture
def setup_test_env(monkeypatch):
    """Set the database path for tests."""
    monkeypatch.setenv("DATABASE_PATH", TEST_DB_PATH)


@pytest.mark.asyncio
async def test_create_record_rejects_invalid_columns(setup_test_env):
    """Test that create_record rejects columns not in the whitelist."""
    result = await create_record(
        "forms",
        json.dumps({
            "id": "$test",
            "title": "Test Form",
            "malicious_column": "DROP TABLE forms;"
        }),
        TEST_DB_PATH
    )
    
    assert "Validation error" in result
    assert "Invalid columns" in result
    assert "malicious_column" in result


@pytest.mark.asyncio
async def test_create_record_rejects_sql_injection_in_column_name(setup_test_env):
    """Test that SQL injection attempts in column names are blocked."""
    result = await create_record(
        "option_items",
        json.dumps({
            "id": "$test",
            "value": "test",
            "label; DROP TABLE option_items; --": "malicious"
        }),
        TEST_DB_PATH
    )
    
    assert "Validation error" in result
    assert "Invalid columns" in result


@pytest.mark.asyncio
async def test_update_record_rejects_invalid_columns(setup_test_env):
    """Test that update_record rejects columns not in the whitelist."""
    result = await update_record(
        "forms",
        "some-id",
        json.dumps({
            "title": "Updated",
            "fake_column": "value"
        }),
        TEST_DB_PATH
    )
    
    assert "Validation error" in result
    assert "Invalid columns" in result
    assert "fake_column" in result


@pytest.mark.asyncio
async def test_create_record_accepts_all_valid_columns(setup_test_env):
    """Test that all legitimate columns for a table are accepted."""
    result = await create_record(
        "option_items",
        json.dumps({
            "id": "$test",
            "option_set_id": "abc-123",
            "value": "test_value",
            "label": "Test Label",
            "position": 1,
            "is_active": 1
        }),
        TEST_DB_PATH
    )
    
    assert "Validation error" not in result or "Invalid columns" not in result


def test_validate_columns_rejects_invalid():
    """Test the validate_columns function directly."""
    with pytest.raises(ValidationError) as exc_info:
        validate_columns("forms", {"id", "title", "not_a_real_column"})
    
    assert "Invalid columns" in str(exc_info.value)
    assert "not_a_real_column" in str(exc_info.value)


def test_validate_columns_accepts_valid():
    """Test that validate_columns accepts all valid columns."""
    try:
        validate_columns("forms", {"id", "title", "description", "status"})
        validate_columns("option_items", {"id", "value", "label", "is_active"})
        validate_columns("form_fields", {"id", "label", "required", "position"})
    except ValidationError as e:
        pytest.fail(f"Valid columns were rejected: {e}")


def test_validate_columns_all_tables_have_definitions():
    """Test that all valid tables have column definitions."""
    from app.agents.validators import VALID_TABLES, TABLE_COLUMNS
    
    for table in VALID_TABLES:
        assert table in TABLE_COLUMNS, f"Table {table} missing column definitions"
        assert len(TABLE_COLUMNS[table]) > 0, f"Table {table} has empty column set"
