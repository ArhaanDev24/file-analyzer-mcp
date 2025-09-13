"""
MCP Server implementation for File Analyzer.

This module implements the Model Context Protocol server that provides
file analysis capabilities to AI assistants through standardized tools.
"""

import asyncio
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    CallToolRequest,
    ListToolsRequest,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    ServerCapabilities,
    InitializeRequest,
    InitializeResult,
)

from .models import AnalysisResult, DirectoryAnalysis, SearchResult
from .analyzer_service import FileAnalyzerService
from .config import FileAnalyzerConfig


class FileAnalyzerMCPServer:
    """
    MCP Server for file analysis operations.
    
    This server provides tools for analyzing files, directories, and searching
    through codebases to extract meaningful information for AI assistants.
    """
    
    def __init__(self, config: Optional[FileAnalyzerConfig] = None):
        """Initialize the File Analyzer MCP Server."""
        self.config = config or FileAnalyzerConfig()
        self.server = Server(self.config.server.name)
        self.analyzer_service = FileAnalyzerService()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up MCP protocol handlers."""
        self.server.initialize = self.handle_initialize
        self.server.list_tools = self.handle_list_tools
        self.server.call_tool = self.handle_call_tool
    
    async def handle_initialize(self, request: InitializeRequest) -> InitializeResult:
        """
        Handle MCP initialize request.
        
        Args:
            request: The initialization request
            
        Returns:
            Server capabilities and version information
        """
        return InitializeResult(
            protocolVersion=self.config.server.protocol_version,
            capabilities=ServerCapabilities(
                tools={},
                resources={},
                prompts={},
                logging={}
            ),
            serverInfo={
                "name": self.config.server.name,
                "version": self.config.server.version,
                "description": self.config.server.description
            }
        )
    
    async def handle_list_tools(self) -> List[Tool]:
        """
        Handle MCP list_tools request.
        
        Returns:
            List of available analysis tools
        """
        return [
            Tool(
                name="analyze_file",
                description="Analyze a single file for code metrics, structure, and quality indicators",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file to analyze"
                        },
                        "analysis_type": {
                            "type": "string",
                            "enum": ["basic", "full", "metrics"],
                            "default": "full",
                            "description": "Type of analysis to perform"
                        }
                    },
                    "required": ["file_path"]
                }
            ),
            Tool(
                name="analyze_directory",
                description="Analyze a directory and its contents recursively",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "directory_path": {
                            "type": "string",
                            "description": "Path to the directory to analyze"
                        },
                        "recursive": {
                            "type": "boolean",
                            "default": True,
                            "description": "Whether to analyze subdirectories recursively"
                        },
                        "filters": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "File extension filters (e.g., ['.py', '.js'])"
                        }
                    },
                    "required": ["directory_path"]
                }
            ),
            Tool(
                name="search_files",
                description="Search for files or content using patterns",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "Search pattern (glob, regex, or text)"
                        },
                        "search_type": {
                            "type": "string",
                            "enum": ["glob", "regex", "content"],
                            "default": "glob",
                            "description": "Type of search to perform"
                        },
                        "filters": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "File extension filters"
                        }
                    },
                    "required": ["pattern"]
                }
            )
        ]
    
    async def handle_call_tool(self, request: CallToolRequest) -> List[TextContent | ImageContent | EmbeddedResource]:
        """
        Handle MCP call_tool request.
        
        Args:
            request: The tool call request
            
        Returns:
            Tool execution results
        """
        try:
            if request.name == "analyze_file":
                return await self.handle_analyze_file(request)
            elif request.name == "analyze_directory":
                return await self.handle_analyze_directory(request)
            elif request.name == "search_files":
                return await self.handle_search_files(request)
            else:
                return [TextContent(
                    type="text", 
                    text=f"Unknown tool: {request.name}"
                )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error executing tool {request.name}: {str(e)}"
            )]
    
    async def handle_analyze_file(self, request: CallToolRequest) -> List[TextContent]:
        """
        Handle analyze_file tool request.
        
        Args:
            request: The tool call request
            
        Returns:
            Analysis results
        """
        try:
            # Extract parameters
            file_path = request.arguments.get("file_path")
            analysis_type = request.arguments.get("analysis_type", "full")
            
            if not file_path:
                return [TextContent(
                    type="text",
                    text="Error: file_path parameter is required"
                )]
            
            # Perform analysis
            result = self.analyzer_service.analyze_file(file_path, analysis_type)
            
            # Format result as JSON
            import json
            from datetime import datetime
            
            # Convert datetime to string for JSON serialization
            result_dict = {
                "file_path": result.file_path,
                "file_size": result.file_size,
                "line_count": result.line_count,
                "language": result.language,
                "last_modified": result.last_modified.isoformat() if result.last_modified else None,
                "is_binary": result.is_binary,
                "encoding": result.encoding,
                "metrics": None,
                "errors": result.errors
            }
            
            if result.metrics:
                result_dict["metrics"] = {
                    "function_count": result.metrics.function_count,
                    "class_count": result.metrics.class_count,
                    "import_count": result.metrics.import_count,
                    "comment_lines": result.metrics.comment_lines,
                    "blank_lines": result.metrics.blank_lines,
                    "cyclomatic_complexity": result.metrics.cyclomatic_complexity,
                    "maintainability_index": result.metrics.maintainability_index,
                    "todos": [
                        {
                            "line_number": todo.line_number,
                            "comment_type": todo.comment_type,
                            "text": todo.text,
                            "file_path": todo.file_path
                        }
                        for todo in result.metrics.todos
                    ]
                }
            
            return [TextContent(
                type="text",
                text=json.dumps(result_dict, indent=2)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error analyzing file: {str(e)}"
            )]
    
    async def handle_analyze_directory(self, request: CallToolRequest) -> List[TextContent]:
        """
        Handle analyze_directory tool request.
        
        Args:
            request: The tool call request
            
        Returns:
            Directory analysis results
        """
        try:
            directory_path = request.arguments.get("directory_path")
            recursive = request.arguments.get("recursive", True)
            
            if not directory_path:
                return [TextContent(
                    type="text",
                    text="Error: directory_path parameter is required"
                )]
            
            result = self.analyzer_service.analyze_directory(directory_path, recursive)
            
            import json
            result_dict = {
                "directory_path": result.directory_path,
                "total_files": result.total_files,
                "file_types": result.file_types,
                "total_size": result.total_size,
                "languages": result.languages,
                "analysis_time": result.analysis_time,
                "errors": result.errors
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result_dict, indent=2)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error analyzing directory: {str(e)}"
            )]
    
    async def handle_search_files(self, request: CallToolRequest) -> List[TextContent]:
        """
        Handle search_files tool request.
        
        Args:
            request: The tool call request
            
        Returns:
            Search results
        """
        try:
            pattern = request.arguments.get("pattern")
            search_type = request.arguments.get("search_type", "glob")
            
            if not pattern:
                return [TextContent(
                    type="text",
                    text="Error: pattern parameter is required"
                )]
            
            result = self.analyzer_service.search_files(pattern, search_type)
            
            import json
            result_dict = {
                "total_matches": result.total_matches,
                "search_time": result.search_time,
                "search_pattern": result.search_pattern,
                "search_type": result.search_type,
                "matches": [
                    {
                        "file_path": match.file_path,
                        "line_number": match.line_number,
                        "content": match.content,
                        "context_before": match.context_before,
                        "context_after": match.context_after
                    }
                    for match in result.matches
                ],
                "errors": result.errors
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result_dict, indent=2)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error searching files: {str(e)}"
            )]
    
    def run(self):
        """Run the MCP server."""
        asyncio.run(self.server.run())