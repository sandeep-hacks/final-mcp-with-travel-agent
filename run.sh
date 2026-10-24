#!/bin/bash

# Determine script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ENV_DIR="$SCRIPT_DIR/langgraph_env3"
PYTHON_BIN="$ENV_DIR/bin/python"
PIP_BIN="$ENV_DIR/bin/pip"

echo "=== Travelsite macOS Run Environment Setup ==="

# 1. Check if virtual environment exists
if [ ! -d "$ENV_DIR" ]; then
    echo "Creating virtual environment 'langgraph_env3'..."
    python3 -m venv "$ENV_DIR"
fi

if [ ! -f "$PYTHON_BIN" ]; then
    echo "Error: Python executable not found in $ENV_DIR/bin/"
    exit 1
fi

# 2. Check and install packages
check_and_install() {
    local module=$1
    local package=$2
    echo -n "Checking $module... "
    if "$PYTHON_BIN" -c "import $module" 2>/dev/null; then
        echo "Installed."
    else
        echo "Missing. Installing $package..."
        "$PYTHON_BIN" -m pip install --force-reinstall "$package"
    fi
}

# Update pip first to ensure compatibility
echo "Checking pip updates..."
"$PYTHON_BIN" -m pip install --upgrade pip

check_and_install "psycopg" "psycopg[binary]"
check_and_install "langgraph" "langgraph"
check_and_install "langgraph.checkpoint.postgres" "langgraph-checkpoint-postgres"
check_and_install "langchain_groq" "langchain-groq"
check_and_install "langchain_core" "langchain-core"
check_and_install "dotenv" "python-dotenv"
check_and_install "requests" "requests"
check_and_install "tavily" "tavily-python"
check_and_install "streamlit" "streamlit"
check_and_install "langchain_mcp_adapters" "langchain-mcp-adapters"

# 3. Verify .env file and required keys
ENV_FILE="$SCRIPT_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "Warning: .env file not found. Creating a template .env file..."
    cat <<EOT > "$ENV_FILE"
# Groq API Key (Required for travel planning LLM)
GROQ_API_KEY=""

# Tavily API Key (Required for hotel/search tool)
TAVILY_API_KEY=""

# AviationStack API Key (Required for flight search tool)
AVIATIONSTACK_API_KEY=""

# Database Connection (Optional. If unset, falls back to in-memory checkpointer)
DATABASE_URL=""
EOT
    echo "Created .env template. Please open .env and add your API keys."
else
    # Function to check key in .env
    check_key() {
        local key=$1
        # Extract key value, remove quotes and spaces
        local val=$(grep "^[[:space:]]*$key[[:space:]]*=" "$ENV_FILE" | cut -d'=' -f2- | xargs 2>/dev/null | tr -d '"' | tr -d "'")
        if [ -z "$val" ]; then
            echo "Warning: $key is empty or not set in .env. Some features may not work."
        fi
    }

    echo "Checking environment keys in .env..."
    check_key "GROQ_API_KEY"
    check_key "TAVILY_API_KEY"
    check_key "AVIATIONSTACK_API_KEY"
fi

echo "=============================================="
echo "Starting Travelsite application..."
echo "=============================================="
echo "Which interface would you like to run?"
echo "1) Streamlit Web Frontend (Recommended)"
echo "2) Command Line Interface (CLI)"
echo -n "Enter choice [1 or 2, default: 1]: "
read -t 10 choice
if [ -z "$choice" ]; then
    choice="1"
fi

if [ "$choice" = "2" ]; then
    echo "Launching CLI..."
    "$PYTHON_BIN" "$SCRIPT_DIR/main.py"
else
    echo "Launching Streamlit Web Frontend..."
    "$PYTHON_BIN" -m streamlit run "$SCRIPT_DIR/frontend.py"
fi
