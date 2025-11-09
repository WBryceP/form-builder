Objective:
Build an AI agent that can take a natural-language user query about the enterprise form management system (similar to a Google Form creator), determine what the user wants to do, and output the set of changes to apply to each relevant database table.
About the Form App:
This is an enterprise form management app. Admins can create multi-page dynamic form using this app. you can play around with the sample app here: https://forms-app-seven-theta.vercel.app/ to get a sense of what it supports.
The app is based on the data provided in this .sqlite file (https://drive.google.com/file/d/1XPHiaDPAsg9aGZ2tbJuQCZ7vfgX-lI4J/view?usp=drive_link). Your agent will have access to the same .sqlite file and some of the queries the agent will handle will be based out of the existing .sqlite file. You can assume that’s all the tables you need to know and manipulate for this project.

Requirements
Input:
A user’s query in natural language (may be vague or missing details).
Optional follow-up answers from the user if the agent asks clarifying questions.
Output:
A structured JSON object of the form:
{
    "table_name": {
      "insert": [ {...}, {...} ],
      "update": [ {...}, {...} ],
      "delete": [ {...}, {...} ]
    },
    ...
}

Your agent must output a single JSON object keyed by table name(s). Each table object may contain insert, update, and/or delete.
For insert, id may be a placeholder token that other rows in the same plan can reference.
For update and delete, you must provide the exact existing id from the corresponding table.
Include all required fields for each inserted/updated row.

Idempotency guidance
Prefer update over insert when modifying existing rows. Only insert when you’re adding something new.
delete only when the request explicitly removes something.
Your agent must resolve existing IDs from the DB for all update/delete operations and for any foreign keys that reference existing rows.

Examples of Queries the Agent Should Handle
[add options to existing form]update the dropdown options for the destination field in the travel request form: 1. add a paris option, 2. change tokyo to milan
output should be:
{
  "option_items": {
    "insert": [
      {
        "id": "$opt_paris",
        "option_set_id": "a930a282-9b59-4099-be59-e4b16fb73ff5",
        "value": "Paris",
        "label": "Paris",
        "position": 6,
        "is_active": 1
      }
    ],
    "update": [
	    {
		    "id" : "1aef8211-2dc0-410d-86f7-87aa84b60416",
		    "value": "Milan",
		    "label": "Milan"
	    }
    ]
  }
}

[Change existing form dynamic behavior] I want the employment-demo form to require university_name when employment_status is “Student”. University name should be a text field
output should be:
{
  "form_fields": {
    "insert": [
      {
        "id": "$fld_university_name",
        "form_id": d9676e07-24e1-457a-835b-ffa13c114842",
        "page_id": "6dbd1407-46ca-48d9-8019-bcfb980b0c0a",
        "type_id": 1,
        "code": "university_name",
        "label": "University name",
        "position": 4,
        "required": 0,
        "read_only": 0,
        "placeholder": "Your university",
        "visible_by_default": 0
      }
    ]
  },
  "logic_rules": {
    "insert": [
      {
        "id": "$rule_student_uni",
        "form_id": "b061ee07-1842-416a-b166-3efdb0307642",
        "name": "Student requires university name",
        "trigger": "on_change",
        "scope": "form",
        "priority": 10,
        "enabled": 1
      }
    ]
  },
  "logic_conditions": {
    "insert": [
      {
        "id": "$cond_student",
        "rule_id": "$rule_student_uni",
        "lhs_ref": "{\\"type\\":\\"field\\",\\"field_id\\":\\"EXISTING_FIELD_ID_employment_status\\",\\"property\\":\\"value\\"}",
        "operator": "=",
        "rhs": "\\"Student\\"",
        "bool_join": "AND",
        "position": 1
      }
    ]
  },
  "logic_actions": {
    "insert": [
      {
        "id": "$act_show_uni",
        "rule_id": "$rule_student_uni",
        "action": "show",
        "target_ref": "{\\"type\\":\\"field\\",\\"field_id\\":\\"$fld_university_name\\"}",
        "params": null,
        "position": 1
      },
      {
        "id": "$act_require_uni",
        "rule_id": "$rule_student_uni",
        "action": "require",
        "target_ref": "{\\"type\\":\\"field\\",\\"field_id\\":\\"$fld_university_name\\"}",
        "params": null,
        "position": 2
      }
    ]
  }
}

[Create new form] I want to create a new form to allow employees to request a new snack. There should be a category field (ice cream/ beverage/ fruit/ chips/ gum), and name of the item (text).

Deliverables
Working code for the AI agent.
An interaction loop where:
User sends a query.
Agent may ask clarifying questions.
Agent returns the final JSON change set.
A short write-up (readme.md) about your solution
how to run your app locally
how you approached the problem and what are the design choices you’ve made
what are some known issues
how did you establish a baseline of your agent’s performance and what have you done to improve it
future enhancements

Resources:
API Key you can use, feel free to use any model you want:
Feel free to use cursor / claude code / whatever coding assistant tool you need.
Feel free to use whatever agent loop framework you need (e.g. ai-sdk, openai-agent-sdk, claude-code-sdk, or even just directly use cursor / claude code + MCP, etc.).
Considerations:
Avoid loading the entire .sqlite in the agent’s context window (what if the db is very large?)
How do you test different scenarios of requests your agent can handle?
What metrics can you use to measure success? How do you know the answer the agent generates is right? Any guardrails?
