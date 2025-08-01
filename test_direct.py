#!/usr/bin/env python3
"""Simple test script to directly test pyrefly functionality."""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

# Import our server components directly for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_pyrefly_autotype.server import (
    PyreflyAnalyzer,
    run_pyrefly_autotype,
    run_pyrefly_check
)

async def test_pyrefly_functions():
    """Test the pyrefly functions directly."""
    
    test_file = Path(__file__).parent / "test_untyped_code.py"
    
    print(f"🧪 Testing Pyrefly Functions")
    print("=" * 50)
    print(f"📄 Test file: {test_file}")
    
    # Test 1: Direct pyrefly check to see what we get
    print(f"\n🔍 Running pyrefly check on test file...")
    try:
        result = subprocess.run(
            ["uv", "run", "pyrefly", "check", str(test_file)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        print(f"📊 Pyrefly check exit code: {result.returncode}")
        print(f"📤 Pyrefly check stdout:\n{result.stdout}")
        if result.stderr:
            print(f"⚠️ Pyrefly check stderr:\n{result.stderr}")
    except Exception as e:
        print(f"❌ Direct pyrefly check failed: {e}")
    
    # Test 2: Test our analyzer
    print(f"\n🔍 Testing PyreflyAnalyzer...")
    analyzer = PyreflyAnalyzer()
    
    try:
        analysis_result = await analyzer.analyze_file(str(test_file))
        print("📊 Analysis result:")
        print(json.dumps(analysis_result, indent=2))
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Test autotype function
    print(f"\n⚡ Testing run_pyrefly_autotype...")
    try:
        autotype_result = await run_pyrefly_autotype(str(test_file), {"safe_mode": True})
        print("✨ Autotype result:")
        print(json.dumps(autotype_result, indent=2))
    except Exception as e:
        print(f"❌ Autotype failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Test check function  
    print(f"\n🎯 Testing run_pyrefly_check...")
    try:
        check_result = await run_pyrefly_check(str(test_file))
        print("🔍 Check result:")
        print(json.dumps(check_result, indent=2))
    except Exception as e:
        print(f"❌ Check failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_pyrefly_functions())
