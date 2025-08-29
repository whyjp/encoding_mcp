#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Encoding MCP - Windows 빌드 환경을 위한 UTF-8 with BOM 파일 관리 도구

이 패키지는 Model Context Protocol (MCP) 서버로서 다음 기능을 제공합니다:
- UTF-8 with BOM 파일 생성 (Windows C++/PowerShell 빌드 최적화)
- 다양한 인코딩 지원 (utf-8-bom, utf-8, cp949, ascii)
- 파일 인코딩 자동 감지 및 변환
- C++, PowerShell, Python, JavaScript 템플릿 지원
"""

__version__ = "1.0.0"
__author__ = "Encoding MCP Team"
__email__ = ""
__description__ = "Windows 빌드 환경에서 필요한 UTF-8 with BOM 인코딩 파일을 생성하고 관리하는 MCP 서버"

# 주요 함수들은 필요시 server 모듈에서 직접 import

__all__ = [
    '__version__',
    '__author__',
    '__email__',
    '__description__'
]
