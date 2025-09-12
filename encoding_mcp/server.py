#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Encoding MCP Server v2.0
모듈화되고 전문적인 인코딩 감지 라이브러리를 사용하는 버전
"""

import asyncio
import sys
import os
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
import mcp.types as types

# 로컬 모듈 import (절대 import로 수정)
try:
    # 모듈로 실행될 때
    from .encoding_detector import detect_file_encoding, get_available_detection_methods, get_recommended_libraries
    from .file_operations import (
        create_empty_file, 
        convert_file_encoding, 
        get_file_info, 
        list_supported_encodings,
        get_encoding_info
    )
except ImportError:
    # 직접 실행될 때
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    try:
        from .encoding_detector import detect_file_encoding, get_available_detection_methods, get_recommended_libraries
        from .file_operations import (
            create_empty_file, 
            convert_file_encoding, 
            get_file_info, 
            list_supported_encodings,
            get_encoding_info
        )
    except ImportError:
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
    인코딩 감지 결과를 포맷팅합니다.
    
    Args:
        result: 인코딩 감지 결과
        file_path: 파일 경로
        
    Returns:
        str: 포맷팅된 결과 문자열
    """
    if "error" in result:
        return f"❌ {result['error']}"
    
    response_text = f"📋 파일 인코딩 정보: {os.path.basename(file_path)}\n\n"
    response_text += f"🔤 인코딩: {result['encoding']}\n"
    response_text += f"📏 파일 크기: {result['file_size']} bytes\n"
    
    if result['has_bom']:
        response_text += f"🏷️  BOM: 있음 ({result['bom_type']})\n"
    else:
        response_text += f"🏷️  BOM: 없음\n"
    
    response_text += f"🎯 신뢰도: {result['confidence']}%\n"
    response_text += f"🔧 감지 방법: {result.get('method', 'unknown')}\n"
    
    if 'language' in result and result['language'] != 'unknown':
        response_text += f"🌍 언어: {result['language']}\n"
    
    if result.get('first_bytes'):
        response_text += f"🔍 처음 16바이트 (hex): {result['first_bytes']}\n"
    
    # Windows 빌드 호환성 조언
    encoding = result['encoding']
    encoding_info = get_encoding_info(encoding)
    
    if encoding == "utf-8-bom":
        response_text += "\n✅ Windows C++/PowerShell 빌드에 적합한 인코딩입니다."
    elif encoding == "utf-8":
        response_text += "\n⚠️  UTF-8 without BOM - Windows C++/PowerShell에서 문제가 될 수 있습니다."
    elif encoding in ["cp949", "euc-kr"]:
        response_text += "\n⚠️  한글 인코딩 - UTF-8 with BOM으로 변환을 권장합니다."
    elif encoding == "ascii":
        response_text += "\n✅ ASCII 인코딩 - 호환성 문제 없음."
    elif encoding_info and encoding_info.get('windows_friendly'):
        response_text += "\n✅ Windows 호환 인코딩입니다."
    else:
        response_text += "\n❓ 알 수 없는 인코딩 - UTF-8 with BOM으로 변환을 고려하세요."
    
    return response_text

def get_system_info() -> str:
    """
    시스템 정보를 반환합니다.
    """
    detection_methods = get_available_detection_methods()
    supported_encodings = list_supported_encodings()
    
    info_text = "🔧 Encoding MCP v2.0 시스템 정보\n\n"
    
    # 감지 방법
    info_text += "📊 사용 가능한 인코딩 감지 방법:\n"
    for method, available in detection_methods.items():
        status = "✅" if available else "❌"
        info_text += f"  {status} {method}\n"
    
    info_text += f"\n📚 권장 라이브러리:\n{get_recommended_libraries()}\n\n"
    
    # 지원 인코딩
    info_text += "🎯 지원하는 인코딩:\n"
    for encoding, info in supported_encodings.items():
        windows_icon = "🪟" if info['windows_friendly'] else "🐧"
        info_text += f"  {windows_icon} {encoding}: {info['name']}\n"
    
    return info_text

# 서버 인스턴스 생성
app = Server("encoding-mcp-v2")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """사용 가능한 도구 목록을 반환합니다."""
    return [
        Tool(
            name="create_empty_file",
            description="지정된 인코딩으로 빈 파일을 생성합니다. Agent가 내용을 채울 수 있도록 빈 파일만 생성합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_name": {
                        "type": "string",
                        "description": "생성할 파일명 (예: hello.cpp, test.h)"
                    },
                    "directory_path": {
                        "type": "string", 
                        "description": "파일을 생성할 디렉터리의 절대 경로"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "파일 인코딩",
                        "enum": ["utf-8-bom", "utf-8", "cp949", "euc-kr", "ascii"],
                        "default": "utf-8-bom"
                    }
                },
                "required": ["file_name", "directory_path"]
            }
        ),
        Tool(
            name="detect_file_encoding",
            description="전문적인 라이브러리를 사용하여 파일의 인코딩을 정확하게 감지합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_name": {
                        "type": "string",
                        "description": "확인할 파일명 (예: hello.cpp, test.h)"
                    },
                    "directory_path": {
                        "type": "string",
                        "description": "파일이 있는 디렉터리의 절대 경로"
                    },
                    "max_bytes": {
                        "type": "integer",
                        "description": "분석할 최대 바이트 수 (기본값: 8192)",
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
            description="파일을 지정된 인코딩으로 변환합니다. 자동 백업 지원.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_name": {
                        "type": "string",
                        "description": "변환할 파일명 (예: hello.cpp, test.h)"
                    },
                    "directory_path": {
                        "type": "string",
                        "description": "파일이 있는 디렉터리의 절대 경로"
                    },
                    "target_encoding": {
                        "type": "string",
                        "description": "목표 인코딩",
                        "enum": ["utf-8-bom", "utf-8", "cp949", "euc-kr", "ascii"],
                        "default": "utf-8-bom"
                    },
                    "backup": {
                        "type": "boolean",
                        "description": "원본 파일 백업 여부",
                        "default": True
                    }
                },
                "required": ["file_name", "directory_path"]
            }
        ),
        Tool(
            name="get_system_info",
            description="Encoding MCP 시스템 정보를 확인합니다. 사용 가능한 라이브러리와 지원 인코딩을 보여줍니다.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """도구를 실행합니다."""
    
    if name == "create_empty_file":
        file_name = arguments.get("file_name", "")
        directory_path = arguments.get("directory_path", "")
        encoding = arguments.get("encoding", "utf-8-bom")
        
        # 파일명과 디렉터리 경로 결합
        file_path = os.path.join(directory_path, file_name)
        
        result = create_empty_file(file_path, encoding)
        
        # 결과에 따른 이모지 선택
        if "성공" in result:
            icon = "✅"
        elif "권한" in result or "실패" in result:
            icon = "❌"
        else:
            icon = "⚠️"
        
        return [
            types.TextContent(
                type="text",
                text=f"{icon} 빈 파일 생성\n\n{result}\n\n💡 Agent가 write 도구를 사용하여 내용을 채워넣을 수 있습니다."
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
                    text="❌ 파일명과 디렉터리 경로가 모두 필요합니다."
                )
            ]
        
        # 파일명과 디렉터리 경로 결합
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
        backup = arguments.get("backup", True)
        
        # 파일명과 디렉터리 경로 결합
        file_path = os.path.join(directory_path, file_name)
        
        result = convert_file_encoding(file_path, target_encoding, backup)
        
        # 결과에 따른 이모지 선택
        if "완료" in result:
            icon = "✅"
        elif "실패" in result or "오류" in result:
            icon = "❌"
        else:
            icon = "ℹ️"
        
        return [
            types.TextContent(
                type="text",
                text=f"{icon} 인코딩 변환\n\n{result}"
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
        raise ValueError(f"알 수 없는 도구입니다: {name}")

async def main():
    """메인 실행 함수"""
    print("🚀 Encoding MCP v2.0 서버 시작 중...", file=sys.stderr)
    print("📚 전문적인 인코딩 감지 라이브러리 지원", file=sys.stderr)
    
    # stdio를 통해 서버 실행
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

def cli_main():
    """CLI 엔트리 포인트"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 서버가 중단되었습니다.", file=sys.stderr)
    except Exception as e:
        print(f"💥 서버 실행 중 오류: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    cli_main()
