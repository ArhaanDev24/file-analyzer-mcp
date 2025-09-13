# Claude Desktop Integration Guide

## Configuration File Location

Claude Desktop looks for MCP configuration at:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

## Basic Configuration

Add this to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "file-analyzer": {
      "command": "python3",
      "args": ["-m", "file_analyzer_mcp"],
      "cwd": "/absolute/path/to/file-analyzer-mcp",
      "env": {
        "PYTHONPATH": "/absolute/path/to/file-analyzer-mcp/src"
      }
    }
  }
}
```

## Advanced Configuration

For production use with custom settings:

```json
{
  "mcpServers": {
    "file-analyzer": {
      "command": "python3",
      "args": [
        "-m", "file_analyzer_mcp",
        "--config", "/path/to/config.json",
        "--log-level", "INFO"
      ],
      "cwd": "/absolute/path/to/file-analyzer-mcp",
      "env": {
        "PYTHONPATH": "/absolute/path/to/file-analyzer-mcp/src",
        "FA_MAX_FILE_SIZE": "104857600",
        "FA_ALLOW_ABSOLUTE_PATHS": "true"
      }
    }
  }
}
```

## Verification

1. Restart Claude Desktop
2. Start a new conversation
3. The file analyzer tools should be available automatically
4. Test with: "Can you analyze the file at /path/to/some/file.py?"

## Example Usage in Claude

Once integrated, you can use commands like:

- "Analyze the Python file at src/main.py"
- "What's the structure of the src/ directory?"
- "Search for all TODO comments in the codebase"
- "Find all Python files containing 'async def'"
- "What's the complexity of the functions in utils.py?"