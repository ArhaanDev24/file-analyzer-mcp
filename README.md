# File Analyzer MCP Server

A Model Context Protocol (MCP) server that provides comprehensive file analysis capabilities for AI assistants. This server enables AI to understand code structure, analyze file contents, detect programming languages, count metrics, and provide insights about codebases.

## Features

- **File Analysis**: Analyze individual files for structure, metrics, and quality indicators
- **Language Detection**: Automatic detection of programming languages based on extensions, shebangs, and content
- **Code Metrics**: Calculate complexity, maintainability index, and code quality metrics
- **Python Analysis**: Advanced AST-based analysis for Python files including functions, classes, imports
- **Generic Analysis**: Regex-based analysis for JavaScript, Java, C++, Go, Rust, and other languages
- **TODO Detection**: Find TODO, FIXME, HACK, and other comment markers
- **Security**: Path validation and permission checking for safe file system access

## Installation

1. Clone or download this repository
2. Install dependencies:

```bash
cd file-analyzer-mcp
pip install -e .
```

## Dependencies

- `mcp` - Model Context Protocol library
- `typing-extensions` - Extended typing support
- Python 3.8+ standard library modules

## Usage

### Running the Server

The server can be run directly:

```bash
python -m file_analyzer_mcp
```

### MCP Client Configuration

Add the server to your MCP client configuration:

```json
{
  "mcpServers": {
    "file-analyzer": {
      "command": "python",
      "args": ["-m", "file_analyzer_mcp"],
      "cwd": "/path/to/file-analyzer-mcp"
    }
  }
}
```

### Available Tools

#### analyze_file

Analyze a single file for code metrics and structure.

**Parameters:**
- `file_path` (required): Path to the file to analyze
- `analysis_type` (optional): Type of analysis ("basic", "full", "metrics")

**Example:**
```json
{
  "name": "analyze_file",
  "arguments": {
    "file_path": "src/main.py",
    "analysis_type": "full"
  }
}
```

#### analyze_directory

Analyze a directory and its contents recursively.

**Parameters:**
- `directory_path` (required): Path to the directory to analyze
- `recursive` (optional): Whether to analyze subdirectories (default: true)
- `filters` (optional): Array of file extensions to include

**Example:**
```json
{
  "name": "analyze_directory",
  "arguments": {
    "directory_path": "src/",
    "recursive": true,
    "filters": [".py", ".js"]
  }
}
```

#### search_files

Search for files or content using patterns.

**Parameters:**
- `pattern` (required): Search pattern
- `search_type` (optional): Type of search ("glob", "regex", "content")
- `filters` (optional): Array of file extensions to include

**Example:**
```json
{
  "name": "search_files",
  "arguments": {
    "pattern": "*.py",
    "search_type": "glob"
  }
}
```

## Supported Languages

### Full Analysis (AST-based)
- Python

### Basic Analysis (Regex-based)
- JavaScript/TypeScript
- Java
- C/C++
- Go
- Rust
- Ruby
- PHP
- Swift
- Kotlin
- Scala
- C#
- HTML/CSS
- JSON/YAML
- Markdown
- Shell scripts

## Analysis Results

### File Analysis Result

```json
{
  "file_path": "src/example.py",
  "file_size": 1024,
  "line_count": 50,
  "language": "python",
  "last_modified": "2024-01-01T12:00:00",
  "is_binary": false,
  "encoding": "utf-8",
  "metrics": {
    "function_count": 5,
    "class_count": 2,
    "import_count": 10,
    "comment_lines": 15,
    "blank_lines": 8,
    "cyclomatic_complexity": 12.5,
    "maintainability_index": 85.2,
    "todos": [
      {
        "line_number": 42,
        "comment_type": "TODO",
        "text": "Implement error handling",
        "file_path": "src/example.py"
      }
    ]
  },
  "errors": []
}
```

## Security

The server implements several security measures:

- Path validation to prevent directory traversal attacks
- Permission checking before file access
- File size limits to prevent memory exhaustion
- Graceful error handling for permission denied scenarios

## Development

### Project Structure

```
file-analyzer-mcp/
├── src/file_analyzer_mcp/
│   ├── __init__.py
│   ├── __main__.py          # Entry point
│   ├── server.py            # MCP server implementation
│   ├── models.py            # Data models
│   ├── analyzer_service.py  # Main service coordinator
│   ├── filesystem.py        # File system operations
│   ├── language_detector.py # Language detection
│   └── analyzers/
│       ├── __init__.py
│       ├── base.py          # Base analyzer class
│       ├── python_analyzer.py # Python-specific analysis
│       └── generic_analyzer.py # Generic language analysis
├── tests/                   # Unit tests
├── pyproject.toml          # Project configuration
└── README.md
```

### Running Tests

```bash
python -m pytest tests/
```

## License

This project is open source. See the license file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.