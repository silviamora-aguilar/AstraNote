#!/usr/bin/env bash
# Helper script for common development tasks

set -e

usage() {
    cat << EOF
Usage: ./run_tests.sh [command]

Commands:
  test          Run all tests (unit + integration)
  test-unit     Run unit tests only
  test-int      Run integration tests only
  test-cov      Run tests with coverage report
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
    black src tests
    echo "✅ Code formatted"
}

lint() {
    echo "Linting with flake8..."
    flake8 src tests --max-line-length=100
    echo "✅ Linting passed"
}

type_check() {
    echo "Type checking with mypy..."
    mypy src --ignore-missing-imports || echo "⚠️  Some type hints need attention"
}

test_unit() {
    echo "Running unit tests..."
    pytest tests/unit -m unit -v --cov=src --cov-report=term-missing
}

test_int() {
    echo "Running integration tests..."
    pytest tests/integration -m integration -v --cov=src --cov-append --cov-report=term-missing
}

test_all() {
    echo "Running all tests..."
    pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing
    echo "✅ All tests passed. Coverage report: htmlcov/index.html"
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
    test-unit)      test_unit ;;
    test-int)       test_int ;;
    test-cov)       test_cov ;;
    lint)           lint ;;
    format)         format ;;
    type-check)     type_check ;;
    all)            all ;;
    help|--help|-h) usage ;;
    *)              usage && exit 1 ;;
esac
