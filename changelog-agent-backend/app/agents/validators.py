VALID_TABLES = {
    "categories",
    "forms",
    "form_pages",
    "field_types",
    "form_fields",
    "option_sets",
    "option_items",
    "field_option_binding",
    "logic_rules",
    "logic_conditions",
    "logic_actions"
}

TABLE_COLUMNS = {
    "categories": {
        "id", "slug", "name", "description", "created_at", "updated_at"
    },
    "forms": {
        "id", "org_id", "slug", "title", "description", "status",
        "category_id", "created_at", "updated_at"
    },
    "form_pages": {
        "id", "form_id", "title", "description", "position",
        "created_at", "updated_at"
    },
    "field_types": {
        "id", "key", "has_options", "allows_multiple", "builtin_validators"
    },
    "form_fields": {
        "id", "form_id", "page_id", "type_id", "code", "label",
        "help_text", "position", "required", "read_only", "placeholder",
        "default_value", "validation_schema", "visible_by_default",
        "created_at", "updated_at"
    },
    "option_sets": {
        "id", "form_id", "name", "created_at", "updated_at"
    },
    "option_items": {
        "id", "option_set_id", "value", "label", "position", "is_active"
    },
    "field_option_binding": {
        "field_id", "option_set_id", "display_pattern"
    },
    "logic_rules": {
        "id", "form_id", "name", "trigger", "scope", "priority", "enabled"
    },
    "logic_conditions": {
        "id", "rule_id", "group_id", "lhs_ref", "operator", "rhs",
        "bool_join", "position"
    },
    "logic_actions": {
        "id", "rule_id", "action", "target_ref", "params", "position"
    }
}


class ValidationError(Exception):
    pass


def validate_table_name(table_name: str) -> None:
    if table_name not in VALID_TABLES:
        raise ValidationError(
            f"Invalid table name '{table_name}'. "
            f"Allowed tables: {', '.join(sorted(VALID_TABLES))}"
        )


def validate_columns(table_name: str, columns: set[str]) -> None:
    """
    Validate that all columns are allowed for the given table.
    Prevents SQL injection through column names.
    
    Args:
        table_name: The table name (must be validated first)
        columns: Set of column names to validate
        
    Raises:
        ValidationError: If any column is not allowed for the table
    """
    if table_name not in TABLE_COLUMNS:
        raise ValidationError(f"No column validation defined for table '{table_name}'")
    
    allowed_columns = TABLE_COLUMNS[table_name]
    invalid_columns = columns - allowed_columns
    
    if invalid_columns:
        raise ValidationError(
            f"Invalid columns for table '{table_name}': {', '.join(sorted(invalid_columns))}. "
            f"Allowed columns: {', '.join(sorted(allowed_columns))}"
        )
