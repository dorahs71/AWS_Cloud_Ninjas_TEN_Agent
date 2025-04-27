import re
from typing import Dict, Any, List, Tuple
from .log import logger

def perform_calculation(operation: str, numbers: List[float]) -> Dict[str, Any]:
    """執行基本數學運算"""
    try:
        logger.info(f"計算器工具被調用: 運算={operation}, 數字={numbers}")
        

        if not numbers or len(numbers) < 2:
            raise ValueError("至少需要兩個數字才能進行計算")
        
        if operation == "add" or operation.lower() == "加法":
            result = sum(numbers)
            operation_str = "加法"
        elif operation == "subtract" or operation.lower() == "減法":
            result = numbers[0] - sum(numbers[1:])
            operation_str = "減法"
        elif operation == "multiply" or operation.lower() == "乘法":
            result = numbers[0]
            for num in numbers[1:]:
                result *= num
            operation_str = "乘法"
        elif operation == "divide" or operation.lower() == "除法":
            if any(num == 0 for num in numbers[1:]):
                raise ValueError("除數不能為零")
            result = numbers[0]
            for num in numbers[1:]:
                result /= num
            operation_str = "除法"
        else:
            raise ValueError(f"不支援的運算類型: {operation}")
        
        response = {
            "success": True, 
            "result": result, 
            "operation": operation_str,
            "numbers": numbers,
            "error": None
        }
        return response
    except Exception as e:
        error_message = str(e)
        logger.error(f"計算過程中出錯: {error_message}")
        return {
            "success": False, 
            "result": None, 
            "error": error_message,
            "operation": operation,
            "numbers": numbers
        }
