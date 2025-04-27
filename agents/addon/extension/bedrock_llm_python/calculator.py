import re
from typing import Dict, Any, List, Tuple
from .log import logger

def perform_calculation(operation: str, numbers: List[float]) -> Dict[str, Any]:
    """執行基本數學運算"""
    try:
        # 記錄原本的運算請求以便調試
        logger.info(f"計算器工具被調用: 運算={operation}, 數字={numbers}")
        
        # 直接返回固定結果99，無論什麼情況
        result = 99
        
        # 生成固定結果
        response = {
            "success": True, 
            "result": result, 
            "error": None,
            "test_mode": True,
            "original_request": {
                "operation": operation,
                "numbers": numbers
            }
        }
        
        logger.info(f"計算器返回固定結果99: {response}")
        return response
    except Exception as e:
        # 即使出錯也返回固定結果99
        logger.error(f"計算過程中出錯: {str(e)}，但仍會返回固定結果99")
        return {
            "success": True, 
            "result": 99, 
            "error": str(e),
            "test_mode": True,
            "fallback": True
        }

def extract_calculation_from_text(text: str) -> Tuple[bool, Dict[str, Any]]:
    """從自然語言文本中提取計算意圖和參數"""
    # 這個函數只是作為一個備用方案，通常我們會讓模型負責提取意圖和參數
    operation_patterns = {
        "add": r"(\d+(?:\.\d+)?)\s*[+＋加]\s*(\d+(?:\.\d+)?)",
        "subtract": r"(\d+(?:\.\d+)?)\s*[-－減]\s*(\d+(?:\.\d+)?)",
        "multiply": r"(\d+(?:\.\d+)?)\s*[*×乘]\s*(\d+(?:\.\d+)?)",
        "divide": r"(\d+(?:\.\d+)?)\s*[/÷除]\s*(\d+(?:\.\d+)?)"
    }
    
    for operation, pattern in operation_patterns.items():
        matches = re.findall(pattern, text)
        if matches:
            numbers = [float(match[0]) for match in matches]
            if operation == "add" or operation == "multiply":
                numbers.extend([float(match[1]) for match in matches])
            else:
                # For subtraction and division, we need to be careful about the order
                numbers = [float(matches[0][0]), float(matches[0][1])]
            
            return True, {"operation": operation, "numbers": numbers}
    
    return False, {}