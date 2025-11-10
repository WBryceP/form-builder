import pytest
import json
import httpx
import time
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


@pytest.fixture
def client():
    """Create an HTTP client for testing."""
    return httpx.Client(base_url=BASE_URL, timeout=300.0)


def assert_changelog_response(response_data: Dict[str, Any], expected_tables: list[str]):
    """Helper to validate changelog response structure."""
    response_json = json.loads(response_data["response"])
    
    assert response_json["type"] == "changelog", "Expected changelog type"
    assert "changes" in response_json, "Missing changes field"
    
    changes = response_json["changes"]
    for table in expected_tables:
        assert table in changes, f"Expected table {table} in changes"


def assert_clarification_response(response_data: Dict[str, Any]):
    """Helper to validate clarification response structure."""
    response_json = json.loads(response_data["response"])
    
    assert response_json["type"] == "clarification", "Expected clarification type"
    assert "clarification" in response_json, "Missing clarification field"
    assert len(response_json["clarification"]) > 0, "Clarification should not be empty"


@pytest.mark.integration
def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.integration
def test_add_single_option(client):
    """Test adding a single option to an existing form field."""
    create_response = client.post("/api/v1/conversations")
    assert create_response.status_code == 200
    session_id = create_response.json()["session_id"]
    
    request_data = {
        "message": "Add a Paris option to the travel form destination field",
        "session_id": session_id
    }
    
    response = client.post("/api/v1/chat", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert_changelog_response(data, ["option_items"])
    
    changes = json.loads(data["response"])["changes"]
    option_items = changes["option_items"]
    
    assert "insert" in option_items
    assert len(option_items["insert"]) == 1
    
    inserted = option_items["insert"][0]
    assert inserted["id"].startswith("$")
    assert inserted["value"] == "Paris"
    assert inserted["label"] == "Paris"


@pytest.mark.integration
def test_add_and_update_options(client):
    """Test adding and updating options in the same request."""
    create_response = client.post("/api/v1/conversations")
    assert create_response.status_code == 200
    session_id = create_response.json()["session_id"]
    
    request_data = {
        "message": "update the dropdown options for the destination field in the travel request form: 1. add a paris option, 2. change tokyo to milan",
        "session_id": session_id
    }
    
    response = client.post("/api/v1/chat", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert_changelog_response(data, ["option_items"])
    
    changes = json.loads(data["response"])["changes"]
    option_items = changes["option_items"]
    
    assert "insert" in option_items
    assert "update" in option_items
    
    assert len(option_items["insert"]) == 1
    assert option_items["insert"][0]["value"] == "Paris"
    
    assert len(option_items["update"]) == 1
    assert option_items["update"][0]["value"] == "Milan"
    assert "id" in option_items["update"][0]
    assert not option_items["update"][0]["id"].startswith("$")


@pytest.mark.integration
def test_create_conditional_logic(client):
    """Test creating conditional form logic with fields and rules."""
    create_response = client.post("/api/v1/conversations")
    assert create_response.status_code == 200
    session_id = create_response.json()["session_id"]
    
    request_data = {
        "message": "I want the employment-demo form to require university_name when employment_status is Student. University name should be a text field",
        "session_id": session_id
    }
    
    response = client.post("/api/v1/chat", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    expected_tables = ["form_fields", "logic_rules", "logic_conditions", "logic_actions"]
    assert_changelog_response(data, expected_tables)
    
    changes = json.loads(data["response"])["changes"]
    
    assert len(changes["form_fields"]["insert"]) >= 1
    field = changes["form_fields"]["insert"][0]
    assert field["code"] == "university_name"
    assert field["id"].startswith("$")
    
    assert len(changes["logic_rules"]["insert"]) >= 1
    rule = changes["logic_rules"]["insert"][0]
    assert rule["id"].startswith("$")
    
    assert len(changes["logic_actions"]["insert"]) >= 1
    has_require_action = any(
        action["action"] == "require" 
        for action in changes["logic_actions"]["insert"]
    )
    assert has_require_action, "Should have a require action"


@pytest.mark.integration
def test_create_new_form(client):
    """Test creating a complete new form from scratch."""
    create_response = client.post("/api/v1/conversations")
    assert create_response.status_code == 200
    session_id = create_response.json()["session_id"]
    
    request_data = {
        "message": "I want to create a new form to allow employees to request a new snack. There should be a category field (ice cream/beverage/fruit/chips/gum), and name of the item (text).",
        "session_id": session_id
    }
    
    response = client.post("/api/v1/chat", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Core tables that must be present
    required_tables = ["forms", "form_fields", "option_sets", "option_items"]
    assert_changelog_response(data, required_tables)
    
    changes = json.loads(data["response"])["changes"]
    
    assert len(changes["forms"]["insert"]) == 1
    form = changes["forms"]["insert"][0]
    assert form["id"].startswith("$")
    assert "snack" in form["title"].lower() or "snack" in form["slug"].lower()
    
    assert len(changes["form_fields"]["insert"]) >= 2
    field_codes = [f["code"] for f in changes["form_fields"]["insert"]]
    assert "category" in field_codes or any("cat" in code for code in field_codes)
    
    assert len(changes["option_items"]["insert"]) == 5
    option_values = [opt["value"] for opt in changes["option_items"]["insert"]]
    expected_options = ["Ice Cream", "Beverage", "Fruit", "Chips", "Gum"]
    for expected in expected_options:
        assert any(expected.lower() in val.lower() for val in option_values)


@pytest.mark.integration
def test_delete_form(client):
    """Test deleting a form."""
    create_response = client.post("/api/v1/conversations")
    assert create_response.status_code == 200
    session_id = create_response.json()["session_id"]
    
    request_data = {
        "message": "Delete the Software Access Request form",
        "session_id": session_id
    }
    
    response = client.post("/api/v1/chat", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert_changelog_response(data, ["forms"])
    
    changes = json.loads(data["response"])["changes"]
    forms = changes["forms"]
    
    assert "delete" in forms
    assert len(forms["delete"]) == 1
    
    deleted = forms["delete"][0]
    assert "id" in deleted
    assert not deleted["id"].startswith("$")


@pytest.mark.integration
def test_update_form_title(client):
    """Test updating a form's title."""
    create_response = client.post("/api/v1/conversations")
    assert create_response.status_code == 200
    session_id = create_response.json()["session_id"]
    
    request_data = {
        "message": "Update the title of the contact form to Contact Us",
        "session_id": session_id
    }
    
    response = client.post("/api/v1/chat", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert_changelog_response(data, ["forms"])
    
    changes = json.loads(data["response"])["changes"]
    forms = changes["forms"]
    
    assert "update" in forms
    assert len(forms["update"]) == 1
    
    updated = forms["update"][0]
    assert updated["title"] == "Contact Us"
    assert "id" in updated
    assert not updated["id"].startswith("$")


@pytest.mark.integration
def test_vague_request_clarification(client):
    """Test that vague requests trigger clarification."""
    create_response = client.post("/api/v1/conversations")
    assert create_response.status_code == 200
    session_id = create_response.json()["session_id"]
    
    request_data = {
        "message": "Add an option",
        "session_id": session_id
    }
    
    response = client.post("/api/v1/chat", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert_clarification_response(data)
    
    clarification = json.loads(data["response"])["clarification"]
    assert "form" in clarification.lower() or "field" in clarification.lower()


@pytest.mark.integration
def test_ambiguous_request_clarification(client):
    """Test that ambiguous requests trigger clarification."""
    create_response = client.post("/api/v1/conversations")
    assert create_response.status_code == 200
    session_id = create_response.json()["session_id"]
    
    request_data = {
        "message": "Make some changes",
        "session_id": session_id
    }
    
    response = client.post("/api/v1/chat", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert_clarification_response(data)


@pytest.mark.integration
def test_complex_multi_table_operation(client):
    """Test a complex operation involving multiple tables and operations."""
    create_response = client.post("/api/v1/conversations")
    assert create_response.status_code == 200
    session_id = create_response.json()["session_id"]
    
    request_data = {
        "message": "For the travel form: add Barcelona and Rome options to destination, remove London, and change the form title to International Travel Request",
        "session_id": session_id
    }
    
    response = client.post("/api/v1/chat", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert_changelog_response(data, ["option_items", "forms"])
    
    changes = json.loads(data["response"])["changes"]
    
    assert "insert" in changes["option_items"]
    assert "delete" in changes["option_items"]
    assert len(changes["option_items"]["insert"]) == 2
    assert len(changes["option_items"]["delete"]) == 1
    
    option_values = [opt["value"] for opt in changes["option_items"]["insert"]]
    assert "Barcelona" in option_values
    assert "Rome" in option_values
    
    assert "update" in changes["forms"]
    assert changes["forms"]["update"][0]["title"] == "International Travel Request"


@pytest.mark.integration
def test_trace_endpoint(client):
    """Test that trace endpoint returns trace information for a session."""
    create_response = client.post("/api/v1/conversations")
    assert create_response.status_code == 200
    session_id = create_response.json()["session_id"]
    
    chat_request = {
        "message": "What forms are in the database?",
        "session_id": session_id
    }
    
    chat_response = client.post("/api/v1/chat", json=chat_request)
    assert chat_response.status_code == 200
    
    trace_response = client.get(f"/api/v1/traces/{session_id}")
    assert trace_response.status_code == 200
    
    trace_data = trace_response.json()
    assert trace_data["session_id"] == session_id
    assert "trace_id" in trace_data
    assert "trace_url" in trace_data
    assert "platform.openai.com" in trace_data["trace_url"]


@pytest.mark.integration
def test_trace_endpoint_not_found(client):
    """Test that trace endpoint returns 404 for non-existent session."""
    response = client.get("/api/v1/traces/nonexistent_session_xyz")
    
    assert response.status_code == 404
    detail = response.json()["detail"].lower()
    assert "no trace found" in detail or "not found" in detail


@pytest.mark.integration
def test_multi_turn_conversation(client):
    """Test multi-turn conversation with follow-up questions."""
    create_response = client.post("/api/v1/conversations")
    assert create_response.status_code == 200
    session_id = create_response.json()["session_id"]
    
    first_request = {
        "message": "I want to add a field",
        "session_id": session_id
    }
    
    first_response = client.post("/api/v1/chat", json=first_request)
    assert first_response.status_code == 200
    
    first_data = first_response.json()
    assert_clarification_response(first_data)
    
    second_request = {
        "message": "Add an email field to the contact form",
        "session_id": session_id
    }
    
    second_response = client.post("/api/v1/chat", json=second_request)
    assert second_response.status_code == 200
    
    second_data = second_response.json()
    response_json = json.loads(second_data["response"])
    
    assert response_json["type"] in ["changelog", "clarification"]


@pytest.mark.integration
def test_conversation_management_endpoints(client):
    """Test conversation management endpoints."""
    # Test create conversation
    create_response = client.post("/api/v1/conversations")
    assert create_response.status_code == 200
    
    create_data = create_response.json()
    assert "session_id" in create_data
    assert "title" in create_data
    assert "created_at" in create_data
    session_id = create_data["session_id"]
    
    # Test list conversations (should have 1)
    list_response = client.get("/api/v1/conversations")
    assert list_response.status_code == 200
    
    list_data = list_response.json()
    assert "conversations" in list_data
    assert "total_count" in list_data
    assert list_data["total_count"] >= 1
    
    found_conversation = None
    for conv in list_data["conversations"]:
        if conv["session_id"] == session_id:
            found_conversation = conv
            break
    
    assert found_conversation is not None
    assert found_conversation["message_count"] == 0
    
    # Send a message to update conversation metadata
    chat_request = {
        "message": "Add a test option to travel form",
        "session_id": session_id
    }
    chat_response = client.post("/api/v1/chat", json=chat_request)
    assert chat_response.status_code == 200
    
    # Test get conversation messages
    messages_response = client.get(f"/api/v1/conversations/{session_id}/messages")
    assert messages_response.status_code == 200
    
    messages_data = messages_response.json()
    assert "messages" in messages_data
    assert "total_count" in messages_data
    assert messages_data["session_id"] == session_id
    assert messages_data["total_count"] >= 1
    
    # Check message structure
    user_message = messages_data["messages"][0]
    assert user_message["role"] == "user"
    assert user_message["content"] == "Add a test option to travel form"
    assert "timestamp" in user_message
    
    # Test delete conversation
    delete_response = client.delete(f"/api/v1/conversations/{session_id}")
    assert delete_response.status_code == 200
    
    delete_data = delete_response.json()
    assert delete_data["success"] is True
    assert delete_data["session_id"] == session_id
    
    # Verify conversation is deleted
    messages_after_delete = client.get(f"/api/v1/conversations/{session_id}/messages")
    assert messages_after_delete.status_code == 404


@pytest.mark.integration
def test_conversation_messages_not_found(client):
    """Test getting messages for non-existent conversation returns 404."""
    response = client.get("/api/v1/conversations/nonexistent_session_xyz/messages")
    assert response.status_code == 404
    
    detail = response.json()["detail"].lower()
    assert "not found" in detail


@pytest.mark.integration
def test_delete_nonexistent_conversation(client):
    """Test deleting non-existent conversation returns 404."""
    response = client.delete("/api/v1/conversations/nonexistent_session_xyz")
    assert response.status_code == 404
    
    detail = response.json()["detail"].lower()
    assert "not found" in detail
