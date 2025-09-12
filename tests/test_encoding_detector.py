#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Encoding MCP 테스트 - 인코딩 감지 기능
"""

import pytest
import tempfile
import os
from pathlib import Path
from encoding_mcp.encoding_detector import detect_encoding, detect_encoding_with_libraries


class TestEncodingDetector:
    """인코딩 감지 기능 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """각 테스트 메서드 실행 후 정리"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_detect_utf8_bom(self):
        """UTF-8 BOM 감지 테스트"""
        test_file = self.temp_path / "test_utf8_bom.txt"
        content = "안녕하세요, 세계!"
        
        # UTF-8 BOM으로 파일 생성
        with open(test_file, 'w', encoding='utf-8-sig') as f:
            f.write(content)
        
        result = detect_encoding(str(test_file))
        assert result['encoding'] == 'utf-8-bom'
        assert result['confidence'] >= 0.9
    
    def test_detect_utf8_no_bom(self):
        """UTF-8 (BOM 없음) 감지 테스트"""
        test_file = self.temp_path / "test_utf8.txt"
        content = "Hello, World!"
        
        # UTF-8 (BOM 없음)으로 파일 생성
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        result = detect_encoding(str(test_file))
        assert result['encoding'] in ['utf-8', 'ascii']
        assert result['confidence'] >= 0.8
    
    def test_detect_cp949(self):
        """CP949 감지 테스트"""
        test_file = self.temp_path / "test_cp949.txt"
        content = "안녕하세요"
        
        try:
            # CP949로 파일 생성
            with open(test_file, 'w', encoding='cp949') as f:
                f.write(content)
            
            result = detect_encoding(str(test_file))
            assert result['encoding'] in ['cp949', 'euc-kr']
            assert result['confidence'] >= 0.7
        except UnicodeEncodeError:
            pytest.skip("CP949 인코딩을 지원하지 않는 환경")
    
    def test_empty_file(self):
        """빈 파일 감지 테스트"""
        test_file = self.temp_path / "empty.txt"
        test_file.touch()
        
        result = detect_encoding(str(test_file))
        assert result['encoding'] in ['utf-8', 'ascii']
        assert result['confidence'] >= 0.0
    
    def test_nonexistent_file(self):
        """존재하지 않는 파일 테스트"""
        nonexistent_file = str(self.temp_path / "nonexistent.txt")
        
        with pytest.raises(FileNotFoundError):
            detect_encoding(nonexistent_file)
    
    def test_binary_file(self):
        """바이너리 파일 테스트"""
        test_file = self.temp_path / "binary.bin"
        
        # 바이너리 데이터 생성
        binary_data = bytes(range(256))
        with open(test_file, 'wb') as f:
            f.write(binary_data)
        
        result = detect_encoding(str(test_file))
        # 바이너리 파일도 어떤 인코딩으로든 감지되어야 함
        assert result['encoding'] is not None
        assert isinstance(result['confidence'], float)
    
    def test_large_file_max_bytes(self):
        """큰 파일에서 최대 바이트 수 제한 테스트"""
        test_file = self.temp_path / "large.txt"
        content = "A" * 10000  # 10KB 파일
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 처음 1000바이트만 분석
        result = detect_encoding(str(test_file), max_bytes=1000)
        assert result['encoding'] in ['utf-8', 'ascii']
        assert result['confidence'] >= 0.8


if __name__ == '__main__':
    pytest.main([__file__])
