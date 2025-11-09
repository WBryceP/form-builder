import pytest
import json
import os
import aiosqlite
from app.agents.database_operations import (
    query_database,
    create_record,
    update_record,
    delete_record
)


TEST_DB_PATH = "data/forms.sqlite"


@pytest.fixture
def setup_test_env(monkeypatch):
    """Set the database path for tests."""
    monkeypatch.setenv("DATABASE_PATH", TEST_DB_PATH)


@pytest.mark.asyncio
async def test_query_database_success(setup_test_env):
    """Test querying the database returns results."""
    result = await query_database("SELECT id, title FROM forms LIMIT 1")
    
    assert "Error" not in result
    results = eval(result)
    assert isinstance(results, list)
    assert len(results) > 0
    assert "id" in results[0]
    assert "title" in results[0]


@pytest.mark.asyncio
async def test_query_database_invalid_sql(setup_test_env):
    """Test querying with invalid SQL returns an error."""
    result = await query_database("SELECT * FROM nonexistent_table")
    
    assert "Error querying database" in result


@pytest.mark.asyncio
async def test_create_record_success(setup_test_env):
    """Test creating a record returns proper change plan and doesn't modify DB."""
    test_data = {
        "id": "$test_option",
        "option_set_id": "test-set-id",
        "value": "Test Value",
        "label": "Test Label",
        "position": 1,
        "is_active": 1
    }
    
    record_count_before = await _get_option_items_count()
    
    result = await create_record("option_items", json.dumps(test_data))
    
    assert "Error" not in result
    change_plan = json.loads(result)
    assert "option_items" in change_plan
    assert "insert" in change_plan["option_items"]
    assert len(change_plan["option_items"]["insert"]) == 1
    assert change_plan["option_items"]["insert"][0]["id"] == "$test_option"
    
    record_count_after = await _get_option_items_count()
    assert record_count_before == record_count_after


@pytest.mark.asyncio
async def test_create_record_invalid_json(setup_test_env):
    """Test creating a record with invalid JSON returns an error."""
    result = await create_record("option_items", "not valid json")
    
    assert "Error parsing record_data JSON" in result


@pytest.mark.asyncio
async def test_create_record_missing_required_field(setup_test_env):
    """Test creating a record with missing required fields returns an error."""
    test_data = {
        "id": "$test_option"
    }
    
    result = await create_record("option_items", json.dumps(test_data))
    
    assert "Error testing insert" in result


@pytest.mark.asyncio
async def test_update_record_success(setup_test_env):
    """Test updating a record returns proper change plan and doesn't modify DB."""
    existing_id = await _get_first_option_item_id()
    original_value = await _get_option_item_value(existing_id)
    
    updates = {
        "value": "Updated Value",
        "label": "Updated Label"
    }
    
    result = await update_record("option_items", existing_id, json.dumps(updates))
    
    assert "Error" not in result
    change_plan = json.loads(result)
    assert "option_items" in change_plan
    assert "update" in change_plan["option_items"]
    assert len(change_plan["option_items"]["update"]) == 1
    assert change_plan["option_items"]["update"][0]["id"] == existing_id
    assert change_plan["option_items"]["update"][0]["value"] == "Updated Value"
    
    current_value = await _get_option_item_value(existing_id)
    assert current_value == original_value


@pytest.mark.asyncio
async def test_update_record_nonexistent_id(setup_test_env):
    """Test updating a nonexistent record returns an error."""
    updates = {"value": "New Value"}
    
    result = await update_record("option_items", "nonexistent-id-123", json.dumps(updates))
    
    assert "Error: Record with id 'nonexistent-id-123' not found" in result


@pytest.mark.asyncio
async def test_update_record_invalid_json(setup_test_env):
    """Test updating with invalid JSON returns an error."""
    result = await update_record("option_items", "some-id", "invalid json")
    
    assert "Error parsing updates JSON" in result


@pytest.mark.asyncio
async def test_delete_record_success(setup_test_env):
    """Test deleting a record returns proper change plan and doesn't modify DB."""
    existing_id = await _get_first_option_item_id()
    record_count_before = await _get_option_items_count()
    
    result = await delete_record("option_items", existing_id)
    
    assert "Error" not in result
    change_plan = json.loads(result)
    assert "option_items" in change_plan
    assert "delete" in change_plan["option_items"]
    assert len(change_plan["option_items"]["delete"]) == 1
    assert change_plan["option_items"]["delete"][0]["id"] == existing_id
    
    record_count_after = await _get_option_items_count()
    assert record_count_before == record_count_after
    
    record_still_exists = await _check_option_item_exists(existing_id)
    assert record_still_exists is True


@pytest.mark.asyncio
async def test_delete_record_nonexistent_id(setup_test_env):
    """Test deleting a nonexistent record returns an error."""
    result = await delete_record("option_items", "nonexistent-id-123")
    
    assert "Error: Record with id 'nonexistent-id-123' not found" in result


async def _get_option_items_count() -> int:
    """Helper to count option_items in the database."""
    async with aiosqlite.connect(TEST_DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM option_items") as cursor:
            row = await cursor.fetchone()
            return row[0]


async def _get_first_option_item_id() -> str:
    """Helper to get the ID of the first option_item."""
    async with aiosqlite.connect(TEST_DB_PATH) as db:
        async with db.execute("SELECT id FROM option_items LIMIT 1") as cursor:
            row = await cursor.fetchone()
            return row[0]


async def _get_option_item_value(item_id: str) -> str:
    """Helper to get the value of an option_item."""
    async with aiosqlite.connect(TEST_DB_PATH) as db:
        async with db.execute("SELECT value FROM option_items WHERE id = ?", (item_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None


async def _check_option_item_exists(item_id: str) -> bool:
    """Helper to check if an option_item exists."""
    async with aiosqlite.connect(TEST_DB_PATH) as db:
        async with db.execute("SELECT 1 FROM option_items WHERE id = ?", (item_id,)) as cursor:
            row = await cursor.fetchone()
            return row is not None
