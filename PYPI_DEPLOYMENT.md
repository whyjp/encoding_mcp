# 🚀 PyPI 배포 가이드

이 문서는 `encoding-mcp` 패키지를 PyPI에 배포하는 방법을 설명합니다.

## 📋 사전 준비사항

### 1. PyPI 계정 생성
- [PyPI.org](https://pypi.org) 계정 생성
- [TestPyPI.org](https://test.pypi.org) 계정 생성 (테스트용)

### 2. API 토큰 생성
PyPI와 TestPyPI에서 API 토큰을 생성합니다:

1. PyPI 로그인 → Account settings → API tokens
2. "Add API token" 클릭
3. Token name: `encoding-mcp-release`
4. Scope: "Entire account" (첫 배포시) 또는 "Project: encoding-mcp"
5. 생성된 토큰을 안전한 곳에 저장

### 3. GitHub Secrets 설정
GitHub 저장소에서 다음 Secrets를 설정합니다:

- `PYPI_API_TOKEN`: PyPI API 토큰
- `TEST_PYPI_API_TOKEN`: TestPyPI API 토큰 (선택사항)

**설정 방법:**
1. GitHub 저장소 → Settings → Secrets and variables → Actions
2. "New repository secret" 클릭
3. Name과 Value 입력 후 저장

## 🛠️ 로컬 개발 환경 설정

### 1. 개발 의존성 설치
```bash
# 개발 환경 설정
pip install -e .[dev,test]

# 또는 개별 설치
pip install build twine pytest flake8 mypy black
```

### 2. 코드 품질 검사
```bash
# 린팅
flake8 encoding_mcp

# 타입 체크
mypy encoding_mcp

# 코드 포맷팅
black encoding_mcp

# 테스트 실행
pytest --cov=encoding_mcp
```

## 📦 수동 배포 방법

### 1. 패키지 빌드
```bash
# 빌드 디렉터리 정리
rm -rf dist/ build/ *.egg-info/

# 패키지 빌드
python -m build
```

### 2. 패키지 검증
```bash
# 패키지 구조 확인
twine check dist/*

# 설치 테스트
pip install dist/*.whl
python -c "import encoding_mcp; print(encoding_mcp.__version__)"
```

### 3. TestPyPI에 업로드 (테스트)
```bash
# TestPyPI에 업로드
twine upload --repository testpypi dist/*

# TestPyPI에서 설치 테스트
pip install --index-url https://test.pypi.org/simple/ encoding-mcp
```

### 4. PyPI에 업로드 (운영)
```bash
# PyPI에 업로드
twine upload dist/*

# PyPI에서 설치 테스트
pip install encoding-mcp
```

## 🤖 자동 배포 방법 (권장)

### 1. GitHub Actions를 통한 자동 배포

프로젝트에는 다음 워크플로우가 설정되어 있습니다:

- **`.github/workflows/test.yml`**: Push/PR 시 자동 테스트
- **`.github/workflows/release.yml`**: 태그 생성 시 자동 배포

### 2. 릴리스 생성 과정

#### A. 버전 업데이트
```bash
# 버전 확인
git tag --list

# 새 버전 태그 생성 (예: v1.1.0)
git tag v1.1.0
git push origin v1.1.0
```

#### B. 자동 배포 과정
1. 태그 푸시 → GitHub Actions 트리거
2. 다중 Python 버전에서 테스트 실행
3. 패키지 빌드 및 검증
4. PyPI에 자동 업로드

#### C. 릴리스 노트 작성
GitHub에서 Release 페이지에 변경사항을 기록합니다.

## 🔧 고급 설정

### 1. Trusted Publishing (권장)
GitHub Actions에서 OIDC를 사용한 보안 배포:

1. PyPI → Account settings → Publishing
2. "Add a new pending publisher" 클릭
3. 저장소 정보 입력:
   - Owner: `whyjp`
   - Repository: `encoding_mcp`
   - Workflow: `release.yml`
   - Environment: `release`

### 2. 버전 자동 관리
`setuptools_scm`을 사용하여 Git 태그에서 자동으로 버전을 생성합니다:

```python
# pyproject.toml에 설정됨
[tool.setuptools_scm]
write_to = "encoding_mcp/_version.py"
```

### 3. 배포 환경 분리
- **개발**: 로컬 테스트
- **스테이징**: TestPyPI
- **운영**: PyPI

## 🐛 문제 해결

### 1. 일반적인 오류

#### "File already exists" 오류
```bash
# 해결: 버전을 올리거나 기존 파일 삭제
twine upload --skip-existing dist/*
```

#### 패키지 빌드 실패
```bash
# 의존성 확인
pip install --upgrade build setuptools wheel

# 빌드 디렉터리 정리
rm -rf dist/ build/ *.egg-info/
```

#### 테스트 실패
```bash
# 의존성 설치 확인
pip install -e .[test]

# 개별 테스트 실행
pytest tests/test_encoding_detector.py -v
```

### 2. GitHub Actions 문제

#### Secrets 설정 확인
- Repository secrets가 올바르게 설정되었는지 확인
- API 토큰이 유효한지 확인

#### 워크플로우 권한 확인
- Repository → Settings → Actions → General
- "Workflow permissions" 확인

## 📊 배포 상태 모니터링

### 1. PyPI 통계
- [PyPI 프로젝트 페이지](https://pypi.org/project/encoding-mcp/)
- 다운로드 수, 버전 정보 확인

### 2. GitHub Actions
- Actions 탭에서 빌드/배포 상태 확인
- 실패 시 로그를 통한 문제 진단

### 3. 설치 테스트
```bash
# 다양한 환경에서 테스트
pip install encoding-mcp
python -c "import encoding_mcp; print('Success!')"
```

## 🎯 배포 체크리스트

### 배포 전 확인사항
- [ ] 모든 테스트 통과
- [ ] 코드 품질 검사 통과
- [ ] README.md 업데이트
- [ ] CHANGELOG 작성
- [ ] 버전 번호 확인
- [ ] GitHub Secrets 설정 확인

### 배포 후 확인사항
- [ ] PyPI에서 패키지 확인
- [ ] 설치 테스트 성공
- [ ] GitHub Release 생성
- [ ] 문서 업데이트

## 🔄 지속적 개선

### 1. 자동화 개선
- 더 많은 테스트 케이스 추가
- 다양한 OS/Python 버전 지원
- 성능 벤치마크 추가

### 2. 품질 관리
- 코드 커버리지 향상
- 정적 분석 도구 추가
- 보안 스캔 도구 통합

### 3. 사용자 피드백
- Issue 추적 및 해결
- 사용자 요청 기능 구현
- 문서 개선

---

**참고 링크:**
- [PyPI Packaging Guide](https://packaging.python.org/)
- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Setuptools Documentation](https://setuptools.pypa.io/)
