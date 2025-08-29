#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
import mcp.types as types

# 서버 인스턴스 생성
app = Server("echo-helloworld-mcp-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """사용 가능한 도구 목록을 반환합니다."""
    return [
        Tool(
            name="echo",
            description="입력받은 텍스트를 그대로 반환합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string", 
                        "description": "에코할 메시지"
                    }
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="hello_world",
            description="간단한 인사말을 반환합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "인사할 대상의 이름 (선택사항)",
                        "default": "World"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="add_numbers",
            description="두 숫자를 더합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "첫 번째 숫자"},
                    "b": {"type": "number", "description": "두 번째 숫자"}
                },
                "required": ["a", "b"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """도구를 실행합니다."""
    
    if name == "echo":
        message = arguments.get("message", "")
        return [
            types.TextContent(
                type="text",
                text=f"Echo: {message}"
            )
        ]
    
    elif name == "hello_world":
        name_arg = arguments.get("name", "World")
        return [
            types.TextContent(
                type="text",
                text=f"안녕하세요, {name_arg}님! 🌍"
            )
        ]
    
    elif name == "add_numbers":
        a = arguments.get("a", 0)
        b = arguments.get("b", 0)
        result = a + b
        return [
            types.TextContent(
                type="text",
                text=f"계산 결과: {a} + {b} = {result}"
            )
        ]
    
    else:
        raise ValueError(f"알 수 없는 도구입니다: {name}")

async def main():
    """메인 실행 함수"""
    print("🚀 Echo/HelloWorld MCP 서버 시작 중...", file=sys.stderr)
    
    # stdio를 통해 서버 실행
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 서버가 중단되었습니다.", file=sys.stderr)
    except Exception as e:
        print(f"💥 서버 실행 중 오류: {e}", file=sys.stderr)
        sys.exit(1)
