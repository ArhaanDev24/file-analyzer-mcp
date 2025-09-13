"""
Main entry point for the File Analyzer MCP server.

This module sets up stdio communication with MCP clients and runs the server
with command-line argument support and configuration management.
"""

import sys
import asyncio
import argparse
import logging
from pathlib import Path
from .server import FileAnalyzerMCPServer
from .config import load_config, FileAnalyzerConfig


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="File Analyzer MCP Server - Comprehensive file analysis for AI assistants"
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to configuration file (JSON format)'
    )
    
    parser.add_argument(
        '--log-level', '-l',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Set logging level (overrides config)'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        help='Path to log file (overrides config)'
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Enable debug mode'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='File Analyzer MCP Server 1.0.0'
    )
    
    parser.add_argument(
        '--validate-config',
        action='store_true',
        help='Validate configuration and exit'
    )
    
    return parser.parse_args()


def setup_configuration(args) -> FileAnalyzerConfig:
    """Set up configuration from file and command-line arguments."""
    # Load base configuration
    config = load_config(args.config)
    
    # Override with command-line arguments
    if args.log_level:
        config.logging.level = args.log_level
    
    if args.log_file:
        config.logging.file_path = args.log_file
    
    if args.debug:
        config.server.debug = True
        config.logging.level = 'DEBUG'
    
    return config


async def main():
    """Main entry point for the MCP server."""
    args = parse_arguments()
    
    # Load and validate configuration
    try:
        config = setup_configuration(args)
        
        # Validate configuration if requested
        if args.validate_config:
            errors = config.validate()
            if errors:
                print("Configuration validation errors:")
                for error in errors:
                    print(f"  - {error}")
                sys.exit(1)
            else:
                print("Configuration is valid")
                sys.exit(0)
        
        # Set up logging
        config.setup_logging()
        logger = logging.getLogger(__name__)
        
        # Log configuration info
        if config.server.debug:
            logger.debug("Configuration loaded:")
            logger.debug(f"  Analysis max file size: {config.analysis.max_file_size}")
            logger.debug(f"  Security allow absolute paths: {config.security.allow_absolute_paths}")
            logger.debug(f"  Logging level: {config.logging.level}")
        
        # Validate configuration
        errors = config.validate()
        if errors:
            logger.warning(f"Configuration validation warnings: {errors}")
        
        logger.info(f"Starting {config.server.name} v{config.server.version}")
        
        # Create and run server
        server = FileAnalyzerMCPServer(config)
        await server.server.run()
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        if args.debug:
            import traceback
            logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())