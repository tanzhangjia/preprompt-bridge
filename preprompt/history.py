"""
HistoryBuilder — 历史对话组装
"""
class HistoryBuilder:
    def __init__(self, ctx):
        self.raw = ctx.his if isinstance(ctx.his, list) else []
        self.max_rounds = ctx.max_history
        self._rounds = 0

    def build(self) -> str:
        if not self.raw:
            return ""
        self._lines = []
        self._rounds = 0
        for item in self.raw[-self.max_rounds:]:
            if not isinstance(item, dict):
                continue
            self._rounds += 1
            query = str(item.get("query") or "")
            answer = str(item.get("answer") or "")
            self._lines.append(f"用户：{query}")
            files = item.get("files")
            if isinstance(files, list):
                names = [f.get("name", "") for f in files if isinstance(f, dict)]
                fstr = "、".join(filter(None, names))
                if fstr:
                    self._lines.append(f"（附带文件：{fstr}）")
            self._lines.append(f"AI：{answer}")
        return "\n".join(self._lines)

    def count_rounds(self) -> int:
        return self._rounds
