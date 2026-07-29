"""
HistoryBuilder — 历史对话组装

职责：
- 从 his[] 数组提取历史记录
- 控制最大轮数
- 支持文件附件信息
- 可选按 token 长度截断
"""
from . import sanitize


class HistoryBuilder:
    """历史对话构建器"""

    def __init__(self, ctx):
        self.raw = ctx.his if isinstance(ctx.his, list) else []
        self.max_rounds = ctx.max_history
        self.safe_mode = ctx.safe_mode
        self.trim = ctx.trim_history
        self._lines = None

    def build(self) -> str:
        """组装历史对话字符串"""
        if not self.raw:
            return ""

        self._lines = []
        rounds = 0

        # 从最新取 max_rounds 轮
        for item in self.raw[-self.max_rounds:]:
            if not isinstance(item, dict):
                continue
            rounds += 1
            query = sanitize.clean(str(item.get("query") or ""), self.safe_mode)
            answer = sanitize.clean(str(item.get("answer") or ""), self.safe_mode)

            self._lines.append(f"用户：{query}")

            files = item.get("files")
            file_str = self._format_files(files)
            if file_str:
                self._lines.append(f"（附带文件：{file_str}）")

            self._lines.append(f"AI：{answer}")

        self._rounds = rounds
        raw = "\n".join(self._lines)

        if self.trim:
            raw = self._trim_tokens(raw)

        return raw

    def count_rounds(self) -> int:
        return getattr(self, "_rounds", 0)

    def _format_files(self, files) -> str:
        if not isinstance(files, list):
            return ""
        names = []
        for f in files:
            if isinstance(f, dict) and f.get("name"):
                names.append(f["name"])
        return "、".join(names) if names else ""

    @staticmethod
    def _trim_tokens(text: str, max_chars: int = 8000) -> str:
        """简化的 token 截断（按字符估算，1 token ≈ 2 中文字符）"""
        if len(text) <= max_chars:
            return text
        return text[:max_chars] + "\n\n...（历史过长已截断）"
