#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

# README 파일 읽기
def read_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()

# requirements.txt 파일 읽기
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="encoding-mcp",
    version="1.0.0",
    author="Encoding MCP Team",
    author_email="",
    description="Windows 빌드 환경에서 필요한 UTF-8 with BOM 인코딩 파일을 생성하고 관리하는 MCP 서버",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/encoding-mcp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Text Processing :: Markup",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "encoding-mcp=encoding_mcp.server:cli_main",
        ],
    },
    include_package_data=True,
    package_data={
        "encoding_mcp": ["*.md", "*.txt"],
    },
    keywords="mcp encoding utf8 bom windows build cpp powershell",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/encoding-mcp/issues",
        "Source": "https://github.com/yourusername/encoding-mcp",
    },
)
