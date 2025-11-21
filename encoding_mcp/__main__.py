#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Encoding MCP module execution entry point
Used when running with python -m encoding_mcp
"""

from .server import cli_main

if __name__ == "__main__":
    cli_main()
