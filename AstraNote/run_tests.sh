#!/usr/bin/env bash
# Helper script for common development tasks

set -e

if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    echo "Python interpreter not found (expected python3 or python)."
    exit 1
fi

usage() {
    cat << EOF
Usage: ./run_tests.sh [command]

Commands:
    test          Run all automated tests (unit + integration + BDD)
    test-smoke    Run fast smoke tests only
  test-unit     Run unit tests only
  test-int      Run integration tests only
    test-bdd      Run feature/BDD tests only
    test-perf     Run performance verification only
  test-cov      Run tests with coverage report
    test-ci       Run the CI-equivalent validation suite locally
  lint          Run linting (black, flake8)
  format        Auto-format code with black
  type-check    Run type checking with mypy
  all           Run tests, lint, and type check
  help          Show this message

Examples:
  ./run_tests.sh test
  ./run_tests.sh lint
  ./run_tests.sh all
EOF
}

format() {
    echo "Formatting code with black..."
    "$PYTHON_BIN" -m black src tests
    echo "✅ Code formatted"
}

lint() {
    echo "Linting with flake8..."
    "$PYTHON_BIN" -m flake8 src tests --max-line-length=100
    echo "✅ Linting passed"
}

type_check() {
    echo "Type checking with mypy..."
    "$PYTHON_BIN" -m mypy src --ignore-missing-imports || echo "⚠️  Some type hints need attention"
}

test_unit() {
    echo "Running unit tests..."
    "$PYTHON_BIN" -m pytest tests/unit -m unit -v --cov=src --cov-report=term-missing
}

test_smoke() {
    echo "Running smoke tests..."
    "$PYTHON_BIN" -m pytest tests -m smoke -v
}

test_int() {
    echo "Running integration tests..."
    "$PYTHON_BIN" -m pytest tests/integration -m integration -v --cov=src --cov-append --cov-report=term-missing
}

test_bdd() {
    echo "Running feature/BDD tests..."
    "$PYTHON_BIN" -m behave tests/feature/features
}

test_perf() {
    echo "Running performance verification..."
    "$PYTHON_BIN" -m pytest tests/performance -m performance -v --cov=src --cov-report=term-missing:skip-covered
}

test_all() {
    echo "Running all tests..."
    "$PYTHON_BIN" -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing
    "$PYTHON_BIN" -m behave tests/feature/features
    echo "✅ All tests passed. Coverage report: htmlcov/index.html"
}

test_ci() {
    echo "Running CI-equivalent validation..."
    "$PYTHON_BIN" -m black --check src tests
    "$PYTHON_BIN" -m flake8 src tests --count --max-complexity=10 --max-line-length=100 --show-source --statistics
    "$PYTHON_BIN" -m mypy src --ignore-missing-imports
    "$PYTHON_BIN" -m pytest tests/unit -m unit -v --cov=src --cov-report=xml
    "$PYTHON_BIN" -m pytest tests/integration -m integration -v --cov=src --cov-append --cov-report=xml
    "$PYTHON_BIN" -m behave tests/feature/features
}

test_cov() {
    echo "Running tests with detailed coverage..."
    pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing:skip-covered
    echo "✅ Coverage report generated: htmlcov/index.html"
}

all() {
    format
    lint
    type_check
    test_all
}

case "${1:-help}" in
    test)           test_all ;;
    test-smoke)     test_smoke ;;
    test-unit)      test_unit ;;
    test-int)       test_int ;;
    test-bdd)       test_bdd ;;
    test-perf)      test_perf ;;
    test-cov)       test_cov ;;
    test-ci)        test_ci ;;
    lint)           lint ;;
    format)         format ;;
    type-check)     type_check ;;
    all)            all ;;
    help|--help|-h) usage ;;
    *)              usage && exit 1 ;;
esac
