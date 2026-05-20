"""
执行 Agent —— 按修复计划执行代码变更，
生成 Git 分支和 PR 摘要，运行验证。
"""
import json
from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class ExecutionResult:
    issue_id: int
    file_path: str
    status: str  # success / failed / skipped
    action_taken: str
    pr_branch: str = ""
    test_result: str = ""
    rollback_reason: str = ""


class ExecutorAgent:
    """执行 Agent：逐条执行修复，自动验证，失败回退"""

    def __init__(self):
        self.results: list[ExecutionResult] = []
        self.pr_counter = 0

    def execute(self, reasoner_output: str) -> str:
        data = json.loads(reasoner_output)
        fix_plan = data.get("fix_plan", [])

        for plan in fix_plan:
            result = self._execute_fix(plan)
            self.results.append(result)

        success_count = sum(1 for r in self.results if r.status == "success")
        failed_count = sum(1 for r in self.results if r.status == "failed")
        skipped_count = sum(1 for r in self.results if r.status == "skipped")

        return json.dumps(
            {
                "agent": "ExecutorAgent",
                "summary": {
                    "total": len(self.results),
                    "success": success_count,
                    "failed": failed_count,
                    "skipped": skipped_count,
                    "auto_fix_rate": f"{success_count / max(len(self.results), 1) * 100:.1f}%",
                },
                "results": [asdict(r) for r in self.results],
            },
            ensure_ascii=False,
            indent=2,
        )

    def _execute_fix(self, plan: dict) -> ExecutionResult:
        risk = plan.get("risk_level", "low")

        if risk == "high":
            return ExecutionResult(
                issue_id=plan["issue_id"],
                file_path=plan["file_path"],
                status="skipped",
                action_taken="高风险项暂停自动处理，已生成 PR 等待人工 Review",
                pr_branch=f"fix/high-risk-{plan['issue_id']:03d}",
                test_result="N/A",
                rollback_reason="需人工确认修复方案",
            )

        self.pr_counter += 1
        pr_branch = f"fix/auto-{plan['issue_id']:03d}-{plan['file_path'].replace('/', '-').replace('.py', '')}"

        # 模拟验证：低风险项 90% 成功率，中风险 75%
        import random

        random.seed(plan["issue_id"])
        success = random.random() < (0.9 if risk == "low" else 0.75)

        if success:
            return ExecutionResult(
                issue_id=plan["issue_id"],
                file_path=plan["file_path"],
                status="success",
                action_taken=plan["suggested_action"],
                pr_branch=pr_branch,
                test_result="ESLint ✅ | Unit Tests ✅ | Coverage 不变",
                rollback_reason="",
            )
        else:
            return ExecutionResult(
                issue_id=plan["issue_id"],
                file_path=plan["file_path"],
                status="failed",
                action_taken=plan["suggested_action"],
                pr_branch=pr_branch,
                test_result="ESLint ✅ | Unit Tests ❌ (2/15 failed)",
                rollback_reason="修复导致回归测试失败，已自动回退并重新推理",
            )
