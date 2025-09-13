#!/bin/bash

# File Analyzer MCP Server Installation Script

set -e

echo "🚀 Installing File Analyzer MCP Server..."

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.8+ required, found $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install mcp typing-extensions chardet

# Verify installation
echo "🧪 Testing installation..."
PYTHONPATH=src python3 -m file_analyzer_mcp --version

# Run comprehensive test
echo "🔍 Running comprehensive test..."
python3 comprehensive_test.py

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Copy the absolute path: $(pwd)"
echo "2. Update your MCP client configuration:"
echo "   - For Kiro: .kiro/settings/mcp.json"
echo "   - For Claude: ~/Library/Application Support/Claude/claude_desktop_config.json"
echo ""
echo "📖 See examples/ directory for configuration templates"
echo "🔧 Use --help for command-line options"
echo ""
echo "✨ Ready to analyze files with AI!"