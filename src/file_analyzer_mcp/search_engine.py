"""
File and content search functionality.

This module provides comprehensive search capabilities including glob patterns,
regex matching, and content-based search with context extraction.
"""

import re
import time
import glob
from pathlib import Path
from typing import List, Optional, Dict, Any, Pattern
import logging
import fnmatch

from .models import SearchResult, FileMatch
from .filesystem import FileSystemManager

logger = logging.getLogger(__name__)


class SearchEngine:
    """
    Engine for searching files and content.
    
    This class provides various search methods including glob patterns,
    regex matching, and content-based search with context extraction.
    """
    
    def __init__(self):
        """Initialize the search engine."""
        self.fs_manager = FileSystemManager()
        self.max_context_lines = 3
        self.max_matches_per_file = 100
        self.max_total_matches = 1000
    
    def search_files(self, pattern: str, search_type: str = 'glob',
                    base_path: str = '.', filters: Optional[List[str]] = None) -> SearchResult:
        """
        Search for files using the specified method.
        
        Args:
            pattern: Search pattern
            search_type: Type of search ('glob', 'regex', 'content')
            base_path: Base directory to search in
            filters: Optional file extension filters
            
        Returns:
            Search results
        """
        start_time = time.time()
        errors = []
        matches = []
        
        try:
            if search_type == 'glob':
                matches = self.search_by_glob(pattern, base_path, filters)
            elif search_type == 'regex':
                matches = self.search_by_regex(pattern, base_path, filters)
            elif search_type == 'content':
                matches = self.search_content(pattern, base_path, filters)
            else:
                errors.append(f"Unknown search type: {search_type}")
            
            search_time = time.time() - start_time
            
            return SearchResult(
                matches=matches[:self.max_total_matches],
                total_matches=len(matches),
                search_time=search_time,
                search_pattern=pattern,
                search_type=search_type,
                errors=errors
            )
            
        except Exception as e:
            errors.append(str(e))
            logger.error(f"Error in search: {e}")
            
            return SearchResult(
                matches=[],
                total_matches=0,
                search_time=time.time() - start_time,
                search_pattern=pattern,
                search_type=search_type,
                errors=errors
            )
    
    def search_by_glob(self, pattern: str, base_path: str = '.',
                      filters: Optional[List[str]] = None) -> List[FileMatch]:
        """
        Search files using glob patterns.
        
        Args:
            pattern: Glob pattern (e.g., '*.py', 'src/**/*.js')
            base_path: Base directory to search in
            filters: Optional file extension filters
            
        Returns:
            List of file matches
        """
        matches = []
        
        try:
            # Convert to Path object
            base_path_obj = Path(base_path).resolve()
            
            # Use glob to find matching files
            if '**' in pattern:
                # Recursive glob
                matching_files = base_path_obj.glob(pattern)
            else:
                # Non-recursive glob
                matching_files = base_path_obj.glob(pattern)
            
            for file_path in matching_files:
                if file_path.is_file():
                    # Apply extension filters
                    if filters and not any(file_path.name.endswith(ext) for ext in filters):
                        continue
                    
                    # Check permissions
                    if self.fs_manager.check_permissions(file_path):
                        matches.append(FileMatch(
                            file_path=str(file_path),
                            line_number=0,  # No specific line for file matches
                            content=f"File: {file_path.name}",
                            context_before=[],
                            context_after=[]
                        ))
                        
                        if len(matches) >= self.max_total_matches:
                            break
                            
        except Exception as e:
            logger.error(f"Error in glob search: {e}")
        
        return matches
    
    def search_by_regex(self, pattern: str, base_path: str = '.',
                       filters: Optional[List[str]] = None) -> List[FileMatch]:
        """
        Search files using regex patterns on filenames.
        
        Args:
            pattern: Regex pattern for filenames
            base_path: Base directory to search in
            filters: Optional file extension filters
            
        Returns:
            List of file matches
        """
        matches = []
        
        try:
            # Compile regex pattern
            regex_pattern = re.compile(pattern, re.IGNORECASE)
            base_path_obj = Path(base_path).resolve()
            
            # Walk through directory tree
            for root, dirs, files in base_path_obj.walk():
                for filename in files:
                    file_path = root / filename
                    
                    # Check if filename matches regex
                    if regex_pattern.search(filename):
                        # Apply extension filters
                        if filters and not any(filename.endswith(ext) for ext in filters):
                            continue
                        
                        # Check permissions
                        if self.fs_manager.check_permissions(file_path):
                            matches.append(FileMatch(
                                file_path=str(file_path),
                                line_number=0,
                                content=f"File: {filename}",
                                context_before=[],
                                context_after=[]
                            ))
                            
                            if len(matches) >= self.max_total_matches:
                                break
                
                if len(matches) >= self.max_total_matches:
                    break
                    
        except re.error as e:
            logger.error(f"Invalid regex pattern: {e}")
        except Exception as e:
            logger.error(f"Error in regex search: {e}")
        
        return matches
    
    def search_content(self, pattern: str, base_path: str = '.',
                      filters: Optional[List[str]] = None) -> List[FileMatch]:
        """
        Search file contents for text patterns.
        
        Args:
            pattern: Text pattern to search for
            base_path: Base directory to search in
            filters: Optional file extension filters
            
        Returns:
            List of content matches with context
        """
        matches = []
        
        try:
            # Compile regex pattern for content search
            regex_pattern = re.compile(re.escape(pattern), re.IGNORECASE)
            base_path_obj = Path(base_path).resolve()
            
            # Walk through directory tree
            for root, dirs, files in base_path_obj.walk():
                for filename in files:
                    file_path = root / filename
                    
                    # Apply extension filters
                    if filters and not any(filename.endswith(ext) for ext in filters):
                        continue
                    
                    # Skip binary files
                    if self._is_likely_binary(file_path):
                        continue
                    
                    # Check permissions
                    if not self.fs_manager.check_permissions(file_path):
                        continue
                    
                    # Search content
                    file_matches = self._search_file_content(file_path, regex_pattern)
                    matches.extend(file_matches)
                    
                    if len(matches) >= self.max_total_matches:
                        break
                
                if len(matches) >= self.max_total_matches:
                    break
                    
        except Exception as e:
            logger.error(f"Error in content search: {e}")
        
        return matches
    
    def filter_by_extensions(self, files: List[Path], extensions: List[str]) -> List[Path]:
        """
        Filter files by multiple extensions.
        
        Args:
            files: List of file paths
            extensions: List of extensions to include (e.g., ['.py', '.js'])
            
        Returns:
            Filtered list of files
        """
        if not extensions:
            return files
        
        filtered_files = []
        for file_path in files:
            if any(file_path.name.endswith(ext) for ext in extensions):
                filtered_files.append(file_path)
        
        return filtered_files
    
    def _search_file_content(self, file_path: Path, pattern: Pattern) -> List[FileMatch]:
        """
        Search content within a single file.
        
        Args:
            file_path: Path to the file
            pattern: Compiled regex pattern
            
        Returns:
            List of matches in the file
        """
        matches = []
        
        try:
            # Read file content
            encoding = self.fs_manager.detect_encoding(file_path)
            content = self.fs_manager.read_file_content(file_path, encoding)
            lines = content.split('\n')
            
            # Search each line
            for line_num, line in enumerate(lines, 1):
                if pattern.search(line):
                    # Extract context
                    context_before = self._get_context_lines(
                        lines, line_num - 1, -self.max_context_lines, 0
                    )
                    context_after = self._get_context_lines(
                        lines, line_num - 1, 1, self.max_context_lines + 1
                    )
                    
                    matches.append(FileMatch(
                        file_path=str(file_path),
                        line_number=line_num,
                        content=line.strip(),
                        context_before=context_before,
                        context_after=context_after
                    ))
                    
                    if len(matches) >= self.max_matches_per_file:
                        break
                        
        except Exception as e:
            logger.warning(f"Error searching content in {file_path}: {e}")
        
        return matches
    
    def _get_context_lines(self, lines: List[str], current_line: int,
                          start_offset: int, end_offset: int) -> List[str]:
        """
        Get context lines around a match.
        
        Args:
            lines: All lines in the file
            current_line: Current line index (0-based)
            start_offset: Start offset (negative for before)
            end_offset: End offset (positive for after)
            
        Returns:
            List of context lines
        """
        start_idx = max(0, current_line + start_offset)
        end_idx = min(len(lines), current_line + end_offset)
        
        return [lines[i].strip() for i in range(start_idx, end_idx)]
    
    def _is_likely_binary(self, file_path: Path) -> bool:
        """
        Quick check if file is likely binary.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if likely binary
        """
        # Check extension first
        binary_extensions = {
            '.exe', '.dll', '.so', '.dylib', '.a', '.lib',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico',
            '.mp3', '.wav', '.mp4', '.avi', '.zip', '.tar',
            '.gz', '.pdf', '.doc', '.docx', '.pyc', '.pyo'
        }
        
        if file_path.suffix.lower() in binary_extensions:
            return True
        
        # Quick content check
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(512)  # Read first 512 bytes
                if b'\x00' in chunk:  # Null bytes indicate binary
                    return True
        except Exception:
            return True  # If we can't read it, assume binary
        
        return False