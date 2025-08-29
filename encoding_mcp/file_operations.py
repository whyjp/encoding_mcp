#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
파일 조작 모듈
인코딩 기반 파일 생성, 변환 등의 기능
"""

import os
import shutil
from typing import Dict, Optional

# UTF-8 BOM 바이트
UTF8_BOM = b'\xef\xbb\xbf'

# 지원하는 인코딩 목록
SUPPORTED_ENCODINGS = {
    "utf-8-bom": {
        "name": "UTF-8 with BOM",
        "description": "Windows C++/PowerShell에 최적화",
        "windows_friendly": True,
        "write_mode": "binary"
    },
    "utf-8": {
        "name": "UTF-8",
        "description": "범용적인 UTF-8 인코딩",
        "windows_friendly": False,
        "write_mode": "text"
    },
    "cp949": {
        "name": "CP949",
        "description": "Windows 한글 인코딩",
        "windows_friendly": True,
        "write_mode": "text"
    },
    "euc-kr": {
        "name": "EUC-KR",
        "description": "Unix/Linux 한글 인코딩",
        "windows_friendly": False,
        "write_mode": "text"
    },
    "ascii": {
        "name": "ASCII",
        "description": "7비트 ASCII 인코딩",
        "windows_friendly": True,
        "write_mode": "text"
    }
}

def validate_encoding(encoding: str) -> bool:
    """
    지원하는 인코딩인지 확인합니다.
    
    Args:
        encoding: 인코딩 이름
        
    Returns:
        bool: 지원 여부
    """
    return encoding in SUPPORTED_ENCODINGS

def get_encoding_info(encoding: str) -> Optional[Dict[str, any]]:
    """
    인코딩 정보를 반환합니다.
    
    Args:
        encoding: 인코딩 이름
        
    Returns:
        dict: 인코딩 정보 또는 None
    """
    return SUPPORTED_ENCODINGS.get(encoding)

def ensure_directory(file_path: str) -> str:
    """
    파일의 디렉터리가 존재하는지 확인하고 생성합니다.
    
    Args:
        file_path: 파일 경로
        
    Returns:
        str: 성공 메시지 또는 오류 메시지
    """
    dir_path = os.path.dirname(file_path)
    if not dir_path:
        return "디렉터리 경로가 필요하지 않습니다."
    
    if os.path.exists(dir_path):
        return "디렉터리가 이미 존재합니다."
    
    try:
        os.makedirs(dir_path, exist_ok=True)
        return f"디렉터리를 생성했습니다: {dir_path}"
    except PermissionError:
        return f"디렉터리 생성 권한이 없습니다: {dir_path}"
    except OSError as e:
        return f"디렉터리 생성 실패: {dir_path} - {str(e)}"

def create_empty_file(file_path: str, encoding: str = "utf-8-bom") -> str:
    """
    지정된 인코딩으로 빈 파일을 생성합니다.
    
    Args:
        file_path: 파일 경로
        encoding: 인코딩 (기본값: utf-8-bom)
        
    Returns:
        str: 결과 메시지
    """
    try:
        # 인코딩 유효성 검사
        if not validate_encoding(encoding):
            supported = ", ".join(SUPPORTED_ENCODINGS.keys())
            return f"지원하지 않는 인코딩입니다: {encoding}. 지원: {supported}"
        
        # 디렉터리 생성
        dir_result = ensure_directory(file_path)
        if "실패" in dir_result or "권한" in dir_result:
            return dir_result
        
        # 인코딩별 빈 파일 생성
        if encoding == "utf-8-bom":
            with open(file_path, 'wb') as f:
                f.write(UTF8_BOM)  # BOM만 쓰기
        elif encoding == "utf-8":
            with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                pass  # 빈 파일
        elif encoding == "cp949":
            with open(file_path, 'w', encoding='cp949') as f:
                pass  # 빈 파일
        elif encoding == "euc-kr":
            with open(file_path, 'w', encoding='euc-kr') as f:
                pass  # 빈 파일
        elif encoding == "ascii":
            with open(file_path, 'w', encoding='ascii') as f:
                pass  # 빈 파일
        
        encoding_info = get_encoding_info(encoding)
        return f"빈 파일이 성공적으로 생성되었습니다: {file_path} ({encoding_info['name']})"
    
    except PermissionError:
        return f"파일 쓰기 권한이 없습니다: {file_path}"
    except FileNotFoundError:
        return f"잘못된 파일 경로입니다: {file_path}"
    except OSError as e:
        return f"파일 시스템 오류: {str(e)}"
    except Exception as e:
        return f"파일 생성 중 예상치 못한 오류 발생: {str(e)}"

def write_file_with_content(file_path: str, content: str, encoding: str = "utf-8-bom") -> str:
    """
    지정된 인코딩으로 내용이 있는 파일을 생성합니다.
    
    Args:
        file_path: 파일 경로
        content: 파일 내용
        encoding: 인코딩 (기본값: utf-8-bom)
        
    Returns:
        str: 결과 메시지
    """
    try:
        # 인코딩 유효성 검사
        if not validate_encoding(encoding):
            supported = ", ".join(SUPPORTED_ENCODINGS.keys())
            return f"지원하지 않는 인코딩입니다: {encoding}. 지원: {supported}"
        
        # 디렉터리 생성
        dir_result = ensure_directory(file_path)
        if "실패" in dir_result or "권한" in dir_result:
            return dir_result
        
        # 인코딩별 파일 쓰기
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
                return f"CP949 인코딩 실패 (한글 이외의 문자 포함): {str(e)}"
        elif encoding == "euc-kr":
            try:
                with open(file_path, 'w', encoding='euc-kr') as f:
                    f.write(content)
            except UnicodeEncodeError as e:
                return f"EUC-KR 인코딩 실패: {str(e)}"
        elif encoding == "ascii":
            try:
                with open(file_path, 'w', encoding='ascii') as f:
                    f.write(content)
            except UnicodeEncodeError as e:
                return f"ASCII 인코딩 실패 (비ASCII 문자 포함): {str(e)}"
        
        encoding_info = get_encoding_info(encoding)
        return f"파일이 성공적으로 생성되었습니다: {file_path} ({encoding_info['name']})"
    
    except PermissionError:
        return f"파일 쓰기 권한이 없습니다: {file_path}"
    except FileNotFoundError:
        return f"잘못된 파일 경로입니다: {file_path}"
    except OSError as e:
        return f"파일 시스템 오류: {str(e)}"
    except Exception as e:
        return f"파일 생성 중 예상치 못한 오류 발생: {str(e)}"

def read_file_with_encoding(file_path: str, source_encoding: str) -> tuple[str, str]:
    """
    지정된 인코딩으로 파일을 읽습니다.
    
    Args:
        file_path: 파일 경로
        source_encoding: 소스 인코딩
        
    Returns:
        tuple: (내용, 결과 메시지)
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
            return "", f"지원하지 않는 인코딩입니다: {source_encoding}"
        
        return content, "파일을 성공적으로 읽었습니다."
    
    except UnicodeDecodeError as e:
        return "", f"인코딩 오류: {str(e)}"
    except FileNotFoundError:
        return "", f"파일을 찾을 수 없습니다: {file_path}"
    except PermissionError:
        return "", f"파일 읽기 권한이 없습니다: {file_path}"
    except Exception as e:
        return "", f"파일 읽기 중 오류: {str(e)}"

def convert_file_encoding(file_path: str, target_encoding: str, backup: bool = True) -> str:
    """
    파일의 인코딩을 변환합니다.
    
    Args:
        file_path: 파일 경로
        target_encoding: 목표 인코딩
        backup: 백업 생성 여부
        
    Returns:
        str: 결과 메시지
    """
    try:
        # 파일 존재 확인
        if not os.path.exists(file_path):
            return f"파일을 찾을 수 없습니다: {file_path}"
        
        # 인코딩 유효성 검사
        if not validate_encoding(target_encoding):
            supported = ", ".join(SUPPORTED_ENCODINGS.keys())
            return f"지원하지 않는 인코딩입니다: {target_encoding}. 지원: {supported}"
        
        # 현재 인코딩 감지 (별도 모듈 사용)
        from .encoding_detector import detect_file_encoding
        
        current_info = detect_file_encoding(file_path)
        if "error" in current_info:
            return f"파일 인코딩 확인 실패: {current_info['error']}"
        
        current_encoding = current_info['encoding']
        
        # 이미 목표 인코딩인 경우
        if current_encoding == target_encoding:
            return f"파일이 이미 {target_encoding} 인코딩입니다: {file_path}"
        
        # 백업 생성
        backup_path = None
        if backup:
            backup_path = file_path + ".backup"
            try:
                shutil.copy2(file_path, backup_path)
            except Exception as e:
                return f"백업 생성 실패: {str(e)}"
        
        # 파일 내용 읽기
        content, read_result = read_file_with_encoding(file_path, current_encoding)
        if not content and "성공" not in read_result:
            return f"파일 읽기 실패: {read_result}"
        
        # 새로운 인코딩으로 저장
        write_result = write_file_with_content(file_path, content, target_encoding)
        if "성공" not in write_result:
            # 실패 시 백업 복원
            if backup_path and os.path.exists(backup_path):
                shutil.copy2(backup_path, file_path)
            return f"파일 쓰기 실패: {write_result}"
        
        backup_msg = f"\n백업 파일: {backup_path}" if backup_path else "\n백업 없음"
        current_info_obj = get_encoding_info(current_encoding)
        target_info_obj = get_encoding_info(target_encoding)
        
        current_name = current_info_obj['name'] if current_info_obj else current_encoding
        target_name = target_info_obj['name'] if target_info_obj else target_encoding
        
        return f"파일 인코딩 변환 완료!\n변환: {current_name} → {target_name}{backup_msg}"
        
    except Exception as e:
        return f"파일 변환 중 오류 발생: {str(e)}"

def get_file_info(file_path: str) -> Dict[str, any]:
    """
    파일의 기본 정보를 반환합니다.
    
    Args:
        file_path: 파일 경로
        
    Returns:
        dict: 파일 정보
    """
    try:
        if not os.path.exists(file_path):
            return {"error": f"파일을 찾을 수 없습니다: {file_path}"}
        
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
        return {"error": f"파일 정보 조회 실패: {str(e)}"}

def list_supported_encodings() -> Dict[str, Dict[str, any]]:
    """
    지원하는 모든 인코딩 목록을 반환합니다.
    
    Returns:
        dict: 지원 인코딩 정보
    """
    return SUPPORTED_ENCODINGS.copy()
