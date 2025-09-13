"""
File Analyzer MCP Server

A Model Context Protocol server that provides comprehensive file analysis capabilities
to AI assistants, including code structure analysis, language detection, and metrics calculation.
"""

__version__ = "0.1.0"
__author__ = "File Analyzer MCP"
__description__ = "MCP server for file analysis and code metrics"

# Package-level imports for convenience
from .models import AnalysisResult, CodeMetrics, DirectoryAnalysis, SearchResult

__all__ = [
    "AnalysisResult",
    "CodeMetrics", 
    "DirectoryAnalysis",
    "SearchResult",
]