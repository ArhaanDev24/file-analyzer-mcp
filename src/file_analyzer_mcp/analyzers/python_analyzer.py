"""
Python-specific code analyzer.

This module provides detailed analysis capabilities for Python source code
using AST parsing and other Python-specific techniques.
"""

import ast
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

from .base import BaseAnalyzer
from ..models import CodeMetrics, TodoItem

logger = logging.getLogger(__name__)


class PythonAnalyzer(BaseAnalyzer):
    """
    Analyzer for Python source code.
    
    This analyzer uses Python's AST module to perform detailed analysis
    of Python code structure, including functions, classes, imports, and
    complexity metrics.
    """
    
    def supports_language(self, language: str) -> bool:
        """Check if this analyzer supports the given language."""
        return language.lower() == 'python'
    
    def analyze_code(self, content: str, file_path: Path) -> Optional[CodeMetrics]:
        """
        Perform Python-specific code analysis.
        
        Args:
            content: Python source code
            file_path: Path to the file
            
        Returns:
            Code metrics or None if analysis fails
        """
        try:
            # Parse AST
            tree = self.parse_ast(content)
            if tree is None:
                return None
            
            # Count line types
            total_lines, blank_lines, comment_lines = self.count_line_types(content)
            
            # Extract code elements
            functions = self.extract_functions(tree)
            classes = self.extract_classes(tree)
            imports = self.extract_imports(tree)
            todos = self.find_todos(content, str(file_path))
            
            # Calculate complexity metrics
            complexity = self.calculate_complexity(tree)
            maintainability = self.calculate_maintainability_index(
                total_lines, complexity, comment_lines
            )
            
            return CodeMetrics(
                function_count=len(functions),
                class_count=len(classes),
                import_count=len(imports),
                comment_lines=comment_lines,
                blank_lines=blank_lines,
                cyclomatic_complexity=complexity,
                maintainability_index=maintainability,
                todos=todos
            )
            
        except Exception as e:
            logger.error(f"Error analyzing Python code in {file_path}: {e}")
            return None
    
    def parse_ast(self, content: str) -> Optional[ast.AST]:
        """
        Parse Python code into AST.
        
        Args:
            content: Python source code
            
        Returns:
            AST tree or None if parsing fails
        """
        try:
            return ast.parse(content)
        except SyntaxError as e:
            logger.warning(f"Syntax error in Python code: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing Python AST: {e}")
            return None
    
    def extract_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Extract function definitions from AST.
        
        Args:
            tree: Python AST
            
        Returns:
            List of function information
        """
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_info = {
                    'name': node.name,
                    'line_number': node.lineno,
                    'is_async': isinstance(node, ast.AsyncFunctionDef),
                    'args': [arg.arg for arg in node.args.args],
                    'decorators': [self._get_decorator_name(dec) for dec in node.decorator_list],
                    'docstring': ast.get_docstring(node),
                    'is_method': self._is_method(node, tree)
                }
                functions.append(func_info)
        
        return functions
    
    def _get_decorator_name(self, decorator: ast.AST) -> str:
        """Get decorator name from AST node."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{self._get_attr_name(decorator.value)}.{decorator.attr}"
        elif isinstance(decorator, ast.Call):
            return self._get_decorator_name(decorator.func)
        else:
            return str(decorator)
    
    def _get_attr_name(self, node: ast.AST) -> str:
        """Get attribute name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_attr_name(node.value)}.{node.attr}"
        else:
            return str(node)
    
    def _is_method(self, func_node: ast.FunctionDef, tree: ast.AST) -> bool:
        """Check if function is a method (inside a class)."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for child in node.body:
                    if child == func_node:
                        return True
        return False
    
    def extract_classes(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Extract class definitions from AST.
        
        Args:
            tree: Python AST
            
        Returns:
            List of class information
        """
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Extract base classes
                bases = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        bases.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        bases.append(self._get_attr_name(base))
                
                # Count methods in the class
                methods = []
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        methods.append({
                            'name': child.name,
                            'line_number': child.lineno,
                            'is_async': isinstance(child, ast.AsyncFunctionDef),
                            'is_property': any(
                                self._get_decorator_name(dec) == 'property' 
                                for dec in child.decorator_list
                            )
                        })
                
                class_info = {
                    'name': node.name,
                    'line_number': node.lineno,
                    'bases': bases,
                    'methods': methods,
                    'method_count': len(methods),
                    'decorators': [self._get_decorator_name(dec) for dec in node.decorator_list],
                    'docstring': ast.get_docstring(node)
                }
                classes.append(class_info)
        
        return classes
    
    def extract_imports(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Extract import statements from AST.
        
        Args:
            tree: Python AST
            
        Returns:
            List of import information
        """
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    import_info = {
                        'type': 'import',
                        'module': alias.name,
                        'alias': alias.asname,
                        'line_number': node.lineno,
                        'is_standard_library': self._is_standard_library(alias.name),
                        'is_relative': False
                    }
                    imports.append(import_info)
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                level = node.level  # Number of dots for relative imports
                
                for alias in node.names:
                    import_info = {
                        'type': 'from_import',
                        'module': module,
                        'name': alias.name,
                        'alias': alias.asname,
                        'line_number': node.lineno,
                        'is_standard_library': self._is_standard_library(module),
                        'is_relative': level > 0,
                        'relative_level': level
                    }
                    imports.append(import_info)
        
        return imports
    
    def _is_standard_library(self, module_name: str) -> bool:
        """Check if module is part of Python standard library."""
        if not module_name:
            return False
        
        # Get the top-level module name
        top_level = module_name.split('.')[0]
        
        # Common standard library modules
        stdlib_modules = {
            'os', 'sys', 'json', 'datetime', 'time', 'math', 'random',
            'collections', 'itertools', 'functools', 'operator', 'copy',
            'pickle', 'sqlite3', 'urllib', 'http', 'email', 'html',
            'xml', 'csv', 'configparser', 'logging', 'unittest', 'doctest',
            'argparse', 'subprocess', 'threading', 'multiprocessing',
            'asyncio', 'concurrent', 'queue', 'socket', 'ssl', 'hashlib',
            'hmac', 'secrets', 'uuid', 'base64', 'binascii', 'struct',
            'codecs', 'locale', 'gettext', 'calendar', 'zoneinfo',
            'pathlib', 'glob', 'fnmatch', 'tempfile', 'shutil', 'stat',
            'filecmp', 'tarfile', 'zipfile', 'gzip', 'bz2', 'lzma',
            'zlib', 'io', 'stringio', 'textwrap', 'unicodedata',
            'string', 're', 'difflib', 'readline', 'rlcompleter'
        }
        
        return top_level in stdlib_modules
    
    def find_todos(self, content: str, file_path: str) -> List[TodoItem]:
        """
        Find TODO, FIXME, HACK comments in Python code.
        
        Args:
            content: Python source code
            file_path: Path to the file
            
        Returns:
            List of TODO items
        """
        todos = []
        lines = content.split('\n')
        
        # Patterns to match TODO-style comments
        todo_patterns = [
            (r'#.*?TODO:?\s*(.*)', 'TODO'),
            (r'#.*?FIXME:?\s*(.*)', 'FIXME'),
            (r'#.*?HACK:?\s*(.*)', 'HACK'),
            (r'#.*?BUG:?\s*(.*)', 'BUG'),
            (r'#.*?NOTE:?\s*(.*)', 'NOTE'),
            (r'#.*?XXX:?\s*(.*)', 'XXX'),
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern, comment_type in todo_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    todo_text = match.group(1).strip() if match.group(1) else line.strip()
                    todos.append(TodoItem(
                        line_number=line_num,
                        comment_type=comment_type,
                        text=todo_text,
                        file_path=file_path
                    ))
                    break  # Only match first pattern per line
        
        return todos
    
    def calculate_complexity(self, tree: ast.AST) -> float:
        """
        Calculate cyclomatic complexity for Python code.
        
        Args:
            tree: Python AST
            
        Returns:
            Cyclomatic complexity score
        """
        complexity = 1  # Base complexity
        
        # Count decision points that increase complexity
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                # And/Or operations add complexity
                complexity += len(node.values) - 1
            elif isinstance(node, ast.comprehension):
                # List/dict/set comprehensions
                complexity += 1
                # Add complexity for conditions in comprehensions
                complexity += len(node.ifs)
        
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
        # Based on Halstead metrics approximation
        volume = lines * 4.0  # Simplified volume calculation
        comment_ratio = comment_lines / lines if lines > 0 else 0
        
        # MI = 171 - 5.2 * ln(V) - 0.23 * G - 16.2 * ln(LOC) + 50 * sin(sqrt(2.4 * C))
        # Simplified version
        import math
        mi = max(0, min(100, 
            171 - 5.2 * math.log(volume) - 0.23 * complexity - 16.2 * math.log(lines) + 50 * comment_ratio
        ))
        
        return round(mi, 2)