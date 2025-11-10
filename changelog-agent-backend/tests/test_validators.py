import pytest
import json
import aiosqlite
from app.agents.database_operations import (
    create_record,
    update_record,
    delete_record
)
from app.agents.validators import validate_table_name, ValidationError, VALID_TABLES


TEST_DB_PATH = "/Users/brycepardo/Documents/Fall 2025/form-builder/forms.sqlite"


@pytest.mark.asyncio
async def test_table_whitelist_validation_reject():
    """Test that invalid table names are rejected."""
    result = await create_record("malicious_table", json.dumps({"id": "test"}), TEST_DB_PATH)
    
    assert "Validation error" in result
    assert "Invalid table name" in result
    assert "malicious_table" in result


@pytest.mark.asyncio
async def test_table_whitelist_validation_accept():
    """Test that valid table names are accepted."""
    for table in VALID_TABLES:
        try:
            validate_table_name(table)
        except ValidationError:
            pytest.fail(f"Valid table {table} was rejected")


@pytest.mark.asyncio
async def test_table_whitelist_sql_injection_attempt():
    """Test that SQL injection attempts via table name are blocked."""
    malicious_table = "forms; DROP TABLE forms; --"
    result = await create_record(malicious_table, json.dumps({"id": "test"}), TEST_DB_PATH)
    
    assert "Validation error" in result




@pytest.mark.asyncio
async def test_unique_constraint_violation():
    """Test that unique constraint violations return explicit errors."""
    existing_form = await _get_first_form()
    
    duplicate_form = {
        "id": "new-unique-id",
        "slug": existing_form["slug"],
        "title": "Duplicate Slug Test",
        "status": "draft"
    }
    
    result = await create_record("forms", json.dumps(duplicate_form), TEST_DB_PATH)
    
    assert "Integrity constraint violation" in result or "UNIQUE constraint failed" in result


@pytest.mark.asyncio
async def test_check_constraint_violation():
    """Test that CHECK constraint violations return explicit errors."""
    invalid_form = {
        "id": "test-invalid-status",
        "slug": "test-invalid-status-slug",
        "title": "Invalid Status Test",
        "status": "invalid_status"
    }
    
    result = await create_record("forms", json.dumps(invalid_form), TEST_DB_PATH)
    
    assert "Integrity constraint violation" in result or "CHECK constraint failed" in result


@pytest.mark.asyncio
async def test_transaction_rollback_guarantees_no_changes():
    """Test that failed operations don't leave partial changes."""
    initial_count = await _get_forms_count()
    
    invalid_form = {
        "id": "test-rollback",
        "slug": "test-rollback-slug",
        "title": "Rollback Test",
        "status": "invalid_status"
    }
    
    result = await create_record("forms", json.dumps(invalid_form), TEST_DB_PATH)
    
    assert "Integrity constraint violation" in result or "CHECK constraint failed" in result
    
    final_count = await _get_forms_count()
    assert initial_count == final_count


@pytest.mark.asyncio
async def test_successful_operations_still_rollback():
    """Test that even successful test operations rollback correctly."""
    initial_count = await _get_option_items_count()
    
    valid_item = {
        "id": "test-item-rollback",
        "option_set_id": await _get_first_option_set_id(),
        "value": "test-unique-value-12345",
        "label": "Test Label",
        "position": 999,
        "is_active": 1
    }
    
    result = await create_record("option_items", json.dumps(valid_item), TEST_DB_PATH)
    
    assert "Error" not in result
    assert "option_items" in result
    
    final_count = await _get_option_items_count()
    assert initial_count == final_count


async def _get_first_form_page_id() -> str:
    async with aiosqlite.connect(TEST_DB_PATH) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        async with db.execute("SELECT id FROM form_pages LIMIT 1") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None


async def _get_form_id_with_pages() -> str:
    async with aiosqlite.connect(TEST_DB_PATH) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        async with db.execute(
            "SELECT form_id FROM form_pages GROUP BY form_id HAVING COUNT(*) > 0 LIMIT 1"
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None


async def _get_first_form() -> dict:
    async with aiosqlite.connect(TEST_DB_PATH) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM forms LIMIT 1") as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def _get_forms_count() -> int:
    async with aiosqlite.connect(TEST_DB_PATH) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        async with db.execute("SELECT COUNT(*) FROM forms") as cursor:
            row = await cursor.fetchone()
            return row[0]


async def _get_option_items_count() -> int:
    async with aiosqlite.connect(TEST_DB_PATH) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        async with db.execute("SELECT COUNT(*) FROM option_items") as cursor:
            row = await cursor.fetchone()
            return row[0]


async def _get_first_option_set_id() -> str:
    async with aiosqlite.connect(TEST_DB_PATH) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        async with db.execute("SELECT id FROM option_sets LIMIT 1") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None
