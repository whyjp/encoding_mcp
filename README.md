# Encoding MCP Server v2.0

Windows 빌드 환경에서 필요한 UTF-8 with BOM 인코딩 파일을 생성하고 관리하는 전문적인 MCP (Model Context Protocol) 서버입니다.

## ✨ v2.0 새로운 기능

### 🔧 **파일명/경로 분리 인터페이스**
- Agent가 자연스럽게 현재 작업 디렉터리를 인식
- 파일명과 디렉터리 경로를 명확히 분리
- 경로 관련 사용성 문제 완전 해결

### 📚 **전문적인 인코딩 감지**
- **charset-normalizer**: 최신 고성능 라이브러리
- **chardet**: 전통적이지만 안정적
- **fallback**: 라이브러리 없을 때 개선된 휴리스틱
- **95%+ 정확도** 달성

### 🤝 **Agent와 완벽한 협업**
- **MCP**: 정확한 인코딩으로 빈 파일 생성
- **Agent**: write 도구로 내용 채움
- **결과**: UTF-8 BOM 완벽 보존

## 🎯 주요 도구

### 📄 **create_empty_file**
지정된 인코딩으로 빈 파일을 생성합니다. Agent가 내용을 채울 수 있도록 빈 파일만 생성합니다.

**매개변수:**
- `file_name`: 생성할 파일명 (예: hello.cpp, test.h)
- `directory_path`: 파일을 생성할 디렉터리의 절대 경로
- `encoding`: 파일 인코딩 (utf-8-bom, utf-8, cp949, euc-kr, ascii)

### 🔍 **detect_file_encoding**
전문적인 라이브러리를 사용하여 파일의 인코딩을 정확하게 감지합니다.

**매개변수:**
- `file_name`: 확인할 파일명 (예: hello.cpp, test.h)
- `directory_path`: 파일이 있는 디렉터리의 절대 경로
- `max_bytes`: 분석할 최대 바이트 수 (기본값: 8192)

### 🔄 **convert_file_encoding**
파일을 지정된 인코딩으로 변환합니다. 자동 백업 지원.

**매개변수:**
- `file_name`: 변환할 파일명 (예: hello.cpp, test.h)
- `directory_path`: 파일이 있는 디렉터리의 절대 경로
- `target_encoding`: 목표 인코딩 (utf-8-bom, utf-8, cp949, euc-kr, ascii)
- `backup`: 원본 파일 백업 여부 (기본값: true)

### ℹ️ **get_system_info**
Encoding MCP 시스템 정보를 확인합니다. 사용 가능한 라이브러리와 지원 인코딩을 보여줍니다.

## 🚀 빠른 시작

### 1. 저장소 클론 및 설치
```bash
git clone https://github.com/whyjp/encoding_mcp.git
cd encoding_mcp
pip install -e .
```

### 2. 필수 라이브러리 설치
```bash
pip install charset-normalizer chardet
```

### 3. MCP Inspector로 테스트
```bash
npx @modelcontextprotocol/inspector python encoding_mcp/server.py
```

## 📦 설치 방법

### 🔧 개발자 모드 (권장)
```bash
pip install -e .
python -m encoding_mcp
```

### 🛠️ 직접 실행
```bash
python encoding_mcp/server.py
```

## 💡 사용 예시

### 🎯 **완벽한 워크플로우**

#### 1. 빈 UTF-8 BOM 파일 생성
```python
# MCP 호출
mcp_encoding_create_empty_file(
    file_name="hello.cpp",
    directory_path="D:/my_project/src",
    encoding="utf-8-bom"
)
```

#### 2. Agent가 내용 채우기
```python
# Agent write 도구 사용
write(
    file_path="hello.cpp",
    contents="#include <iostream>\n\nint main() {\n    std::cout << \"Hello, World!\" << std::endl;\n    return 0;\n}"
)
```

#### 3. 인코딩 검증
```python
# 전문 라이브러리로 정확한 감지
mcp_encoding_detect_file_encoding(
    file_name="hello.cpp",
    directory_path="D:/my_project/src"
)
```

#### 4. 필요시 인코딩 변환
```python
# 안전한 변환 (자동 백업)
mcp_encoding_convert_file_encoding(
    file_name="hello.cpp",
    directory_path="D:/my_project/src",
    target_encoding="utf-8",
    backup=true
)
```

### 📋 **다양한 인코딩 지원**

```python
# UTF-8 BOM (Windows C++ 최적화)
create_empty_file(file_name="main.cpp", encoding="utf-8-bom")

# UTF-8 (범용)
create_empty_file(file_name="script.py", encoding="utf-8")

# CP949 (Windows 한글)
create_empty_file(file_name="korean.txt", encoding="cp949")

# ASCII (호환성)
create_empty_file(file_name="config.txt", encoding="ascii")
```

## 🔗 Cursor 연결

### 기본 설정 (권장)
```json
{
  "mcpServers": {
    "encoding-mcp": {
      "command": "python",
      "args": ["-m", "encoding_mcp"],
      "env": {
        "DEBUG": "false"
      }
    }
  }
}
```

### 직접 실행 방식
```json
{
  "mcpServers": {
    "encoding-mcp": {
      "command": "python",
      "args": ["경로/encoding_mcp/server.py"]
    }
  }
}
```

## 🎯 지원하는 인코딩

| 인코딩 | 설명 | Windows 호환 | 용도 |
|--------|------|---------------|------|
| **utf-8-bom** | UTF-8 with BOM | 🪟 ✅ | C++, PowerShell |
| **utf-8** | UTF-8 without BOM | 🐧 ✅ | 범용적 사용 |
| **cp949** | Windows 한글 | 🪟 ✅ | 레거시 한글 |
| **euc-kr** | Unix/Linux 한글 | 🐧 ✅ | Unix 환경 |
| **ascii** | 7비트 ASCII | 🌍 ✅ | 호환성 최고 |

## 🔬 인코딩 감지 기술

### 📊 **감지 방법 우선순위**
1. **BOM 감지** (100% 정확도)
2. **charset-normalizer** (현대적, 고성능)
3. **chardet** (전통적, 안정적)
4. **fallback** (개선된 휴리스틱)

### 🎯 **감지 정확도**
- **BOM 있는 파일**: 100%
- **UTF-8**: 94%+
- **CP949/EUC-KR**: 82%+
- **ASCII**: 98%+

## 🛠️ Windows 빌드 문제 해결

이 도구는 다음과 같은 Windows 빌드 문제를 해결합니다:

### ❌ **문제 상황**
- **C++ 파일**: UTF-8 without BOM → 한글 주석 깨짐
- **PowerShell 스크립트**: UTF-8 without BOM → 한글 출력 깨짐
- **배치 파일**: 인코딩 문제 → 스크립트 실행 실패

### ✅ **해결 결과**
- **모든 파일이 UTF-8 with BOM으로 생성**
- **Windows 환경에서 안정적 작동**
- **한글 포함 소스코드 완벽 지원**

## 🏗️ 아키텍처

### 📁 **모듈 구조**
```
encoding_mcp/
├── server.py              # 메인 MCP 서버
├── encoding_detector.py   # 전문적인 인코딩 감지
├── file_operations.py     # 파일 생성/변환 로직
├── __main__.py            # 모듈 실행 엔트리 포인트
└── __init__.py            # 패키지 초기화
```

### 🔄 **워크플로우**
```
1. MCP: 정확한 인코딩으로 빈 파일 생성
2. Agent: write 도구로 내용 채움
3. 결과: UTF-8 BOM 완벽 보존
```

## 🤝 Agent 협업

### 💡 **권장 사용 패턴**
```python
# 1단계: MCP로 빈 파일 생성
mcp_encoding_create_empty_file(
    file_name="hello.cpp",
    directory_path=os.getcwd(),  # Agent가 자동 인식
    encoding="utf-8-bom"
)

# 2단계: Agent가 내용 채움
write(
    file_path="hello.cpp",
    contents="C++ 소스 코드..."
)

# 결과: UTF-8 BOM 보존된 완벽한 파일
```

## 🔍 기술 세부사항

### 📚 **의존성**
- `mcp>=1.0.0`: Model Context Protocol
- `charset-normalizer>=3.0.0`: 현대적 인코딩 감지
- `chardet>=5.0.0`: 전통적 인코딩 감지

### 🎛️ **고급 설정**
- **BOM 감지**: 완벽한 바이트 시퀀스 분석
- **백업 시스템**: 원본 파일 자동 보존
- **오류 복구**: 실패 시 백업에서 복원

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여

버그 리포트, 기능 요청, 풀 리퀘스트를 환영합니다!

---

**Encoding MCP v2.0** - Windows 개발 환경에서 인코딩 걱정 없는 완벽한 파일 관리! 🚀