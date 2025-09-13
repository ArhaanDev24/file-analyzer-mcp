"""
Data models for the File Analyzer MCP server.

This module contains all the dataclasses used for representing analysis results,
file metadata, and other structured data returned by the MCP server.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any


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
class DirectoryTree:
    """
    Represents the hierarchical structure of a directory.
    """
    name: str
    path: str
    is_directory: bool
    size: int
    children: List['DirectoryTree']


@dataclass
class DirectoryAnalysis:
    """
    Represents the analysis result for a directory.
    
    This dataclass contains aggregated information about all files
    in a directory, including file counts, size distribution,
    and language statistics.
    """
    directory_path: str
    total_files: int
    file_types: Dict[str, int]  # extension -> count
    total_size: int
    languages: Dict[str, int]  # language -> count
    structure: DirectoryTree
    analysis_time: float
    errors: List[str]


@dataclass
class FileMatch:
    """
    Represents a single file match in search results.
    """
    file_path: str
    line_number: int
    content: str
    context_before: List[str]
    context_after: List[str]


@dataclass
class SearchResult:
    """
    Represents the result of a file or content search operation.
    
    This dataclass contains all matches found during a search,
    along with metadata about the search operation.
    """
    matches: List[FileMatch]
    total_matches: int
    search_time: float
    search_pattern: str
    search_type: str  # 'glob', 'regex', 'content'
    errors: List[str]


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