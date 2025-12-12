#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Encoding MCP Server v2.0.1
Modular version using professional encoding detection libraries
"""

from __future__ import annotations

import asyncio
import sys
import os
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
import mcp.types as types

# Import local modules
try:
    # When run as package
    from .encoding_detector import detect_file_encoding, get_available_detection_methods, get_recommended_libraries
    from .file_operations import (
        create_empty_file, 
        convert_file_encoding, 
        get_file_info, 
        list_supported_encodings,
        get_encoding_info
    )
except ImportError:
    # When run directly
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from encoding_detector import detect_file_encoding, get_available_detection_methods, get_recommended_libraries
    from file_operations import (
        create_empty_file, 
        convert_file_encoding, 
        get_file_info, 
        list_supported_encodings,
        get_encoding_info
    )

def format_encoding_result(result: dict, file_path: str) -> str:
    """
    Format encoding detection result.
    
    Args:
        result: Encoding detection result
        file_path: File path
        
    Returns:
        str: Formatted result string
    """
    if "error" in result:
        return f"❌ {result['error']}"
    
    response_text = f"📋 File encoding information: {os.path.basename(file_path)}\n\n"
    response_text += f"🔤 Encoding: {result['encoding']}\n"
    response_text += f"📏 File size: {result['file_size']} bytes\n"
    
    if result['has_bom']:
        response_text += f"🏷️  BOM: Yes ({result['bom_type']})\n"
    else:
        response_text += f"🏷️  BOM: No\n"
    
    response_text += f"🎯 Confidence: {result['confidence']}%\n"
    response_text += f"🔧 Detection method: {result.get('method', 'unknown')}\n"
    
    if 'language' in result and result['language'] != 'unknown':
        response_text += f"🌍 Language: {result['language']}\n"
    
    if result.get('first_bytes'):
        response_text += f"🔍 First 16 bytes (hex): {result['first_bytes']}\n"
    
    # Windows build compatibility advice
    encoding = result['encoding']
    encoding_info = get_encoding_info(encoding)
    
    if encoding == "utf-8-bom":
        response_text += "\n✅ Suitable encoding for Windows C++/PowerShell builds."
    elif encoding == "utf-8":
        response_text += "\n⚠️  UTF-8 without BOM - May cause issues in Windows C++/PowerShell."
    elif encoding in ["cp949", "euc-kr"]:
        response_text += "\n⚠️  Korean encoding - Recommend converting to UTF-8 with BOM."
    elif encoding == "ascii":
        response_text += "\n✅ ASCII encoding - No compatibility issues."
    elif encoding_info and encoding_info.get('windows_friendly'):
        response_text += "\n✅ Windows-compatible encoding."
    else:
        response_text += "\n❓ Unknown encoding - Consider converting to UTF-8 with BOM."
    
    return response_text

def get_system_info() -> str:
    """
    Return system information.
    """
    detection_methods = get_available_detection_methods()
    supported_encodings = list_supported_encodings()
    
    info_text = "🔧 Encoding MCP v2.0.1 System Information\n\n"
    
    # Detection methods
    info_text += "📊 Available encoding detection methods:\n"
    for method, available in detection_methods.items():
        status = "✅" if available else "❌"
        info_text += f"  {status} {method}\n"
    
    info_text += f"\n📚 Recommended libraries:\n{get_recommended_libraries()}\n\n"
    
    # Supported encodings
    info_text += "🎯 Supported encodings:\n"
    for encoding, info in supported_encodings.items():
        windows_icon = "🪟" if info['windows_friendly'] else "🐧"
        info_text += f"  {windows_icon} {encoding}: {info['name']}\n"
    
    return info_text

# Create server instance
app = Server("encoding-mcp-v2")

@app.list_tools()
async def list_tools():
    """Return list of available tools."""
    return [
        Tool(
            name="create_empty_file",
            description="Create an empty file with specified encoding. Creates only an empty file so Agent can fill in content.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_name": {
                        "type": "string",
                        "description": "File name to create (e.g., hello.cpp, test.h)"
                    },
                    "directory_path": {
                        "type": "string", 
                        "description": "Absolute path of directory to create file in"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "File encoding",
                        "enum": ["utf-8-bom", "utf-8", "cp949", "euc-kr", "ascii"],
                        "default": "utf-8-bom"
                    }
                },
                "required": ["file_name", "directory_path"]
            }
        ),
        Tool(
            name="detect_file_encoding",
            description="Accurately detect file encoding using professional libraries.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_name": {
                        "type": "string",
                        "description": "File name to check (e.g., hello.cpp, test.h)"
                    },
                    "directory_path": {
                        "type": "string",
                        "description": "Absolute path of directory containing the file"
                    },
                    "max_bytes": {
                        "type": "integer",
                        "description": "Maximum bytes to analyze (default: 8192)",
                        "default": 8192,
                        "minimum": 512,
                        "maximum": 65536
                    }
                },
                "required": ["file_name", "directory_path"]
            }
        ),
        Tool(
            name="convert_file_encoding",
            description="Convert file to specified encoding. Automatic backup support.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_name": {
                        "type": "string",
                        "description": "File name to convert (e.g., hello.cpp, test.h)"
                    },
                    "directory_path": {
                        "type": "string",
                        "description": "Absolute path of directory containing the file"
                    },
                    "target_encoding": {
                        "type": "string",
                        "description": "Target encoding",
                        "enum": ["utf-8-bom", "utf-8", "cp949", "euc-kr", "ascii"],
                        "default": "utf-8-bom"
                    },
                    "backup": {
                        "type": "boolean",
                        "description": "Whether to backup original file",
                        "default": False
                    }
                },
                "required": ["file_name", "directory_path"]
            }
        ),
        Tool(
            name="get_system_info",
            description="Check Encoding MCP system information. Shows available libraries and supported encodings.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """Execute tool."""
    
    if name == "create_empty_file":
        file_name = arguments.get("file_name", "")
        directory_path = arguments.get("directory_path", "")
        encoding = arguments.get("encoding", "utf-8-bom")
        
        # Combine file name and directory path
        file_path = os.path.join(directory_path, file_name)
        
        result = create_empty_file(file_path, encoding)
        
        # Select icon based on result
        if "successfully" in result.lower() or "success" in result.lower():
            icon = "✅"
        elif "permission" in result.lower() or "failed" in result.lower() or "error" in result.lower():
            icon = "❌"
        else:
            icon = "⚠️"
        
        return [
            types.TextContent(
                type="text",
                text=f"{icon} Create empty file\n\n{result}\n\n💡 Agent can use write tool to fill in content."
            )
        ]
    
    elif name == "detect_file_encoding":
        file_name = arguments.get("file_name", "")
        directory_path = arguments.get("directory_path", "")
        max_bytes = arguments.get("max_bytes", 8192)
        
        if not file_name or not directory_path:
            return [
                types.TextContent(
                    type="text",
                    text="❌ Both file name and directory path are required."
                )
            ]
        
        # Combine file name and directory path
        file_path = os.path.join(directory_path, file_name)
        
        result = detect_file_encoding(file_path, max_bytes)
        formatted_result = format_encoding_result(result, file_path)
        
        return [
            types.TextContent(
                type="text",
                text=formatted_result
            )
        ]
    
    elif name == "convert_file_encoding":
        file_name = arguments.get("file_name", "")
        directory_path = arguments.get("directory_path", "")
        target_encoding = arguments.get("target_encoding", "utf-8-bom")
        backup = arguments.get("backup", False)
        
        # Combine file name and directory path
        file_path = os.path.join(directory_path, file_name)
        
        result = convert_file_encoding(file_path, target_encoding, backup)
        
        # Select icon based on result
        if "completed" in result.lower() or "complete" in result.lower():
            icon = "✅"
        elif "failed" in result.lower() or "error" in result.lower():
            icon = "❌"
        else:
            icon = "ℹ️"
        
        return [
            types.TextContent(
                type="text",
                text=f"{icon} Encoding conversion\n\n{result}"
            )
        ]
    
    elif name == "get_system_info":
        system_info = get_system_info()
        
        return [
            types.TextContent(
                type="text",
                text=system_info
            )
        ]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Main execution function"""
    print("🚀 Starting Encoding MCP v2.0.1 server...", file=sys.stderr)
    print("📚 Professional encoding detection library support", file=sys.stderr)
    
    # Run server via stdio
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

def cli_main():
    """CLI entry point"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Server interrupted.", file=sys.stderr)
    except Exception as e:
        import traceback
        print(f"💥 Server error: {e}", file=sys.stderr)
        print("Full traceback:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    cli_main()
