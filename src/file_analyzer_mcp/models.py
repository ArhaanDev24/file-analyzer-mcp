"""
Data models for the File Analyzer MCP server.

This module contains all the dataclasses used for representing analysis results,
file metadata, and other structured data returned by the MCP server.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict


@dataclass
class TodoItem:
    """
    Represents a TODO, FIXME, or HACK comment found in code.
    """
    line_number: int
    comment_type: str  # 'TODO', 'FIXME', 'HACK'
    text: str
    file_path: str


@dataclass
class CodeMetrics:
    """
    Represents code analysis metrics for a file.
    
    This dataclass contains quantitative metrics about code structure,
    complexity, and quality indicators that can be calculated from
    source code analysis.
    """
    function_count: int
    class_count: int
    import_count: int
    comment_lines: int
    blank_lines: int
    cyclomatic_complexity: float
    maintainability_index: float
    todos: List[TodoItem]


@dataclass
class AnalysisResult:
    """
    Represents the complete analysis result for a single file.
    
    This dataclass contains all the metadata and analysis information
    that can be extracted from a file, including basic file properties,
    language detection, and optional code metrics.
    """
    file_path: str
    file_size: int
    line_count: int
    language: str
    last_modified: datetime
    is_binary: bool
    encoding: str
    metrics: Optional['CodeMetrics']
    errors: List[str]