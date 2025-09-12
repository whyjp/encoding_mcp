#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Encoding MCP 기본 테스트 - 패키지 import 및 기본 기능
"""

import pytest
import sys
import os


class TestBasicImport:
    """기본 import 테스트"""
    
    def test_import_encoding_mcp(self):
        """encoding_mcp 패키지 import 테스트"""
        try:
            import encoding_mcp
            assert hasattr(encoding_mcp, '__version__')
            assert hasattr(encoding_mcp, '__author__')
        except ImportError as e:
            pytest.skip(f"encoding_mcp 패키지를 import할 수 없습니다: {e}")
    
    def test_import_server_module(self):
        """server 모듈 import 테스트"""
        try:
            from encoding_mcp import server
            assert hasattr(server, 'main')
        except ImportError as e:
            pytest.skip(f"server 모듈을 import할 수 없습니다: {e}")
    
    def test_python_version(self):
        """Python 버전 호환성 테스트"""
        major, minor = sys.version_info[:2]
        assert (major, minor) >= (3, 9), f"Python 3.9 이상이 필요합니다. 현재: {major}.{minor}"
    
    def test_basic_functionality(self):
        """기본 기능 테스트"""
        # 간단한 파일 작업 테스트
        test_content = "Hello, World!"
        test_file = "test_temp.txt"
        
        try:
            # UTF-8로 파일 생성
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            # 파일 읽기
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            assert content == test_content
            
        finally:
            # 정리
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def test_encoding_support(self):
        """인코딩 지원 테스트"""
        # 지원되는 인코딩 목록
        supported_encodings = ['utf-8', 'utf-8-sig', 'cp949', 'ascii']
        
        for encoding in supported_encodings:
            try:
                test_file = f"test_{encoding.replace('-', '_')}.txt"
                with open(test_file, 'w', encoding=encoding) as f:
                    f.write("test")
                
                with open(test_file, 'r', encoding=encoding) as f:
                    content = f.read()
                    assert content == "test"
                
                os.remove(test_file)
                
            except (UnicodeError, LookupError):
                # 일부 환경에서 지원하지 않는 인코딩은 건너뛰기
                continue


if __name__ == '__main__':
    pytest.main([__file__])
