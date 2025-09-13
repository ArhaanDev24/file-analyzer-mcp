"""
Programming language detection for files.

This module provides functionality to detect programming languages
based on file extensions, shebang lines, and content analysis.
"""

import re
from pathlib import Path
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class LanguageDetector:
    """
    Detects programming languages and file types.
    
    This class uses multiple detection methods including file extensions,
    shebang lines, and content-based heuristics to identify the programming
    language of source code files.
    """
    
    def __init__(self):
        """Initialize the LanguageDetector."""
        self.extension_map = {
            # Python
            '.py': 'python',
            '.pyw': 'python',
            '.pyi': 'python',
            
            # JavaScript/TypeScript
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.mjs': 'javascript',
            
            # Java
            '.java': 'java',
            '.class': 'java',
            
            # C/C++
            '.c': 'c',
            '.h': 'c',
            '.cpp': 'c++',
            '.cxx': 'c++',
            '.cc': 'c++',
            '.hpp': 'c++',
            '.hxx': 'c++',
            
            # Go
            '.go': 'go',
            
            # Rust
            '.rs': 'rust',
            
            # Web
            '.html': 'html',
            '.htm': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sass': 'sass',
            '.less': 'less',
            
            # Data formats
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.xml': 'xml',
            '.toml': 'toml',
            
            # Shell
            '.sh': 'shell',
            '.bash': 'shell',
            '.zsh': 'shell',
            '.fish': 'shell',
            
            # Other languages
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.clj': 'clojure',
            '.hs': 'haskell',
            '.ml': 'ocaml',
            '.fs': 'fsharp',
            '.cs': 'csharp',
            '.vb': 'vbnet',
            '.pl': 'perl',
            '.r': 'r',
            '.R': 'r',
            '.m': 'matlab',
            '.sql': 'sql',
            
            # Documentation
            '.md': 'markdown',
            '.rst': 'restructuredtext',
            '.tex': 'latex',
            
            # Configuration
            '.ini': 'ini',
            '.cfg': 'ini',
            '.conf': 'config',
            '.properties': 'properties',
            
            # Docker
            'Dockerfile': 'dockerfile',
            '.dockerfile': 'dockerfile',
        }
        
        self.shebang_patterns = {
            r'#!/usr/bin/env python': 'python',
            r'#!/usr/bin/python': 'python',
            r'#!/usr/bin/env python3': 'python',
            r'#!/usr/bin/python3': 'python',
            r'#!/usr/bin/env node': 'javascript',
            r'#!/usr/bin/node': 'javascript',
            r'#!/bin/bash': 'shell',
            r'#!/usr/bin/bash': 'shell',
            r'#!/bin/sh': 'shell',
            r'#!/usr/bin/sh': 'shell',
            r'#!/usr/bin/env bash': 'shell',
            r'#!/usr/bin/env sh': 'shell',
            r'#!/usr/bin/env zsh': 'shell',
            r'#!/usr/bin/zsh': 'shell',
            r'#!/usr/bin/env ruby': 'ruby',
            r'#!/usr/bin/ruby': 'ruby',
            r'#!/usr/bin/env perl': 'perl',
            r'#!/usr/bin/perl': 'perl',
            r'#!/usr/bin/env php': 'php',
            r'#!/usr/bin/php': 'php',
        }
    
    def detect_language(self, file_path: Path, content: Optional[str] = None) -> str:
        """
        Detect the programming language of a file.
        
        Args:
            file_path: Path to the file
            content: Optional file content (if already read)
            
        Returns:
            Detected language name or 'unknown'
        """
        # Try extension-based detection first
        language = self.detect_by_extension(file_path)
        if language != 'unknown':
            return language
        
        # Try shebang detection if content is available
        if content:
            language = self.detect_by_shebang(content)
            if language != 'unknown':
                return language
        
        # Try content-based heuristics
        if content:
            language = self.detect_by_content(content)
            if language != 'unknown':
                return language
        
        return 'unknown'
    
    def detect_by_extension(self, file_path: Path) -> str:
        """
        Detect language by file extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Language name or 'unknown'
        """
        # Check file name first (for files like Dockerfile)
        file_name = file_path.name
        if file_name in self.extension_map:
            return self.extension_map[file_name]
        
        # Check extension
        extension = file_path.suffix.lower()
        if extension in self.extension_map:
            return self.extension_map[extension]
        
        # Check for multiple extensions (e.g., .spec.ts)
        if len(file_path.suffixes) > 1:
            combined_ext = ''.join(file_path.suffixes[-2:]).lower()
            if combined_ext in self.extension_map:
                return self.extension_map[combined_ext]
        
        return 'unknown'
    
    def detect_by_shebang(self, content: str) -> str:
        """
        Detect language by shebang line.
        
        Args:
            content: File content
            
        Returns:
            Language name or 'unknown'
        """
        if not content.startswith('#!'):
            return 'unknown'
        
        # Get the first line
        first_line = content.split('\n')[0].strip()
        
        # Check against known shebang patterns
        for pattern, language in self.shebang_patterns.items():
            if re.match(pattern, first_line):
                return language
        
        # Try to extract interpreter from shebang
        shebang_match = re.match(r'#!.*?([a-zA-Z0-9_]+)(?:\s|$)', first_line)
        if shebang_match:
            interpreter = shebang_match.group(1).lower()
            interpreter_map = {
                'python': 'python',
                'python3': 'python',
                'node': 'javascript',
                'bash': 'shell',
                'sh': 'shell',
                'zsh': 'shell',
                'ruby': 'ruby',
                'perl': 'perl',
                'php': 'php',
            }
            if interpreter in interpreter_map:
                return interpreter_map[interpreter]
        
        return 'unknown'
    
    def detect_by_content(self, content: str) -> str:
        """
        Detect language by content analysis.
        
        Args:
            content: File content
            
        Returns:
            Language name or 'unknown'
        """
        # Basic content-based detection
        if not content.strip():
            return 'unknown'
        
        # Look for common language patterns
        if re.search(r'def\s+\w+\s*\(.*\):', content):
            return 'python'
        elif re.search(r'function\s+\w+\s*\(.*\)\s*{', content):
            return 'javascript'
        elif re.search(r'public\s+class\s+\w+', content):
            return 'java'
        elif re.search(r'#include\s*<.*>', content):
            return 'c++'
        
        return 'unknown'
    
    def is_binary_file(self, file_path: Path) -> bool:
        """
        Check if a file is binary.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file is binary, False otherwise
        """
        # Known binary extensions
        binary_extensions = {
            '.exe', '.dll', '.so', '.dylib', '.a', '.lib',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.tiff',
            '.mp3', '.wav', '.ogg', '.flac', '.aac',
            '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.zip', '.tar', '.gz', '.bz2', '.xz', '.7z', '.rar',
            '.bin', '.dat', '.db', '.sqlite', '.sqlite3',
            '.class', '.jar', '.war', '.ear',
            '.pyc', '.pyo', '.pyd',
            '.o', '.obj', '.out',
        }
        
        extension = file_path.suffix.lower()
        if extension in binary_extensions:
            return True
        
        # Check file content for null bytes (binary indicator)
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(8192)  # Read first 8KB
                if b'\x00' in chunk:
                    return True
                
                # Check for high ratio of non-printable characters
                if chunk:
                    printable_chars = sum(1 for byte in chunk if 32 <= byte <= 126 or byte in (9, 10, 13))
                    ratio = printable_chars / len(chunk)
                    if ratio < 0.7:  # Less than 70% printable characters
                        return True
                        
        except (IOError, OSError):
            # If we can't read the file, assume it might be binary
            return True
        
        return False
    
    def get_file_type_info(self, file_path: Path, content: Optional[str] = None) -> Dict[str, str]:
        """
        Get comprehensive file type information.
        
        Args:
            file_path: Path to the file
            content: Optional file content
            
        Returns:
            Dictionary with file type information
        """
        is_binary = self.is_binary_file(file_path)
        language = 'binary' if is_binary else self.detect_language(file_path, content)
        
        return {
            'language': language,
            'is_binary': is_binary,
            'extension': file_path.suffix.lower(),
            'filename': file_path.name
        }