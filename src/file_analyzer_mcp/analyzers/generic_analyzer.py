"""
Generic code analyzer for non-Python languages.

This module provides analysis capabilities for various programming languages
using regex-based parsing and heuristics.
"""

import re
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
import logging

from .base import BaseAnalyzer
from ..models import CodeMetrics, TodoItem

logger = logging.getLogger(__name__)


class GenericAnalyzer(BaseAnalyzer):
    """
    Generic analyzer for various programming languages.
    
    This analyzer uses regex patterns and heuristics to analyze
    code in languages other than Python.
    """
    
    def __init__(self):
        """Initialize the generic analyzer."""
        super().__init__()
        self.supported_languages = {
            'javascript', 'typescript', 'java', 'c', 'c++', 'go', 'rust',
            'ruby', 'php', 'swift', 'kotlin', 'scala', 'csharp', 'html',
            'css', 'json', 'yaml', 'markdown', 'shell'
        }
    
    def supports_language(self, language: str) -> bool:
        """Check if this analyzer supports the given language."""
        return language.lower() in self.supported_languages
    
    def analyze_code(self, content: str, file_path: Path) -> Optional[CodeMetrics]:
        """
        Perform generic code analysis.
        
        Args:
            content: Source code content
            file_path: Path to the file
            
        Returns:
            Code metrics or None if analysis fails
        """
        try:
            # Count line types
            total_lines, blank_lines, comment_lines = self.count_line_types(content)
            
            # Extract code elements using regex
            functions = self.extract_functions_regex(content)
            classes = self.extract_classes_regex(content)
            imports = self.count_imports(content)
            todos = self.find_todos(content, str(file_path))
            
            # Calculate basic complexity
            complexity = self.calculate_basic_complexity(content)
            maintainability = self.calculate_maintainability_index(
                total_lines, complexity, comment_lines
            )
            
            return CodeMetrics(
                function_count=len(functions),
                class_count=len(classes),
                import_count=imports,
                comment_lines=comment_lines,
                blank_lines=blank_lines,
                cyclomatic_complexity=complexity,
                maintainability_index=maintainability,
                todos=todos
            )
            
        except Exception as e:
            logger.error(f"Error analyzing code in {file_path}: {e}")
            return None
    
    def extract_functions_regex(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract function definitions using regex patterns.
        
        Args:
            content: Source code content
            
        Returns:
            List of function information
        """
        functions = []
        
        # Function patterns for different languages
        patterns = [
            # JavaScript/TypeScript functions
            (r'(?:function\s+(\w+)\s*\([^)]*\)|(\w+)\s*:\s*function\s*\([^)]*\)|(\w+)\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))', 'javascript'),
            # Java methods
            (r'(?:public|private|protected|static|\s)*\s*\w+\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+\w+(?:\s*,\s*\w+)*)?\s*\{', 'java'),
            # C/C++ functions
            (r'(?:\w+\s+)*(\w+)\s*\([^)]*\)\s*\{', 'c'),
            # Go functions
            (r'func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\([^)]*\)', 'go'),
            # Rust functions
            (r'fn\s+(\w+)\s*\([^)]*\)', 'rust'),
            # Ruby methods
            (r'def\s+(\w+)(?:\([^)]*\))?', 'ruby'),
            # PHP functions
            (r'function\s+(\w+)\s*\([^)]*\)', 'php'),
        ]
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern, lang_type in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    # Get the first non-None group (function name)
                    func_name = next((g for g in match.groups() if g), 'unknown')
                    if func_name and func_name != 'unknown':
                        functions.append({
                            'name': func_name,
                            'line_number': line_num,
                            'language_type': lang_type
                        })
        
        return functions
    
    def extract_classes_regex(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract class definitions using regex patterns.
        
        Args:
            content: Source code content
            
        Returns:
            List of class information
        """
        classes = []
        
        # Class patterns for different languages
        patterns = [
            # JavaScript/TypeScript classes
            (r'class\s+(\w+)(?:\s+extends\s+\w+)?', 'javascript'),
            # Java classes
            (r'(?:public|private|protected|\s)*class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+[\w,\s]+)?', 'java'),
            # C++ classes
            (r'class\s+(\w+)(?:\s*:\s*(?:public|private|protected)\s+\w+)?', 'c++'),
            # C# classes
            (r'(?:public|private|protected|internal|\s)*class\s+(\w+)(?:\s*:\s*\w+)?', 'csharp'),
            # Ruby classes
            (r'class\s+(\w+)(?:\s*<\s*\w+)?', 'ruby'),
            # PHP classes
            (r'class\s+(\w+)(?:\s+extends\s+\w+)?', 'php'),
        ]
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern, lang_type in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    class_name = match.group(1)
                    if class_name:
                        classes.append({
                            'name': class_name,
                            'line_number': line_num,
                            'language_type': lang_type
                        })
        
        return classes
    
    def count_imports(self, content: str) -> int:
        """
        Count import statements using regex.
        
        Args:
            content: Source code content
            
        Returns:
            Number of import statements
        """
        import_patterns = [
            r'import\s+',  # JavaScript, Java, Python
            r'#include\s*<',  # C/C++
            r'use\s+',  # Rust
            r'require\s*\(',  # JavaScript/Node.js
            r'@import\s+',  # CSS
        ]
        
        import_count = 0
        for pattern in import_patterns:
            import_count += len(re.findall(pattern, content, re.IGNORECASE))
        
        return import_count
    
    def find_todos(self, content: str, file_path: str) -> List[TodoItem]:
        """
        Find TODO, FIXME, HACK comments in code.
        
        Args:
            content: Source code content
            file_path: Path to the file
            
        Returns:
            List of TODO items
        """
        todos = []
        lines = content.split('\n')
        
        # Patterns for different comment styles
        todo_patterns = [
            # Single-line comments (// # --)
            (r'(?://|#|--)\s*(?:TODO|FIXME|HACK|BUG|NOTE|XXX):?\s*(.*)', r'(?://|#|--)\s*(TODO|FIXME|HACK|BUG|NOTE|XXX)'),
            # Multi-line comments (/* */)
            (r'/\*.*?(?:TODO|FIXME|HACK|BUG|NOTE|XXX):?\s*(.*?)\*/', r'/\*.*?(TODO|FIXME|HACK|BUG|NOTE|XXX)'),
            # HTML comments
            (r'<!--.*?(?:TODO|FIXME|HACK|BUG|NOTE|XXX):?\s*(.*?)-->', r'<!--.*?(TODO|FIXME|HACK|BUG|NOTE|XXX)'),
        ]
        
        for line_num, line in enumerate(lines, 1):
            for text_pattern, type_pattern in todo_patterns:
                text_match = re.search(text_pattern, line, re.IGNORECASE | re.DOTALL)
                type_match = re.search(type_pattern, line, re.IGNORECASE)
                
                if text_match and type_match:
                    comment_type = type_match.group(1).upper()
                    todo_text = text_match.group(1).strip() if text_match.group(1) else line.strip()
                    
                    todos.append(TodoItem(
                        line_number=line_num,
                        comment_type=comment_type,
                        text=todo_text,
                        file_path=file_path
                    ))
                    break  # Only match first pattern per line
        
        return todos
    
    def calculate_basic_complexity(self, content: str) -> float:
        """
        Calculate basic cyclomatic complexity using regex.
        
        Args:
            content: Source code content
            
        Returns:
            Approximate complexity score
        """
        complexity = 1  # Base complexity
        
        # Patterns that increase complexity
        complexity_patterns = [
            r'\bif\b',
            r'\belse\s+if\b',
            r'\belif\b',
            r'\bwhile\b',
            r'\bfor\b',
            r'\bswitch\b',
            r'\bcase\b',
            r'\bcatch\b',
            r'\b&&\b',
            r'\b\|\|\b',
            r'\?.*:',  # Ternary operator
        ]
        
        for pattern in complexity_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            complexity += len(matches)
        
        return float(complexity)
    
    def calculate_maintainability_index(self, lines: int, complexity: float, comment_lines: int) -> float:
        """
        Calculate maintainability index.
        
        Args:
            lines: Total lines of code
            complexity: Cyclomatic complexity
            comment_lines: Number of comment lines
            
        Returns:
            Maintainability index (0-100)
        """
        if lines == 0:
            return 100.0
        
        # Simplified maintainability index calculation
        import math
        volume = lines * 4.0  # Simplified volume calculation
        comment_ratio = comment_lines / lines if lines > 0 else 0
        
        # MI = 171 - 5.2 * ln(V) - 0.23 * G - 16.2 * ln(LOC) + 50 * sin(sqrt(2.4 * C))
        # Simplified version
        mi = max(0, min(100, 
            171 - 5.2 * math.log(max(1, volume)) - 0.23 * complexity - 16.2 * math.log(max(1, lines)) + 50 * comment_ratio
        ))
        
        return round(mi, 2)