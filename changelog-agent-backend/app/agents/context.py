from dataclasses import dataclass


@dataclass
class FormContext:
    """
    Context object for form agent operations.
    Provides dependency injection for database paths and configuration.
    """
    db_path: str
    user_id: str | None = None
    max_query_results: int = 1000
