#!/bin/bash

# Knowledge Forge Smoke Test Script
# Tests file search, web search, file reader, and plain chat functionality
#
# Usage: ./run-all.sh [--quick] [--verbose] [--server URL]
#
# Options:
#   --quick    Run shorter tests with minimal output
#   --verbose  Show detailed output and debug information
#   --server   Specify Knowledge Forge server URL (default: http://localhost:9999)

set -e # Exit on any error

# Default settings
QUICK_MODE=false
VERBOSE=false
SERVER_URL="${KNOWLEDGE_FORGE_URL:-http://localhost:9999}"
TEST_PDF="../en.pdf"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
  --quick)
    QUICK_MODE=true
    shift
    ;;
  --verbose)
    VERBOSE=true
    shift
    ;;
  --server)
    SERVER_URL="$2"
    shift 2
    ;;
  -h | --help)
    echo "Usage: $0 [--quick] [--verbose] [--server URL]"
    echo ""
    echo "Options:"
    echo "  --quick    Run shorter tests with minimal output"
    echo "  --verbose  Show detailed output and debug information"
    echo "  --server   Specify Knowledge Forge server URL"
    echo "  --help     Show this help message"
    exit 0
    ;;
  *)
    echo "Unknown option: $1"
    exit 1
    ;;
  esac
done

# Helper functions
log_info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
  echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

log_test() {
  echo -e "${YELLOW}[TEST]${NC} $1"
}

# Check if server is running
check_server() {
  log_info "Checking if Knowledge Forge server is running at $SERVER_URL..."

  if command -v curl >/dev/null 2>&1; then
    if curl -s -f "$SERVER_URL/serverstatus" >/dev/null 2>&1; then
      log_success "Server is running at $SERVER_URL"
      return 0
    else
      log_error "Server is not responding at $SERVER_URL"
      log_info "Please start the server first: python server.py"
      return 1
    fi
  else
    log_warning "curl not found, skipping server check"
    return 0
  fi
}

# Check if test file exists
check_test_file() {
  if [[ ! -f "$TEST_PDF" ]]; then
    log_warning "Test PDF not found at $TEST_PDF, will use alternative test file"
    # Try to find any PDF file
    for pdf in ../*.pdf; do
      if [[ -f "$pdf" ]]; then
        TEST_PDF="$pdf"
        log_info "Using test file: $TEST_PDF"
        return 0
      fi
    done
    log_warning "No PDF files found for testing file upload functionality"
    TEST_PDF=""
    return 1
  else
    log_info "Using test file: $TEST_PDF"
    return 0
  fi
}

# Run a test with proper error handling
run_test() {
  local test_name="$1"
  local command="$2"
  local timeout_duration="${3:-60}" # Default 60 seconds timeout

  log_test "Running $test_name..."

  if [[ "$VERBOSE" == "true" ]]; then
    echo "Command: $command"
  fi

  # Create a temporary file for output
  local temp_output=$(mktemp)
  local temp_error=$(mktemp)

  # Run command with timeout
  if timeout "$timeout_duration" bash -c "$command" >"$temp_output" 2>"$temp_error"; then
    log_success "$test_name completed successfully"
    if [[ "$VERBOSE" == "true" ]]; then
      echo "Output:"
      cat "$temp_output"
    elif [[ "$QUICK_MODE" == "false" ]]; then
      # Show first few lines of output
      echo "Sample output:"
      head -n 5 "$temp_output" | sed 's/^/  /'
    fi
    rm -f "$temp_output" "$temp_error"
    return 0
  else
    log_error "$test_name failed"
    echo "Error output:"
    cat "$temp_error" | sed 's/^/  /'
    if [[ "$VERBOSE" == "true" ]]; then
      echo "Full output:"
      cat "$temp_output" | sed 's/^/  /'
    fi
    rm -f "$temp_output" "$temp_error"
    return 1
  fi
}

# Test functions
test_plain_chat() {
  local query="Hello, please respond with 'Smoke test successful' if you can understand this message."
  local cmd="cd '$SCRIPT_DIR' && KNOWLEDGE_FORGE_URL='$SERVER_URL' uv run hello-async.py"

  if [[ "$QUICK_MODE" == "true" ]]; then
    cmd="$cmd --quick"
  fi

  run_test "Plain Chat" "$cmd" 30
}

test_web_search() {
  local query="What is today's date?"
  local debug_flag=""

  if [[ "$VERBOSE" == "true" ]]; then
    debug_flag="--debug"
  fi

  local cmd="cd '$SCRIPT_DIR' && KNOWLEDGE_FORGE_URL='$SERVER_URL' uv run hello-web-search.py $debug_flag -q \"$query\""

  run_test "Web Search" "$cmd" 45
}

test_file_reader() {
  if [[ -z "$TEST_PDF" ]]; then
    log_warning "Skipping file reader test - no test file available"
    return 0
  fi

  local debug_flag=""
  if [[ "$VERBOSE" == "true" ]]; then
    debug_flag="--debug"
  fi

  # Test file reader with a sample file ID (this will fail gracefully if no file is uploaded)
  local cmd="cd '$SCRIPT_DIR' && KNOWLEDGE_FORGE_URL='$SERVER_URL' uv run hello-file-reader.py $debug_flag -q \"What is this document about?\""

  run_test "File Reader" "$cmd" 60
}

test_file_search() {
  if [[ -z "$TEST_PDF" ]]; then
    log_warning "Skipping file search test - no test file available"
    return 0
  fi

  local debug_flag=""
  if [[ "$VERBOSE" == "true" ]]; then
    debug_flag="--debug"
  fi

  # Use the complete file search flow (note: simple-flow-filesearch.py doesn't support --debug)
  local cmd="cd '$SCRIPT_DIR' && KNOWLEDGE_FORGE_URL='$SERVER_URL' uv run simple-flow-filesearch.py -f '$TEST_PDF' -n 'Smoke Test Collection' -q \"What topics are covered in this document?\""

  if [[ "$QUICK_MODE" == "true" ]]; then
    cmd="$cmd --effort low"
  fi

  run_test "File Search Flow" "$cmd" 120
}

# Main execution
main() {
  echo "=============================================="
  echo "Knowledge Forge Smoke Test Suite"
  echo "=============================================="
  echo
  echo "Configuration:"
  echo "  Server URL: $SERVER_URL"
  echo "  Quick Mode: $QUICK_MODE"
  echo "  Verbose Mode: $VERBOSE"
  echo "  Test File: ${TEST_PDF:-"None available"}"
  echo

  # Pre-checks
  if ! check_server; then
    exit 1
  fi

  check_test_file

  # Set environment variable for all tests
  export KNOWLEDGE_FORGE_URL="$SERVER_URL"

  # Track test results
  local total_tests=0
  local passed_tests=0
  local failed_tests=0

  echo "=============================================="
  echo "Starting Tests..."
  echo "=============================================="
  echo

  # Test 1: Plain Chat
  total_tests=$((total_tests + 1))
  if test_plain_chat; then
    passed_tests=$((passed_tests + 1))
  else
    failed_tests=$((failed_tests + 1))
  fi
  echo

  # Test 2: Web Search
  total_tests=$((total_tests + 1))
  if test_web_search; then
    passed_tests=$((passed_tests + 1))
  else
    failed_tests=$((failed_tests + 1))
  fi
  echo

  # Test 3: File Reader
  if [[ -n "$TEST_PDF" ]]; then
    total_tests=$((total_tests + 1))
    if test_file_reader; then
      passed_tests=$((passed_tests + 1))
    else
      failed_tests=$((failed_tests + 1))
    fi
    echo
  fi

  # Test 4: File Search Flow
  if [[ -n "$TEST_PDF" ]]; then
    total_tests=$((total_tests + 1))
    if test_file_search; then
      passed_tests=$((passed_tests + 1))
    else
      failed_tests=$((failed_tests + 1))
    fi
    echo
  fi

  # Summary
  echo "=============================================="
  echo "Test Results Summary"
  echo "=============================================="
  echo "Total Tests: $total_tests"
  echo "Passed: $passed_tests"
  echo "Failed: $failed_tests"
  echo

  if [[ $failed_tests -eq 0 ]]; then
    log_success "All tests passed! 🎉"
    echo
    echo "The Knowledge Forge API is functioning correctly."
    exit 0
  else
    log_error "$failed_tests test(s) failed"
    echo
    echo "Please check the server logs and fix any issues."
    exit 1
  fi
}

# Change to script directory for relative path resolution
cd "$SCRIPT_DIR"

# Run main function
main "$@"

