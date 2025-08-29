#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
인코딩 감지 모듈
전문적인 라이브러리를 사용한 정확한 인코딩 감지
"""

import os
from typing import Dict, Tuple, Optional

# 인코딩 감지 라이브러리들 (우선순위대로)
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

# UTF-8 BOM 바이트 시퀀스
UTF8_BOM = b'\xef\xbb\xbf'
UTF16_LE_BOM = b'\xff\xfe'
UTF16_BE_BOM = b'\xfe\xff'
UTF32_LE_BOM = b'\xff\xfe\x00\x00'
UTF32_BE_BOM = b'\x00\x00\xfe\xff'

def detect_bom(raw_data: bytes) -> Tuple[Optional[str], Optional[str]]:
    """
    BOM(Byte Order Mark)을 감지합니다.
    
    Args:
        raw_data: 파일의 바이너리 데이터
        
    Returns:
        tuple: (인코딩명, BOM 타입명) 또는 (None, None)
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

def detect_encoding_with_charset_normalizer(raw_data: bytes) -> Dict[str, any]:
    """
    charset-normalizer를 사용한 인코딩 감지 (가장 현대적)
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
        print(f"charset-normalizer 오류: {e}")
    
    return {"encoding": None, "confidence": 0, "method": "charset-normalizer"}

def detect_encoding_with_chardet(raw_data: bytes) -> Dict[str, any]:
    """
    chardet를 사용한 인코딩 감지 (전통적인 방법)
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
        print(f"chardet 오류: {e}")
    
    return {"encoding": None, "confidence": 0, "method": "chardet"}

def fallback_encoding_detection(raw_data: bytes) -> Dict[str, any]:
    """
    라이브러리가 없을 때 사용하는 폴백 방법
    기존의 휴리스틱 방법을 개선한 버전
    """
    # ASCII 체크 (가장 확실한 경우)
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
    
    # UTF-8 체크
    try:
        decoded = raw_data.decode('utf-8')
        # 한글 문자 확인
        has_korean = any('\uAC00' <= c <= '\uD7AF' for c in decoded)
        # 중국어/일본어 문자 확인
        has_cjk = any('\u4E00' <= c <= '\u9FFF' for c in decoded)
        
        confidence = 85
        if has_korean or has_cjk:
            confidence = 90  # 동아시아 문자가 있으면 UTF-8일 가능성 높음
        
        return {
            "encoding": "utf-8",
            "confidence": confidence,
            "method": "fallback-utf8"
        }
    except UnicodeDecodeError:
        pass
    
    # CP949 체크 (한국어 환경)
    try:
        raw_data.decode('cp949')
        return {
            "encoding": "cp949",
            "confidence": 75,
            "method": "fallback-cp949"
        }
    except UnicodeDecodeError:
        pass
    
    # EUC-KR 체크
    try:
        raw_data.decode('euc-kr')
        return {
            "encoding": "euc-kr",
            "confidence": 70,
            "method": "fallback-euc-kr"
        }
    except UnicodeDecodeError:
        pass
    
    # ISO-8859-1 (Latin-1) - 거의 모든 바이트 허용
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

def detect_file_encoding(file_path: str, max_bytes: int = 8192) -> Dict[str, any]:
    """
    파일의 인코딩을 감지합니다.
    
    Args:
        file_path: 파일 경로
        max_bytes: 분석할 최대 바이트 수 (기본 8KB)
        
    Returns:
        dict: 인코딩 정보
    """
    try:
        if not os.path.exists(file_path):
            return {
                "error": f"파일을 찾을 수 없습니다: {file_path}",
                "encoding": None,
                "has_bom": False,
                "confidence": 0
            }
        
        # 파일 크기 확인
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
        
        # 파일 읽기
        with open(file_path, 'rb') as f:
            raw_data = f.read(min(max_bytes, file_size))
        
        # BOM 확인 (최우선)
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
        
        # 라이브러리 기반 감지 (우선순위: charset-normalizer > chardet > fallback)
        detection_result = None
        
        if HAS_CHARSET_NORMALIZER:
            detection_result = detect_encoding_with_charset_normalizer(raw_data)
        elif HAS_CHARDET:
            detection_result = detect_encoding_with_chardet(raw_data)
        
        # 라이브러리 결과가 없거나 신뢰도가 낮으면 폴백 사용
        if not detection_result or detection_result["confidence"] < 60:
            fallback_result = fallback_encoding_detection(raw_data)
            if not detection_result or fallback_result["confidence"] > detection_result["confidence"]:
                detection_result = fallback_result
        
        # 최종 결과 구성
        result = {
            "encoding": detection_result["encoding"],
            "has_bom": False,
            "bom_type": None,
            "confidence": detection_result["confidence"],
            "file_size": file_size,
            "first_bytes": ' '.join(f'{b:02x}' for b in raw_data[:16]),
            "method": detection_result["method"]
        }
        
        # 추가 정보가 있으면 포함
        if "language" in detection_result:
            result["language"] = detection_result["language"]
        
        return result
        
    except Exception as e:
        return {
            "error": f"파일 인코딩 감지 중 오류: {str(e)}",
            "encoding": None,
            "has_bom": False,
            "confidence": 0
        }

def get_available_detection_methods() -> Dict[str, bool]:
    """
    사용 가능한 인코딩 감지 방법들을 반환합니다.
    """
    return {
        "charset-normalizer": HAS_CHARSET_NORMALIZER,
        "chardet": HAS_CHARDET,
        "fallback": True  # 항상 사용 가능
    }

def get_recommended_libraries() -> str:
    """
    권장하는 라이브러리 설치 명령을 반환합니다.
    """
    missing_libs = []
    
    if not HAS_CHARSET_NORMALIZER:
        missing_libs.append("charset-normalizer")
    
    if not HAS_CHARDET:
        missing_libs.append("chardet")
    
    if missing_libs:
        return f"pip install {' '.join(missing_libs)}"
    else:
        return "모든 권장 라이브러리가 설치되어 있습니다."
