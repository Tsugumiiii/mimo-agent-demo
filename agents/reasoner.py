"""
推理 Agent —— 接收 Scanner 输出，进行长链推理分析，
生成带优先级的修复计划。
"""
import json
from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class FixPlan:
    issue_id: int
    file_path: str
    severity: str
    root_cause: str
    impact_scope: str
    risk_level: str
    priority: int
    suggested_action: str
    estimated_effort: str


class ReasonerAgent:
    """推理 Agent：多步链式推理，分析根因、影响面、优先级"""

    def analyze(self, scanner_output: str) -> str:
        data = json.loads(scanner_output)
        issues = data.get("issues", [])
        fix_plans: list[FixPlan] = []

        for idx, issue in enumerate(issues):
            root_cause = self._diagnose_root_cause(issue)
            impact = self._assess_impact(issue)
            risk = self._evaluate_risk(issue, impact)
            priority = self._calculate_priority(issue, risk)

            fix_plans.append(
                FixPlan(
                    issue_id=idx + 1,
                    file_path=issue["file_path"],
                    severity=issue["severity"],
                    root_cause=root_cause,
                    impact_scope=impact,
                    risk_level=risk,
                    priority=priority,
                    suggested_action=self._generate_action(issue),
                    estimated_effort=self._estimate_effort(issue),
                )
            )

        fix_plans.sort(key=lambda p: (-p.priority, p.risk_level))

        return json.dumps(
            {
                "agent": "ReasonerAgent",
                "reasoning_chain": "Scanner输出 → 根因诊断 → 影响面评估 → 风险评级 → 优先级排序",
                "summary": {
                    "total_issues": len(fix_plans),
                    "auto_fixable": sum(1 for p in fix_plans if p.risk_level == "low"),
                    "needs_review": sum(1 for p in fix_plans if p.risk_level != "low"),
                },
                "fix_plan": [asdict(p) for p in fix_plans],
            },
            ensure_ascii=False,
            indent=2,
        )

    def _diagnose_root_cause(self, issue: dict) -> str:
        causes = {
            "deprecated-api": "历史遗留 —— 框架升级后未同步迁移旧 API 调用",
            "naming-convention": "规范意识不足 —— 开发者未遵循团队编码规范",
            "circular-dependency": "架构退化 —— 模块边界模糊，职责未分离",
            "missing-error-handling": "历史累积 —— 快速迭代中忽略了错误处理",
            "hardcoded-secret": "安全意识薄弱 —— 开发阶段临时写入后未移除",
            "unused-import": "重构遗漏 —— 删除功能时未同步清理导入",
        }
        return causes.get(issue["rule_id"], "需进一步排查")

    def _assess_impact(self, issue: dict) -> str:
        severity_map = {
            "critical": "影响安全性和系统稳定性，需立即处理",
            "high": "影响代码可维护性，可能引发运行时错误",
            "medium": "影响代码质量，降低可读性和健壮性",
            "low": "影响代码风格一致性，无运行时影响",
        }
        return severity_map.get(issue["severity"], "待评估")

    def _evaluate_risk(self, issue: dict, impact: str) -> str:
        if issue["severity"] in ("critical", "high"):
            return "high"
        elif "循环依赖" in issue.get("message", ""):
            return "medium"
        return "low"

    def _calculate_priority(self, issue: dict, risk: str) -> int:
        base = {"critical": 10, "high": 7, "medium": 4, "low": 1}
        risk_bonus = {"high": 3, "medium": 1, "low": 0}
        return base.get(issue["severity"], 1) + risk_bonus.get(risk, 0)

    def _generate_action(self, issue: dict) -> str:
        actions = {
            "deprecated-api": "查阅最新 API 文档，替换为推荐写法，补充单元测试",
            "naming-convention": "使用 IDE 重命名功能批量修正，确保引用同步更新",
            "circular-dependency": "提取共享接口到独立模块，解除双向引用",
            "missing-error-handling": "添加 try-catch 块，统一错误日志格式",
            "hardcoded-secret": "迁移到环境变量 / Vault，清理 Git 历史",
            "unused-import": "运行 auto-import 清理工具，删除未使用导入",
        }
        return actions.get(issue["rule_id"], "分配工程师人工处理")

    def _estimate_effort(self, issue: dict) -> str:
        effort = {"critical": "2-4h", "high": "1-2h", "medium": "30min-1h", "low": "5-15min"}
        return effort.get(issue["severity"], "未知")
