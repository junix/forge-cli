#!/usr/bin/env python3
"""
RAG Test Runner - Loads and executes test cases from rag-test-spec.json
"""

import argparse
import asyncio
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import aiohttp
from logger import logger


class RAGTestRunner:
    """Test runner for RAG API testing based on JSON specification."""

    def __init__(self, spec_file: str = "rag-test-spec.json"):
        """Initialize test runner with specification file."""
        self.spec_file = spec_file
        self.spec = self._load_spec()
        self.results = []
        self.base_url = self._resolve_base_url()

    def _load_spec(self) -> Dict[str, Any]:
        """Load test specification from JSON file."""
        try:
            with open(self.spec_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Test specification file not found: {self.spec_file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in test specification: {e}")
            sys.exit(1)

    def _resolve_base_url(self) -> str:
        """Resolve base URL from spec or environment."""
        base_url = self.spec["defaults"]["base_url"]
        # Handle environment variable substitution
        if "${" in base_url:
            match = re.search(r"\$\{(\w+):-(.*?)\}", base_url)
            if match:
                env_var, default = match.groups()
                base_url = os.environ.get(env_var, default)
        return base_url

    def _substitute_defaults(self, value: Any) -> Any:
        """Recursively substitute default values in test parameters."""
        if isinstance(value, str) and value.startswith("${defaults."):
            key = value[11:-1]  # Extract key from ${defaults.key}
            return self.spec["defaults"].get(key, value)
        elif isinstance(value, dict):
            return {k: self._substitute_defaults(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._substitute_defaults(v) for v in value]
        return value

    async def run_all_tests(
        self, suite_filter: Optional[str] = None, test_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run all tests or filtered subset."""
        logger.info("🚀 Starting RAG Test Runner")
        logger.info(f"   Base URL: {self.base_url}")
        logger.info(f"   Spec Version: {self.spec.get('version', 'unknown')}")

        start_time = time.time()
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        skipped_tests = 0

        for suite in self.spec["test_suites"]:
            # Apply suite filter
            if suite_filter and suite_filter not in suite["name"]:
                continue

            logger.info(f"\n📋 Test Suite: {suite['name']}")
            logger.info(f"   {suite['description']}")

            for test in suite["tests"]:
                # Apply test filter
                if test_filter and test_filter not in test["id"]:
                    skipped_tests += 1
                    continue

                total_tests += 1
                result = await self.run_single_test(test, suite["name"])

                if result["status"] == "passed":
                    passed_tests += 1
                    logger.success(f"   ✅ {test['name']}")
                elif result["status"] == "failed":
                    failed_tests += 1
                    logger.error(f"   ❌ {test['name']}: {result.get('error', 'Unknown error')}")
                else:
                    logger.warning(f"   ⚠️  {test['name']}: {result.get('error', 'Unknown status')}")

                self.results.append(result)
                # TODO: remove this later
                break
            break

        # Summary
        duration = time.time() - start_time
        logger.info("\n" + "=" * 60)
        logger.info("📊 Test Summary")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"⏭️  Skipped: {skipped_tests}")
        logger.info(f"⏱️  Duration: {duration:.2f}s")
        logger.info(f"📈 Success Rate: {(passed_tests / total_tests * 100):.1f}%" if total_tests > 0 else "N/A")

        return {
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "skipped": skipped_tests,
                "duration": duration,
                "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
            },
            "results": self.results,
        }

    async def run_single_test(self, test: Dict[str, Any], suite_name: str) -> Dict[str, Any]:
        """Run a single test case."""
        test_id = test["id"]
        logger.debug(f"Running test: {test_id}")

        try:
            # Build request
            request_data = self._build_request(test["request"])

            # Execute request
            start_time = time.time()
            response_data = await self._execute_request(request_data)
            duration = time.time() - start_time

            # Validate response
            validation_result = self._validate_response(
                response_data, test.get("expected", {}), test["request"]["task_type"]
            )

            return {
                "test_id": test_id,
                "test_name": test["name"],
                "suite": suite_name,
                "status": "passed" if validation_result["valid"] else "failed",
                "duration": duration,
                "error": validation_result.get("error"),
                "details": validation_result.get("details", {}),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.exception(f"Test execution error for {test_id}")
            return {
                "test_id": test_id,
                "test_name": test["name"],
                "suite": suite_name,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _build_request(self, request_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Build request data from test specification."""
        task_type = request_spec["task_type"]
        params = self._substitute_defaults(request_spec["parameters"])

        # Get default values
        defaults = self.spec["defaults"]

        # Build base request
        request_data = {
            "model": params.get("model", defaults["model"]),
            "effort": params.get("effort", defaults["effort"]),
            "store": True,
            "input": [{"role": "user", "id": f"test_{int(time.time())}", "content": params.get("query", "Test query")}],
        }

        # Add tool_choice if specified
        if "tool_choice" in params:
            request_data["tool_choice"] = params["tool_choice"]

        # Handle different task types
        if isinstance(task_type, list):
            # Multi-tool request
            request_data["tools"] = []

            if "file-search" in task_type:
                request_data["tools"].append(
                    {
                        "type": "file_search",
                        "vector_store_ids": [params.get("vector_store_id", defaults["vector_store_id"])],
                        "max_num_results": 5,
                    }
                )

            if "web-search" in task_type:
                request_data["tools"].append(
                    {
                        "type": "web_search",
                        "search_context_size": "medium",
                        "user_location": {"type": "approximate", "country": "US", "city": "San Francisco"},
                    }
                )

            if "file-reader" in task_type:
                # Convert content to array format
                request_data["input"][0]["content"] = [
                    {"type": "input_file", "file_id": params.get("file_id", defaults["file_id"])},
                    {"type": "input_text", "text": params.get("query", "Test query")},
                ]

        else:
            # Single task type
            if task_type == "file-search":
                request_data["tools"] = [
                    {
                        "type": "file_search",
                        "vector_store_ids": [params.get("vector_store_id", defaults["vector_store_id"])],
                        "max_num_results": 5,
                    }
                ]
            elif task_type == "web-search":
                request_data["tools"] = [
                    {
                        "type": "web_search",
                        "search_context_size": "medium",
                        "user_location": {"type": "approximate", "country": "US", "city": "San Francisco"},
                    }
                ]
            elif task_type == "file-reader":
                request_data["input"][0]["content"] = [
                    {"type": "input_file", "file_id": params.get("file_id", defaults["file_id"])},
                    {"type": "input_text", "text": params.get("query", "Test query")},
                ]

        return request_data

    async def _execute_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute HTTP request and collect response data."""
        url = f"{self.base_url}/v1/responses"
        timeout = aiohttp.ClientTimeout(total=self.spec["defaults"]["timeout"])

        events_collected = []
        response_text = []
        status_code = None
        headers = {}

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=request_data) as response:
                status_code = response.status
                headers = dict(response.headers)

                if response.status != 200:
                    error_text = await response.text()
                    return {
                        "status_code": status_code,
                        "headers": headers,
                        "error": error_text,
                        "events": [],
                        "response_text": "",
                    }

                # Process SSE stream
                async for line in response.content:
                    line = line.decode("utf-8").strip()
                    if not line:
                        continue

                    if line.startswith("event:"):
                        event_type = line[6:].strip()
                        events_collected.append({"type": event_type})

                        if event_type == "response.done":
                            break

                    elif line.startswith("data:"):
                        data_str = line[5:].strip()
                        if data_str:
                            try:
                                data = json.loads(data_str)

                                # Extract text content
                                if "text" in data:
                                    text_data = data["text"]
                                    if isinstance(text_data, dict) and "text" in text_data:
                                        response_text.append(text_data["text"])
                                    elif isinstance(text_data, str):
                                        response_text.append(text_data)

                                # Add data to last event
                                if events_collected:
                                    events_collected[-1]["data"] = data

                            except json.JSONDecodeError:
                                pass

        return {
            "status_code": status_code,
            "headers": headers,
            "events": events_collected,
            "response_text": "".join(response_text),
            "event_types": [e["type"] for e in events_collected],
        }

    def _validate_response(
        self, response_data: Dict[str, Any], expected: Dict[str, Any], task_type: str
    ) -> Dict[str, Any]:
        """Validate response against expected criteria."""
        errors = []
        details = {}

        # Check status code
        expected_status = expected.get("status_code", 200)
        if isinstance(expected_status, list):
            if response_data["status_code"] not in expected_status:
                errors.append(f"Status code {response_data['status_code']} not in expected {expected_status}")
        else:
            if response_data["status_code"] != expected_status:
                errors.append(f"Status code {response_data['status_code']} != expected {expected_status}")

        # Only validate further if we got a successful response
        if response_data["status_code"] == 200:
            event_types = set(response_data["event_types"])

            # Check required events
            if "required_events" in expected:
                required = set(expected["required_events"])
                missing = required - event_types
                if missing:
                    errors.append(f"Missing required events: {missing}")

            # Check for tool calls
            tool_events = [e for e in response_data["events"] if ".searching" in e["type"] or ".completed" in e["type"]]

            if expected.get("no_tool_calls", False):
                if tool_events:
                    errors.append(f"Expected no tool calls but found: {[e['type'] for e in tool_events]}")

            if expected.get("tool_calls"):
                found_tools = set()
                for event in tool_events:
                    if "file_search" in event["type"]:
                        found_tools.add("file_search")
                    elif "web_search" in event["type"]:
                        found_tools.add("web_search")

                expected_tools = set(expected["tool_calls"])
                if expected_tools != found_tools:
                    errors.append(f"Tool calls mismatch. Expected: {expected_tools}, Found: {found_tools}")

            # Check response content
            if "response_contains" in expected:
                response_lower = response_data["response_text"].lower()
                for term in expected["response_contains"]:
                    if term.lower() not in response_lower:
                        errors.append(f"Response missing expected term: '{term}'")

            # Check response length
            if "min_response_length" in expected:
                actual_length = len(response_data["response_text"])
                if actual_length < expected["min_response_length"]:
                    errors.append(f"Response too short: {actual_length} < {expected['min_response_length']}")

            # Collect details for reporting
            details = {
                "event_count": len(response_data["events"]),
                "event_types": list(event_types),
                "response_length": len(response_data["response_text"]),
                "has_reasoning": any("reasoning" in e["type"] for e in response_data["events"]),
            }

        return {"valid": len(errors) == 0, "error": "; ".join(errors) if errors else None, "details": details}

    def save_results(self, filepath: str = "rag-test-results.json"):
        """Save test results to JSON file."""
        with open(filepath, "w") as f:
            json.dump(
                {
                    "spec_version": self.spec.get("version"),
                    "test_run": datetime.now().isoformat(),
                    "base_url": self.base_url,
                    "results": self.results,
                },
                f,
                indent=2,
            )
        logger.info(f"💾 Results saved to: {filepath}")


async def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(description="RAG Test Runner")
    parser.add_argument("--spec", default="rag-test-spec.json", help="Path to test specification file")
    parser.add_argument("--suite", help="Filter tests by suite name (partial match)")
    parser.add_argument("--test", help="Filter tests by test ID (partial match)")
    parser.add_argument("--save-results", action="store_true", help="Save results to JSON file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Configure logging
    if args.verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")

    # Run tests
    runner = RAGTestRunner(args.spec)
    results = await runner.run_all_tests(suite_filter=args.suite, test_filter=args.test)

    # Save results if requested
    if args.save_results:
        runner.save_results()

    # Exit with appropriate code
    sys.exit(0 if results["summary"]["failed"] == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
