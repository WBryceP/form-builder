import aiosqlite
import json
from typing import Callable, Any
from .validators import validate_table_name, validate_columns, ValidationError


MAX_QUERY_RESULTS = 1000


def _validate_select_query(sql: str) -> None:
    """
    Validate that SQL query is a safe SELECT statement.
    
    Args:
        sql: SQL query string to validate
        
    Raises:
        ValidationError: If query is not a safe SELECT statement
    """
    sql_lower = sql.strip().lower()
    
    if not sql_lower.startswith('select'):
        raise ValidationError("Only SELECT queries are allowed")
    
    forbidden = ['drop', 'delete', 'insert', 'update', 'alter', 'create', 
                 'pragma', 'attach', 'detach', 'truncate', 'replace']
    for keyword in forbidden:
        if f' {keyword} ' in f' {sql_lower} ' or sql_lower.endswith(f' {keyword}'):
            raise ValidationError(f"Query contains forbidden keyword: {keyword}")


async def _validate_and_parse_json(data: str, error_prefix: str) -> tuple[dict | None, str | None]:
    """Parse JSON and return (parsed_data, error_message)."""
    try:
        return json.loads(data), None
    except json.JSONDecodeError as e:
        return None, f"{error_prefix}: {str(e)}"


async def _execute_in_transaction(
    table_name: str,
    db_path: str,
    operation: Callable[[aiosqlite.Connection], Any]
) -> str:
    """
    Execute a database operation within a rolled-back transaction.
    
    Args:
        table_name: Table name (already validated)
        db_path: Path to database
        operation: Async function that performs the DB operation and returns change plan
        
    Returns:
        JSON string of change plan or error message
    """
    async with aiosqlite.connect(db_path) as db:
        await db.execute("PRAGMA foreign_keys = OFF")
        
        try:
            await db.execute("BEGIN")
            change_plan = await operation(db)
            return json.dumps({table_name: change_plan}, indent=2)
        except aiosqlite.IntegrityError as e:
            return f"Integrity constraint violation: {str(e)}"
        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error testing operation: {str(e)}"
        finally:
            await db.execute("ROLLBACK")


async def query_database(sql_query: str, db_path: str, max_results: int = MAX_QUERY_RESULTS) -> str:
    """
    Execute a SELECT query against the forms database.
    
    Args:
        sql_query: A SELECT SQL query to execute
        db_path: Path to the SQLite database file
        max_results: Maximum number of rows to return (default: 1000)
        
    Returns:
        JSON string containing query results
    """
    try:
        _validate_select_query(sql_query)
    except ValidationError as e:
        return f"Validation error: {str(e)}"
    
    try:
        async with aiosqlite.connect(db_path) as db:
            await db.execute("PRAGMA foreign_keys = OFF")
            db.row_factory = aiosqlite.Row
            async with db.execute(sql_query) as cursor:
                rows = await cursor.fetchmany(max_results + 1)
                truncated = len(rows) > max_results
                
                if truncated:
                    rows = rows[:max_results]
                
                results = [dict(row) for row in rows]
                
                if truncated:
                    return json.dumps({
                        "results": results,
                        "truncated": True,
                        "message": f"Results limited to {max_results} rows. Refine your query for more specific results."
                    }, indent=2)
                
                return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error querying database: {str(e)}"


async def create_record(table_name: str, record_data: str, db_path: str) -> str:
    """
    Test creating a new record in the database within a transaction.
    The transaction is rolled back, so no actual changes are made.
    
    Args:
        table_name: The name of the table to insert into
        record_data: JSON string of column names to values for the new record
        db_path: Path to the SQLite database file
        
    Returns:
        JSON string containing the insert change plan
    """
    try:
        validate_table_name(table_name)
    except ValidationError as e:
        return f"Validation error: {str(e)}"
    
    record_dict, error = await _validate_and_parse_json(record_data, "Error parsing record_data JSON")
    if error:
        return error
    
    try:
        validate_columns(table_name, set(record_dict.keys()))
    except ValidationError as e:
        return f"Validation error: {str(e)}"
    
    async def perform_insert(db: aiosqlite.Connection) -> dict:
        columns = list(record_dict.keys())
        placeholders = ["?" for _ in columns]
        values = [record_dict[col] for col in columns]
        
        insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        await db.execute(insert_sql, values)
        
        return {"insert": [record_dict]}
    
    try:
        return await _execute_in_transaction(table_name, db_path, perform_insert)
    except Exception as e:
        return f"Error connecting to database: {str(e)}"


async def update_record(table_name: str, record_id: str, updates: str, db_path: str) -> str:
    """
    Test updating an existing record in the database within a transaction.
    The transaction is rolled back, so no actual changes are made.
    
    Args:
        table_name: The name of the table to update
        record_id: The exact existing ID of the record to update
        updates: JSON string of column names to new values
        db_path: Path to the SQLite database file
        
    Returns:
        JSON string containing the update change plan
    """
    try:
        validate_table_name(table_name)
    except ValidationError as e:
        return f"Validation error: {str(e)}"
    
    updates_dict, error = await _validate_and_parse_json(updates, "Error parsing updates JSON")
    if error:
        return error
    
    try:
        validate_columns(table_name, set(updates_dict.keys()))
    except ValidationError as e:
        return f"Validation error: {str(e)}"
    
    async def perform_update(db: aiosqlite.Connection) -> dict:
        check_sql = f"SELECT id FROM {table_name} WHERE id = ?"
        async with db.execute(check_sql, (record_id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                raise ValueError(f"Record with id '{record_id}' not found in table '{table_name}'")
        
        set_clauses = [f"{col} = ?" for col in updates_dict.keys()]
        values = list(updates_dict.values())
        values.append(record_id)
        
        update_sql = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE id = ?"
        await db.execute(update_sql, values)
        
        update_record = {"id": record_id, **updates_dict}
        return {"update": [update_record]}
    
    try:
        return await _execute_in_transaction(table_name, db_path, perform_update)
    except Exception as e:
        return f"Error connecting to database: {str(e)}"


async def delete_record(table_name: str, record_id: str, db_path: str) -> str:
    """
    Test deleting a record from the database within a transaction.
    The transaction is rolled back, so no actual changes are made.
    
    Args:
        table_name: The name of the table to delete from
        record_id: The exact existing ID of the record to delete
        db_path: Path to the SQLite database file
        
    Returns:
        JSON string containing the delete change plan
    """
    try:
        validate_table_name(table_name)
    except ValidationError as e:
        return f"Validation error: {str(e)}"
    
    async def perform_delete(db: aiosqlite.Connection) -> dict:
        check_sql = f"SELECT id FROM {table_name} WHERE id = ?"
        async with db.execute(check_sql, (record_id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                raise ValueError(f"Record with id '{record_id}' not found in table '{table_name}'")
        
        delete_sql = f"DELETE FROM {table_name} WHERE id = ?"
        await db.execute(delete_sql, (record_id,))
        
        return {"delete": [{"id": record_id}]}
    
    try:
        return await _execute_in_transaction(table_name, db_path, perform_delete)
    except Exception as e:
        return f"Error connecting to database: {str(e)}"
