"""
Context — 参数解析与标准化

支持用户注册自定义变量提取器，任意自定义参数都会统一放进 extra 空间。
"""
import copy


# ── 自定义变量提取器注册表 ──
_VARIABLE_EXTRACTORS = {}


def register_variable(name: str, extractor: callable):
    """注册自定义变量提取器。

    Args:
        name: 变量名（在模板中用 {{name}}）
        extractor: callable(params: dict) -> str，从原始参数中提取值
    """
    _VARIABLE_EXTRACTORS[name] = extractor


def list_variables() -> dict:
    """列出所有已注册的变量"""
    return dict(_VARIABLE_EXTRACTORS)


class Context:
    """统一参数容器"""

    def __init__(self, params: dict):
        _p = params if isinstance(params, dict) else {}

        self.max_history = max(0, int(_p.get("max_history", 20)))
        self.lang = _p.get("lang", "zh") or "zh"
        self.mode = _p.get("mode", "") or ""
        self.role = _p.get("role", "") or ""

        self.question = _p.get("question") or _p.get("quesion") or _p.get("Q") or ""
        self.his = _p.get("his", [])
        self.sys_prompt = _p.get("sys_prompt") or ""
        self.context = _p.get("context") or {}
        self.template = _p.get("template") or ""
        self.style_rules = _p.get("style_rules") or ""
        self.output_format = _p.get("output_format") or ""

        # 用户自定义拼接规则
        raw_rules = _p.get("rules", None)
        self.rules = raw_rules if isinstance(raw_rules, list) else None

        # 全部原始参数（供自定义提取器用）
        self._raw = _p

    def get_question(self) -> str:
        return str(self.question).strip()

    def get_extra_variables(self) -> dict:
        """运行所有已注册的变量提取器，返回 {name: value}"""
        result = {}
        for name, extractor in _VARIABLE_EXTRACTORS.items():
            try:
                val = extractor(self._raw)
                if val is not None:
                    result[name] = str(val)
            except Exception:
                pass
        return result
