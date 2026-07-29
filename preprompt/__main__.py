"""
PrePrompt Bridge — CLI 入口（调试用）
"""
from .handler import handler
import json, sys

if __name__ == "__main__":
    params = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
    result = handler(params)
    print(json.dumps(result, indent=2, ensure_ascii=False))
