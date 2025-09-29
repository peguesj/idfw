#!/bin/bash

# IDFWU - IDEA Framework Unified Project Initialization Script
# This script sets up the development environment for the unified framework

set -e

echo "🚀 Initializing IDFWU - IDEA Framework Unified Project"
echo "Linear Project ID: 4d649a6501f7"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check prerequisites
check_prerequisites() {
    echo -e "${BLUE}Checking prerequisites...${NC}"

    # Check Python
    if command -v python3 &> /dev/null; then
        echo -e "${GREEN}✓${NC} Python3 found: $(python3 --version)"
    else
        echo -e "${RED}✗${NC} Python3 not found. Please install Python 3.10+"
        exit 1
    fi

    # Check Node
    if command -v node &> /dev/null; then
        echo -e "${GREEN}✓${NC} Node.js found: $(node --version)"
    else
        echo -e "${RED}✗${NC} Node.js not found. Please install Node.js 18+"
        exit 1
    fi

    # Check Git
    if command -v git &> /dev/null; then
        echo -e "${GREEN}✓${NC} Git found: $(git --version)"
    else
        echo -e "${RED}✗${NC} Git not found. Please install Git"
        exit 1
    fi
}

# Create directory structure
create_directories() {
    echo -e "${BLUE}Creating project directories...${NC}"

    directories=(
        "unified_framework/core"
        "unified_framework/schemas"
        "unified_framework/commands"
        "unified_framework/agents"
        "unified_framework/mcp"
        "unified_framework/cli"
        "unified_framework/tests/unit"
        "unified_framework/tests/integration"
        "unified_framework/tests/e2e"
        "logs"
        "data/cache"
    )

    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        echo -e "${GREEN}✓${NC} Created: $dir"
    done
}

# Initialize Python virtual environment
setup_python_env() {
    echo -e "${BLUE}Setting up Python environment...${NC}"

    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo -e "${GREEN}✓${NC} Created virtual environment"
    else
        echo -e "${YELLOW}⚠${NC} Virtual environment already exists"
    fi

    # Activate venv
    source venv/bin/activate

    # Upgrade pip
    pip install --upgrade pip
    echo -e "${GREEN}✓${NC} Upgraded pip"
}

# Install Python dependencies
install_python_deps() {
    echo -e "${BLUE}Installing Python dependencies...${NC}"

    # Core dependencies
    pip install fastapi uvicorn pydantic click aiohttp pytest pytest-asyncio pytest-cov black isort flake8 mypy

    # IDFW dependencies
    pip install openai jsonschema pyyaml

    echo -e "${GREEN}✓${NC} Installed Python dependencies"
}

# Setup Node environment
setup_node_env() {
    echo -e "${BLUE}Setting up Node environment...${NC}"

    # Create package.json if it doesn't exist
    if [ ! -f "package.json" ]; then
        cat > package.json << 'EOF'
{
  "name": "idfw-unified",
  "version": "1.0.0",
  "description": "IDFW - IDEA Framework Unified",
  "main": "index.js",
  "scripts": {
    "test": "jest",
    "lint": "eslint .",
    "build": "tsc",
    "dev": "nodemon"
  },
  "keywords": ["idfw", "dev-sentinel", "mcp", "unified-framework"],
  "author": "Pegues Innovations",
  "license": "MIT"
}
EOF
        echo -e "${GREEN}✓${NC} Created package.json"
    fi

    # Install Node dependencies
    npm install --save-dev typescript @types/node jest eslint nodemon
    echo -e "${GREEN}✓${NC} Installed Node dependencies"
}

# Setup Git configuration
setup_git() {
    echo -e "${BLUE}Setting up Git configuration...${NC}"

    # Create .gitignore if it doesn't exist
    if [ ! -f ".gitignore" ]; then
        cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Project specific
logs/
data/cache/
*.log
.env
.env.local
secrets/
*.key
*.pem

# Build
dist/
build/
*.egg-info/
.coverage
htmlcov/
.pytest_cache/
.mypy_cache/

# Documentation
docs/_build/
EOF
        echo -e "${GREEN}✓${NC} Created .gitignore"
    fi

    # Set up git hooks
    if [ -d ".git" ]; then
        # Pre-commit hook
        cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Run tests before commit
echo "Running pre-commit tests..."
python -m pytest tests/unit/ -v --tb=short
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
echo "Tests passed!"
EOF
        chmod +x .git/hooks/pre-commit
        echo -e "${GREEN}✓${NC} Set up git hooks"
    fi
}

# Create initial configuration files
create_config_files() {
    echo -e "${BLUE}Creating configuration files...${NC}"

    # Create unified config
    cat > unified_framework/config.yaml << 'EOF'
# IDFWU Configuration
project:
  name: "IDFW Unified Framework"
  version: "1.0.0"
  linear_project_id: "4d649a6501f7"

idfw:
  enabled: true
  schema_version: "2020-12"
  generators:
    - IDDG
    - IDPG
    - IDAA

dev_sentinel:
  enabled: true
  agents:
    - SAA
    - VCMA
    - VCLA
    - CDIA
    - RDIA

integration:
  command_prefix:
    yung: "$"
    idfw: "@"
    unified: "#"
    slash: "/"

mcp:
  stdio: true
  http: true
  port: 8888

state:
  sync_interval: 1000
  cache_ttl: 3600
EOF
    echo -e "${GREEN}✓${NC} Created config.yaml"
}

# Create initial Python files
create_python_files() {
    echo -e "${BLUE}Creating initial Python files...${NC}"

    # Create __init__.py files
    touch unified_framework/__init__.py
    touch unified_framework/core/__init__.py
    touch unified_framework/schemas/__init__.py
    touch unified_framework/commands/__init__.py
    touch unified_framework/agents/__init__.py
    touch unified_framework/mcp/__init__.py
    touch unified_framework/cli/__init__.py
    touch unified_framework/tests/__init__.py

    # Create main entry point
    cat > unified_framework/main.py << 'EOF'
"""
IDFWU - IDEA Framework Unified
Main entry point for the unified framework
Linear Project: 4d649a6501f7
"""

import asyncio
from typing import Optional
import click
import yaml
from pathlib import Path

@click.group()
def cli():
    """IDFW Unified Framework CLI"""
    pass

@cli.command()
def init():
    """Initialize the unified framework"""
    click.echo("Initializing IDFW Unified Framework...")
    click.echo("Linear Project: IDFWU (4d649a6501f7)")

@cli.command()
@click.argument('command')
def execute(command: str):
    """Execute a unified command"""
    click.echo(f"Executing: {command}")
    # Command execution logic here

if __name__ == "__main__":
    cli()
EOF
    echo -e "${GREEN}✓${NC} Created Python entry points"
}

# Create test files
create_test_files() {
    echo -e "${BLUE}Creating test files...${NC}"

    # Create pytest.ini
    cat > pytest.ini << 'EOF'
[pytest]
testpaths = unified_framework/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers --cov=unified_framework --cov-report=term-missing
asyncio_mode = auto
EOF

    # Create sample test
    cat > unified_framework/tests/test_main.py << 'EOF'
"""Test main module"""

def test_import():
    """Test that main module can be imported"""
    import unified_framework.main
    assert unified_framework.main is not None
EOF

    echo -e "${GREEN}✓${NC} Created test configuration"
}

# Setup Linear integration
setup_linear() {
    echo -e "${BLUE}Setting up Linear integration...${NC}"

    # Create Linear configuration
    cat > .linear.yaml << 'EOF'
# Linear Configuration for IDFWU
project_id: "4d649a6501f7"
project_name: "IDFWU - IDEA Framework Unified"
team: "Pegues Innovations"
workflow:
  states:
    - Todo
    - In Progress
    - In Review
    - Done
    - Cancelled
labels:
  - idfw
  - dev-sentinel
  - integration
  - schema
  - agent
  - mcp
  - cli
  - testing
  - documentation
EOF

    echo -e "${GREEN}✓${NC} Created Linear configuration"
}

# Main execution
main() {
    echo -e "${YELLOW}Starting IDFWU Project Initialization${NC}"
    echo "======================================"

    check_prerequisites
    create_directories
    setup_python_env
    install_python_deps
    setup_node_env
    setup_git
    create_config_files
    create_python_files
    create_test_files
    setup_linear

    echo ""
    echo -e "${GREEN}✨ Project initialization complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Activate Python environment: source venv/bin/activate"
    echo "2. Run tests: pytest"
    echo "3. Start development: python unified_framework/main.py"
    echo "4. Check Linear project: https://linear.app/pegues-innovations/project/idfwu-idea-framework-unified-4d649a6501f7"
    echo ""
    echo "Available slash commands in .claude/slash-commands/"
    echo "Run '/autofix' to start automatic issue resolution"
}

# Run main function
main