"""
Configuration management for the File Analyzer MCP server.

This module provides configuration loading, validation, and default settings
for the MCP server and its analysis components.
"""

import os
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
import sys

logger = logging.getLogger(__name__)


@dataclass
class AnalysisConfig:
    """Configuration for analysis operations."""
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    chunk_size: int = 8192  # 8KB
    max_context_lines: int = 3
    max_matches_per_file: int = 100
    max_total_matches: int = 1000
    enable_complexity_analysis: bool = True
    enable_todo_detection: bool = True
    enable_docstring_analysis: bool = True


@dataclass
class SecurityConfig:
    """Configuration for security settings."""
    allow_absolute_paths: bool = True
    allow_symlinks: bool = False
    restricted_paths: List[str] = field(default_factory=list)
    max_directory_depth: int = 50


@dataclass
class LoggingConfig:
    """Configuration for logging."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


@dataclass
class ServerConfig:
    """Configuration for the MCP server."""
    name: str = "file-analyzer-mcp"
    version: str = "1.0.0"
    description: str = "MCP server for comprehensive file and code analysis"
    protocol_version: str = "2024-11-05"
    debug: bool = False


@dataclass
class FileAnalyzerConfig:
    """Main configuration class for the File Analyzer MCP server."""
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    
    @classmethod
    def load_from_file(cls, config_path: str) -> 'FileAnalyzerConfig':
        """
        Load configuration from a JSON file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Configuration instance
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            return cls.from_dict(config_data)
            
        except FileNotFoundError:
            logger.warning(f"Configuration file not found: {config_path}")
            return cls()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            return cls()
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return cls()
    
    @classmethod
    def load_from_env(cls) -> 'FileAnalyzerConfig':
        """
        Load configuration from environment variables.
        
        Returns:
            Configuration instance
        """
        config = cls()
        
        # Analysis settings
        if os.getenv('FA_MAX_FILE_SIZE'):
            try:
                config.analysis.max_file_size = int(os.getenv('FA_MAX_FILE_SIZE'))
            except ValueError:
                logger.warning("Invalid FA_MAX_FILE_SIZE value")
        
        if os.getenv('FA_CHUNK_SIZE'):
            try:
                config.analysis.chunk_size = int(os.getenv('FA_CHUNK_SIZE'))
            except ValueError:
                logger.warning("Invalid FA_CHUNK_SIZE value")
        
        if os.getenv('FA_MAX_CONTEXT_LINES'):
            try:
                config.analysis.max_context_lines = int(os.getenv('FA_MAX_CONTEXT_LINES'))
            except ValueError:
                logger.warning("Invalid FA_MAX_CONTEXT_LINES value")
        
        # Security settings
        if os.getenv('FA_ALLOW_ABSOLUTE_PATHS'):
            config.security.allow_absolute_paths = os.getenv('FA_ALLOW_ABSOLUTE_PATHS').lower() == 'true'
        
        if os.getenv('FA_ALLOW_SYMLINKS'):
            config.security.allow_symlinks = os.getenv('FA_ALLOW_SYMLINKS').lower() == 'true'
        
        if os.getenv('FA_RESTRICTED_PATHS'):
            config.security.restricted_paths = os.getenv('FA_RESTRICTED_PATHS').split(',')
        
        # Logging settings
        if os.getenv('FA_LOG_LEVEL'):
            config.logging.level = os.getenv('FA_LOG_LEVEL').upper()
        
        if os.getenv('FA_LOG_FILE'):
            config.logging.file_path = os.getenv('FA_LOG_FILE')
        
        # Server settings
        if os.getenv('FA_DEBUG'):
            config.server.debug = os.getenv('FA_DEBUG').lower() == 'true'
        
        return config
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileAnalyzerConfig':
        """
        Create configuration from dictionary.
        
        Args:
            data: Configuration dictionary
            
        Returns:
            Configuration instance
        """
        config = cls()
        
        # Analysis configuration
        if 'analysis' in data:
            analysis_data = data['analysis']
            if 'max_file_size' in analysis_data:
                config.analysis.max_file_size = analysis_data['max_file_size']
            if 'chunk_size' in analysis_data:
                config.analysis.chunk_size = analysis_data['chunk_size']
            if 'max_context_lines' in analysis_data:
                config.analysis.max_context_lines = analysis_data['max_context_lines']
            if 'max_matches_per_file' in analysis_data:
                config.analysis.max_matches_per_file = analysis_data['max_matches_per_file']
            if 'max_total_matches' in analysis_data:
                config.analysis.max_total_matches = analysis_data['max_total_matches']
            if 'enable_complexity_analysis' in analysis_data:
                config.analysis.enable_complexity_analysis = analysis_data['enable_complexity_analysis']
            if 'enable_todo_detection' in analysis_data:
                config.analysis.enable_todo_detection = analysis_data['enable_todo_detection']
            if 'enable_docstring_analysis' in analysis_data:
                config.analysis.enable_docstring_analysis = analysis_data['enable_docstring_analysis']
        
        # Security configuration
        if 'security' in data:
            security_data = data['security']
            if 'allow_absolute_paths' in security_data:
                config.security.allow_absolute_paths = security_data['allow_absolute_paths']
            if 'allow_symlinks' in security_data:
                config.security.allow_symlinks = security_data['allow_symlinks']
            if 'restricted_paths' in security_data:
                config.security.restricted_paths = security_data['restricted_paths']
            if 'max_directory_depth' in security_data:
                config.security.max_directory_depth = security_data['max_directory_depth']
        
        # Logging configuration
        if 'logging' in data:
            logging_data = data['logging']
            if 'level' in logging_data:
                config.logging.level = logging_data['level']
            if 'format' in logging_data:
                config.logging.format = logging_data['format']
            if 'file_path' in logging_data:
                config.logging.file_path = logging_data['file_path']
            if 'max_file_size' in logging_data:
                config.logging.max_file_size = logging_data['max_file_size']
            if 'backup_count' in logging_data:
                config.logging.backup_count = logging_data['backup_count']
        
        # Server configuration
        if 'server' in data:
            server_data = data['server']
            if 'name' in server_data:
                config.server.name = server_data['name']
            if 'version' in server_data:
                config.server.version = server_data['version']
            if 'description' in server_data:
                config.server.description = server_data['description']
            if 'protocol_version' in server_data:
                config.server.protocol_version = server_data['protocol_version']
            if 'debug' in server_data:
                config.server.debug = server_data['debug']
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Configuration dictionary
        """
        return {
            'analysis': {
                'max_file_size': self.analysis.max_file_size,
                'chunk_size': self.analysis.chunk_size,
                'max_context_lines': self.analysis.max_context_lines,
                'max_matches_per_file': self.analysis.max_matches_per_file,
                'max_total_matches': self.analysis.max_total_matches,
                'enable_complexity_analysis': self.analysis.enable_complexity_analysis,
                'enable_todo_detection': self.analysis.enable_todo_detection,
                'enable_docstring_analysis': self.analysis.enable_docstring_analysis,
            },
            'security': {
                'allow_absolute_paths': self.security.allow_absolute_paths,
                'allow_symlinks': self.security.allow_symlinks,
                'restricted_paths': self.security.restricted_paths,
                'max_directory_depth': self.security.max_directory_depth,
            },
            'logging': {
                'level': self.logging.level,
                'format': self.logging.format,
                'file_path': self.logging.file_path,
                'max_file_size': self.logging.max_file_size,
                'backup_count': self.logging.backup_count,
            },
            'server': {
                'name': self.server.name,
                'version': self.server.version,
                'description': self.server.description,
                'protocol_version': self.server.protocol_version,
                'debug': self.server.debug,
            }
        }
    
    def validate(self) -> List[str]:
        """
        Validate configuration values.
        
        Returns:
            List of validation errors
        """
        errors = []
        
        # Validate analysis settings
        if self.analysis.max_file_size <= 0:
            errors.append("max_file_size must be positive")
        
        if self.analysis.chunk_size <= 0:
            errors.append("chunk_size must be positive")
        
        if self.analysis.max_context_lines < 0:
            errors.append("max_context_lines must be non-negative")
        
        if self.analysis.max_matches_per_file <= 0:
            errors.append("max_matches_per_file must be positive")
        
        if self.analysis.max_total_matches <= 0:
            errors.append("max_total_matches must be positive")
        
        # Validate security settings
        if self.security.max_directory_depth <= 0:
            errors.append("max_directory_depth must be positive")
        
        # Validate logging settings
        valid_log_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if self.logging.level not in valid_log_levels:
            errors.append(f"logging level must be one of: {valid_log_levels}")
        
        if self.logging.max_file_size <= 0:
            errors.append("logging max_file_size must be positive")
        
        if self.logging.backup_count < 0:
            errors.append("logging backup_count must be non-negative")
        
        return errors
    
    def setup_logging(self):
        """Set up logging based on configuration."""
        # Convert string level to logging constant
        level = getattr(logging, self.logging.level.upper(), logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(self.logging.format)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        
        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Add console handler
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # Add file handler if specified
        if self.logging.file_path:
            try:
                from logging.handlers import RotatingFileHandler
                file_handler = RotatingFileHandler(
                    self.logging.file_path,
                    maxBytes=self.logging.max_file_size,
                    backupCount=self.logging.backup_count
                )
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)
            except Exception as e:
                logger.error(f"Failed to set up file logging: {e}")


def load_config(config_path: Optional[str] = None) -> FileAnalyzerConfig:
    """
    Load configuration from file or environment.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Configuration instance
    """
    if config_path and Path(config_path).exists():
        config = FileAnalyzerConfig.load_from_file(config_path)
    else:
        # Try to load from default locations
        default_paths = [
            'file_analyzer_config.json',
            '~/.file_analyzer_config.json',
            '/etc/file_analyzer_config.json'
        ]
        
        config = None
        for path in default_paths:
            expanded_path = Path(path).expanduser()
            if expanded_path.exists():
                config = FileAnalyzerConfig.load_from_file(str(expanded_path))
                break
        
        if config is None:
            # Load from environment variables
            config = FileAnalyzerConfig.load_from_env()
    
    # Validate configuration
    errors = config.validate()
    if errors:
        logger.warning(f"Configuration validation errors: {errors}")
    
    return config