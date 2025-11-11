from agents import Agent, AgentOutputSchema, function_tool, RunContextWrapper
from app.agents import database_operations
from app.agents.context import FormContext
from app.agents.tool_models import RecordData, RecordUpdate
from app.models.schemas import AgentOutput
import json


def tool_error_handler(ctx: RunContextWrapper[FormContext], error: Exception) -> str:
    """Handle tool errors gracefully."""
    return f"Tool execution failed: {str(error)}. Please check your parameters and try again."


@function_tool(failure_error_function=tool_error_handler)
async def query_forms_database(
    ctx: RunContextWrapper[FormContext],
    sql_query: str
) -> str:
    """
    Query the forms.sqlite database to get information about forms.
    Use this when you need to understand form structure or retrieve form data.

    Args:
        sql_query: A SELECT SQL query to execute against the forms database

    Returns:
        JSON string containing query results with proper formatting
    """
    return await database_operations.query_database(sql_query, ctx.context.db_path)


@function_tool(failure_error_function=tool_error_handler, strict_mode=False)
async def create_database_record(
    ctx: RunContextWrapper[FormContext],
    table_name: str,
    record_data: RecordData
) -> str:
    """
    Validate creating a new record in the database. This validates the insert in a transaction
    but does NOT modify the database (transaction is rolled back).

    YOU MUST call this tool for EVERY record you want to insert to validate the operation.

    Args:
        table_name: The name of the table to insert into (e.g., "option_items", "form_fields")
        record_data: A RecordData object with a 'data' field containing column:value pairs.
                    Use placeholder IDs starting with $ for new records (e.g., "$opt_paris")

    Returns:
        JSON string containing the validated insert change plan
    """
    return await database_operations.create_record(
        table_name,
        json.dumps(record_data.data),
        ctx.context.db_path
    )


@function_tool(failure_error_function=tool_error_handler, strict_mode=False)
async def update_database_record(
    ctx: RunContextWrapper[FormContext],
    table_name: str,
    record_id: str,
    updates: RecordUpdate
) -> str:
    """
    Validate updating an existing record in the database. This validates the update in a
    transaction but does NOT modify the database (transaction is rolled back).

    YOU MUST call this tool for EVERY record you want to update to validate the operation.

    Args:
        table_name: The name of the table to update
        record_id: The exact existing ID of the record to update (must exist in database)
        updates: A RecordUpdate object with an 'updates' field containing changed column:value pairs

    Returns:
        JSON string containing the validated update change plan
    """
    return await database_operations.update_record(
        table_name,
        record_id,
        json.dumps(updates.updates),
        ctx.context.db_path
    )


@function_tool(failure_error_function=tool_error_handler)
async def delete_database_record(
    ctx: RunContextWrapper[FormContext],
    table_name: str,
    record_id: str
) -> str:
    """
    Validate deleting a record from the database. This validates the delete in a transaction
    but does NOT modify the database (transaction is rolled back).

    YOU MUST call this tool for EVERY record you want to delete to validate the operation.

    Args:
        table_name: The name of the table to delete from
        record_id: The exact existing ID of the record to delete (must exist in database)

    Returns:
        JSON string containing the validated delete change plan
    """
    return await database_operations.delete_record(
        table_name,
        record_id,
        ctx.context.db_path
    )


AGENT_INSTRUCTIONS = """
You are a changelog generator for a form management system.

## Database Schema
The database powers a form builder application with these tables:
- forms: Main form definitions
- form_pages: Multi-page form structure
- form_fields: Input fields on forms
- option_sets: Collections of choices (dropdowns/radios)
- option_items: Individual choice options
- field_option_bindings: Links fields to their option sets
- logic_rules, logic_conditions, logic_actions: Conditional field visibility

## Your Mission
Convert user requests into validated database change plans using your tools.

## Critical Workflow

### Step 1: Query First
Use `query_forms_database` to understand the current state:
- Find relevant forms, fields, option sets, etc.
- Get existing IDs you'll need for updates/deletes
- Understand the schema structure

### Step 2: Validate EVERY Change
For each database modification, you MUST call the validation tool:

**For Inserts:**
```
create_database_record(
    table_name="option_items",
    record_data={"data": {"id": "$opt_paris", "option_set_id": "abc-123", "value": "Paris", ...}}
)
```

**For Updates:**
```
update_database_record(
    table_name="forms",
    record_id="existing-uuid-123",
    updates={"updates": {"title": "New Title", "is_active": 1}}
)
```

**For Deletes:**
```
delete_database_record(
    table_name="form_fields",
    record_id="existing-uuid-456"
)
```

Each tool validates the operation and returns a JSON change plan fragment. When calling the tools ensure that they strictly
adhere to the user's request. You must justify every change and make sure it does not make assumptions beyond the request.
If there is clarity needed, ask the user before proceeding with the clarification output format.

### Step 3: Collect Tool Outputs
Gather all the JSON responses from your mutation tool calls.

### Step 4: Merge into Final Changelog
Combine all tool outputs into one unified changelog structure.

## Output Format

Return ONLY one of:

**Clarification** (when unclear):
```json
{
  "type": "clarification",
  "clarification": "Which form should I add this field to?"
}
```

**Changelog** (when complete):
```json
{
  "type": "changelog",
  "changes": {
    "table_name": {
      "insert": [{"id": "$placeholder", ...}],
      "update": [{"id": "existing-id", ...}],
      "delete": [{"id": "existing-id"}]
    }
  }
}
```

## Important Rules

1. **Always validate**: Call mutation tools for EVERY insert/update/delete
2. **Use placeholder IDs**: New records get $-prefixed IDs ("$opt_paris")
3. **Use real IDs**: Updates/deletes need actual database UUIDs from queries
4. **Think holistically**: Consider ALL affected tables (e.g., adding a field with options needs form_fields + option_items + field_option_bindings)
5. **Ask when unclear**: Better to clarify than guess

## Examples

**User**: "Add a Paris option to the travel form destination field"

**Your Process**:
1. Query to find the destination field's option_set_id
2. Call create_database_record for the new option_item
3. Return the changelog from tool output

**User**: "Delete the contact form"

**Your Process**:
1. Query to find the form's ID
2. Query to find all related records (fields, pages, logic rules, etc.)
3. Call delete_database_record for each record (children first, then parent)
4. Merge all tool outputs into final changelog

"""


form_agent = Agent[FormContext](
    name="FormAgent",
    instructions=AGENT_INSTRUCTIONS,
    tools=[
        query_forms_database,
        create_database_record,
        update_database_record,
        delete_database_record
    ],
    model="gpt-5",
    output_type=AgentOutputSchema(AgentOutput, strict_json_schema=False)
)
