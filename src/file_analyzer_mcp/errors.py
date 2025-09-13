"""
Error handling and custom exceptions for the File Analyzer MCP server.

This module defines custom exception classes and error handling utilities
for different types of errors that can occur during file analysis.
"""

from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class FileAnalyzerError(Exception):
    """Base exception class for File Analyzer errors."""
    
    def __init__(self, message: str, error_code: str = "GENERAL_ERROR", 
                 details: Optional[Dict[str, Any]] = None):
        """
        Initialize the error.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary representation."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }


class FileSystemError(FileAnalyzerError):
    """Errors related to file system operations."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, 
                 error_code: str = "FILESYSTEM_ERROR"):
        super().__init__(message, error_code, {"file_path": file_path})
        self.file_path = file_path


class PathValidationError(FileSystemError):
    """Errors related to path validation and security."""
    
    def __init__(self, message: str, file_path: Optional[str] = None):
        super().__init__(message, file_path, "PATH_VALIDATION_ERROR")


class PermissionError(FileSystemError):
    """Errors related to file permissions."""
    
    def __init__(self, message: str, file_path: Optional[str] = None):
        super().__init__(message, file_path, "PERMISSION_ERROR")


class FileSizeError(FileSystemError):
    """Errors related to file size limits."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, 
                 file_size: Optional[int] = None, max_size: Optional[int] = None):
        details = {"file_path": file_path, "file_size": file_size, "max_size": max_size}
        super().__init__(message, file_path, "FILE_SIZE_ERROR")
        self.details.update(details)


class AnalysisError(FileAnalyzerError):
    """Errors related to code analysis operations."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, 
                 language: Optional[str] = None, error_code: str = "ANALYSIS_ERROR"):
        details = {"file_path": file_path, "language": language}
        super().__init__(message, error_code, details)
        self.file_path = file_path
        self.language = language


class SyntaxAnalysisError(AnalysisError):
    """Errors related to syntax parsing."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, 
                 language: Optional[str] = None, line_number: Optional[int] = None):
        super().__init__(message, file_path, language, "SYNTAX_ERROR")
        self.details["line_number"] = line_number
        self.line_number = line_number


class EncodingError(FileAnalyzerError):
    """Errors related to file encoding detection and handling."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, 
                 encoding: Optional[str] = None):
        details = {"file_path": file_path, "encoding": encoding}
        super().__init__(message, "ENCODING_ERROR", details)
        self.file_path = file_path
        self.encoding = encoding


class SearchError(FileAnalyzerError):
    """Errors related to file and content search operations."""
    
    def __init__(self, message: str, pattern: Optional[str] = None, 
                 search_type: Optional[str] = None):
        details = {"pattern": pattern, "search_type": search_type}
        super().__init__(message, "SEARCH_ERROR", details)
        self.pattern = pattern
        self.search_type = search_type


class ConfigurationError(FileAnalyzerError):
    """Errors related to configuration loading and validation."""
    
    def __init__(self, message: str, config_path: Optional[str] = None, 
                 validation_errors: Optional[List[str]] = None):
        details = {"config_path": config_path, "validation_errors": validation_errors}
        super().__init__(message, "CONFIGURATION_ERROR", details)
        self.config_path = config_path
        self.validation_errors = validation_errors or []


class MCPError(FileAnalyzerError):
    """Errors related to MCP protocol operations."""
    
    def __init__(self, message: str, tool_name: Optional[str] = None, 
                 request_id: Optional[str] = None):
        details = {"tool_name": tool_name, "request_id": request_id}
        super().__init__(message, "MCP_ERROR", details)
        self.tool_name = tool_name
        self.request_id = request_id


class ErrorHandler:
    """Centralized error handling and logging."""
    
    def __init__(self, logger_name: str = __name__):
        """Initialize the error handler."""
        self.logger = logging.getLogger(logger_name)
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle an error and return standardized error information.
        
        Args:
            error: The exception that occurred
            context: Additional context information
            
        Returns:
            Standardized error dictionary
        """
        context = context or {}
        
        if isinstance(error, FileAnalyzerError):
            # Custom error with structured information
            error_dict = error.to_dict()
            error_dict["context"] = context
            
            # Log with appropriate level
            if isinstance(error, (PathValidationError, PermissionError)):
                self.logger.warning(f"{error.error_code}: {error.message}")
            else:
                self.logger.error(f"{error.error_code}: {error.message}")
            
            return error_dict
        else:
            # Generic exception
            error_dict = {
                "error_type": "UnhandledException",
                "error_code": "UNHANDLED_ERROR",
                "message": str(error),
                "details": {"exception_type": type(error).__name__},
                "context": context
            }
            
            self.logger.error(f"Unhandled error: {error}", exc_info=True)
            return error_dict
    
    def handle_partial_failure(self, operation: str, total_items: int, 
                             failed_items: List[Dict[str, Any]], 
                             errors: List[Exception]) -> Dict[str, Any]:
        """
        Handle partial failures in batch operations.
        
        Args:
            operation: Name of the operation
            total_items: Total number of items processed
            failed_items: List of items that failed
            errors: List of errors that occurred
            
        Returns:
            Partial failure summary
        """
        success_count = total_items - len(failed_items)
        failure_count = len(failed_items)
        
        summary = {
            "operation": operation,
            "total_items": total_items,
            "success_count": success_count,
            "failure_count": failure_count,
            "success_rate": success_count / total_items if total_items > 0 else 0,
            "failed_items": failed_items,
            "errors": [self.handle_error(error) for error in errors]
        }
        
        if failure_count > 0:
            self.logger.warning(
                f"Partial failure in {operation}: {success_count}/{total_items} succeeded"
            )
        
        return summary
    
    def create_error_response(self, error: Exception, 
                            context: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a user-friendly error response message.
        
        Args:
            error: The exception that occurred
            context: Additional context information
            
        Returns:
            Formatted error message
        """
        error_dict = self.handle_error(error, context)
        
        if isinstance(error, FileAnalyzerError):
            # Structured error message
            message = f"Error: {error.message}"
            if error.details:
                details = []
                for key, value in error.details.items():
                    if value is not None:
                        details.append(f"{key}: {value}")
                if details:
                    message += f" ({', '.join(details)})"
            return message
        else:
            # Generic error message
            return f"An unexpected error occurred: {str(error)}"


# Global error handler instance
error_handler = ErrorHandler()


def handle_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function for error handling."""
    return error_handler.handle_error(error, context)


def create_error_response(error: Exception, context: Optional[Dict[str, Any]] = None) -> str:
    """Convenience function for creating error responses."""
    return error_handler.create_error_response(error, context)