ㅈ# Encoding MCP Server

Windows 빌드 환경에서 필요한 UTF-8 with BOM 인코딩 파일을 생성하고 관리하는 MCP (Model Context Protocol) 서버입니다.

## 주요 기능

### 🎯 기본 도구 (UTF-8 BOM 전용, Windows 빌드 최적화)
- **create_utf8_bom_file**: UTF-8 with BOM 파일 생성
- **convert_to_utf8_bom**: 기존 파일을 UTF-8 with BOM으로 변환

### ⚙️ 범용 도구 (다양한 인코딩 지원)
- **create_file**: 지정된 인코딩으로 파일 생성 (utf-8-bom, utf-8, cp949, ascii)
- **convert_file_encoding**: 파일을 지정된 인코딩으로 변환

### 🔍 공통 도구
- **get_file_encoding**: 파일의 인코딩 정보 확인 및 BOM 감지

### 📝 템플릿 지원
- **C++ 템플릿**: basic_cpp, basic_header, class_header
- **PowerShell 템플릿**: basic_ps1, build_script



## 🚀 빠른 시작

### 1. 저장소 클론 및 설치
```bash
git clone <repository-url>
cd encoding_mcp
pip install .
```

### 2. 서버 실행
```bash
encoding-mcp
```

### 3. MCP Inspector로 테스트
```bash
npx @modelcontextprotocol/inspector encoding-mcp
```

## 📦 설치 방법

### 🔧 패키지 설치 (권장)
```bash
pip install .
encoding-mcp
```

### 🛠️ 직접 실행
```bash
python encoding_mcp/server.py
```

### 🔨 개발자 모드
```bash
pip install -e .
encoding-mcp
```

## 사용 예시

### 🎯 기본 도구 (Windows 빌드 최적화)

#### UTF-8 BOM C++ 파일 생성
```json
{
  "name": "create_utf8_bom_file",
  "arguments": {
    "file_path": "src/MyClass.cpp"
  }
}
```

#### 기존 파일을 UTF-8 BOM으로 변환
```json
{
  "name": "convert_to_utf8_bom",
  "arguments": {
    "file_path": "src/legacy_file.cpp",
    "backup": true
  }
}
```

### ⚙️ 범용 도구 (다양한 인코딩)

#### 인코딩 선택 가능한 파일 생성
```json
{
  "name": "create_file",
  "arguments": {
    "file_path": "script.py",
    "encoding": "utf-8",
    "template": "basic_py"
  }
}
```

#### 파일 인코딩 변환 (CP949 → UTF-8 BOM)
```json
{
  "name": "convert_file_encoding",
  "arguments": {
    "file_path": "old_script.ps1",
    "target_encoding": "utf-8-bom",
    "backup": true
  }
}
```

### 🔍 공통 도구

#### 파일 인코딩 확인
```json
{
  "name": "get_file_encoding",
  "arguments": {
    "file_path": "src/unknown_file.cpp"
  }
}
```



## 🔗 Cursor 연결

패키지 설치 후 Cursor 설정:

```json
{
  "mcpServers": {
    "encoding-mcp": {
      "command": "encoding-mcp"
    }
  }
}
```

또는 Python 모듈로:

```json
{
  "mcpServers": {
    "encoding-mcp": {
      "command": "python",
      "args": ["-m", "encoding_mcp"]
    }
  }
}
```



## Windows 빌드 문제 해결

이 도구는 다음과 같은 Windows 빌드 문제를 해결합니다:

- **C++ 파일**: UTF-8 with BOM이 없으면 한글 주석이 깨짐
- **PowerShell 스크립트**: UTF-8 with BOM이 없으면 한글 출력이 깨짐
- **배치 파일**: 인코딩 문제로 스크립트 실행 실패

모든 파일이 UTF-8 with BOM으로 생성되어 Windows 환경에서 안정적으로 작동합니다.
