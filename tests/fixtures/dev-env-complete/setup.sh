#!/bin/bash
# Setup script for development environment

set -e

echo "Setting up development environment..."

# Create Python virtual environment if needed
if [ ! -d "venv" ]; then
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate

# Install dependencies
pip install -e ".[dev]"

echo "Development environment setup complete!"
