#!/usr/bin/env python3
"""
Validate and analyze the RAG test specification.
(Simple version without external dependencies)
"""

import json
import sys
from collections import defaultdict
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_success(msg):
    print(f"{Colors.GREEN}{msg}{Colors.ENDC}")


def print_error(msg):
    print(f"{Colors.RED}{msg}{Colors.ENDC}")


def print_warning(msg):
    print(f"{Colors.YELLOW}{msg}{Colors.ENDC}")


def print_info(msg):
    print(f"{Colors.BLUE}{msg}{Colors.ENDC}")


def validate_spec(spec_file: str = "rag-test-spec.json"):
    """Validate test specification and show statistics."""

    # Load and validate JSON
    try:
        with open(spec_file, "r") as f:
            spec = json.load(f)
        print_success(f"✅ Valid JSON format in {spec_file}")
    except FileNotFoundError:
        print_error(f"❌ File not found: {spec_file}")
        return False
    except json.JSONDecodeError as e:
        print_error(f"❌ Invalid JSON: {e}")
        return False

    # Validate structure
    required_keys = ["version", "defaults", "test_suites"]
    missing_keys = [k for k in required_keys if k not in spec]
    if missing_keys:
        print_error(f"❌ Missing required keys: {missing_keys}")
        return False
    print_success("✅ Valid spec structure")

    # Collect statistics
    stats = {
        "total_tests": 0,
        "suites": [],
        "task_types": defaultdict(int),
        "effort_levels": defaultdict(int),
        "tool_choices": defaultdict(int),
        "models": defaultdict(int),
        "test_ids": set(),
    }

    # Analyze test suites
    for suite in spec["test_suites"]:
        suite_info = {
            "name": suite["name"],
            "description": suite.get("description", ""),
            "test_count": len(suite.get("tests", [])),
        }
        stats["suites"].append(suite_info)

        for test in suite.get("tests", []):
            stats["total_tests"] += 1

            # Check for duplicate IDs
            test_id = test.get("id")
            if test_id in stats["test_ids"]:
                print_warning(f"⚠️  Duplicate test ID: {test_id}")
            stats["test_ids"].add(test_id)

            # Analyze request parameters
            request = test.get("request", {})
            task_type = request.get("task_type")

            if isinstance(task_type, list):
                stats["task_types"]["multi-tool"] += 1
                for t in task_type:
                    stats["task_types"][f"  - {t}"] += 1
            else:
                stats["task_types"][task_type] += 1

            params = request.get("parameters", {})
            stats["effort_levels"][params.get("effort", "default")] += 1
            stats["models"][params.get("model", "default")] += 1

            if "tool_choice" in params:
                tc = params["tool_choice"]
                if isinstance(tc, dict):
                    stats["tool_choices"][f"object:{tc.get('type')}"] += 1
                else:
                    stats["tool_choices"][tc] += 1

    # Display statistics
    print("\n📊 Test Specification Statistics")
    print("=" * 50)
    print(f"Version: {spec.get('version', 'unknown')}")
    print(f"Total Tests: {stats['total_tests']}")

    print("\n📋 Test Suites:")
    for suite in stats["suites"]:
        print(f"  - {suite['name']}: {suite['test_count']} tests")
        if suite["description"]:
            print(f"    {suite['description']}")

    print("\n🎯 Task Type Coverage:")
    for task_type, count in sorted(stats["task_types"].items()):
        print(f"  - {task_type}: {count}")

    print("\n⚡ Effort Level Distribution:")
    for effort, count in sorted(stats["effort_levels"].items()):
        print(f"  - {effort}: {count}")

    print("\n🤖 Model Coverage:")
    for model, count in sorted(stats["models"].items()):
        print(f"  - {model}: {count}")

    if stats["tool_choices"]:
        print("\n🔧 Tool Choice Variations:")
        for tc, count in sorted(stats["tool_choices"].items()):
            print(f"  - {tc}: {count}")

    # Validate test cases
    print("\n🔍 Validating Individual Tests...")
    errors = []
    warnings = []

    for suite in spec["test_suites"]:
        for test in suite.get("tests", []):
            test_id = test.get("id", "unknown")

            # Check required fields
            if not test.get("name"):
                errors.append(f"Test {test_id}: missing 'name'")
            if not test.get("request"):
                errors.append(f"Test {test_id}: missing 'request'")
            else:
                request = test["request"]
                if not request.get("task_type"):
                    errors.append(f"Test {test_id}: missing 'task_type'")
                if not request.get("parameters"):
                    warnings.append(f"Test {test_id}: missing 'parameters'")

            # Check expected section
            if not test.get("expected"):
                warnings.append(f"Test {test_id}: missing 'expected' section")

    if errors:
        print_error(f"\n❌ Found {len(errors)} errors:")
        for error in errors[:5]:  # Show first 5
            print_error(f"  - {error}")
        if len(errors) > 5:
            print_error(f"  ... and {len(errors) - 5} more")

    if warnings:
        print_warning(f"\n⚠️  Found {len(warnings)} warnings:")
        for warning in warnings[:5]:  # Show first 5
            print_warning(f"  - {warning}")
        if len(warnings) > 5:
            print_warning(f"  ... and {len(warnings) - 5} more")

    # Coverage analysis
    print("\n✅ Coverage Summary:")

    # Check if all effort levels are tested
    expected_efforts = {"dev", "low", "medium", "high"}
    tested_efforts = set(stats["effort_levels"].keys()) - {"default"}
    missing_efforts = expected_efforts - tested_efforts
    if missing_efforts:
        print_warning(f"  ⚠️  Missing effort levels: {missing_efforts}")
    else:
        print_success("  ✅ All effort levels covered")

    # Check if all task types are tested
    expected_tasks = {"plain-chat", "file-search", "web-search", "file-reader"}
    tested_tasks = set()
    for task in stats["task_types"].keys():
        if not task.startswith("  -") and task != "multi-tool":
            tested_tasks.add(task)
    missing_tasks = expected_tasks - tested_tasks
    if missing_tasks:
        print_warning(f"  ⚠️  Missing task types: {missing_tasks}")
    else:
        print_success("  ✅ All task types covered")

    # Check tool choice coverage
    expected_tool_choices = {"auto", "none", "required"}
    tested_tool_choices = set()
    for tc in stats["tool_choices"].keys():
        if not tc.startswith("object:"):
            tested_tool_choices.add(tc)
    missing_tool_choices = expected_tool_choices - tested_tool_choices
    if missing_tool_choices:
        print_warning(f"  ⚠️  Missing tool_choice options: {missing_tool_choices}")
    else:
        print_success("  ✅ All basic tool_choice options covered")

    # Final verdict
    if errors:
        print_error("\n❌ Validation FAILED - fix errors before running tests")
        return False
    else:
        print_success("\n✅ Validation PASSED - specification is ready for testing!")
        return True


if __name__ == "__main__":
    spec_file = sys.argv[1] if len(sys.argv) > 1 else "rag-test-spec.json"
    success = validate_spec(spec_file)
    sys.exit(0 if success else 1)
