#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File operations module
Encoding-based file creation, conversion, and other functions
"""

import os
import shutil
from typing import Dict, Optional, Any

# UTF-8 BOM bytes
UTF8_BOM = b'\xef\xbb\xbf'

# Supported encodings list
SUPPORTED_ENCODINGS = {
    "utf-8-bom": {
        "name": "UTF-8 with BOM",
        "description": "Optimized for Windows C++/PowerShell",
        "windows_friendly": True,
        "write_mode": "binary"
    },
    "utf-8": {
        "name": "UTF-8",
        "description": "Universal UTF-8 encoding",
        "windows_friendly": False,
        "write_mode": "text"
    },
    "cp949": {
        "name": "CP949",
        "description": "Windows Korean encoding",
        "windows_friendly": True,
        "write_mode": "text"
    },
    "euc-kr": {
        "name": "EUC-KR",
        "description": "Unix/Linux Korean encoding",
        "windows_friendly": False,
        "write_mode": "text"
    },
    "ascii": {
        "name": "ASCII",
        "description": "7-bit ASCII encoding",
        "windows_friendly": True,
        "write_mode": "text"
    }
}

def validate_encoding(encoding: str) -> bool:
    """
    Check if encoding is supported.
    
    Args:
        encoding: Encoding name
        
    Returns:
        bool: Whether supported
    """
    return encoding in SUPPORTED_ENCODINGS

def get_encoding_info(encoding: str) -> Optional[Dict[str, Any]]:
    """
    Return encoding information.
    
    Args:
        encoding: Encoding name
        
    Returns:
        dict: Encoding information or None
    """
    return SUPPORTED_ENCODINGS.get(encoding)

def ensure_directory(file_path: str) -> str:
    """
    Check if file's directory exists and create it if needed.
    
    Args:
        file_path: File path
        
    Returns:
        str: Success message or error message
    """
    dir_path = os.path.dirname(file_path)
    if not dir_path:
        return "Directory path not required."
    
    if os.path.exists(dir_path):
        return "Directory already exists."
    
    try:
        os.makedirs(dir_path, exist_ok=True)
        return f"Directory created: {dir_path}"
    except PermissionError:
        return f"No permission to create directory: {dir_path}"
    except OSError as e:
        return f"Directory creation failed: {dir_path} - {str(e)}"

def create_empty_file(file_path: str, encoding: str = "utf-8-bom") -> str:
    """
    Create an empty file with specified encoding.
    
    Args:
        file_path: File path
        encoding: Encoding (default: utf-8-bom)
        
    Returns:
        str: Result message
    """
    try:
        # Validate encoding
        if not validate_encoding(encoding):
            supported = ", ".join(SUPPORTED_ENCODINGS.keys())
            return f"Unsupported encoding: {encoding}. Supported: {supported}"
        
        # Create directory
        dir_result = ensure_directory(file_path)
        if "failed" in dir_result.lower() or "permission" in dir_result.lower():
            return dir_result
        
        # Create empty file by encoding
        if encoding == "utf-8-bom":
            with open(file_path, 'wb') as f:
                f.write(UTF8_BOM)  # Write BOM only
        elif encoding == "utf-8":
            with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                pass  # Empty file
        elif encoding == "cp949":
            with open(file_path, 'w', encoding='cp949') as f:
                pass  # Empty file
        elif encoding == "euc-kr":
            with open(file_path, 'w', encoding='euc-kr') as f:
                pass  # Empty file
        elif encoding == "ascii":
            with open(file_path, 'w', encoding='ascii') as f:
                pass  # Empty file
        
        encoding_info = get_encoding_info(encoding)
        return f"Empty file created successfully: {file_path} ({encoding_info['name']})"
    
    except PermissionError:
        return f"No permission to write file: {file_path}"
    except FileNotFoundError:
        return f"Invalid file path: {file_path}"
    except OSError as e:
        return f"File system error: {str(e)}"
    except Exception as e:
        return f"Unexpected error creating file: {str(e)}"

def write_file_with_content(file_path: str, content: str, encoding: str = "utf-8-bom") -> str:
    """
    Create a file with content using specified encoding.
    
    Args:
        file_path: File path
        content: File content
        encoding: Encoding (default: utf-8-bom)
        
    Returns:
        str: Result message
    """
    try:
        # Validate encoding
        if not validate_encoding(encoding):
            supported = ", ".join(SUPPORTED_ENCODINGS.keys())
            return f"Unsupported encoding: {encoding}. Supported: {supported}"
        
        # Create directory
        dir_result = ensure_directory(file_path)
        if "failed" in dir_result.lower() or "permission" in dir_result.lower():
            return dir_result
        
        # Write file by encoding
        if encoding == "utf-8-bom":
            with open(file_path, 'wb') as f:
                f.write(UTF8_BOM)
                f.write(content.encode('utf-8'))
        elif encoding == "utf-8":
            with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)
        elif encoding == "cp949":
            try:
                with open(file_path, 'w', encoding='cp949') as f:
                    f.write(content)
            except UnicodeEncodeError as e:
                return f"CP949 encoding failed (contains non-Korean characters): {str(e)}"
        elif encoding == "euc-kr":
            try:
                with open(file_path, 'w', encoding='euc-kr') as f:
                    f.write(content)
            except UnicodeEncodeError as e:
                return f"EUC-KR encoding failed: {str(e)}"
        elif encoding == "ascii":
            try:
                with open(file_path, 'w', encoding='ascii') as f:
                    f.write(content)
            except UnicodeEncodeError as e:
                return f"ASCII encoding failed (contains non-ASCII characters): {str(e)}"
        
        encoding_info = get_encoding_info(encoding)
        return f"File created successfully: {file_path} ({encoding_info['name']})"
    
    except PermissionError:
        return f"No permission to write file: {file_path}"
    except FileNotFoundError:
        return f"Invalid file path: {file_path}"
    except OSError as e:
        return f"File system error: {str(e)}"
    except Exception as e:
        return f"Unexpected error creating file: {str(e)}"

def read_file_with_encoding(file_path: str, source_encoding: str) -> tuple[str, str]:
    """
    Read file with specified encoding.
    
    Args:
        file_path: File path
        source_encoding: Source encoding
        
    Returns:
        tuple: (content, result message)
    """
    try:
        if source_encoding == "utf-8-bom":
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
        elif source_encoding == "utf-8":
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        elif source_encoding == "cp949":
            with open(file_path, 'r', encoding='cp949') as f:
                content = f.read()
        elif source_encoding == "euc-kr":
            with open(file_path, 'r', encoding='euc-kr') as f:
                content = f.read()
        elif source_encoding == "ascii":
            with open(file_path, 'r', encoding='ascii') as f:
                content = f.read()
        else:
            return "", f"Unsupported encoding: {source_encoding}"
        
        return content, "File read successfully."
    
    except UnicodeDecodeError as e:
        return "", f"Encoding error: {str(e)}"
    except FileNotFoundError:
        return "", f"File not found: {file_path}"
    except PermissionError:
        return "", f"No permission to read file: {file_path}"
    except Exception as e:
        return "", f"Error reading file: {str(e)}"

def convert_file_encoding(file_path: str, target_encoding: str, backup: bool = False) -> str:
    """
    Convert file encoding.
    
    Args:
        file_path: File path
        target_encoding: Target encoding
        backup: Whether to create backup
        
    Returns:
        str: Result message
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return f"File not found: {file_path}"
        
        # Validate encoding
        if not validate_encoding(target_encoding):
            supported = ", ".join(SUPPORTED_ENCODINGS.keys())
            return f"Unsupported encoding: {target_encoding}. Supported: {supported}"
        
        # Detect current encoding (using separate module)
        from .encoding_detector import detect_file_encoding
        
        current_info = detect_file_encoding(file_path)
        if "error" in current_info:
            return f"Failed to detect file encoding: {current_info['error']}"
        
        current_encoding = current_info['encoding']
        
        # Already in target encoding
        if current_encoding == target_encoding:
            return f"File is already in {target_encoding} encoding: {file_path}"
        
        # Create backup
        backup_path = None
        if backup:
            backup_path = file_path + ".backup"
            try:
                shutil.copy2(file_path, backup_path)
            except Exception as e:
                return f"Backup creation failed: {str(e)}"
        
        # Read file content
        content, read_result = read_file_with_encoding(file_path, current_encoding)
        if not content and "successfully" not in read_result.lower():
            return f"File read failed: {read_result}"
        
        # Save with new encoding
        write_result = write_file_with_content(file_path, content, target_encoding)
        if "successfully" not in write_result.lower():
            # Restore backup on failure
            if backup_path and os.path.exists(backup_path):
                shutil.copy2(backup_path, file_path)
            return f"File write failed: {write_result}"
        
        backup_msg = f"\nBackup file: {backup_path}" if backup_path else "\nNo backup"
        current_info_obj = get_encoding_info(current_encoding)
        target_info_obj = get_encoding_info(target_encoding)
        
        current_name = current_info_obj['name'] if current_info_obj else current_encoding
        target_name = target_info_obj['name'] if target_info_obj else target_encoding
        
        return f"File encoding conversion completed!\nConversion: {current_name} → {target_name}{backup_msg}"
        
    except Exception as e:
        return f"Error during file conversion: {str(e)}"

def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Return basic file information.
    
    Args:
        file_path: File path
        
    Returns:
        dict: File information
    """
    try:
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        stat = os.stat(file_path)
        
        return {
            "path": file_path,
            "name": os.path.basename(file_path),
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "created": stat.st_ctime,
            "is_file": os.path.isfile(file_path),
            "is_directory": os.path.isdir(file_path),
            "extension": os.path.splitext(file_path)[1].lower()
        }
    
    except Exception as e:
        return {"error": f"Failed to retrieve file information: {str(e)}"}

def list_supported_encodings() -> Dict[str, Dict[str, Any]]:
    """
    Return list of all supported encodings.
    
    Returns:
        dict: Supported encoding information
    """
    return SUPPORTED_ENCODINGS.copy()
