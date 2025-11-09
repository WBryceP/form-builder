# Data Directory

This directory contains the `forms.sqlite` database file that the agent queries.

## Database File

- **forms.sqlite**: SQLite database containing form information
- Mounted to `/app/data/forms.sqlite` inside the Docker container
- Agent uses `query_forms_database` tool to access this data

## Usage

The agent can query this database when users ask questions about forms or when generating changelogs that involve form data.
