#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Encoding MCP - UTF-8 with BOM file management tool for Windows build environments

This package provides the following features as a Model Context Protocol (MCP) server:
- UTF-8 with BOM file creation (optimized for Windows C++/PowerShell builds)
- Support for various encodings (utf-8-bom, utf-8, cp949, ascii)
- Automatic file encoding detection and conversion
- C++, PowerShell, Python, JavaScript template support
"""

try:
    from ._version import __version__
except ImportError:
    # Fallback for development installations
    __version__ = "1.0.0"
__author__ = "Encoding MCP Team"
__email__ = "whyj.park@gmail.com"
__description__ = "MCP server for creating and managing UTF-8 with BOM encoded files required for Windows build environments"

# Main functions can be imported directly from server module when needed

__all__ = [
    '__version__',
    '__author__',
    '__email__',
    '__description__'
]
