"""
Base analyzer for common file analysis operations.

This module provides the base analyzer class with common functionality
shared across different language-specific analyzers.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from abc import ABC, abstractmethod
import logging

from ..models import AnalysisResult, CodeMetrics, TodoItem
from ..filesystem import FileSystemManager
from ..language_detector import LanguageDetector

logger = logging.getLogger(__name__)


class BaseAnalyzer(ABC):
    """
    Base class for file analyzers.
    
    This abstract class defines the common interface and provides
    shared functionality for analyzing files of different types.
    """
    
    def __init__(self):
        """Initialize the base analyzer."""
        self.fs_manager = FileSystemManager()
        self.language_detector = LanguageDetector()
    
    def analyze_file(self, file_path: str) -> AnalysisResult:
        """
        Analyze a file and return comprehensive results.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Complete analysis result
        """
        errors = []
        
        try:
            # Validate and get file path
            path_obj = self.fs_manager.validate_path(file_path)
            
            # Get basic file metadata
            metadata = self.get_file_metadata(path_obj)
            
            # Detect language and check if binary
            file_type_info = self.language_detector.get_file_type_info(path_obj)
            
            # Initialize result with basic info
            result = AnalysisResult(
                file_path=str(path_obj),
                file_size=metadata['size'],
                line_count=0,
                language=file_type_info['language'],
                last_modified=datetime.fromtimestamp(metadata['modified']),
                is_binary=file_type_info['is_binary'],
                encoding='',
                metrics=None,
                errors=errors
            )
            
            # Skip detailed analysis for binary files
            if file_type_info['is_binary']:
                return result
            
            # Read file content and detect encoding
            encoding = self.fs_manager.detect_encoding(path_obj)
            result.encoding = encoding
            
            try:
                content = self.fs_manager.read_file_content(path_obj, encoding)
                
                # Count lines
                result.line_count = self.count_lines(content)
                
                # Perform language-specific analysis
                if self.supports_language(file_type_info['language']):
                    result.metrics = self.analyze_code(content, path_obj)
                
            except Exception as e:
                errors.append(f"Error reading file content: {e}")
                logger.error(f"Error analyzing {file_path}: {e}")
            
            result.errors = errors
            return result
            
        except Exception as e:
            errors.append(f"Error analyzing file: {e}")
            logger.error(f"Error analyzing {file_path}: {e}")
            
            # Return minimal result with error
            return AnalysisResult(
                file_path=file_path,
                file_size=0,
                line_count=0,
                language='unknown',
                last_modified=datetime.now(),
                is_binary=False,
                encoding='utf-8',
                metrics=None,
                errors=errors
            )
    
    def get_file_metadata(self, path: Path) -> Dict:
        """
        Extract basic file metadata.
        
        Args:
            path: Path to the file
            
        Returns:
            Dictionary with file metadata
        """
        try:
            stat_info = path.stat()
            return {
                'size': stat_info.st_size,
                'modified': stat_info.st_mtime,
                'created': getattr(stat_info, 'st_birthtime', stat_info.st_ctime),
                'permissions': oct(stat_info.st_mode)[-3:],
                'is_file': path.is_file(),
                'is_dir': path.is_dir(),
                'is_symlink': path.is_symlink(),
                'exists': path.exists()
            }
        except (OSError, IOError) as e:
            logger.error(f"Error getting metadata for {path}: {e}")
            return {
                'size': 0,
                'modified': 0,
                'created': 0,
                'permissions': '000',
                'is_file': False,
                'is_dir': False,
                'is_symlink': False,
                'exists': False
            }
    
    def count_lines(self, content: str) -> int:
        """
        Count lines in file content.
        
        Args:
            content: File content
            
        Returns:
            Number of lines
        """
        if not content:
            return 0
        
        # Count newlines and add 1 if content doesn't end with newline
        line_count = content.count('\n')
        if content and not content.endswith('\n'):
            line_count += 1
        
        return line_count
    
    def count_line_types(self, content: str) -> Tuple[int, int, int]:
        """
        Count different types of lines in content.
        
        Args:
            content: File content
            
        Returns:
            Tuple of (total_lines, blank_lines, comment_lines)
        """
        if not content:
            return 0, 0, 0
        
        lines = content.split('\n')
        total_lines = len(lines)
        blank_lines = 0
        comment_lines = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                blank_lines += 1
            elif self.is_comment_line(stripped):
                comment_lines += 1
        
        return total_lines, blank_lines, comment_lines
    
    def is_comment_line(self, line: str) -> bool:
        """
        Check if a line is a comment (basic implementation).
        
        Args:
            line: Stripped line content
            
        Returns:
            True if line appears to be a comment
        """
        # Basic comment detection for common languages
        comment_prefixes = ['#', '//', '/*', '*', '--', '%', ';']
        return any(line.startswith(prefix) for prefix in comment_prefixes)
    
    @abstractmethod
    def supports_language(self, language: str) -> bool:
        """
        Check if this analyzer supports the given language.
        
        Args:
            language: Programming language name
            
        Returns:
            True if supported, False otherwise
        """
        pass
    
    @abstractmethod
    def analyze_code(self, content: str, file_path: Path) -> Optional[CodeMetrics]:
        """
        Perform language-specific code analysis.
        
        Args:
            content: File content
            file_path: Path to the file
            
        Returns:
            Code metrics or None if analysis fails
        """
        pass