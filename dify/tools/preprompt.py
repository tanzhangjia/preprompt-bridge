"""
Dify Plugin Tool — PrePrompt Bridge

将此文件放置在 Dify Plugin 项目中的 tools/ 目录下。
"""
from typing import Any
from preprompt import handler as preprompt_handler


class PrePromptTool:
    """Dify Tool: 组装结构化 prompt"""

    def __init__(self):
        pass

    def validate_parameters(self, parameters: dict) -> dict:
        """参数校验"""
        validated = {}
        # question 是必填项
        if not parameters.get("question") and not parameters.get("quesion"):
            # Dify 层面已有 required 校验，这里仅做二次确认
            pass
        return parameters

    def run(self, parameters: dict, **kwargs) -> list[dict]:
        """执行 prompt 组装，返回 Dify 工具结果格式"""
        # 参数重命名：Dify 历史参数名叫 history，核心库是 his
        params = dict(parameters)
        if "history" in params and "his" not in params:
            params["his"] = params.pop("history")

        # 调用核心库
        result = preprompt_handler(params)

        prompt = result.get("prompt", "")
        meta = result.get("meta", {})

        # Dify 工具返回格式：list of dict
        # text 类型
        return [
            {
                "type": "text",
                "text": prompt,
            },
            {
                "type": "json",
                "text": meta,
            },
        ]
