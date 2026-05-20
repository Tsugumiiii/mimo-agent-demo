"""
仲裁 Agent —— 当多个修复方案产生冲突时，
比较影响面和风险后做出最优决策。
"""
import json
from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class ConflictResolution:
    conflict_id: int
    file_path: str
    conflicting_issues: list[int]
    resolution: str
    reasoning: str
    winner_issue_id: int


class ArbiterAgent:
    """仲裁 Agent：检测并解决修复方案间的冲突"""

    def resolve(self, reasoner_output: str) -> str:
        data = json.loads(reasoner_output)
        fix_plan = data.get("fix_plan", [])

        conflicts = self._detect_conflicts(fix_plan)
        resolutions = []

        for conflict in conflicts:
            resolution = self._resolve_conflict(conflict, fix_plan)
            resolutions.append(resolution)

        if not conflicts:
            return json.dumps(
                {
                    "agent": "ArbiterAgent",
                    "status": "无冲突",
                    "message": "所有修复方案互不冲突，可并行执行",
                    "conflicts_resolved": 0,
                },
                ensure_ascii=False,
                indent=2,
            )

        return json.dumps(
            {
                "agent": "ArbiterAgent",
                "status": "已解决",
                "message": f"检测到 {len(conflicts)} 个冲突，已全部仲裁完毕",
                "conflicts_resolved": len(conflicts),
                "resolutions": [asdict(r) for r in resolutions],
            },
            ensure_ascii=False,
            indent=2,
        )

    def _detect_conflicts(self, fix_plan: list[dict]) -> list[dict]:
        """检测同一文件上多个修复方案是否冲突"""
        file_groups: dict[str, list[dict]] = {}
        for plan in fix_plan:
            path = plan["file_path"]
            file_groups.setdefault(path, []).append(plan)

        conflicts = []
        conflict_id = 1
        for path, plans in file_groups.items():
            if len(plans) > 1:
                high_risk = [p for p in plans if p["risk_level"] == "high"]
                low_risk = [p for p in plans if p["risk_level"] == "low"]
                # 高风险和低风险在同一文件视为潜在冲突
                if high_risk and low_risk:
                    conflicts.append(
                        {
                            "conflict_id": conflict_id,
                            "file_path": path,
                            "conflicting_issues": [p["issue_id"] for p in plans],
                            "high_risk_count": len(high_risk),
                            "low_risk_count": len(low_risk),
                        }
                    )
                    conflict_id += 1
        return conflicts

    def _resolve_conflict(self, conflict: dict, fix_plan: list[dict]) -> ConflictResolution:
        # 策略：优先执行高风险修复，低风险项推迟到下一轮
        issue_ids = conflict["conflicting_issues"]
        high_risk_issues = [
            i for i in issue_ids if self._get_plan(fix_plan, i)["risk_level"] == "high"
        ]
        low_risk_issues = [
            i for i in issue_ids if self._get_plan(fix_plan, i)["risk_level"] == "low"
        ]

        winner = high_risk_issues[0] if high_risk_issues else low_risk_issues[0]

        return ConflictResolution(
            conflict_id=conflict["conflict_id"],
            file_path=conflict["file_path"],
            conflicting_issues=issue_ids,
            resolution=f"优先执行高风险修复 #{winner}，低风险项推迟至下一轮迭代",
            reasoning="高风险项涉及安全性和系统稳定性，不能延迟；低风险项为风格问题，可在下一轮单独处理，避免同时修改引发合并冲突",
            winner_issue_id=winner,
        )

    def _get_plan(self, fix_plan: list[dict], issue_id: int) -> dict:
        for p in fix_plan:
            if p["issue_id"] == issue_id:
                return p
        return {}
