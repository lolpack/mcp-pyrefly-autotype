#!/usr/bin/env python3
"""
Simple test script to demonstrate the MCP Pyrefly Autotype server.
Run this script to test the server functionality locally.
"""

import asyncio
import tempfile
import os
from mcp_pyrefly_autotype.server import PyreflyAnalyzer, run_pyrefly_autotype, run_pyrefly_check

async def test_workflow():
    """Test the complete workflow with the example untyped file."""
    
    # Use the example file in the project
    example_file = "example_untyped.py"
    
    if not os.path.exists(example_file):
        print(f"❌ Example file {example_file} not found!")
        return
    
    print(f"🔍 Testing MCP Pyrefly Autotype Server with {example_file}")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = PyreflyAnalyzer()
    
    # Step 1: Analyze the file
    print("\n1️⃣ Analyzing file for type annotation needs...")
    try:
        analysis = await analyzer.analyze_file(example_file)
        if "error" in analysis:
            print(f"❌ Analysis failed: {analysis['error']}")
            print("ℹ️  This is expected if Pyrefly is not installed")
            print("   Install with: pip install pyrefly")
            return
        
        print(f"✅ Analysis complete!")
        print(f"   Functions needing types: {len(analysis.get('functions_needing_types', []))}")
        print(f"   Variables needing types: {len(analysis.get('variables_needing_types', []))}")
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        print("ℹ️  This is likely because Pyrefly is not installed")
        return
    
    # Step 2: Create a copy for type addition
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            with open(example_file, 'r') as original:
                f.write(original.read())
            temp_file = f.name
    
        print(f"\n2️⃣ Adding type annotations to {os.path.basename(temp_file)}...")
        try:
            result = await run_pyrefly_autotype(temp_file, {"safe_mode": True})
            if result["success"]:
                print("✅ Type annotations added successfully!")
                print(f"   Pyrefly output: {result['stdout'][:100]}...")
            else:
                print(f"❌ Type addition failed: {result.get('error', result.get('stderr', 'Unknown error'))}")
                
        except Exception as e:
            print(f"❌ Type addition error: {e}")
        
        # Step 3: Type check the result
        print(f"\n3️⃣ Type checking {os.path.basename(temp_file)}...")
        try:
            pyrefly_result = await run_pyrefly_check(temp_file)
            if pyrefly_result["success"]:
                print("✅ Type checking passed!")
            else:
                print("⚠️  Type checking found issues:")
                print(pyrefly_result["output"][:200] + "..." if len(pyrefly_result["output"]) > 200 else pyrefly_result["output"])
                
        except Exception as e:
            print(f"❌ Type checking error: {e}")
        
        # Step 4: Show the differences
        print(f"\n4️⃣ Comparing original and typed versions...")
        try:
            with open(example_file, 'r') as orig:
                original_lines = orig.readlines()
            
            with open(temp_file, 'r') as typed:
                typed_lines = typed.readlines()
            
            print(f"   Original file: {len(original_lines)} lines")
            print(f"   Typed file: {len(typed_lines)} lines")
            
            # Show first few lines that are different
            print("   📝 Sample differences:")
            for i, (orig, typed) in enumerate(zip(original_lines[:10], typed_lines[:10])):
                if orig.strip() != typed.strip():
                    print(f"   Line {i+1}:")
                    print(f"     - {orig.rstrip()}")
                    print(f"     + {typed.rstrip()}")
                    
        except Exception as e:
            print(f"❌ Comparison error: {e}")
    
    finally:
        # Cleanup with better error handling
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except (OSError, PermissionError):
                # On Windows, sometimes files are still locked
                import time
                time.sleep(0.1)
                try:
                    os.unlink(temp_file)
                except (OSError, PermissionError):
                    # If we still can't delete it, just leave it
                    pass
    
    print("\n🎉 Test workflow complete!")
    print("\nℹ️  To use with an MCP client:")
    print("   python -m mcp_pyrefly_autotype.server")

if __name__ == "__main__":
    asyncio.run(test_workflow())
