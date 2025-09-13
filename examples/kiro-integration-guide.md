# Kiro Integration Guide

## Method 1: Workspace-Level Configuration

Create `.kiro/settings/mcp.json` in your workspace root:

```json
{
  "mcpServers": {
    "file-analyzer": {
      "command": "python3",
      "args": ["-m", "file_analyzer_mcp"],
      "cwd": "/absolute/path/to/file-analyzer-mcp",
      "env": {
        "PYTHONPATH": "/absolute/path/to/file-analyzer-mcp/src"
      },
      "disabled": false,
      "autoApprove": [
        "analyze_file",
        "analyze_directory", 
        "search_files"
      ]
    }
  }
}
```

## Method 2: User-Level Configuration

Create `~/.kiro/settings/mcp.json` for global access:

```json
{
  "mcpServers": {
    "file-analyzer": {
      "command": "python3",
      "args": ["-m", "file_analyzer_mcp", "--config", "/path/to/config.json"],
      "cwd": "/absolute/path/to/file-analyzer-mcp",
      "env": {
        "PYTHONPATH": "/absolute/path/to/file-analyzer-mcp/src",
        "FA_LOG_LEVEL": "INFO"
      },
      "disabled": false,
      "autoApprove": ["analyze_file"]
    }
  }
}
```

## Method 3: Using Command Palette

1. Open Kiro IDE
2. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
3. Type "MCP" and select "Open Kiro MCP UI"
4. Add a new server with these settings:
   - **Name**: file-analyzer
   - **Command**: python3
   - **Args**: -m file_analyzer_mcp
   - **Working Directory**: /path/to/file-analyzer-mcp
   - **Environment**: PYTHONPATH=/path/to/file-analyzer-mcp/src

## Configuration Options

### Basic Configuration
```json
{
  "command": "python3",
  "args": ["-m", "file_analyzer_mcp"],
  "cwd": "/path/to/file-analyzer-mcp",
  "env": {
    "PYTHONPATH": "/path/to/file-analyzer-mcp/src"
  }
}
```

### Advanced Configuration with Custom Settings
```json
{
  "command": "python3", 
  "args": [
    "-m", "file_analyzer_mcp",
    "--config", "/path/to/custom-config.json",
    "--log-level", "DEBUG"
  ],
  "cwd": "/path/to/file-analyzer-mcp",
  "env": {
    "PYTHONPATH": "/path/to/file-analyzer-mcp/src",
    "FA_MAX_FILE_SIZE": "52428800",
    "FA_ALLOW_ABSOLUTE_PATHS": "true"
  }
}
```

### Auto-Approval Settings
```json
{
  "autoApprove": [
    "analyze_file",      // Auto-approve file analysis
    "analyze_directory", // Auto-approve directory analysis  
    "search_files"       // Auto-approve file searches
  ]
}
```

## Verification Steps

1. **Check Server Status**: Look for "file-analyzer" in the MCP Server view
2. **Test Connection**: The server should show as "Connected" 
3. **Verify Tools**: You should see 3 tools available:
   - analyze_file
   - analyze_directory
   - search_files

## Troubleshooting

### Server Won't Start
- Check Python path: `which python3`
- Verify PYTHONPATH is correct
- Test manually: `PYTHONPATH=src python3 -m file_analyzer_mcp --help`

### Permission Issues
- Ensure the working directory is accessible
- Check file permissions on the server files
- Verify Python can import the modules

### Tools Not Appearing
- Check MCP Server view for connection status
- Look at server logs for error messages
- Restart Kiro IDE after configuration changes