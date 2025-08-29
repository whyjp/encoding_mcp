# Encoding MCP Server

간단한 Echo/HelloWorld 기능을 제공하는 MCP (Model Context Protocol) 서버입니다.

## 기능

- **echo**: 입력받은 텍스트를 그대로 반환
- **hello_world**: 간단한 인사말 반환
- **add_numbers**: 두 숫자 덧셈

## 설치 및 실행

1. 의존성 설치:
```bash
pip install mcp
```

2. 서버 실행:
```bash
python src/server.py
```

3. MCP Inspector로 테스트:
```bash
npx @modelcontextprotocol/inspector python src/server.py
```

## Cursor 연결

Cursor의 설정 파일에 다음과 같이 추가:

```json
{
  "mcpServers": {
    "encoding-mcp": {
      "command": "python",
      "args": ["D:/exam/encoding_mcp/src/server.py"]
    }
  }
}
```
