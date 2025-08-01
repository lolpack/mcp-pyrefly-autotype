import asyncio
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio

server = Server("mcp-pyrefly-autotype")

class PyreflyAnalyzer:
    """Wrapper for Pyrefly autotype functionality."""
    
    def __init__(self):
        self.project_context: Dict[str, Any] = {}
    
    async def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a Python file using Pyrefly's analysis capabilities."""
        try:
            # Use Pyrefly to analyze the file
            result = await self.run_pyrefly_command([
                "uv", "run", "pyrefly", "autotype", file_path
            ])
            
            if result["success"]:
                # Parse Pyrefly's output for analysis information
                analysis = self._parse_pyrefly_analysis(result["stdout"], file_path)
                return analysis
            else:
                return {
                    "error": result.get("error", result.get("stderr", "Unknown error")),
                    "file_path": file_path
                }
                
        except Exception as e:
            return {"error": str(e), "file_path": file_path}
    
    def _parse_pyrefly_analysis(self, output: str, file_path: str) -> Dict[str, Any]:
        """Parse Pyrefly analysis output into structured data."""
        functions_needing_types: List[str] = []
        variables_needing_types: List[str] = []
        
        analysis: Dict[str, Any] = {
            "file_path": file_path,
            "functions_needing_types": functions_needing_types,
            "variables_needing_types": variables_needing_types,
            "suggested_types": {},
            "total_functions": 0,
            "total_variables": 0,
            "pyrefly_output": output
        }
        
        # Parse the output to extract type information
        lines = output.split('\n')
        for line in lines:
            line = line.strip()
            if "function" in line.lower() and "type" in line.lower():
                # Extract function information from Pyrefly output
                # This will depend on Pyrefly's actual output format
                functions_needing_types.append(line)
            elif "variable" in line.lower() and "type" in line.lower():
                variables_needing_types.append(line)
        
        return analysis
    
    async def get_project_context(self, project_path: str) -> Dict[str, Any]:
        """Get project-wide type information using Pyrefly."""
        context: Dict[str, Any] = {
            "project_path": project_path,
            "python_files": [],
            "pyrefly_compatible": False,
            "analysis_summary": {}
        }
        
        try:
            # Check if Pyrefly can analyze this project
            pyrefly_check = await self.run_pyrefly_command([
                "uv", "run", "pyrefly", "check", project_path
            ])
            
            context["pyrefly_compatible"] = pyrefly_check["success"]
            
            # Collect Python files
            for root, dirs, files in os.walk(project_path):
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
                
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        context["python_files"].append(file_path)
            
            if pyrefly_check["success"]:
                context["analysis_summary"] = {
                    "output": pyrefly_check["stdout"],
                    "total_files": len(context["python_files"])
                }
        
        except Exception as e:
            context["error"] = str(e)
        
        return context
    
    async def run_pyrefly_command(self, cmd: List[str], timeout: int = 60) -> Dict[str, Any]:
        """Run a Pyrefly command and return the results."""
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Pyrefly execution timed out after {timeout}s"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

async def run_pyrefly_autotype(file_path: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Run Pyrefly autotype on a file and return the results."""
    try:
        cmd = ["uv", "run", "pyrefly", "autotype", file_path]
        
        # Note: Pyrefly autotype doesn't have --aggressive, --safe, or --dry-run flags
        # We can add other valid options from the help if needed
        if options:
            if options.get("verbose"):
                cmd.append("--verbose")
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=60
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Pyrefly autotype execution timed out"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

async def run_pyrefly_check(file_path: str) -> Dict[str, Any]:
    """Run pyrefly type checking on a file."""
    try:
        result = subprocess.run(
            ["uv", "run", "pyrefly", "check", file_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "errors": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Pyrefly check execution timed out"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Initialize the Pyrefly analyzer
pyrefly_analyzer = PyreflyAnalyzer()

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """
    List available resources for Python type analysis.
    """
    return [
        types.Resource(
            uri=AnyUrl("pyrefly://analysis/status"),
            name="Pyrefly Analysis Status",
            description="Current status and capabilities of the Pyrefly type analyzer",
            mimeType="application/json",
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """
    Read resource information about Pyrefly capabilities.
    """
    if uri.scheme != "pyrefly":
        raise ValueError(f"Unsupported URI scheme: {uri.scheme}")
    
    if str(uri) == "pyrefly://analysis/status":
        return """{
    "status": "active",
    "capabilities": [
        "Python file analysis",
        "Type inference",
        "Type checking",
        "Project context analysis"
    ],
    "supported_tools": [
        "analyze_python_file",
        "add_types_to_file", 
        "type_check_file",
        "get_project_context"
    ]
}"""
    
    raise ValueError(f"Unknown resource: {uri}")

@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """
    List available prompts for Python type analysis.
    """
    return [
        types.Prompt(
            name="analyze_typing_needs",
            description="Analyze a Python file or project to determine typing needs",
            arguments=[
                types.PromptArgument(
                    name="file_path",
                    description="Path to the Python file to analyze",
                    required=True,
                ),
                types.PromptArgument(
                    name="include_suggestions",
                    description="Include type suggestions in the analysis",
                    required=False,
                )
            ],
        ),
        types.Prompt(
            name="type_improvement_plan",
            description="Create a plan for improving type coverage in a project",
            arguments=[
                types.PromptArgument(
                    name="project_path",
                    description="Path to the project directory",
                    required=True,
                ),
                types.PromptArgument(
                    name="priority",
                    description="Priority level (high/medium/low)",
                    required=False,
                )
            ],
        )
    ]

@server.get_prompt()
async def handle_get_prompt(
    name: str, arguments: dict[str, str] | None
) -> types.GetPromptResult:
    """
    Generate prompts for Python type analysis tasks.
    """
    if name == "analyze_typing_needs":
        file_path = (arguments or {}).get("file_path", "")
        include_suggestions = (arguments or {}).get("include_suggestions", "false").lower() == "true"
        
        if not file_path:
            raise ValueError("file_path argument is required")
        
        # Analyze the file
        analysis = await pyrefly_analyzer.analyze_file(file_path)
        
        suggestions_text = ""
        if include_suggestions:
            suggestions_text = "\n\nPlease provide specific type annotations for the identified functions and variables."
        
        return types.GetPromptResult(
            description=f"Type analysis for {file_path}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"""Analyze this Python file for type annotation opportunities:

File: {file_path}
Pyrefly Analysis Results:

Functions needing types: {len(analysis.get('functions_needing_types', []))}
Variables needing types: {len(analysis.get('variables_needing_types', []))}

Pyrefly Output:
{analysis.get('pyrefly_output', 'No output available')}

Details:
{analysis}
{suggestions_text}""",
                    ),
                )
            ],
        )
    
    elif name == "type_improvement_plan":
        project_path = (arguments or {}).get("project_path", "")
        priority = (arguments or {}).get("priority", "medium")
        
        if not project_path:
            raise ValueError("project_path argument is required")
        
        context = await pyrefly_analyzer.get_project_context(project_path)
        
        return types.GetPromptResult(
            description=f"Type improvement plan for {project_path}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"""Create a type improvement plan for this Python project:

Project: {project_path}
Priority: {priority}
Python files found: {len(context.get('python_files', []))}

Project context:
{context}

Please suggest a prioritized plan for adding type annotations, considering:
1. Files with the lowest type coverage
2. Critical functions and public APIs
3. Dependencies between modules
4. Incremental typing strategy""",
                    ),
                )
            ],
        )
    
    raise ValueError(f"Unknown prompt: {name}")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools for Python type analysis and modification.
    """
    return [
        types.Tool(
            name="analyze_python_file",
            description="Analyze a Python file for missing type annotations",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the Python file to analyze"
                    },
                    "detailed": {
                        "type": "boolean", 
                        "description": "Include detailed analysis information",
                        "default": False
                    }
                },
                "required": ["file_path"],
            },
        ),
        types.Tool(
            name="add_types_to_file",
            description="Add type annotations to a Python file using Pyrefly",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the Python file to add types to"
                    },
                    "backup": {
                        "type": "boolean",
                        "description": "Create a backup of the original file",
                        "default": True
                    },
                    "aggressive": {
                        "type": "boolean",
                        "description": "Use aggressive type inference",
                        "default": False
                    },
                    "safe_mode": {
                        "type": "boolean",
                        "description": "Use safe mode for type inference",
                        "default": True
                    }
                },
                "required": ["file_path"],
            },
        ),
        types.Tool(
            name="type_check_file",
            description="Run type checking on a Python file using Pyrefly",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the Python file to type check"
                    }
                },
                "required": ["file_path"],
            },
        ),
        types.Tool(
            name="get_project_context",
            description="Get project-wide type information for better type inference",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to the project directory"
                    }
                },
                "required": ["project_path"],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests for Python type analysis.
    """
    if not arguments:
        raise ValueError("Missing arguments")

    if name == "analyze_python_file":
        file_path = arguments.get("file_path")
        detailed = arguments.get("detailed", False)
        
        if not file_path:
            raise ValueError("Missing file_path argument")
        
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")
        
        analysis = await pyrefly_analyzer.analyze_file(file_path)
        
        if detailed:
            result_text = f"""Detailed Pyrefly Analysis for {file_path}:

Functions needing types ({len(analysis.get('functions_needing_types', []))}):
{chr(10).join(f"  - {func}" for func in analysis.get('functions_needing_types', []))}

Variables needing types ({len(analysis.get('variables_needing_types', []))}):
{chr(10).join(f"  - {var}" for var in analysis.get('variables_needing_types', []))}

Suggested types:
{chr(10).join(f"  - {name}: {type_hint}" for name, type_hint in analysis.get('suggested_types', {}).items())}

Pyrefly Output:
{analysis.get('pyrefly_output', 'No output available')}"""
        else:
            result_text = f"""Pyrefly Analysis for {file_path}:
Functions needing types: {len(analysis.get('functions_needing_types', []))}
Variables needing types: {len(analysis.get('variables_needing_types', []))}"""
        
        return [types.TextContent(type="text", text=result_text)]
    
    elif name == "add_types_to_file":
        file_path = arguments.get("file_path")
        backup = arguments.get("backup", True)
        aggressive = arguments.get("aggressive", False)
        safe_mode = arguments.get("safe_mode", True)
        
        if not file_path:
            raise ValueError("Missing file_path argument")
        
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")
        
        # Create backup if requested
        if backup:
            backup_path = f"{file_path}.backup"
            try:
                import shutil
                shutil.copy2(file_path, backup_path)
            except Exception as e:
                return [types.TextContent(type="text", text=f"Failed to create backup: {e}")]
        
        # Run Pyrefly
        options = {
            "aggressive": aggressive,
            "safe_mode": safe_mode
        }
        
        result = await run_pyrefly_autotype(file_path, options)
        
        if result["success"]:
            return [types.TextContent(
                type="text", 
                text=f"Successfully added types to {file_path}\n\nOutput:\n{result['stdout']}"
            )]
        else:
            return [types.TextContent(
                type="text", 
                text=f"Failed to add types to {file_path}\n\nError:\n{result.get('error', result.get('stderr', 'Unknown error'))}"
            )]
    
    elif name == "type_check_file":
        file_path = arguments.get("file_path")
        
        if not file_path:
            raise ValueError("Missing file_path argument")
        
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")
        
        result = await run_pyrefly_check(file_path)
        
        if result["success"]:
            return [types.TextContent(
                type="text", 
                text=f"Type checking passed for {file_path}\n\nOutput:\n{result['output']}"
            )]
        else:
            return [types.TextContent(
                type="text", 
                text=f"Type checking found issues in {file_path}\n\nErrors:\n{result['output']}\n{result.get('errors', '')}"
            )]
    
    elif name == "get_project_context":
        project_path = arguments.get("project_path")
        
        if not project_path:
            raise ValueError("Missing project_path argument")
        
        if not os.path.exists(project_path):
            raise ValueError(f"Project path not found: {project_path}")
        
        context = await pyrefly_analyzer.get_project_context(project_path)
        
        result_text = f"""Project Context for {project_path}:

Python files found: {len(context.get('python_files', []))}
Pyrefly compatible: {context.get('pyrefly_compatible', False)}

Analysis summary:
{context.get('analysis_summary', {}).get('output', 'No analysis available')}

Files:
{chr(10).join(f"  - {file}" for file in context.get('python_files', [])[:20])}
{"  ... and more" if len(context.get('python_files', [])) > 20 else ""}"""
        
        return [types.TextContent(type="text", text=result_text)]
    
    raise ValueError(f"Unknown tool: {name}")

async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-pyrefly-autotype",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())