"""
Context — 参数解析与标准化

职责：
- 从 params dict 提取所有配置项
- 兼容拼写错误
- 设置合理默认值
- 不做任何业务逻辑
"""
import copy


class Context:
    """统一参数容器"""

    def __init__(self, params: dict):
        _p = params if isinstance(params, dict) else {}

        self.safe_mode = bool(_p.get("safe_mode", False))
        self.max_history = max(0, int(_p.get("max_history", 20)))
        self.trim_history = bool(_p.get("trim_history", False))
        self.lang = _p.get("lang", "zh") or "zh"
        self.mode = _p.get("mode", "") or ""
        self.role = _p.get("role", "") or ""
        self.style_rules = _p.get("style_rules", "") or ""

        self.question = _p.get("question")
        self.quesion = _p.get("quesion")
        self.Q = _p.get("Q")

        self.his = _p.get("his")
        self.sys_prompt = _p.get("sys_prompt") or ""
        self.context = _p.get("context")
        self.template = _p.get("template") or ""

        # 自定义参数（传递给 filter / mode）
        self.extra = {
            k: v for k, v in _p.items()
            if k not in {
                "safe_mode", "max_history", "trim_history", "lang", "mode",
                "role", "style_rules", "question", "quesion", "Q",
                "his", "sys_prompt", "context", "template",
                "filter_rules", "output_format",
            }
        }

        self.filter_rules = _p.get("filter_rules", None)  # 用户自定义过滤规则
        self.output_format = _p.get("output_format", "")  # 输出格式要求

    def get_question(self) -> str:
        """获取问题（兼容拼写）"""
        return (self.question or self.quesion or self.Q or "").strip()

    def to_dict(self) -> dict:
        """dump 全部配置（调试用）"""
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
