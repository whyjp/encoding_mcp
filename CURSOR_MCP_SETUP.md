# 🔗 Cursor MCP 설정 가이드

이 가이드는 `encoding-mcp` 패키지를 Cursor에서 MCP 서버로 사용하는 방법을 설명합니다.

## 📋 사전 요구사항

- **Python 3.10+** 설치
- **Cursor IDE** 설치
- **encoding-mcp** PyPI 패키지 설치: `pip install encoding-mcp`

## 🚀 빠른 설정

### 1단계: 패키지 설치
```bash
pip install encoding-mcp
```

### 2단계: Cursor MCP 설정
Cursor의 MCP 설정 파일에 다음을 추가:

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

### 3단계: Cursor 재시작
설정을 적용하려면 Cursor를 재시작합니다.

### 4단계: 사용 확인
Cursor에서 다음과 같이 MCP 도구를 사용할 수 있습니다:
- `mcp_encoding_create_empty_file()` - 빈 파일 생성
- `mcp_encoding_detect_file_encoding()` - 인코딩 감지
- `mcp_encoding_convert_file_encoding()` - 인코딩 변환

## 🔧 고급 설정

### 개발자 모드 (디버그 활성화)
```json
{
  "mcpServers": {
    "encoding-mcp-dev": {
      "command": "python",
      "args": ["-m", "encoding_mcp"],
      "env": {
        "DEBUG": "true",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### 특정 Python 버전 사용
```json
{
  "mcpServers": {
    "encoding-mcp": {
      "command": "python3.11",
      "args": ["-m", "encoding_mcp"],
      "env": {
        "DEBUG": "false"
      }
    }
  }
}
```

### 가상환경 사용
```json
{
  "mcpServers": {
    "encoding-mcp": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "encoding_mcp"],
      "env": {
        "DEBUG": "false"
      }
    }
  }
}
```

### Windows 전용 설정
```json
{
  "mcpServers": {
    "encoding-mcp": {
      "command": "python",
      "args": ["-m", "encoding_mcp"],
      "env": {
        "DEBUG": "false",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONPATH": "C:/additional/modules"
      }
    }
  }
}
```

## 🛠️ 문제 해결

### 일반적인 문제

#### 1. "command not found" 오류
**원인**: Python이 PATH에 없거나 잘못된 경로
**해결**: 
```bash
# Python 경로 확인
which python
# 또는
where python

# 전체 경로 사용
{
  "command": "/usr/bin/python3",
  "args": ["-m", "encoding_mcp"]
}
```

#### 2. "module not found" 오류
**원인**: encoding-mcp 패키지가 설치되지 않음
**해결**:
```bash
pip install encoding-mcp
# 또는 특정 환경에
/path/to/python -m pip install encoding-mcp
```

#### 3. 권한 오류
**원인**: Python 실행 권한 부족
**해결**:
```bash
# 권한 확인
ls -la $(which python)
# 권한 부여 (필요시)
chmod +x /path/to/python
```

#### 4. 가상환경 문제
**원인**: 잘못된 가상환경 경로
**해결**:
```bash
# 가상환경 활성화 후 경로 확인
source /path/to/venv/bin/activate
which python

# Windows
venv\Scripts\activate
where python
```

## 🧪 설정 테스트

### MCP Inspector로 테스트
```bash
npx @modelcontextprotocol/inspector python -m encoding_mcp
```

### 직접 실행 테스트
```bash
python -m encoding_mcp
```

### 버전 확인
```bash
python -c "import encoding_mcp; print(encoding_mcp.__version__)"
```

## 📚 추가 리소스

- **PyPI 패키지**: https://pypi.org/project/encoding-mcp/
- **GitHub 저장소**: https://github.com/whyjp/encoding_mcp
- **MCP 공식 문서**: https://modelcontextprotocol.io/
- **Cursor 공식 문서**: https://cursor.sh/

## 💡 사용 팁

1. **디버그 모드**: 문제 발생 시 `DEBUG: true` 설정
2. **로그 확인**: Cursor 개발자 도구에서 MCP 로그 확인
3. **경로 문제**: 절대 경로 사용 권장
4. **환경 변수**: 필요에 따라 추가 환경 변수 설정
5. **다중 서버**: 여러 MCP 서버와 함께 사용 가능

---

**🎉 이제 Cursor에서 encoding-mcp를 사용할 준비가 완료되었습니다!**
