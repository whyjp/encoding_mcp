#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sys
import os
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
import mcp.types as types

# UTF-8 BOM 바이트
UTF8_BOM = b'\xef\xbb\xbf'

def detect_file_encoding(file_path: str) -> dict:
    """파일의 인코딩을 감지합니다."""
    try:
        if not os.path.exists(file_path):
            return {
                "error": f"파일을 찾을 수 없습니다: {file_path}",
                "encoding": None,
                "has_bom": False,
                "confidence": 0
            }
        
        # 파일 크기 확인
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return {
                "encoding": "empty",
                "has_bom": False,
                "confidence": 100,
                "file_size": 0,
                "first_bytes": ""
            }
        
        # 파일의 처음 몇 바이트 읽기
        with open(file_path, 'rb') as f:
            raw_data = f.read(min(1024, file_size))  # 최대 1KB만 읽기
        
        # BOM 확인
        has_bom = False
        bom_type = None
        
        if raw_data.startswith(b'\xef\xbb\xbf'):
            has_bom = True
            bom_type = "UTF-8 BOM"
            encoding = "utf-8-bom"
            confidence = 100
        elif raw_data.startswith(b'\xff\xfe'):
            has_bom = True
            bom_type = "UTF-16 LE BOM"
            encoding = "utf-16-le"
            confidence = 100
        elif raw_data.startswith(b'\xfe\xff'):
            has_bom = True
            bom_type = "UTF-16 BE BOM"
            encoding = "utf-16-be"
            confidence = 100
        else:
            # BOM이 없는 경우 인코딩 추측
            encoding, confidence = guess_encoding_without_bom(raw_data)
        
        # 처음 16바이트를 hex로 표시
        first_bytes_hex = ' '.join(f'{b:02x}' for b in raw_data[:16])
        
        return {
            "encoding": encoding,
            "has_bom": has_bom,
            "bom_type": bom_type,
            "confidence": confidence,
            "file_size": file_size,
            "first_bytes": first_bytes_hex
        }
        
    except Exception as e:
        return {
            "error": f"파일 인코딩 감지 중 오류: {str(e)}",
            "encoding": None,
            "has_bom": False,
            "confidence": 0
        }

def guess_encoding_without_bom(raw_data: bytes) -> tuple:
    """BOM이 없는 파일의 인코딩을 추측합니다."""
    try:
        # UTF-8 시도
        raw_data.decode('utf-8')
        return "utf-8", 90
    except UnicodeDecodeError:
        pass
    
    try:
        # CP949 (Windows 한글) 시도
        raw_data.decode('cp949')
        return "cp949", 80
    except UnicodeDecodeError:
        pass
    
    try:
        # ASCII 시도
        raw_data.decode('ascii')
        return "ascii", 95
    except UnicodeDecodeError:
        pass
    
    # 다른 인코딩들도 시도할 수 있지만, 일단 기본적인 것들만
    try:
        # ISO-8859-1 (Latin-1) - 거의 모든 바이트를 허용
        raw_data.decode('iso-8859-1')
        return "iso-8859-1", 50
    except UnicodeDecodeError:
        pass
    
    return "unknown", 0

def write_file_with_encoding(file_path: str, content: str, encoding: str = "utf-8-bom") -> str:
    """지정된 인코딩으로 파일을 작성합니다."""
    try:
        # 디렉터리 생성
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if encoding == "utf-8-bom":
            # UTF-8 with BOM으로 파일 작성
            with open(file_path, 'wb') as f:
                f.write(UTF8_BOM)
                f.write(content.encode('utf-8'))
        elif encoding == "utf-8":
            # UTF-8 (BOM 없음)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        elif encoding == "cp949":
            # CP949 (Windows 한글)
            with open(file_path, 'w', encoding='cp949') as f:
                f.write(content)
        elif encoding == "ascii":
            # ASCII
            with open(file_path, 'w', encoding='ascii') as f:
                f.write(content)
        else:
            return f"지원하지 않는 인코딩입니다: {encoding}"
        
        return f"파일이 성공적으로 생성되었습니다: {file_path} (인코딩: {encoding})"
    except Exception as e:
        return f"파일 생성 중 오류 발생: {str(e)}"

# 하위 호환성을 위한 래퍼 함수
def write_utf8_bom_file(file_path: str, content: str) -> str:
    """UTF-8 with BOM 인코딩으로 파일을 작성합니다. (하위 호환성)"""
    return write_file_with_encoding(file_path, content, "utf-8-bom")

def get_template(template_type: str, class_name: str = None, file_path: str = None) -> str:
    """파일 템플릿을 반환합니다."""
    templates = {
        # C++ 템플릿
        "basic_cpp": """#include <iostream>

int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
""",
        "basic_header": """#pragma once

// 헤더 가드
#ifndef HEADER_NAME_H
#define HEADER_NAME_H

// 선언부

#endif // HEADER_NAME_H
""",
        "class_header": f"""#pragma once

class {class_name or 'MyClass'} {{
public:
    {class_name or 'MyClass'}();
    ~{class_name or 'MyClass'}();
    
    // 공개 메서드
    
private:
    // 비공개 멤버 변수
}};
""",
        # PowerShell 템플릿
        "basic_ps1": """#!/usr/bin/env pwsh
# PowerShell 스크립트

Write-Host "PowerShell 스크립트 실행 중..."

# 스크립트 내용을 여기에 작성하세요
""",
        "build_script": """#!/usr/bin/env pwsh
# 빌드 스크립트

param(
    [string]$Configuration = "Debug",
    [string]$Platform = "x64"
)

Write-Host "빌드 시작: $Configuration | $Platform"

try {
    # 빌드 명령어를 여기에 작성하세요
    # msbuild 또는 cmake 등
    
    Write-Host "빌드 완료!" -ForegroundColor Green
} catch {
    Write-Host "빌드 실패: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
""",
        # Python 템플릿
        "basic_py": """#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def main():
    print("Hello, Python!")

if __name__ == "__main__":
    main()
""",
        # JavaScript 템플릿
        "basic_js": """// JavaScript 파일
console.log("Hello, JavaScript!");
"""
    }
    return templates.get(template_type, "")

def get_default_template_by_extension(file_path: str) -> str:
    """확장자에 따라 기본 템플릿을 자동 선택합니다."""
    if not file_path:
        return "none"
    
    ext = os.path.splitext(file_path)[1].lower()
    
    template_map = {
        '.cpp': 'basic_cpp',
        '.cxx': 'basic_cpp', 
        '.cc': 'basic_cpp',
        '.h': 'basic_header',
        '.hpp': 'basic_header',
        '.hxx': 'basic_header',
        '.ps1': 'basic_ps1',
        '.py': 'basic_py',
        '.js': 'basic_js',
        '.mjs': 'basic_js'
    }
    
    return template_map.get(ext, "none")

# 하위 호환성을 위한 래퍼 함수들
def get_cpp_template(template_type: str, class_name: str = None) -> str:
    """C++ 파일 템플릿을 반환합니다. (하위 호환성)"""
    return get_template(template_type, class_name)

def get_powershell_template(template_type: str) -> str:
    """PowerShell 스크립트 템플릿을 반환합니다. (하위 호환성)"""
    return get_template(template_type)

# 서버 인스턴스 생성
app = Server("encoding-mcp")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """사용 가능한 도구 목록을 반환합니다."""
    return [

        Tool(
            name="create_file",
            description="지정된 인코딩으로 파일을 생성합니다. 기본값은 UTF-8 with BOM입니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "생성할 파일의 경로"
                    },
                    "content": {
                        "type": "string",
                        "description": "파일 내용"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "파일 인코딩",
                        "enum": ["utf-8-bom", "utf-8", "cp949", "ascii"],
                        "default": "utf-8-bom"
                    },
                    "template": {
                        "type": "string",
                        "description": "사용할 템플릿 (확장자에 따라 자동 선택)",
                        "enum": ["basic_cpp", "basic_header", "class_header", "basic_ps1", "build_script", "basic_py", "basic_js", "none"],
                        "default": "none"
                    },
                    "class_name": {
                        "type": "string",
                        "description": "클래스 이름 (class_header 템플릿 사용시)"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="get_file_encoding",
            description="파일의 인코딩 정보를 확인합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "확인할 파일의 경로"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="create_utf8_bom_file",
            description="UTF-8 with BOM 인코딩으로 파일을 생성합니다. (Windows 빌드 최적화)",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "생성할 파일의 경로"
                    },
                    "content": {
                        "type": "string",
                        "description": "파일 내용"
                    },
                    "template": {
                        "type": "string",
                        "description": "사용할 템플릿 (확장자에 따라 자동 선택)",
                        "enum": ["basic_cpp", "basic_header", "class_header", "basic_ps1", "build_script", "basic_py", "basic_js", "none"],
                        "default": "none"
                    },
                    "class_name": {
                        "type": "string",
                        "description": "클래스 이름 (class_header 템플릿 사용시)"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="convert_to_utf8_bom",
            description="기존 파일을 UTF-8 with BOM 인코딩으로 변환합니다. (Windows 빌드 최적화)",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "변환할 파일의 경로"
                    },
                    "backup": {
                        "type": "boolean",
                        "description": "원본 파일 백업 여부",
                        "default": True
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="convert_file_encoding",
            description="파일을 지정된 인코딩으로 변환합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "변환할 파일의 경로"
                    },
                    "target_encoding": {
                        "type": "string",
                        "description": "목표 인코딩",
                        "enum": ["utf-8-bom", "utf-8", "cp949", "ascii"],
                        "default": "utf-8-bom"
                    },
                    "backup": {
                        "type": "boolean",
                        "description": "원본 파일 백업 여부",
                        "default": True
                    }
                },
                "required": ["file_path"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """도구를 실행합니다."""
    
    if name == "create_file":
        file_path = arguments.get("file_path", "")
        content = arguments.get("content", "")
        encoding = arguments.get("encoding", "utf-8-bom")
        template = arguments.get("template", "none")
        class_name = arguments.get("class_name", "MyClass")
        
        # 템플릿 자동 선택 (template이 "none"이고 content가 없는 경우)
        if template == "none" and not content:
            template = get_default_template_by_extension(file_path)
        
        # 템플릿이 지정된 경우 템플릿 내용 사용
        if template != "none" and not content:
            content = get_template(template, class_name, file_path)
        elif not content:
            # 기본 내용 (확장자별)
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.cpp', '.h', '.hpp', '.cxx', '.hxx', '.cc']:
                content = "// C++ 소스 파일\n\n"
            elif ext == '.ps1':
                content = "# PowerShell 스크립트\n\n"
            elif ext == '.py':
                content = "#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n\n"
            elif ext in ['.js', '.mjs']:
                content = "// JavaScript 파일\n\n"
            else:
                content = "// 파일 내용\n\n"
        
        result = write_file_with_encoding(file_path, content, encoding)
        
        # 파일 타입 이모지 선택
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.cpp', '.h', '.hpp', '.cxx', '.hxx', '.cc']:
            emoji = "🔧"
            file_type = "C++"
        elif ext == '.ps1':
            emoji = "📜"
            file_type = "PowerShell"
        elif ext == '.py':
            emoji = "🐍"
            file_type = "Python"
        elif ext in ['.js', '.mjs']:
            emoji = "⚡"
            file_type = "JavaScript"
        else:
            emoji = "📄"
            file_type = "파일"
        
        return [
            types.TextContent(
                type="text",
                text=f"{emoji} {file_type} 파일 생성 완료!\n\n{result}\n\n인코딩: {encoding}\n템플릿: {template}"
            )
        ]
    
    elif name == "create_utf8_bom_file":
        file_path = arguments.get("file_path", "")
        content = arguments.get("content", "")
        template = arguments.get("template", "none")
        class_name = arguments.get("class_name", "MyClass")
        
        # 템플릿 자동 선택 (template이 "none"이고 content가 없는 경우)
        if template == "none" and not content:
            template = get_default_template_by_extension(file_path)
        
        # 템플릿이 지정된 경우 템플릿 내용 사용
        if template != "none" and not content:
            content = get_template(template, class_name, file_path)
        elif not content:
            # 기본 내용 (확장자별)
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.cpp', '.h', '.hpp', '.cxx', '.hxx', '.cc']:
                content = "// C++ 소스 파일\n\n"
            elif ext == '.ps1':
                content = "# PowerShell 스크립트\n\n"
            elif ext == '.py':
                content = "#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n\n"
            elif ext in ['.js', '.mjs']:
                content = "// JavaScript 파일\n\n"
            else:
                content = "// 파일 내용\n\n"
        
        # 항상 UTF-8 with BOM으로 생성
        result = write_file_with_encoding(file_path, content, "utf-8-bom")
        
        # 파일 타입 이모지 선택
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.cpp', '.h', '.hpp', '.cxx', '.hxx', '.cc']:
            emoji = "🔧"
            file_type = "C++"
        elif ext == '.ps1':
            emoji = "📜"
            file_type = "PowerShell"
        elif ext == '.py':
            emoji = "🐍"
            file_type = "Python"
        elif ext in ['.js', '.mjs']:
            emoji = "⚡"
            file_type = "JavaScript"
        else:
            emoji = "📄"
            file_type = "파일"
        
        return [
            types.TextContent(
                type="text",
                text=f"{emoji} {file_type} 파일 생성 완료! (Windows 빌드 최적화)\n\n{result}\n\n인코딩: UTF-8 with BOM\n템플릿: {template}"
            )
        ]
    
    elif name == "get_file_encoding":
        file_path = arguments.get("file_path", "")
        
        if not file_path:
            return [
                types.TextContent(
                    type="text",
                    text="❌ 파일 경로가 지정되지 않았습니다."
                )
            ]
        
        result = detect_file_encoding(file_path)
        
        if "error" in result:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ {result['error']}"
                )
            ]
        
        # 결과 포맷팅
        response_text = f"📋 파일 인코딩 정보: {os.path.basename(file_path)}\n\n"
        response_text += f"🔤 인코딩: {result['encoding']}\n"
        response_text += f"📏 파일 크기: {result['file_size']} bytes\n"
        
        if result['has_bom']:
            response_text += f"🏷️  BOM: 있음 ({result['bom_type']})\n"
        else:
            response_text += f"🏷️  BOM: 없음\n"
        
        response_text += f"🎯 신뢰도: {result['confidence']}%\n"
        
        if result['first_bytes']:
            response_text += f"🔍 처음 16바이트 (hex): {result['first_bytes']}\n"
        
        # Windows 빌드 호환성 조언
        if result['encoding'] == "utf-8-bom":
            response_text += "\n✅ Windows C++/PowerShell 빌드에 적합한 인코딩입니다."
        elif result['encoding'] == "utf-8":
            response_text += "\n⚠️  UTF-8 without BOM - Windows C++/PowerShell에서 문제가 될 수 있습니다."
        elif result['encoding'] == "cp949":
            response_text += "\n⚠️  CP949 인코딩 - UTF-8 with BOM으로 변환을 권장합니다."
        elif result['encoding'] == "ascii":
            response_text += "\n✅ ASCII 인코딩 - 호환성 문제 없음."
        else:
            response_text += "\n❓ 알 수 없는 인코딩 - UTF-8 with BOM으로 변환을 고려하세요."
        
        return [
            types.TextContent(
                type="text",
                text=response_text
            )
        ]
    
    elif name == "convert_to_utf8_bom":
        file_path = arguments.get("file_path", "")
        backup = arguments.get("backup", True)
        
        try:
            # 파일이 존재하는지 확인
            if not os.path.exists(file_path):
                return [
                    types.TextContent(
                        type="text",
                        text=f"❌ 파일을 찾을 수 없습니다: {file_path}"
                    )
                ]
            
            # 백업 생성
            if backup:
                backup_path = file_path + ".backup"
                import shutil
                shutil.copy2(file_path, backup_path)
            
            # 파일 읽기 (자동 인코딩 감지)
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # UTF-8 with BOM으로 다시 저장
            result = write_utf8_bom_file(file_path, content)
            
            backup_msg = f"\n백업 파일: {backup_path}" if backup else "\n백업 없음"
            
            return [
                types.TextContent(
                    type="text",
                    text=f"🔄 파일 인코딩 변환 완료!\n\n{result}\n\n변환: 기존 인코딩 → UTF-8 with BOM{backup_msg}"
                )
            ]
            
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ 파일 변환 중 오류 발생: {str(e)}"
                )
            ]
    
    elif name == "convert_file_encoding":
        file_path = arguments.get("file_path", "")
        target_encoding = arguments.get("target_encoding", "utf-8-bom")
        backup = arguments.get("backup", True)
        
        try:
            # 파일이 존재하는지 확인
            if not os.path.exists(file_path):
                return [
                    types.TextContent(
                        type="text",
                        text=f"❌ 파일을 찾을 수 없습니다: {file_path}"
                    )
                ]
            
            # 현재 인코딩 확인
            current_info = detect_file_encoding(file_path)
            if "error" in current_info:
                return [
                    types.TextContent(
                        type="text",
                        text=f"❌ 파일 인코딩 확인 실패: {current_info['error']}"
                    )
                ]
            
            current_encoding = current_info['encoding']
            
            # 이미 목표 인코딩인 경우
            if current_encoding == target_encoding:
                return [
                    types.TextContent(
                        type="text",
                        text=f"ℹ️ 파일이 이미 {target_encoding} 인코딩입니다: {file_path}"
                    )
                ]
            
            # 백업 생성
            if backup:
                backup_path = file_path + ".backup"
                import shutil
                shutil.copy2(file_path, backup_path)
            
            # 파일 내용 읽기 (현재 인코딩 고려)
            if current_encoding == "utf-8-bom":
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
            elif current_encoding == "utf-8":
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif current_encoding == "cp949":
                with open(file_path, 'r', encoding='cp949') as f:
                    content = f.read()
            elif current_encoding == "ascii":
                with open(file_path, 'r', encoding='ascii') as f:
                    content = f.read()
            else:
                # 기본값으로 UTF-8 시도
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
            
            # 새로운 인코딩으로 저장
            result = write_file_with_encoding(file_path, content, target_encoding)
            
            backup_msg = f"\n백업 파일: {backup_path}" if backup else "\n백업 없음"
            
            return [
                types.TextContent(
                    type="text",
                    text=f"🔄 파일 인코딩 변환 완료!\n\n{result}\n\n변환: {current_encoding} → {target_encoding}{backup_msg}"
                )
            ]
            
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ 파일 변환 중 오류 발생: {str(e)}"
                )
            ]
    
    else:
        raise ValueError(f"알 수 없는 도구입니다: {name}")

async def main():
    """메인 실행 함수"""
    print("🚀 Encoding MCP 서버 시작 중...", file=sys.stderr)
    
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

