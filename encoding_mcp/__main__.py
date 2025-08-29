#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Encoding MCP 모듈 실행 엔트리 포인트
python -m encoding_mcp 로 실행할 때 사용됩니다.
"""

from .server import cli_main

if __name__ == "__main__":
    cli_main()
