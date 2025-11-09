from agents import Agent, function_tool
from app.agents import database_operations
from app.models.schemas import ClarificationOutput, ChangelogOutput


@function_tool
async def query_forms_database(sql_query: str) -> str:
    """
    Query the forms.sqlite database to get information about forms.
    Use this when you need to understand form structure or retrieve form data.

    Args:
        sql_query: A SELECT SQL query to execute against the forms database

    Returns:
        JSON string containing query results
    """
    return await database_operations.query_database(sql_query)


@function_tool
async def create_database_record(table_name: str, record_data: str) -> str:
    """
    Test creating a new record in the database. This does NOT actually modify the database.
    Instead, it validates the insert in a transaction and returns the change plan.

    Args:
        table_name: The name of the table to insert into
        record_data: JSON string of column names to values for the new record.
                    Use placeholder IDs starting with $ for new records (e.g., "$opt_paris")

    Returns:
        JSON string containing the insert change plan in the format:
        {
          "table_name": {
            "insert": [{"id": "$placeholder", ...}]
          }
        }
    """
    return await database_operations.create_record(table_name, record_data)


@function_tool
async def update_database_record(table_name: str, record_id: str, updates: str) -> str:
    """
    Test updating an existing record in the database. This does NOT actually modify the database.
    Instead, it validates the update in a transaction and returns the change plan.

    Args:
        table_name: The name of the table to update
        record_id: The exact existing ID of the record to update (must exist in database)
        updates: JSON string of column names to new values (only include changed fields)

    Returns:
        JSON string containing the update change plan in the format:
        {
          "table_name": {
            "update": [{"id": "existing-id", "field": "new_value", ...}]
          }
        }
    """
    return await database_operations.update_record(table_name, record_id, updates)


@function_tool
async def delete_database_record(table_name: str, record_id: str) -> str:
    """
    Test deleting a record from the database. This does NOT actually modify the database.
    Instead, it validates the delete in a transaction and returns the change plan.

    Args:
        table_name: The name of the table to delete from
        record_id: The exact existing ID of the record to delete (must exist in database)

    Returns:
        JSON string containing the delete change plan in the format:
        {
          "table_name": {
            "delete": [{"id": "existing-id"}]
          }
        }
    """
    return await database_operations.delete_record(table_name, record_id)


AGENT_INSTRUCTIONS = """
You are a changelog generator for a form management system.

Your goal: Convert user requests into JSON describing database changes.

## Output Format

Return ONLY one of these:

### Clarification (if request is unclear):
{
  "type": "clarification",
  "clarification": "Your question here"
}

### Changelog (if request is clear):
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

## Workflow

1. Use query_forms_database to find the entities referenced in the request
2. Determine what changes are needed
3. Directly return the JSON - either clarification OR changelog

Do NOT use create/update/delete_database_record tools - they are for validation only.
Just query the database, figure out the changes, and return the JSON.

## ID Rules

- INSERT: Use $-prefixed placeholder IDs ("$opt_paris", "$fld_name")
- UPDATE/DELETE: Use exact existing database IDs
- FK references: Use existing IDs or $-prefixed placeholders

## Examples

### Example 1
User: "Add Paris option to travel destination field"

Steps:
1. Query: Find travel form, destination field, option_set_id
2. Return:
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

### Example 2
User: "Add an option"

Return:
{
  "type": "clarification",
  "clarification": "Which form and field should I add the option to?"
}

No explanations. No tool validation. Just query → compile → return JSON.
"""


form_agent = Agent(
    name="FormAgent",
    instructions=AGENT_INSTRUCTIONS,
    tools=[
        query_forms_database,
        create_database_record,
        update_database_record,
        delete_database_record
    ],
    model="gpt-5"
)
