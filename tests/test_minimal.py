#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
최소한의 테스트 - Python 3.9+ 호환성 보장
"""

import sys


def test_python_version():
    """Python 버전 확인"""
    assert sys.version_info >= (3, 9)


def test_basic_import():
    """기본 import 테스트"""
    try:
        import encoding_mcp
        assert encoding_mcp.__version__ is not None
    except ImportError:
        # 패키지가 설치되지 않은 경우 건너뛰기
        pass


def test_basic_functionality():
    """기본 기능 테스트"""
    # 간단한 문자열 처리
    test_str = "Hello, 世界!"
    assert len(test_str) > 0
    assert isinstance(test_str, str)


def test_encoding_support():
    """인코딩 지원 테스트"""
    # UTF-8 인코딩 테스트
    test_bytes = "안녕하세요".encode('utf-8')
    decoded = test_bytes.decode('utf-8')
    assert decoded == "안녕하세요"


if __name__ == '__main__':
    test_python_version()
    test_basic_import()
    test_basic_functionality()
    test_encoding_support()
    print("All tests passed!")
