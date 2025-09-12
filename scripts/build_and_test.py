#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
패키지 빌드 및 테스트 스크립트
PyPI 배포 전 로컬에서 패키지를 빌드하고 테스트합니다.
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path


def run_command(cmd, description="", check=True):
    """명령어 실행"""
    print(f"\n🔨 {description}")
    print(f"실행: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ 오류 발생: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def clean_build_dirs():
    """빌드 디렉터리 정리"""
    print("\n🧹 빌드 디렉터리 정리")
    
    dirs_to_clean = ['dist', 'build', 'encoding_mcp.egg-info']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"삭제: {dir_name}/")
    
    # __pycache__ 디렉터리들 정리
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs[:]:
            if dir_name == '__pycache__':
                full_path = os.path.join(root, dir_name)
                shutil.rmtree(full_path)
                print(f"삭제: {full_path}")
                dirs.remove(dir_name)


def check_dependencies():
    """필수 의존성 확인"""
    print("\n📋 필수 의존성 확인")
    
    required_packages = ['build', 'twine', 'pytest', 'flake8', 'mypy', 'black']
    missing_packages = []
    
    for package in required_packages:
        result = subprocess.run([sys.executable, '-m', package, '--version'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            missing_packages.append(package)
        else:
            print(f"✅ {package}: 설치됨")
    
    if missing_packages:
        print(f"\n❌ 누락된 패키지: {', '.join(missing_packages)}")
        print("다음 명령어로 설치하세요:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True


def run_tests():
    """테스트 실행"""
    print("\n🧪 테스트 실행")
    
    # 린팅
    if not run_command([sys.executable, '-m', 'flake8', 'encoding_mcp'], "Flake8 린팅", check=False):
        print("⚠️ 린팅 경고가 있지만 계속 진행합니다.")
    
    # 타입 체크
    if not run_command([sys.executable, '-m', 'mypy', 'encoding_mcp'], "MyPy 타입 체크", check=False):
        print("⚠️ 타입 체크 경고가 있지만 계속 진행합니다.")
    
    # 단위 테스트
    return run_command([sys.executable, '-m', 'pytest', 'tests/', '-v'], "단위 테스트")


def build_package():
    """패키지 빌드"""
    print("\n📦 패키지 빌드")
    return run_command([sys.executable, '-m', 'build'], "패키지 빌드")


def check_package():
    """패키지 검증"""
    print("\n🔍 패키지 검증")
    
    # twine으로 패키지 검증
    if not run_command([sys.executable, '-m', 'twine', 'check', 'dist/*'], "Twine 패키지 검증"):
        return False
    
    # 패키지 내용 확인
    dist_files = list(Path('dist').glob('*'))
    print(f"\n📄 생성된 파일:")
    for file in dist_files:
        print(f"  - {file.name} ({file.stat().st_size} bytes)")
    
    return True


def test_installation():
    """패키지 설치 테스트"""
    print("\n🚀 패키지 설치 테스트")
    
    # wheel 파일 찾기
    wheel_files = list(Path('dist').glob('*.whl'))
    if not wheel_files:
        print("❌ wheel 파일을 찾을 수 없습니다.")
        return False
    
    wheel_file = wheel_files[0]
    
    # 임시 환경에서 설치 테스트
    test_commands = [
        [sys.executable, '-m', 'pip', 'install', '--force-reinstall', str(wheel_file)],
        [sys.executable, '-c', 'import encoding_mcp; print(f"버전: {encoding_mcp.__version__}")'],
        [sys.executable, '-c', 'from encoding_mcp.server import main; print("서버 모듈 로드 성공")']
    ]
    
    for cmd in test_commands:
        if not run_command(cmd, f"설치 테스트: {' '.join(cmd)}"):
            return False
    
    return True


def main():
    """메인 함수"""
    print("🚀 Encoding MCP 패키지 빌드 및 테스트 스크립트")
    print("=" * 50)
    
    # 현재 디렉터리가 프로젝트 루트인지 확인
    if not Path('pyproject.toml').exists():
        print("❌ pyproject.toml 파일이 없습니다. 프로젝트 루트에서 실행하세요.")
        sys.exit(1)
    
    steps = [
        ("의존성 확인", check_dependencies),
        ("빌드 디렉터리 정리", clean_build_dirs),
        ("테스트 실행", run_tests),
        ("패키지 빌드", build_package),
        ("패키지 검증", check_package),
        ("설치 테스트", test_installation),
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        print(f"\n{'=' * 20} {step_name} {'=' * 20}")
        
        if callable(step_func):
            success = step_func()
        else:
            success = step_func
        
        if not success:
            failed_steps.append(step_name)
            print(f"❌ {step_name} 실패")
        else:
            print(f"✅ {step_name} 성공")
    
    print("\n" + "=" * 50)
    print("📊 빌드 및 테스트 결과")
    print("=" * 50)
    
    if failed_steps:
        print(f"❌ 실패한 단계: {', '.join(failed_steps)}")
        print("\n⚠️ 문제를 해결한 후 다시 시도하세요.")
        sys.exit(1)
    else:
        print("✅ 모든 단계가 성공적으로 완료되었습니다!")
        print("\n🚀 PyPI 배포 준비 완료!")
        print("\n다음 단계:")
        print("1. TestPyPI에 업로드: twine upload --repository testpypi dist/*")
        print("2. PyPI에 업로드: twine upload dist/*")
        print("3. 또는 Git 태그 생성으로 자동 배포: git tag v1.x.x && git push origin v1.x.x")


if __name__ == '__main__':
    main()
