#!/usr/bin/env python3
"""
Example of using the RAG test specification programmatically.
Shows how to load test cases and execute them individually or in custom workflows.
"""

import json
from typing import Dict, List, Any
from pathlib import Path
import requests
from logger import logger


class TestCaseLoader:
    """Load and manage test cases from the specification."""

    def __init__(self, spec_file: str = "rag-test-spec.json"):
        self.spec = self._load_spec(spec_file)
        self.test_index = self._build_test_index()

    def _load_spec(self, spec_file: str) -> Dict[str, Any]:
        """Load the test specification."""
        with open(spec_file, "r") as f:
            return json.load(f)

    def _build_test_index(self) -> Dict[str, Dict[str, Any]]:
        """Build an index of all tests by ID."""
        index = {}
        for suite in self.spec["test_suites"]:
            for test in suite["tests"]:
                test_copy = test.copy()
                test_copy["suite_name"] = suite["name"]
                test_copy["suite_description"] = suite["description"]
                index[test["id"]] = test_copy
        return index

    def get_test_by_id(self, test_id: str) -> Dict[str, Any]:
        """Get a specific test by ID."""
        return self.test_index.get(test_id)

    def get_tests_by_suite(self, suite_name: str) -> List[Dict[str, Any]]:
        """Get all tests from a specific suite."""
        tests = []
        for suite in self.spec["test_suites"]:
            if suite["name"] == suite_name:
                for test in suite["tests"]:
                    test_copy = test.copy()
                    test_copy["suite_name"] = suite["name"]
                    tests.append(test_copy)
                break
        return tests

    def get_tests_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Get tests by tag/task type."""
        tests = []
        for test_id, test in self.test_index.items():
            task_type = test["request"]["task_type"]
            if isinstance(task_type, list):
                if tag in task_type:
                    tests.append(test)
            elif task_type == tag:
                tests.append(test)
        return tests

    def get_smoke_tests(self) -> List[Dict[str, Any]]:
        """Get only smoke tests."""
        return self.get_tests_by_suite("smoke_tests")

    def build_request(self, test: Dict[str, Any]) -> Dict[str, Any]:
        """Build a request from test specification."""
        request_spec = test["request"]
        params = request_spec["parameters"]
        defaults = self.spec["defaults"]

        # Start with basic request structure
        request_data = {
            "model": params.get("model", defaults["model"]),
            "effort": params.get("effort", defaults["effort"]),
            "store": True,
            "input": [{"role": "user", "id": f"test_{test['id']}", "content": params.get("query", "Test query")}],
        }

        # Add tools based on task type
        task_type = request_spec["task_type"]

        if task_type == "file-search" or (isinstance(task_type, list) and "file-search" in task_type):
            if "tools" not in request_data:
                request_data["tools"] = []
            request_data["tools"].append(
                {
                    "type": "file_search",
                    "vector_store_ids": [params.get("vector_store_id", defaults["vector_store_id"])],
                    "max_num_results": 5,
                }
            )

        if task_type == "web-search" or (isinstance(task_type, list) and "web-search" in task_type):
            if "tools" not in request_data:
                request_data["tools"] = []
            request_data["tools"].append(
                {
                    "type": "web_search",
                    "search_context_size": "medium",
                    "user_location": {"type": "approximate", "country": "US", "city": "San Francisco"},
                }
            )

        if task_type == "file-reader" or (isinstance(task_type, list) and "file-reader" in task_type):
            # Convert content to array format
            request_data["input"][0]["content"] = [
                {"type": "input_file", "file_id": params.get("file_id", defaults["file_id"])},
                {"type": "input_text", "text": params.get("query", "Test query")},
            ]

        # Add tool_choice if specified
        if "tool_choice" in params:
            request_data["tool_choice"] = params["tool_choice"]

        return request_data


def example_usage():
    """Demonstrate how to use the test case loader."""

    # Load test cases
    loader = TestCaseLoader()

    # Example 1: Get and execute a specific test
    logger.info("📋 Example 1: Load specific test case")
    test = loader.get_test_by_id("smoke_file_search")
    if test:
        logger.info(f"   Test: {test['name']}")
        logger.info(f"   Description: {test['description']}")
        request = loader.build_request(test)
        logger.info(f"   Request model: {request['model']}")
        logger.info(f"   Request effort: {request['effort']}")
        logger.info(f"   Has tools: {'tools' in request}")

    # Example 2: Get all smoke tests
    logger.info("\n📋 Example 2: Load all smoke tests")
    smoke_tests = loader.get_smoke_tests()
    logger.info(f"   Found {len(smoke_tests)} smoke tests:")
    for test in smoke_tests:
        logger.info(f"   - {test['id']}: {test['name']}")

    # Example 3: Get tests by task type
    logger.info("\n📋 Example 3: Load tests by task type")
    file_search_tests = loader.get_tests_by_tag("file-search")
    logger.info(f"   Found {len(file_search_tests)} file-search tests:")
    for test in file_search_tests[:3]:  # Show first 3
        logger.info(f"   - {test['id']}: {test['name']}")

    # Example 4: Build requests for different test types
    logger.info("\n📋 Example 4: Build requests for different test types")

    # Plain chat
    plain_test = loader.get_test_by_id("smoke_plain_chat")
    plain_request = loader.build_request(plain_test)
    logger.info(f"   Plain chat query: {plain_request['input'][0]['content']}")

    # Multi-tool
    multi_test = loader.get_test_by_id("multi_file_web_search")
    multi_request = loader.build_request(multi_test)
    logger.info(f"   Multi-tool query: {multi_request['input'][0]['content']}")
    logger.info(f"   Tools configured: {len(multi_request.get('tools', []))}")

    # Tool choice test
    tool_choice_test = loader.get_test_by_id("tool_choice_required")
    tc_request = loader.build_request(tool_choice_test)
    logger.info(f"   Tool choice setting: {tc_request.get('tool_choice', 'not set')}")

    # Example 5: Custom test execution
    logger.info("\n📋 Example 5: Execute a test with custom logic")

    def execute_test_with_custom_validation(test_case: Dict[str, Any]) -> bool:
        """Execute a test with custom validation logic."""
        request = loader.build_request(test_case)

        # In real usage, you would send the request
        # response = requests.post(url, json=request, stream=True)

        # Custom validation logic here
        logger.info(f"   Would execute test: {test_case['name']}")
        logger.info(f"   Task type: {test_case['request']['task_type']}")
        logger.info(f"   Expected status: {test_case.get('expected', {}).get('status_code', 200)}")

        # Return validation result
        return True

    test_to_run = loader.get_test_by_id("effort_high")
    if test_to_run:
        result = execute_test_with_custom_validation(test_to_run)
        logger.info(f"   Test result: {'✅ Passed' if result else '❌ Failed'}")

    # Example 6: Generate test matrix
    logger.info("\n📋 Example 6: Generate test matrix for effort levels")
    effort_levels = ["dev", "low", "medium", "high"]
    task_types = ["plain-chat", "file-search", "web-search"]

    logger.info("   Test Matrix:")
    logger.info("   " + "-" * 50)
    for effort in effort_levels:
        tests_with_effort = [
            test for test in loader.test_index.values() if test["request"]["parameters"].get("effort") == effort
        ]
        logger.info(f"   Effort {effort}: {len(tests_with_effort)} tests")

    # Example 7: Export filtered tests
    logger.info("\n📋 Example 7: Export filtered test cases")

    # Get all high-effort tests
    high_effort_tests = [
        test for test in loader.test_index.values() if test["request"]["parameters"].get("effort") == "high"
    ]

    # Export to new file
    export_data = {"description": "High effort test cases", "source": "rag-test-spec.json", "tests": high_effort_tests}

    export_file = "high-effort-tests.json"
    with open(export_file, "w") as f:
        json.dump(export_data, f, indent=2)
    logger.info(f"   Exported {len(high_effort_tests)} tests to {export_file}")

    # Clean up
    Path(export_file).unlink()


if __name__ == "__main__":
    logger.info("🚀 RAG Test Specification Usage Examples")
    logger.info("=" * 60)
    example_usage()
    logger.info("\n✅ Examples completed!")
