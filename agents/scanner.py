"""
扫描 Agent —— 负责遍历代码仓库，基于规则库逐文件扫描，
输出结构化问题清单（JSON 格式）。
"""
import json
import re
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

RULES = {
    "deprecated-api": {
        "pattern": r"\.subscribe\(|\.toPromise\(|React\.createClass|\.waitFor\(|\.observe\(",
        "severity": "high",
        "message": "使用了已废弃的 API，请迁移到最新写法",
    },
    "naming-convention": {
        "pattern": r"\bclass\s+([a-z_][a-z0-9_]*)\s*[\(:]|\b(?:let|const|var)\s+([a-z][a-z0-9]*_[A-Z])|\bdef\s+([a-z][a-z0-9]*_[a-z])",
        "severity": "low",
        "message": "命名不符合规范（class 应大驼峰，函数/变量应小驼峰）",
    },
    "circular-dependency": {
        "pattern": r"from\s+\.\..+\s+import|import\s+.*from\s+['\"]\.\.\/.*['\"]",
        "severity": "high",
        "message": "存在潜在的循环依赖，建议重构导入路径",
    },
    "missing-error-handling": {
        "pattern": r"await\s+\w+\(.*\)\s*$|\.get\(|\.post\(|\.put\(|\.delete\(\s*$",
        "severity": "medium",
        "message": "异步调用或 HTTP 请求缺少 try-catch 错误处理",
    },
    "hardcoded-secret": {
        "pattern": r"(?:api_key|secret|token|password)\s*[:=]\s*['\"][^'\"]{8,}['\"]",
        "severity": "critical",
        "message": "代码中存在硬编码的敏感信息",
    },
    "unused-import": {
        "pattern": r"^import\s+\{[^}]*\}",
        "severity": "low",
        "message": "可能存在未使用的导入，建议清理",
    },
}


@dataclass
class Issue:
    file_path: str
    line_number: int
    rule_id: str
    severity: str
    message: str
    code_snippet: str
    fix_suggestion: str = ""


class ScannerAgent:
    """扫描 Agent：逐文件扫描代码仓库，输出结构化问题清单"""

    def __init__(self, target_dir: str):
        self.target_dir = Path(target_dir)
        self.issues: list[Issue] = []

    def scan(self) -> str:
        """执行扫描并返回 JSON 格式的问题清单"""
        for file_path in self.target_dir.rglob("*.py"):
            if "__pycache__" in str(file_path):
                continue
            self._scan_file(file_path)

        self.issues.sort(
            key=lambda i: {"critical": 0, "high": 1, "medium": 2, "low": 3}[i.severity]
        )
        return json.dumps(
            {
                "agent": "ScannerAgent",
                "summary": {
                    "total_files_scanned": self._count_files(),
                    "total_issues": len(self.issues),
                    "by_severity": self._count_by_severity(),
                },
                "issues": [asdict(i) for i in self.issues],
            },
            ensure_ascii=False,
            indent=2,
        )

    def _scan_file(self, file_path: Path):
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return
        for line_no, line in enumerate(content.splitlines(), 1):
            for rule_id, rule in RULES.items():
                match = re.search(rule["pattern"], line)
                if match:
                    self.issues.append(
                        Issue(
                            file_path=str(file_path.relative_to(self.target_dir)),
                            line_number=line_no,
                            rule_id=rule_id,
                            severity=rule["severity"],
                            message=rule["message"],
                            code_snippet=line.strip()[:120],
                            fix_suggestion=self._suggest_fix(rule_id, match),
                        )
                    )

    def _suggest_fix(self, rule_id: str, match: re.Match) -> str:
        suggestions = {
            "deprecated-api": "替换为最新 API 调用方式",
            "naming-convention": "重命名为小驼峰风格，如 camelCase",
            "circular-dependency": "提取公共依赖到独立模块",
            "missing-error-handling": "使用 try-catch 包裹异步调用",
            "hardcoded-secret": "改用环境变量或密钥管理服务",
            "unused-import": "移除未使用的导入项",
        }
        return suggestions.get(rule_id, "请人工审查")

    def _count_files(self) -> int:
        return sum(1 for _ in self.target_dir.rglob("*.py") if "__pycache__" not in str(_))

    def _count_by_severity(self) -> dict:
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for i in self.issues:
            counts[i.severity] += 1
        return counts
