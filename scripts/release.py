#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
릴리스 생성 스크립트
새로운 버전 태그를 생성하고 GitHub에 푸시하여 자동 배포를 트리거합니다.
"""

import subprocess
import sys
import re
from pathlib import Path


def run_command(cmd, description=""):
    """명령어 실행"""
    print(f"\n🔨 {description}")
    print(f"실행: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout.strip():
            print(result.stdout.strip())
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ 오류 발생: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return None


def get_current_version():
    """현재 버전 가져오기"""
    try:
        # Git 태그에서 버전 가져오기
        result = subprocess.run(['git', 'describe', '--tags', '--abbrev=0'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip().lstrip('v')
        else:
            # 태그가 없으면 __init__.py에서 가져오기
            init_file = Path('encoding_mcp/__init__.py')
            if init_file.exists():
                content = init_file.read_text(encoding='utf-8')
                match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
    except Exception as e:
        print(f"버전 확인 중 오류: {e}")
    
    return "0.0.0"


def get_git_tags():
    """Git 태그 목록 가져오기"""
    result = run_command(['git', 'tag', '--list'], "기존 태그 목록 조회")
    if result:
        return result.split('\n')
    return []


def validate_version(version):
    """버전 형식 검증"""
    pattern = r'^\d+\.\d+\.\d+(?:-[a-zA-Z0-9]+)?$'
    return re.match(pattern, version) is not None


def increment_version(version, part='patch'):
    """버전 증가"""
    parts = version.split('.')
    if len(parts) != 3:
        return None
    
    try:
        major, minor, patch = map(int, parts)
        
        if part == 'major':
            return f"{major + 1}.0.0"
        elif part == 'minor':
            return f"{major}.{minor + 1}.0"
        elif part == 'patch':
            return f"{major}.{minor}.{patch + 1}"
        else:
            return None
    except ValueError:
        return None


def check_git_status():
    """Git 상태 확인"""
    print("\n📋 Git 상태 확인")
    
    # 현재 브랜치 확인
    branch = run_command(['git', 'branch', '--show-current'], "현재 브랜치 확인")
    if not branch:
        return False
    
    print(f"현재 브랜치: {branch}")
    
    # 변경사항 확인
    status = run_command(['git', 'status', '--porcelain'], "변경사항 확인")
    if status:
        print("❌ 커밋되지 않은 변경사항이 있습니다:")
        print(status)
        return False
    
    # 원격 저장소와 동기화 확인
    result = subprocess.run(['git', 'fetch'], capture_output=True)
    if result.returncode != 0:
        print("❌ 원격 저장소에서 가져오기 실패")
        return False
    
    # 로컬과 원격 차이 확인
    behind = run_command(['git', 'rev-list', '--count', 'HEAD..@{u}'], "원격 저장소와 비교")
    if behind and behind != '0':
        print(f"❌ 원격 저장소보다 {behind} 커밋 뒤처져 있습니다.")
        print("git pull을 실행하세요.")
        return False
    
    print("✅ Git 상태 정상")
    return True


def create_release():
    """릴리스 생성"""
    print("🚀 Encoding MCP 릴리스 생성 스크립트")
    print("=" * 50)
    
    # 프로젝트 루트 확인
    if not Path('pyproject.toml').exists():
        print("❌ pyproject.toml 파일이 없습니다. 프로젝트 루트에서 실행하세요.")
        return False
    
    # Git 상태 확인
    if not check_git_status():
        return False
    
    # 현재 버전 확인
    current_version = get_current_version()
    print(f"\n📌 현재 버전: {current_version}")
    
    # 기존 태그 표시
    tags = get_git_tags()
    if tags and tags != ['']:
        print(f"기존 태그: {', '.join(tags[-5:])}")  # 최근 5개만 표시
    
    # 새 버전 입력
    print("\n새 버전을 입력하세요:")
    print("1. 직접 입력 (예: 1.2.0)")
    print("2. 자동 증가:")
    print(f"   - patch (현재: {current_version} → {increment_version(current_version, 'patch')})")
    print(f"   - minor (현재: {current_version} → {increment_version(current_version, 'minor')})")
    print(f"   - major (현재: {current_version} → {increment_version(current_version, 'major')})")
    
    choice = input("\n선택하세요 (버전 번호 또는 patch/minor/major): ").strip()
    
    if choice in ['patch', 'minor', 'major']:
        new_version = increment_version(current_version, choice)
    elif validate_version(choice):
        new_version = choice
    else:
        print("❌ 잘못된 버전 형식입니다.")
        return False
    
    if not new_version:
        print("❌ 버전 생성 실패")
        return False
    
    # 태그 중복 확인
    tag_name = f"v{new_version}"
    if tag_name in tags:
        print(f"❌ 태그 {tag_name}가 이미 존재합니다.")
        return False
    
    # 확인
    print(f"\n📋 릴리스 정보:")
    print(f"   버전: {new_version}")
    print(f"   태그: {tag_name}")
    
    confirm = input("\n릴리스를 생성하시겠습니까? (y/N): ").strip().lower()
    if confirm != 'y':
        print("취소되었습니다.")
        return False
    
    # 태그 생성
    tag_message = f"Release version {new_version}"
    if not run_command(['git', 'tag', '-a', tag_name, '-m', tag_message], f"태그 {tag_name} 생성"):
        return False
    
    # 태그 푸시
    if not run_command(['git', 'push', 'origin', tag_name], f"태그 {tag_name} 푸시"):
        print("❌ 태그 푸시 실패. 로컬 태그를 삭제합니다.")
        subprocess.run(['git', 'tag', '-d', tag_name])
        return False
    
    print(f"\n✅ 릴리스 {tag_name} 생성 완료!")
    print("\n🔄 GitHub Actions 워크플로우가 자동으로 실행됩니다:")
    print("1. 테스트 실행")
    print("2. 패키지 빌드")
    print("3. PyPI 배포")
    
    print(f"\n🌐 GitHub에서 진행 상황을 확인하세요:")
    print("https://github.com/whyjp/encoding_mcp/actions")
    
    return True


if __name__ == '__main__':
    try:
        success = create_release()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        sys.exit(1)
