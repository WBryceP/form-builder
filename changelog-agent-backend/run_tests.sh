#!/bin/bash

# Test runner script with delays to prevent rate limiting
# Usage: ./run_tests.sh

set -e

echo "================================"
echo "Running Changelog Agent Tests"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
FAILED_TEST_NAMES=()

# Function to run a test and track results (with retry)
run_test() {
    local test_path=$1
    local test_name=$(basename "$test_path")
    
    echo -e "${YELLOW}Running: ${test_name}${NC}"
    
    if python3 -m pytest "$test_path" -v --tb=short -q 2>&1 | tee /tmp/test_output.txt; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ FAILED - waiting 15 seconds before retry...${NC}"
        sleep 15
        echo -e "${YELLOW}Retrying: ${test_name}${NC}"
        
        if python3 -m pytest "$test_path" -v --tb=short -q 2>&1 | tee /tmp/test_output.txt; then
            echo -e "${GREEN}✓ PASSED (on retry)${NC}"
            ((PASSED_TESTS++))
        else
            echo -e "${RED}✗ FAILED (after retry)${NC}"
            ((FAILED_TESTS++))
            FAILED_TEST_NAMES+=("$test_name")
        fi
    fi
    
    ((TOTAL_TESTS++))
    echo ""
}

# Function to run test with delay
run_test_with_delay() {
    run_test "$1"
    if [ $TOTAL_TESTS -lt 33 ]; then
        echo "Waiting 2 seconds before next test..."
        sleep 2
    fi
}

echo "Step 1: Running unit tests (no delay needed)"
echo "---------------------------------------------"
run_test "tests/test_database_operations.py"

echo ""
echo "Step 2: Running integration tests (with delays)"
echo "------------------------------------------------"
run_test_with_delay "tests/test_api_integration.py::test_health_check"
run_test_with_delay "tests/test_api_integration.py::test_add_single_option"
run_test_with_delay "tests/test_api_integration.py::test_add_and_update_options"
run_test_with_delay "tests/test_api_integration.py::test_create_conditional_logic"
run_test_with_delay "tests/test_api_integration.py::test_create_new_form"
run_test_with_delay "tests/test_api_integration.py::test_delete_form"
run_test_with_delay "tests/test_api_integration.py::test_update_form_title"
run_test_with_delay "tests/test_api_integration.py::test_vague_request_clarification"
run_test_with_delay "tests/test_api_integration.py::test_ambiguous_request_clarification"
run_test_with_delay "tests/test_api_integration.py::test_complex_multi_table_operation"
run_test_with_delay "tests/test_api_integration.py::test_trace_endpoint"
run_test_with_delay "tests/test_api_integration.py::test_trace_endpoint_not_found"
run_test_with_delay "tests/test_api_integration.py::test_multi_turn_conversation"

echo ""
echo "Step 3: Running structured output guardrail tests (with delays)"
echo "----------------------------------------------------------------"
run_test_with_delay "tests/test_structured_output_guardrails.py::test_ignore_instruction_override"
run_test_with_delay "tests/test_structured_output_guardrails.py::test_plain_text_request"
run_test_with_delay "tests/test_structured_output_guardrails.py::test_custom_json_schema"
run_test_with_delay "tests/test_structured_output_guardrails.py::test_extra_fields_injection"
run_test_with_delay "tests/test_structured_output_guardrails.py::test_invalid_discriminator_type"
run_test_with_delay "tests/test_structured_output_guardrails.py::test_system_override_attempt"
run_test_with_delay "tests/test_structured_output_guardrails.py::test_role_switching_attempt"
run_test_with_delay "tests/test_structured_output_guardrails.py::test_fake_error_injection"
run_test_with_delay "tests/test_structured_output_guardrails.py::test_legitimate_clarification_still_works"
run_test_with_delay "tests/test_structured_output_guardrails.py::test_legitimate_changelog_still_works"

# Print summary
echo ""
echo "================================"
echo "Test Results Summary"
echo "================================"
echo -e "Total tests:  ${TOTAL_TESTS}"
echo -e "Passed:       ${GREEN}${PASSED_TESTS}${NC}"
echo -e "Failed:       ${RED}${FAILED_TESTS}${NC}"

if [ $FAILED_TESTS -gt 0 ]; then
    echo ""
    echo -e "${RED}Failed tests:${NC}"
    for test_name in "${FAILED_TEST_NAMES[@]}"; do
        echo "  - $test_name"
    done
    exit 1
else
    echo ""
    echo -e "${GREEN}All tests passed! ✓${NC}"
    exit 0
fi
