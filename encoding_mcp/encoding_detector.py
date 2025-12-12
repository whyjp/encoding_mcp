#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Encoding detection module
Accurate encoding detection using professional libraries
"""

import os
from typing import Dict, Tuple, Optional, Any

# Encoding detection libraries (in priority order)
try:
    import charset_normalizer as cn
    HAS_CHARSET_NORMALIZER = True
except ImportError:
    HAS_CHARSET_NORMALIZER = False

try:
    import chardet
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False

# UTF-8 BOM byte sequences
UTF8_BOM = b'\xef\xbb\xbf'
UTF16_LE_BOM = b'\xff\xfe'
UTF16_BE_BOM = b'\xfe\xff'
UTF32_LE_BOM = b'\xff\xfe\x00\x00'
UTF32_BE_BOM = b'\x00\x00\xfe\xff'

def detect_bom(raw_data: bytes) -> Tuple[Optional[str], Optional[str]]:
    """
    Detect BOM (Byte Order Mark).
    
    Args:
        raw_data: Binary data of file
        
    Returns:
        tuple: (encoding name, BOM type name) or (None, None)
    """
    if raw_data.startswith(UTF32_BE_BOM):
        return "utf-32-be", "UTF-32 BE BOM"
    elif raw_data.startswith(UTF32_LE_BOM):
        return "utf-32-le", "UTF-32 LE BOM"
    elif raw_data.startswith(UTF8_BOM):
        return "utf-8-bom", "UTF-8 BOM"
    elif raw_data.startswith(UTF16_BE_BOM):
        return "utf-16-be", "UTF-16 BE BOM"
    elif raw_data.startswith(UTF16_LE_BOM):
        return "utf-16-le", "UTF-16 LE BOM"
    
    return None, None

def detect_encoding_with_charset_normalizer(raw_data: bytes) -> Dict[str, Any]:
    """
    Encoding detection using charset-normalizer (most modern)
    """
    try:
        results = cn.from_bytes(raw_data)
        if results:
            best_result = results.best()
            if best_result:
                return {
                    "encoding": best_result.encoding.lower(),
                    "confidence": int(best_result.coherence * 100),
                    "language": getattr(best_result, 'language', 'unknown'),
                    "method": "charset-normalizer"
                }
    except Exception as e:
        print(f"charset-normalizer error: {e}")
    
    return {"encoding": None, "confidence": 0, "method": "charset-normalizer"}

def detect_encoding_with_chardet(raw_data: bytes) -> Dict[str, Any]:
    """
    Encoding detection using chardet (traditional method)
    """
    try:
        result = chardet.detect(raw_data)
        if result and result['encoding']:
            return {
                "encoding": result['encoding'].lower(),
                "confidence": int(result['confidence'] * 100),
                "language": result.get('language', 'unknown'),
                "method": "chardet"
            }
    except Exception as e:
        print(f"chardet error: {e}")
    
    return {"encoding": None, "confidence": 0, "method": "chardet"}

def fallback_encoding_detection(raw_data: bytes) -> Dict[str, Any]:
    """
    Fallback method when libraries are not available
    Improved version of heuristic method
    """
    # ASCII check (most certain case)
    try:
        raw_data.decode('ascii')
        if all(b < 0x80 for b in raw_data):
            return {
                "encoding": "ascii",
                "confidence": 95,
                "method": "fallback-ascii"
            }
    except UnicodeDecodeError:
        pass
    
    # UTF-8 check
    try:
        decoded = raw_data.decode('utf-8')
        # Check for Korean characters
        has_korean = any('\uAC00' <= c <= '\uD7AF' for c in decoded)
        # Check for Chinese/Japanese characters
        has_cjk = any('\u4E00' <= c <= '\u9FFF' for c in decoded)
        
        confidence = 85
        if has_korean or has_cjk:
            confidence = 90  # Higher probability of UTF-8 if East Asian characters present
        
        return {
            "encoding": "utf-8",
            "confidence": confidence,
            "method": "fallback-utf8"
        }
    except UnicodeDecodeError:
        pass
    
    # CP949 check (Korean environment)
    try:
        raw_data.decode('cp949')
        return {
            "encoding": "cp949",
            "confidence": 75,
            "method": "fallback-cp949"
        }
    except UnicodeDecodeError:
        pass
    
    # EUC-KR check
    try:
        raw_data.decode('euc-kr')
        return {
            "encoding": "euc-kr",
            "confidence": 70,
            "method": "fallback-euc-kr"
        }
    except UnicodeDecodeError:
        pass
    
    # ISO-8859-1 (Latin-1) - accepts almost all bytes
    try:
        raw_data.decode('iso-8859-1')
        return {
            "encoding": "iso-8859-1",
            "confidence": 40,
            "method": "fallback-latin1"
        }
    except UnicodeDecodeError:
        pass
    
    return {
        "encoding": "unknown",
        "confidence": 0,
        "method": "fallback-unknown"
    }

def detect_file_encoding(file_path: str, max_bytes: int = 8192) -> Dict[str, Any]:
    """
    Detect file encoding.
    
    Args:
        file_path: File path
        max_bytes: Maximum bytes to analyze (default 8KB)
        
    Returns:
        dict: Encoding information
    """
    try:
        if not os.path.exists(file_path):
            return {
                "error": f"File not found: {file_path}",
                "encoding": None,
                "has_bom": False,
                "confidence": 0
            }
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return {
                "encoding": "empty",
                "has_bom": False,
                "confidence": 100,
                "file_size": 0,
                "first_bytes": "",
                "method": "empty-file"
            }
        
        # Read file
        with open(file_path, 'rb') as f:
            raw_data = f.read(min(max_bytes, file_size))
        
        # Check BOM (highest priority)
        bom_encoding, bom_type = detect_bom(raw_data)
        if bom_encoding:
            return {
                "encoding": bom_encoding,
                "has_bom": True,
                "bom_type": bom_type,
                "confidence": 100,
                "file_size": file_size,
                "first_bytes": ' '.join(f'{b:02x}' for b in raw_data[:16]),
                "method": "bom-detection"
            }
        
        # Library-based detection (priority: charset-normalizer > chardet > fallback)
        detection_result = None
        
        if HAS_CHARSET_NORMALIZER:
            detection_result = detect_encoding_with_charset_normalizer(raw_data)
        elif HAS_CHARDET:
            detection_result = detect_encoding_with_chardet(raw_data)
        
        # Use fallback if library result is unavailable or confidence is low
        if not detection_result or detection_result["confidence"] < 60:
            fallback_result = fallback_encoding_detection(raw_data)
            if not detection_result or fallback_result["confidence"] > detection_result["confidence"]:
                detection_result = fallback_result
        
        # Build final result
        result = {
            "encoding": detection_result["encoding"],
            "has_bom": False,
            "bom_type": None,
            "confidence": detection_result["confidence"],
            "file_size": file_size,
            "first_bytes": ' '.join(f'{b:02x}' for b in raw_data[:16]),
            "method": detection_result["method"]
        }
        
        # Include additional information if available
        if "language" in detection_result:
            result["language"] = detection_result["language"]
        
        return result
        
    except Exception as e:
        return {
            "error": f"Error detecting file encoding: {str(e)}",
            "encoding": None,
            "has_bom": False,
            "confidence": 0
        }

def get_available_detection_methods() -> Dict[str, bool]:
    """
    Return available encoding detection methods.
    """
    return {
        "charset-normalizer": HAS_CHARSET_NORMALIZER,
        "chardet": HAS_CHARDET,
        "fallback": True  # Always available
    }

def get_recommended_libraries() -> str:
    """
    Return recommended library installation command.
    """
    missing_libs = []
    
    if not HAS_CHARSET_NORMALIZER:
        missing_libs.append("charset-normalizer")
    
    if not HAS_CHARDET:
        missing_libs.append("chardet")
    
    if missing_libs:
        return f"pip install {' '.join(missing_libs)}"
    else:
        return "All recommended libraries are installed."
