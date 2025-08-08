"""Tests for the Pyrefly autotype MCP server."""

import asyncio
import json
import subprocess
import tempfile
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from mcp_pyrefly_autotype.server import (
    PyreflyAnalyzer,
    run_pyrefly_check,
    server
)


class TestPyreflyAnalyzer:
    """Test the PyreflyAnalyzer class."""
    
    async def test_analyze_file_success(self):
        """Test successful file analysis."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def hello(name):
    return f"Hello {name}"

x = 42
""")
            f.flush()
            
            # Mock the Pyrefly command
            analyzer = PyreflyAnalyzer()
            with patch.object(analyzer, 'run_pyrefly_command') as mock_cmd:
                mock_cmd.return_value = {
                    "success": True,
                    "stdout": "Function hello needs type annotations\nVariable x inferred as int",
                    "stderr": "",
                    "returncode": 0
                }
                
                result = await analyzer.analyze_file(f.name)
                
                assert result["file_path"] == f.name
                assert "functions_needing_types" in result
                assert "variables_needing_types" in result
                assert "pyrefly_output" in result
        
        # Clean up
        os.unlink(f.name)
    
    async def test_analyze_file_error(self):
        """Test file analysis with error."""
        analyzer = PyreflyAnalyzer()
        with patch.object(analyzer, 'run_pyrefly_command') as mock_cmd:
            mock_cmd.return_value = {
                "success": False,
                "stderr": "File not found",
                "error": "File not found"
            }

            result = await analyzer.analyze_file("nonexistent.py")

            assert "error" in result
            assert result["file_path"] == "nonexistent.py"


async def test_utility_functions():
    """Test utility functions."""
    
    # Test autotype via analyzer command success
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Types added successfully"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        analyzer = PyreflyAnalyzer()
        result = await analyzer.run_pyrefly_command(["uv", "run", "pyrefly", "autotype", "test.py"])
        
        assert result["success"] is True
        assert result["stdout"] == "Types added successfully"
    
    # Test run_pyrefly_check_success
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success: no issues found"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = await run_pyrefly_check("test.py")
        
        assert result["success"] is True
        assert "no issues found" in result["output"]


async def test_integration_workflow():
    """Test a complete workflow from analysis to type addition."""
    # Create temporary file with proper cleanup
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def greet(name):
    return f"Hello, {name}!"

def add_numbers(a, b):
    return a + b

age = 25
""")
            f.flush()
            temp_file = f.name
        
        # Mock all subprocess calls
        with patch('subprocess.run') as mock_run:
            # Mock Pyrefly analysis
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "Functions greet, add_numbers need type annotations"
            mock_result.stderr = ""
            mock_run.return_value = mock_result
            
            # Test analyze tool
            analyzer = PyreflyAnalyzer()
            analysis = await analyzer.analyze_file(temp_file)
            
            assert analysis["file_path"] == temp_file
            assert "functions_needing_types" in analysis
            
            # Mock Pyrefly autotype
            mock_result.stdout = "Types added successfully to " + temp_file
            
            # Test add types tool
            result = await analyzer.run_pyrefly_command(["uv", "run", "pyrefly", "autotype", temp_file])
            assert result["success"] is True
            
            # Mock Pyrefly check
            mock_result.stdout = "Success: no issues found"
            
            # Test type check tool
            pyrefly_result = await run_pyrefly_check(temp_file)
            assert pyrefly_result["success"] is True
            
    finally:
        # Clean up with better error handling
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except (OSError, PermissionError):
                # On Windows, sometimes files are still locked
                # Try again after a short delay
                import time
                time.sleep(0.1)
                try:
                    os.unlink(temp_file)
                except (OSError, PermissionError):
                    # If we still can't delete it, just leave it
                    # The OS will clean it up eventually
                    pass


async def run_all_tests():
    """Run all tests."""
    print("Running Pyrefly MCP Server Tests...")
    
    # Test PyreflyAnalyzer
    test_analyzer = TestPyreflyAnalyzer()
    
    try:
        await test_analyzer.test_analyze_file_success()
        print("✓ test_analyze_file_success passed")
    except Exception as e:
        print(f"✗ test_analyze_file_success failed: {e}")
    
    try:
        await test_analyzer.test_analyze_file_error()
        print("✓ test_analyze_file_error passed")
    except Exception as e:
        print(f"✗ test_analyze_file_error failed: {e}")
    
    # Test utility functions
    try:
        await test_utility_functions()
        print("✓ test_utility_functions passed")
    except Exception as e:
        print(f"✗ test_utility_functions failed: {e}")
    
    # Test integration workflow
    try:
        await test_integration_workflow()
        print("✓ test_integration_workflow passed")
    except Exception as e:
        print(f"✗ test_integration_workflow failed: {e}")
    
    print("Test run complete!")


if __name__ == "__main__":
    # Run basic tests
    asyncio.run(run_all_tests())
