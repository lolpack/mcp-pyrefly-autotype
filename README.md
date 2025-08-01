# [WORK IN PROGRESS AND UNTESTED - USE AT OWN RISK] MCP Pyrefly Autotype Server

A Model Context Protocol (MCP) server that provides automatic Python type annotation using Pyrefly. This server enables LLMs and AI coding assistants to analyze Python code, add type annotations, and perform type checking seamlessly.

## What is the Model Context Protocol (MCP)?

The Model Context Protocol (MCP) is an open standard that enables AI assistants and language models to securely access external data sources and tools. MCP servers act as bridges between AI systems and various resources, providing structured access to information and capabilities.

### How MCP Works

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LLM/AI Client │◄──►│   MCP Server    │◄──►│  External Tools │
│   (e.g. Claude) │    │  (This Project) │    │   (Pyrefly)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

MCP servers can provide:
- **Resources**: Static or dynamic data sources (files, databases, APIs)
- **Tools**: Executable functions that perform actions 
- **Prompts**: Templated prompts for specific tasks

This allows AI assistants to:
- Access real-time information
- Perform complex operations
- Integrate with existing tools and workflows
- Maintain security through controlled access

## Features

This MCP server provides comprehensive Python type annotation capabilities:

### 🔍 **Analysis Tools**
- **File Analysis**: Analyze individual Python files for missing type annotations
- **Project Context**: Get project-wide type information for better inference
- **Pyrefly Integration**: Leverage Pyrefly's powerful type inference engine

### ⚡ **Type Enhancement**
- **Automatic Type Addition**: Add type annotations using Pyrefly's autotype feature
- **File-based Processing**: Process individual Python files with type annotations
- **Optional Backup**: Can create backup files before modification (when requested)
- **Project Integration**: Respects pyrefly configuration files

### ✅ **Type Checking**
- **Pyrefly Integration**: Validate type annotations using Pyrefly's built-in type checker
- **Error Reporting**: Basic type checking results and error output
- **File-based Validation**: Check individual files for type errors

### 🤖 **LLM Integration**
- **Basic Prompts**: Pre-built prompts for type analysis tasks
- **Structured Data**: JSON-formatted analysis results
- **Simple Workflows**: Basic analyze → annotate → verify workflows

## Why Use This MCP Server?

### For LLMs and AI Assistants
- **MCP Integration**: Works with MCP-compatible AI clients
- **JSON Responses**: Provides structured data for better decision making
- **Basic Context**: Simple project structure analysis
- **Error Handling**: Basic error reporting and graceful failure handling

### For Developers
- **Cold Start Helper**: Assists with completely untyped codebases
- **Basic Typing**: Simple type annotation workflows
- **File Processing**: Individual file type checking and annotation
- **Tool Integration**: Basic integration with existing Python development workflows

## Installation

### Prerequisites
- Python 3.8 or higher
- uv (fast Python package manager): `pip install uv` or see [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/)

### Install the MCP Server

```bash
# Clone or download this repository
git clone https://github.com/your-username/mcp-pyrefly-autotype.git
cd mcp-pyrefly-autotype

# Install dependencies with uv
uv sync

# For development (includes dev dependencies)
uv sync --dev

# Alternative: traditional pip install
# pip install -e .
# pip install -e ".[dev]"
```

## Usage

### Running the Server

The server can be run directly or integrated with MCP-compatible clients:

```bash
# Run directly (for testing)
uv run python -m mcp_pyrefly_autotype.server

# Or use the installed script (after uv sync)
uv run mcp-pyrefly-autotype

# Alternative: activate virtual environment first
uv shell
python -m mcp_pyrefly_autotype.server
```

### Integration with AI Clients

#### Claude Desktop (Example Configuration)

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "pyrefly-autotype": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_pyrefly_autotype.server"],
      "env": {}
    }
  }
}
```

#### VS Code with Copilot

1. Install the MCP extension for VS Code
2. Configure the server in your workspace settings:

```json
{
  "mcp.servers": [
    {
      "name": "pyrefly-autotype",
      "command": ["uv", "run", "python", "-m", "mcp_pyrefly_autotype.server"]
    }
  ]
}
```

## Available Tools

### `analyze_python_file`
Analyze a Python file for missing type annotations.

**Parameters:**
- `file_path` (required): Path to the Python file
- `detailed` (optional): Include detailed analysis information

**Example:**
```python
# LLM can request:
# "Analyze the file 'src/utils.py' for type annotation needs"
```

### `add_types_to_file`
Add type annotations to a Python file using Pyrefly.

**Parameters:**
- `file_path` (required): Path to the Python file
- `backup` (optional): Create backup before modifying (default: true)

**Example:**
```python
# LLM can request:
# "Add type annotations to 'src/models.py'"
```

### `type_check_file`
Run type checking on a Python file using Pyrefly.

**Parameters:**
- `file_path` (required): Path to the Python file

**Example:**
```python
# LLM can request:
# "Type check the file 'src/api.py' and report any errors"
```

### `get_project_context`
Get project-wide type information for better inference.

**Parameters:**
- `project_path` (required): Path to the project directory

**Example:**
```python
# LLM can request:
# "Analyze the project structure for type annotation opportunities"
```

## Available Prompts

### `analyze_typing_needs`
Generate analysis prompts for type annotation needs.

### `type_improvement_plan`
Create a comprehensive plan for improving type coverage in a project.

## Example Workflows

### 1. Complete File Type Enhancement

```python
# LLM workflow:
# 1. "Analyze 'calculator.py' for type needs"
# 2. "Add types to 'calculator.py'"
# 3. "Type check 'calculator.py' and report results"
```

### 2. Project-Wide Type Analysis

```python
# LLM workflow:
# 1. "Get project context for '/my-project'"
# 2. "Create a type improvement plan for the project"
# 3. "Prioritize files for type annotation"
```

### 3. Cold Start Type Addition

```python
# For completely untyped files:
# 1. "Analyze 'legacy_code.py' - it has no types at all"
# 2. "Add types to 'legacy_code.py'" 
# 3. "Check for type errors and suggest corrections"
```

## Use Cases

### 🥶 **Cold Start Projects**
- **Challenge**: Legacy codebases with no type annotations
- **Solution**: Use Pyrefly autotype with basic MCP integration
- **Benefit**: Start adding types to untyped codebases

### 📈 **Incremental Typing**
- **Challenge**: Adding types to active projects gradually
- **Solution**: File-by-file type annotation with basic project context
- **Benefit**: Gradual type adoption without major disruption

### 🔧 **CI/CD Integration**
- **Challenge**: Maintaining type quality in team projects
- **Solution**: Basic type checking integration in pipelines
- **Benefit**: Simple type validation workflows

### 🤝 **LLM-Assisted Development**
- **Challenge**: LLMs need context about typing needs
- **Solution**: Basic structured analysis data and simple prompts
- **Benefit**: Improved AI assistance for Python type annotation tasks

## Configuration

### Pyrefly Configuration

The server respects Pyrefly's configuration. You can configure Pyrefly in your project using either:

1. **`pyrefly.toml`** file in your project root:

```toml
# Files to include in type checking  
project-includes = ["src/**/*.py"]

# Files to exclude from type checking
project-excludes = ["tests/**", "**/__pycache__/**"]

# Python version to assume
python-version = "3.12"

# How to handle untyped function definitions
untyped-def-behavior = "check-and-infer-return-type"

# Configure specific error types
[errors]
# Enable/disable specific error types
bad-assignment = true
missing-return-type = true
```

2. **`pyproject.toml`** file under the `[tool.pyrefly]` section:

```toml
[tool.pyrefly]
# Files to include in type checking
project-includes = ["src/**/*.py"]

# Files to exclude from type checking  
project-excludes = ["tests/**", "**/__pycache__/**"]

# Python version and platform
python-version = "3.12"
python-platform = "linux"

# Type checking behavior
untyped-def-behavior = "check-and-infer-return-type"
ignore-missing-imports = ["requests.*", "numpy.*"]

# Error configuration
[tool.pyrefly.errors]
bad-assignment = true
missing-return-type = true
```

See the [Pyrefly Configuration Documentation](https://pyrefly.org/en/docs/configuration/) for all available options.

## Development

### Running Tests

```bash
# Run all tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=mcp_pyrefly_autotype

# Run specific test
uv run python tests/test_server.py

# Test server functions directly
uv run python test_direct.py

# Run demo workflow
uv run python test_demo.py
```

### Testing the MCP Server

The project includes several test files to verify functionality:

- `tests/test_server.py` - Comprehensive test suite with mocked pyrefly calls
- `test_direct.py` - Direct testing of server functions with real pyrefly
- `test_demo.py` - Interactive demo showing the complete workflow
- `simple_untyped.py` - Example file for testing type annotation

To test the server end-to-end:

```bash
# 1. Test with a simple untyped file
uv run python test_demo.py

# 2. Test server functions directly  
uv run python test_direct.py

# 3. Run the MCP server (for client integration)
uv run python -m mcp_pyrefly_autotype.server
```

### Code Quality

```bash
# Format code
uv run black src/ tests/

# Lint code  
uv run ruff check src/ tests/

# Type check
uv run pyrefly check src/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Related Projects

- [Pyrefly](https://github.com/facebook/pyrefly) - The core type inference engine
- [Model Context Protocol](https://github.com/modelcontextprotocol/specification) - The MCP specification

## Support

For questions and support:
- Open an issue on GitHub
- Check the Pyrefly documentation
- Review the MCP specification

---

*This MCP server bridges the gap between AI assistants and Python type annotation tools, enabling seamless integration of type enhancement workflows in AI-powered development environments.*
