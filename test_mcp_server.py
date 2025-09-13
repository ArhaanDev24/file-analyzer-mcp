#!/usr/bin/env python3
"""
Test script to verify MCP server functionality.
"""

import asyncio
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from file_analyzer_mcp.server import FileAnalyzerMCPServer
from mcp.types import CallToolRequest


async def test_server():
    """Test the MCP server functionality."""
    print("Testing File Analyzer MCP Server...")
    
    # Create server instance
    server = FileAnalyzerMCPServer()
    
    # Test list_tools
    print("\n1. Testing list_tools...")
    tools = await server.handle_list_tools()
    print(f"Available tools: {[tool.name for tool in tools]}")
    
    # Test analyze_file
    print("\n2. Testing analyze_file...")
    
    # Create a mock request object
    class MockRequest:
        def __init__(self, name, arguments):
            self.name = name
            self.arguments = arguments
    
    request = MockRequest(
        name="analyze_file",
        arguments={
            "file_path": "file-analyzer-mcp/src/file_analyzer_mcp/models.py",
            "analysis_type": "full"
        }
    )
    
    try:
        result = await server.handle_call_tool(request)
        if result and len(result) > 0:
            # Parse the JSON result
            result_data = json.loads(result[0].text)
            print(f"Analysis successful!")
            print(f"  Language: {result_data['language']}")
            print(f"  Lines: {result_data['line_count']}")
            print(f"  Size: {result_data['file_size']} bytes")
            if result_data['metrics']:
                print(f"  Functions: {result_data['metrics']['function_count']}")
                print(f"  Classes: {result_data['metrics']['class_count']}")
                print(f"  Complexity: {result_data['metrics']['cyclomatic_complexity']}")
        else:
            print("No result returned")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test analyze_directory
    print("\n3. Testing analyze_directory...")
    request = MockRequest(
        name="analyze_directory",
        arguments={
            "directory_path": "file-analyzer-mcp/src/file_analyzer_mcp",
            "recursive": False
        }
    )
    
    try:
        result = await server.handle_call_tool(request)
        if result and len(result) > 0:
            result_data = json.loads(result[0].text)
            print(f"Directory analysis result: {result_data}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test search_files
    print("\n4. Testing search_files...")
    request = MockRequest(
        name="search_files",
        arguments={
            "pattern": "class",
            "search_type": "content"
        }
    )
    
    try:
        result = await server.handle_call_tool(request)
        if result and len(result) > 0:
            result_data = json.loads(result[0].text)
            print(f"Search completed!")
            print(f"  Total matches: {result_data['total_matches']}")
            print(f"  Search time: {result_data['search_time']:.3f}s")
            print(f"  First match: {result_data['matches'][0]['file_path'] if result_data['matches'] else 'None'}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nMCP Server test completed!")


if __name__ == "__main__":
    asyncio.run(test_server())