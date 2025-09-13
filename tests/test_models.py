"""
Unit tests for data models.
"""

import pytest
from datetime import datetime
from file_analyzer_mcp.models import (
    AnalysisResult,
    CodeMetrics,
    TodoItem,
    DirectoryAnalysis,
    DirectoryTree,
    SearchResult,
    FileMatch
)


class TestTodoItem:
    """Test cases for TodoItem dataclass."""
    
    def test_todo_item_creation(self):
        """Test TodoItem creation with valid data."""
        todo = TodoItem(
            line_number=42,
            comment_type="TODO",
            text="Fix this later",
            file_path="/path/to/file.py"
        )
        assert todo.line_number == 42
        assert todo.comment_type == "TODO"
        assert todo.text == "Fix this later"
        assert todo.file_path == "/path/to/file.py"


class TestCodeMetrics:
    """Test cases for CodeMetrics dataclass."""
    
    def test_code_metrics_creation(self):
        """Test CodeMetrics creation with valid data."""
        todo = TodoItem(1, "TODO", "test", "file.py")
        metrics = CodeMetrics(
            function_count=5,
            class_count=2,
            import_count=10,
            comment_lines=20,
            blank_lines=15,
            cyclomatic_complexity=3.5,
            maintainability_index=85.2,
            todos=[todo]
        )
        assert metrics.function_count == 5
        assert metrics.class_count == 2
        assert len(metrics.todos) == 1


class TestAnalysisResult:
    """Test cases for AnalysisResult dataclass."""
    
    def test_analysis_result_creation(self):
        """Test AnalysisResult creation with valid data."""
        result = AnalysisResult(
            file_path="/path/to/file.py",
            file_size=1024,
            line_count=50,
            language="python",
            last_modified=datetime.now(),
            is_binary=False,
            encoding="utf-8",
            metrics=None,
            errors=[]
        )
        assert result.file_path == "/path/to/file.py"
        assert result.file_size == 1024
        assert result.language == "python"
        assert not result.is_binary