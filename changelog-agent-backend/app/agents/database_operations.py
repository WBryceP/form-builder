import aiosqlite
import os
import json


async def query_database(sql_query: str) -> str:
    """
    Execute a SELECT query against the forms database.
    
    Args:
        sql_query: A SELECT SQL query to execute
        
    Returns:
        JSON string containing query results
    """
    db_path = os.getenv("DATABASE_PATH", "/app/data/forms.sqlite")
    try:
        async with aiosqlite.connect(db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(sql_query) as cursor:
                rows = await cursor.fetchall()
                results = [dict(row) for row in rows]
                return str(results)
    except Exception as e:
        return f"Error querying database: {str(e)}"


async def create_record(table_name: str, record_data: str) -> str:
    """
    Test creating a new record in the database within a transaction.
    The transaction is rolled back, so no actual changes are made.
    
    Args:
        table_name: The name of the table to insert into
        record_data: JSON string of column names to values for the new record
        
    Returns:
        JSON string containing the insert change plan
    """
    db_path = os.getenv("DATABASE_PATH", "/app/data/forms.sqlite")
    
    try:
        record_dict = json.loads(record_data)
        
        async with aiosqlite.connect(db_path) as db:
            await db.execute("BEGIN TRANSACTION")
            
            try:
                columns = list(record_dict.keys())
                placeholders = ["?" for _ in columns]
                values = [record_dict[col] for col in columns]
                
                insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
                
                await db.execute(insert_sql, values)
                
                change_plan = {
                    table_name: {
                        "insert": [record_dict]
                    }
                }
                
                await db.execute("ROLLBACK")
                
                return json.dumps(change_plan, indent=2)
                
            except Exception as e:
                await db.execute("ROLLBACK")
                return f"Error testing insert: {str(e)}"
                
    except json.JSONDecodeError as e:
        return f"Error parsing record_data JSON: {str(e)}"
    except Exception as e:
        return f"Error connecting to database: {str(e)}"


async def update_record(table_name: str, record_id: str, updates: str) -> str:
    """
    Test updating an existing record in the database within a transaction.
    The transaction is rolled back, so no actual changes are made.
    
    Args:
        table_name: The name of the table to update
        record_id: The exact existing ID of the record to update
        updates: JSON string of column names to new values
        
    Returns:
        JSON string containing the update change plan
    """
    db_path = os.getenv("DATABASE_PATH", "/app/data/forms.sqlite")
    
    try:
        updates_dict = json.loads(updates)
        
        async with aiosqlite.connect(db_path) as db:
            await db.execute("BEGIN TRANSACTION")
            
            try:
                check_sql = f"SELECT id FROM {table_name} WHERE id = ?"
                async with db.execute(check_sql, (record_id,)) as cursor:
                    row = await cursor.fetchone()
                    if not row:
                        await db.execute("ROLLBACK")
                        return f"Error: Record with id '{record_id}' not found in table '{table_name}'"
                
                set_clauses = [f"{col} = ?" for col in updates_dict.keys()]
                values = list(updates_dict.values())
                values.append(record_id)
                
                update_sql = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE id = ?"
                
                await db.execute(update_sql, values)
                
                update_record = {"id": record_id}
                update_record.update(updates_dict)
                
                change_plan = {
                    table_name: {
                        "update": [update_record]
                    }
                }
                
                await db.execute("ROLLBACK")
                
                return json.dumps(change_plan, indent=2)
                
            except Exception as e:
                await db.execute("ROLLBACK")
                return f"Error testing update: {str(e)}"
                
    except json.JSONDecodeError as e:
        return f"Error parsing updates JSON: {str(e)}"
    except Exception as e:
        return f"Error connecting to database: {str(e)}"


async def delete_record(table_name: str, record_id: str) -> str:
    """
    Test deleting a record from the database within a transaction.
    The transaction is rolled back, so no actual changes are made.
    
    Args:
        table_name: The name of the table to delete from
        record_id: The exact existing ID of the record to delete
        
    Returns:
        JSON string containing the delete change plan
    """
    db_path = os.getenv("DATABASE_PATH", "/app/data/forms.sqlite")
    
    try:
        async with aiosqlite.connect(db_path) as db:
            await db.execute("BEGIN TRANSACTION")
            
            try:
                check_sql = f"SELECT * FROM {table_name} WHERE id = ?"
                async with db.execute(check_sql, (record_id,)) as cursor:
                    cursor.row_factory = aiosqlite.Row
                    row = await cursor.fetchone()
                    if not row:
                        await db.execute("ROLLBACK")
                        return f"Error: Record with id '{record_id}' not found in table '{table_name}'"
                
                delete_sql = f"DELETE FROM {table_name} WHERE id = ?"
                
                await db.execute(delete_sql, (record_id,))
                
                change_plan = {
                    table_name: {
                        "delete": [{"id": record_id}]
                    }
                }
                
                await db.execute("ROLLBACK")
                
                return json.dumps(change_plan, indent=2)
                
            except Exception as e:
                await db.execute("ROLLBACK")
                return f"Error testing delete: {str(e)}"
                
    except Exception as e:
        return f"Error connecting to database: {str(e)}"
