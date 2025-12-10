#!/bin/bash
# Run tests

# Ensure we are in the backend directory
cd "$(dirname "$0")/.."

# Check if venv exists and use it
if [ -f "venv/bin/pytest" ]; then
    PYTEST_CMD="venv/bin/pytest"
elif [ -f ".venv/bin/pytest" ]; then
    PYTEST_CMD=".venv/bin/pytest"
else
    PYTEST_CMD="pytest"
fi

# Check if a specific test file was provided
if [ -n "$1" ]; then
    echo "Running tests in $1..."
    $PYTEST_CMD "$1" -v
else
    echo "Running all tests..."
    $PYTEST_CMD -v
fi
