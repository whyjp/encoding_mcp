#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Encoding MCP 테스트 - 파일 작업 기능
"""

import pytest
import tempfile
import os
from pathlib import Path
from encoding_mcp.file_operations import (
    create_empty_file_with_encoding,
    convert_file_encoding,
    get_supported_encodings
)


class TestFileOperations:
    """파일 작업 기능 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """각 테스트 메서드 실행 후 정리"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_utf8_bom_file(self):
        """UTF-8 BOM 빈 파일 생성 테스트"""
        file_path = str(self.temp_path / "test_utf8_bom.cpp")
        
        result = create_empty_file_with_encoding(file_path, 'utf-8-bom')
        
        assert result['success'] is True
        assert os.path.exists(file_path)
        
        # BOM 확인
        with open(file_path, 'rb') as f:
            content = f.read()
            assert content.startswith(b'\xef\xbb\xbf')  # UTF-8 BOM
    
    def test_create_utf8_file(self):
        """UTF-8 (BOM 없음) 빈 파일 생성 테스트"""
        file_path = str(self.temp_path / "test_utf8.py")
        
        result = create_empty_file_with_encoding(file_path, 'utf-8')
        
        assert result['success'] is True
        assert os.path.exists(file_path)
        
        # BOM이 없는지 확인
        with open(file_path, 'rb') as f:
            content = f.read()
            assert not content.startswith(b'\xef\xbb\xbf')
    
    def test_create_cp949_file(self):
        """CP949 빈 파일 생성 테스트"""
        file_path = str(self.temp_path / "test_cp949.txt")
        
        result = create_empty_file_with_encoding(file_path, 'cp949')
        
        assert result['success'] is True
        assert os.path.exists(file_path)
    
    def test_create_file_invalid_encoding(self):
        """잘못된 인코딩으로 파일 생성 테스트"""
        file_path = str(self.temp_path / "test_invalid.txt")
        
        result = create_empty_file_with_encoding(file_path, 'invalid-encoding')
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_create_file_invalid_path(self):
        """잘못된 경로로 파일 생성 테스트"""
        invalid_path = "/nonexistent/directory/test.txt"
        
        result = create_empty_file_with_encoding(invalid_path, 'utf-8')
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_convert_encoding_utf8_to_utf8_bom(self):
        """UTF-8에서 UTF-8 BOM으로 변환 테스트"""
        file_path = str(self.temp_path / "convert_test.txt")
        content = "안녕하세요, 세계!"
        
        # UTF-8 파일 생성
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        result = convert_file_encoding(file_path, 'utf-8-bom', backup=True)
        
        assert result['success'] is True
        assert os.path.exists(file_path)
        
        # BOM 확인
        with open(file_path, 'rb') as f:
            file_content = f.read()
            assert file_content.startswith(b'\xef\xbb\xbf')
        
        # 백업 파일 확인
        backup_path = file_path + '.backup'
        assert os.path.exists(backup_path)
    
    def test_convert_encoding_no_backup(self):
        """백업 없이 인코딩 변환 테스트"""
        file_path = str(self.temp_path / "no_backup_test.txt")
        content = "Hello, World!"
        
        # UTF-8 파일 생성
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        result = convert_file_encoding(file_path, 'utf-8-bom', backup=False)
        
        assert result['success'] is True
        
        # 백업 파일이 없는지 확인
        backup_path = file_path + '.backup'
        assert not os.path.exists(backup_path)
    
    def test_convert_nonexistent_file(self):
        """존재하지 않는 파일 변환 테스트"""
        nonexistent_file = str(self.temp_path / "nonexistent.txt")
        
        result = convert_file_encoding(nonexistent_file, 'utf-8-bom')
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_get_supported_encodings(self):
        """지원되는 인코딩 목록 테스트"""
        encodings = get_supported_encodings()
        
        assert isinstance(encodings, list)
        assert len(encodings) > 0
        assert 'utf-8-bom' in encodings
        assert 'utf-8' in encodings
        assert 'cp949' in encodings
        assert 'ascii' in encodings
    
    def test_create_directory_structure(self):
        """디렉터리 구조 생성 테스트"""
        nested_path = str(self.temp_path / "nested" / "deep" / "directory" / "test.cpp")
        
        result = create_empty_file_with_encoding(nested_path, 'utf-8-bom')
        
        assert result['success'] is True
        assert os.path.exists(nested_path)


if __name__ == '__main__':
    pytest.main([__file__])
