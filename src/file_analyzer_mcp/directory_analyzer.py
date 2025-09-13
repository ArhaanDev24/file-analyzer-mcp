"""
Directory analysis functionality.

This module provides comprehensive directory analysis capabilities including
file counting, size calculation, language distribution, and directory structure
mapping with .gitignore support.
"""

import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import logging
import fnmatch

from .models import DirectoryAnalysis, DirectoryTree
from .filesystem import FileSystemManager
from .language_detector import LanguageDetector

logger = logging.getLogger(__name__)


class DirectoryAnalyzer:
    """
    Analyzer for directory contents and structure.
    
    This class provides methods for analyzing directories recursively,
    counting files by type, calculating sizes, and building directory
    structure representations.
    """
    
    def __init__(self):
        """Initialize the directory analyzer."""
        self.fs_manager = FileSystemManager()
        self.language_detector = LanguageDetector()
        self.gitignore_patterns = set()
    
    def analyze_directory(self, directory_path: str, recursive: bool = True, 
                         filters: Optional[List[str]] = None) -> DirectoryAnalysis:
        """
        Analyze a directory and return comprehensive results.
        
        Args:
            directory_path: Path to the directory to analyze
            recursive: Whether to analyze subdirectories
            filters: Optional list of file extensions to include
            
        Returns:
            Complete directory analysis
        """
        start_time = time.time()
        errors = []
        
        try:
            # Validate directory path
            path_obj = self.fs_manager.validate_path(directory_path)
            
            if not path_obj.is_dir():
                raise ValueError(f"Path is not a directory: {directory_path}")
            
            # Load .gitignore patterns
            self._load_gitignore_patterns(path_obj)
            
            # Traverse directory
            files = self.traverse_directory(path_obj, recursive, filters)
            
            # Count file types and languages
            file_types, languages = self.count_file_types(files)
            
            # Calculate total size
            total_size = self.calculate_total_size(files)
            
            # Build directory structure
            structure = self._build_directory_tree(path_obj, recursive, filters)
            
            analysis_time = time.time() - start_time
            
            return DirectoryAnalysis(
                directory_path=str(path_obj),
                total_files=len(files),
                file_types=file_types,
                total_size=total_size,
                languages=languages,
                structure=structure,
                analysis_time=analysis_time,
                errors=errors
            )
            
        except Exception as e:
            errors.append(str(e))
            logger.error(f"Error analyzing directory {directory_path}: {e}")
            
            return DirectoryAnalysis(
                directory_path=directory_path,
                total_files=0,
                file_types={},
                total_size=0,
                languages={},
                structure=None,
                analysis_time=time.time() - start_time,
                errors=errors
            )
    
    def traverse_directory(self, directory_path: Path, recursive: bool = True,
                          filters: Optional[List[str]] = None) -> List[Path]:
        """
        Traverse directory and collect file paths.
        
        Args:
            directory_path: Directory to traverse
            recursive: Whether to traverse subdirectories
            filters: Optional file extension filters
            
        Returns:
            List of file paths
        """
        files = []
        
        try:
            if recursive:
                for root, dirs, filenames in os.walk(directory_path):
                    root_path = Path(root)
                    
                    # Filter out ignored directories
                    dirs[:] = [d for d in dirs if not self._should_ignore(root_path / d)]
                    
                    for filename in filenames:
                        file_path = root_path / filename
                        
                        # Skip ignored files
                        if self._should_ignore(file_path):
                            continue
                        
                        # Apply extension filters
                        if filters and not any(filename.endswith(ext) for ext in filters):
                            continue
                        
                        # Check permissions
                        if self.fs_manager.check_permissions(file_path):
                            files.append(file_path)
            else:
                # Non-recursive: only direct children
                for item in directory_path.iterdir():
                    if item.is_file() and not self._should_ignore(item):
                        # Apply extension filters
                        if filters and not any(item.name.endswith(ext) for ext in filters):
                            continue
                        
                        if self.fs_manager.check_permissions(item):
                            files.append(item)
                            
        except Exception as e:
            logger.error(f"Error traversing directory {directory_path}: {e}")
        
        return files
    
    def count_file_types(self, files: List[Path]) -> Tuple[Dict[str, int], Dict[str, int]]:
        """
        Count files by extension and programming language.
        
        Args:
            files: List of file paths
            
        Returns:
            Tuple of (file_types_dict, languages_dict)
        """
        file_types = {}
        languages = {}
        
        for file_path in files:
            try:
                # Count by extension
                extension = file_path.suffix.lower() or 'no_extension'
                file_types[extension] = file_types.get(extension, 0) + 1
                
                # Count by language
                file_type_info = self.language_detector.get_file_type_info(file_path)
                language = file_type_info['language']
                if language != 'unknown':
                    languages[language] = languages.get(language, 0) + 1
                    
            except Exception as e:
                logger.warning(f"Error analyzing file type for {file_path}: {e}")
        
        return file_types, languages
    
    def calculate_total_size(self, files: List[Path]) -> int:
        """
        Calculate total size of all files.
        
        Args:
            files: List of file paths
            
        Returns:
            Total size in bytes
        """
        total_size = 0
        
        for file_path in files:
            try:
                file_info = self.fs_manager.get_file_info(file_path)
                total_size += file_info.get('size', 0)
            except Exception as e:
                logger.warning(f"Error getting size for {file_path}: {e}")
        
        return total_size
    
    def _build_directory_tree(self, directory_path: Path, recursive: bool = True,
                             filters: Optional[List[str]] = None) -> DirectoryTree:
        """
        Build a hierarchical directory tree structure.
        
        Args:
            directory_path: Root directory
            recursive: Whether to include subdirectories
            filters: Optional file extension filters
            
        Returns:
            Directory tree structure
        """
        try:
            children = []
            
            # Get directory size
            dir_size = 0
            
            for item in directory_path.iterdir():
                if self._should_ignore(item):
                    continue
                
                if item.is_file():
                    # Apply extension filters
                    if filters and not any(item.name.endswith(ext) for ext in filters):
                        continue
                    
                    if self.fs_manager.check_permissions(item):
                        file_info = self.fs_manager.get_file_info(item)
                        file_size = file_info.get('size', 0)
                        dir_size += file_size
                        
                        children.append(DirectoryTree(
                            name=item.name,
                            path=str(item),
                            is_directory=False,
                            size=file_size,
                            children=[]
                        ))
                
                elif item.is_dir() and recursive:
                    if self.fs_manager.check_permissions(item):
                        subtree = self._build_directory_tree(item, recursive, filters)
                        dir_size += subtree.size
                        children.append(subtree)
            
            return DirectoryTree(
                name=directory_path.name,
                path=str(directory_path),
                is_directory=True,
                size=dir_size,
                children=children
            )
            
        except Exception as e:
            logger.error(f"Error building directory tree for {directory_path}: {e}")
            return DirectoryTree(
                name=directory_path.name,
                path=str(directory_path),
                is_directory=True,
                size=0,
                children=[]
            )
    
    def _load_gitignore_patterns(self, directory_path: Path):
        """
        Load .gitignore patterns from the directory.
        
        Args:
            directory_path: Directory to search for .gitignore
        """
        self.gitignore_patterns = set()
        
        gitignore_path = directory_path / '.gitignore'
        if gitignore_path.exists() and gitignore_path.is_file():
            try:
                with open(gitignore_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            self.gitignore_patterns.add(line)
            except Exception as e:
                logger.warning(f"Error reading .gitignore: {e}")
        
        # Add common ignore patterns
        self.gitignore_patterns.update({
            '__pycache__',
            '*.pyc',
            '*.pyo',
            '*.pyd',
            '.git',
            '.svn',
            '.hg',
            '.DS_Store',
            'Thumbs.db',
            'node_modules',
            '.venv',
            'venv',
            '.env',
            '*.log',
            '.pytest_cache',
            '.mypy_cache',
            '.coverage',
            'htmlcov',
            'dist',
            'build',
            '*.egg-info'
        })
    
    def _should_ignore(self, path: Path) -> bool:
        """
        Check if a path should be ignored based on .gitignore patterns.
        
        Args:
            path: Path to check
            
        Returns:
            True if path should be ignored
        """
        path_str = str(path)
        name = path.name
        
        for pattern in self.gitignore_patterns:
            # Direct name match
            if fnmatch.fnmatch(name, pattern):
                return True
            
            # Path match
            if fnmatch.fnmatch(path_str, pattern):
                return True
            
            # Directory pattern (ends with /)
            if pattern.endswith('/') and path.is_dir():
                if fnmatch.fnmatch(name, pattern[:-1]):
                    return True
        
        return False