"""
File system operations and security management.

This module provides secure file system access with path validation,
permission checking, and streaming capabilities for large files.
"""

import os
import stat
from pathlib import Path
from typing import Iterator, Optional, List
import logging

logger = logging.getLogger(__name__)


class FileSystemManager:
    """
    Manages secure file system operations for the MCP server.
    
    This class provides methods for validating paths, checking permissions,
    and reading files safely with appropriate security measures.
    """
    
    def __init__(self, max_file_size: int = 100 * 1024 * 1024):  # 100MB default
        """
        Initialize the FileSystemManager.
        
        Args:
            max_file_size: Maximum file size to process in bytes
        """
        self.max_file_size = max_file_size
        self.chunk_size = 8192  # 8KB chunks for streaming
    
    def validate_path(self, path: str) -> Path:
        """
        Validate and normalize a file path.
        
        Args:
            path: The file path to validate
            
        Returns:
            Validated Path object
            
        Raises:
            ValueError: If path is invalid or unsafe
        """
        if not path:
            raise ValueError("Path cannot be empty")
        
        # Convert to Path object and resolve
        try:
            path_obj = Path(path).resolve()
        except (OSError, ValueError) as e:
            raise ValueError(f"Invalid path: {e}")
        
        # Check for path traversal attempts
        path_str = str(path_obj)
        if '..' in path_str or path_str.startswith('/'):
            # Allow absolute paths but log them
            logger.warning(f"Absolute path access: {path_str}")
        
        # Check if path exists
        if not path_obj.exists():
            raise ValueError(f"Path does not exist: {path_obj}")
        
        # Check file size if it's a file
        if path_obj.is_file():
            file_size = path_obj.stat().st_size
            if file_size > self.max_file_size:
                raise ValueError(f"File too large: {file_size} bytes (max: {self.max_file_size})")
        
        return path_obj
    
    def check_permissions(self, path: Path) -> bool:
        """
        Check if the file/directory is readable.
        
        Args:
            path: Path to check
            
        Returns:
            True if readable, False otherwise
        """
        try:
            # Check if path exists
            if not path.exists():
                logger.error(f"Path does not exist: {path}")
                return False
            
            # Check read permissions
            if not os.access(path, os.R_OK):
                logger.error(f"No read permission for: {path}")
                return False
            
            # For directories, check if we can list contents
            if path.is_dir():
                try:
                    list(path.iterdir())
                except PermissionError:
                    logger.error(f"Cannot list directory contents: {path}")
                    return False
            
            # For files, try to open for reading
            elif path.is_file():
                try:
                    with open(path, 'rb') as f:
                        f.read(1)  # Try to read one byte
                except PermissionError:
                    logger.error(f"Cannot read file: {path}")
                    return False
                except IOError as e:
                    logger.error(f"IO error reading file {path}: {e}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking permissions for {path}: {e}")
            return False
    
    def read_file_chunked(self, path: Path, encoding: str = 'utf-8') -> Iterator[str]:
        """
        Read a file in chunks for memory efficiency.
        
        Args:
            path: Path to the file to read
            encoding: File encoding to use
            
        Yields:
            File content chunks
            
        Raises:
            IOError: If file cannot be read
            UnicodeDecodeError: If file cannot be decoded with specified encoding
        """
        if not self.check_permissions(path):
            raise IOError(f"Cannot read file: {path}")
        
        try:
            with open(path, 'r', encoding=encoding, errors='replace') as file:
                while True:
                    chunk = file.read(self.chunk_size)
                    if not chunk:
                        break
                    yield chunk
        except UnicodeDecodeError as e:
            logger.error(f"Unicode decode error for {path}: {e}")
            # Try with binary mode and decode with error handling
            try:
                with open(path, 'rb') as file:
                    while True:
                        chunk = file.read(self.chunk_size)
                        if not chunk:
                            break
                        try:
                            yield chunk.decode(encoding, errors='replace')
                        except UnicodeDecodeError:
                            yield chunk.decode('latin1', errors='replace')
            except Exception as e:
                raise IOError(f"Failed to read file {path}: {e}")
        except Exception as e:
            raise IOError(f"Error reading file {path}: {e}")
    
    def read_file_content(self, path: Path, encoding: str = 'utf-8') -> str:
        """
        Read entire file content.
        
        Args:
            path: Path to the file to read
            encoding: File encoding to use
            
        Returns:
            Complete file content as string
        """
        return ''.join(self.read_file_chunked(path, encoding))
    
    def detect_encoding(self, path: Path) -> str:
        """
        Detect file encoding.
        
        Args:
            path: Path to the file
            
        Returns:
            Detected encoding or 'utf-8' as fallback
        """
        try:
            import chardet
            with open(path, 'rb') as file:
                raw_data = file.read(min(10000, path.stat().st_size))  # Read first 10KB
                result = chardet.detect(raw_data)
                return result.get('encoding', 'utf-8') or 'utf-8'
        except ImportError:
            # chardet not available, use utf-8 as default
            return 'utf-8'
        except Exception:
            return 'utf-8'
    
    def get_file_info(self, path: Path) -> dict:
        """
        Get basic file information.
        
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
                'is_file': path.is_file(),
                'is_dir': path.is_dir(),
                'exists': path.exists()
            }
        except (OSError, IOError) as e:
            logger.error(f"Error getting file info for {path}: {e}")
            return {
                'size': 0,
                'modified': 0,
                'is_file': False,
                'is_dir': False,
                'exists': False
            }