"""
Main file analyzer service that coordinates all analysis operations.

This module provides the central service that routes analysis requests
to appropriate analyzers and aggregates results.
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

from .models import AnalysisResult, DirectoryAnalysis, SearchResult
from .analyzers.python_analyzer import PythonAnalyzer
from .analyzers.generic_analyzer import GenericAnalyzer
from .filesystem import FileSystemManager
from .language_detector import LanguageDetector
from .directory_analyzer import DirectoryAnalyzer
from .search_engine import SearchEngine

logger = logging.getLogger(__name__)


class FileAnalyzerService:
    """
    Main service for coordinating file analysis operations.
    
    This service acts as the central coordinator, routing requests to
    appropriate analyzers and handling errors gracefully.
    """
    
    def __init__(self):
        """Initialize the analyzer service."""
        self.fs_manager = FileSystemManager()
        self.language_detector = LanguageDetector()
        self.python_analyzer = PythonAnalyzer()
        self.generic_analyzer = GenericAnalyzer()
        self.directory_analyzer = DirectoryAnalyzer()
        self.search_engine = SearchEngine()
    
    def analyze_file(self, file_path: str, analysis_type: str = 'full') -> AnalysisResult:
        """
        Analyze a single file.
        
        Args:
            file_path: Path to the file to analyze
            analysis_type: Type of analysis ('basic', 'full', 'metrics')
            
        Returns:
            Complete analysis result
        """
        try:
            # Validate path
            path_obj = self.fs_manager.validate_path(file_path)
            
            # Get appropriate analyzer
            analyzer = self.get_analyzer(path_obj)
            
            if analyzer:
                return analyzer.analyze_file(file_path)
            else:
                # Fallback to basic analysis
                return self._basic_file_analysis(path_obj)
                
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            return AnalysisResult(
                file_path=file_path,
                file_size=0,
                line_count=0,
                language='unknown',
                last_modified=None,
                is_binary=False,
                encoding='utf-8',
                metrics=None,
                errors=[str(e)]
            )
    
    def get_analyzer(self, file_path: Path) -> Optional[Any]:
        """
        Get the appropriate analyzer for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Analyzer instance or None
        """
        try:
            # Detect language
            file_type_info = self.language_detector.get_file_type_info(file_path)
            language = file_type_info['language']
            
            # Route to appropriate analyzer
            if self.python_analyzer.supports_language(language):
                return self.python_analyzer
            elif self.generic_analyzer.supports_language(language):
                return self.generic_analyzer
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting analyzer for {file_path}: {e}")
            return None
    
    def _basic_file_analysis(self, file_path: Path) -> AnalysisResult:
        """
        Perform basic file analysis when no specific analyzer is available.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Basic analysis result
        """
        try:
            # Get file metadata
            file_info = self.fs_manager.get_file_info(file_path)
            file_type_info = self.language_detector.get_file_type_info(file_path)
            
            # Try to read content for line counting
            line_count = 0
            encoding = 'utf-8'
            if not file_type_info['is_binary']:
                try:
                    encoding = self.fs_manager.detect_encoding(file_path)
                    content = self.fs_manager.read_file_content(file_path, encoding)
                    line_count = content.count('\n') + (1 if content and not content.endswith('\n') else 0)
                except Exception as e:
                    logger.warning(f"Could not read file content for {file_path}: {e}")
            
            from datetime import datetime
            return AnalysisResult(
                file_path=str(file_path),
                file_size=file_info['size'],
                line_count=line_count,
                language=file_type_info['language'],
                last_modified=datetime.fromtimestamp(file_info['modified']),
                is_binary=file_type_info['is_binary'],
                encoding=encoding,
                metrics=None,
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"Error in basic analysis of {file_path}: {e}")
            from datetime import datetime
            return AnalysisResult(
                file_path=str(file_path),
                file_size=0,
                line_count=0,
                language='unknown',
                last_modified=datetime.now(),
                is_binary=False,
                encoding='utf-8',
                metrics=None,
                errors=[str(e)]
            )
    
    def analyze_directory(self, directory_path: str, recursive: bool = True, 
                         filters: Optional[List[str]] = None) -> DirectoryAnalysis:
        """
        Analyze a directory and its contents.
        
        Args:
            directory_path: Path to the directory
            recursive: Whether to analyze recursively
            filters: Optional file extension filters
            
        Returns:
            Directory analysis result
        """
        try:
            return self.directory_analyzer.analyze_directory(directory_path, recursive, filters)
        except Exception as e:
            logger.error(f"Error in directory analysis service: {e}")
            from datetime import datetime
            return DirectoryAnalysis(
                directory_path=directory_path,
                total_files=0,
                file_types={},
                total_size=0,
                languages={},
                structure=None,
                analysis_time=0.0,
                errors=[str(e)]
            )
    
    def search_files(self, pattern: str, search_type: str = 'glob', 
                    base_path: str = '.', filters: Optional[List[str]] = None) -> SearchResult:
        """
        Search for files matching a pattern.
        
        Args:
            pattern: Search pattern
            search_type: Type of search ('glob', 'regex', 'content')
            base_path: Base directory to search in
            filters: Optional file extension filters
            
        Returns:
            Search results
        """
        try:
            return self.search_engine.search_files(pattern, search_type, base_path, filters)
        except Exception as e:
            logger.error(f"Error in search service: {e}")
            return SearchResult(
                matches=[],
                total_matches=0,
                search_time=0.0,
                search_pattern=pattern,
                search_type=search_type,
                errors=[str(e)]
            )