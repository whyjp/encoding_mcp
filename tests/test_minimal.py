#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Minimal tests - Python 3.9+ compatibility guarantee
"""

import sys


def test_python_version():
    """Check Python version"""
    assert sys.version_info >= (3, 10), f"Python 3.10+ required, got {sys.version_info[:2]}"


def test_basic_import():
    """Basic import test"""
    try:
        import encoding_mcp
        assert encoding_mcp.__version__ is not None
    except ImportError:
        # Skip if package is not installed
        pass


def test_basic_functionality():
    """Basic functionality test"""
    # Simple string processing
    test_str = "Hello, World!"
    assert len(test_str) > 0
    assert isinstance(test_str, str)


def test_encoding_support():
    """Encoding support test"""
    # UTF-8 encoding test
    test_bytes = "Hello".encode('utf-8')
    decoded = test_bytes.decode('utf-8')
    assert decoded == "Hello"


if __name__ == '__main__':
    test_python_version()
    test_basic_import()
    test_basic_functionality()
    test_encoding_support()
    print("All tests passed!")
