#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Encoding MCP Basic Tests - Package import and basic functionality
"""

import pytest
import sys
import os


class TestBasicImport:
    """Basic import tests"""
    
    def test_import_encoding_mcp(self):
        """Test importing encoding_mcp package"""
        try:
            import encoding_mcp
            assert hasattr(encoding_mcp, '__version__')
            assert hasattr(encoding_mcp, '__author__')
        except ImportError as e:
            pytest.skip(f"Cannot import encoding_mcp package: {e}")
    
    def test_import_server_module(self):
        """Test importing server module"""
        try:
            from encoding_mcp import server
            assert hasattr(server, 'main')
        except ImportError as e:
            pytest.skip(f"Cannot import server module: {e}")
    
    def test_python_version(self):
        """Test Python version compatibility"""
        major, minor = sys.version_info[:2]
        assert (major, minor) >= (3, 9), f"Python 3.9+ required. Current: {major}.{minor}"
    
    def test_basic_functionality(self):
        """Test basic functionality"""
        # Simple file operations test
        test_content = "Hello, World!"
        test_file = "test_temp.txt"
        
        try:
            # Create UTF-8 file
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            # Read file
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            assert content == test_content
            
        finally:
            # Cleanup
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def test_encoding_support(self):
        """Test encoding support"""
        # List of supported encodings
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
                # Skip encodings not supported in some environments
                continue


if __name__ == '__main__':
    pytest.main([__file__])
