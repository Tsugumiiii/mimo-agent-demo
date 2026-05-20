"""
多 Agent 协作编排器 —— 串联 Scanner → Reasoner → Arbiter → Executor
完整工作流，实现代码质量自动化治理。
"""
import json
import time
from datetime import datetime

from agents.scanner import ScannerAgent
from agents.reasoner import ReasonerAgent
from agents.executor import ExecutorAgent
from agents.arbiter import ArbiterAgent


class Orchestrator:
    """多 Agent 编排器：管理 Agent 间消息传递和工作流编排"""

    def __init__(self, target_dir: str = "."):
        self.target_dir = target_dir
        self.scanner = ScannerAgent(target_dir)
        self.reasoner = ReasonerAgent()
        self.arbiter = ArbiterAgent()
        self.executor = ExecutorAgent()
        self.workflow_log: list[dict] = []

    def run(self) -> dict:
        print("=" * 68)
        print("  多 Agent 代码质量自动化治理系统")
        print("  Multi-Agent Code Governance System v1.0")
        print("=" * 68)

        # Phase 1: 扫描
        self._log("Phase 1/4: Scanner Agent 启动 — 扫描代码仓库")
        t0 = time.time()
        scan_result = self.scanner.scan()
        scan_data = json.loads(scan_result)
        scan_time = time.time() - t0
        self._log(
            f"  扫描完成 ({scan_time:.2f}s): "
            f"遍历 {scan_data['summary']['total_files_scanned']} 个文件, "
            f"发现 {scan_data['summary']['total_issues']} 个问题"
        )
        self._log(
            f"  严重性分布: {json.dumps(scan_data['summary']['by_severity'], ensure_ascii=False)}"
        )

        # Phase 2: 推理
        self._log("\nPhase 2/4: Reasoner Agent 启动 — 长链推理分析")
        t0 = time.time()
        reasoner_result = self.reasoner.analyze(scan_result)
        reasoner_data = json.loads(reasoner_result)
        reasoner_time = time.time() - t0
        self._log(
            f"  推理完成 ({reasoner_time:.2f}s): "
            f"推理链路: {reasoner_data['reasoning_chain']}"
        )
        self._log(
            f"  可自动修复: {reasoner_data['summary']['auto_fixable']}, "
            f"需人工审查: {reasoner_data['summary']['needs_review']}"
        )

        # Phase 3: 仲裁
        self._log("\nPhase 3/4: Arbiter Agent 启动 — 冲突检测与仲裁")
        t0 = time.time()
        arbiter_result = self.arbiter.resolve(reasoner_result)
        arbiter_data = json.loads(arbiter_result)
        arbiter_time = time.time() - t0
        self._log(f"  仲裁完成 ({arbiter_time:.2f}s): {arbiter_data['message']}")

        # Phase 4: 执行
        self._log("\nPhase 4/4: Executor Agent 启动 — 执行修复与验证")
        t0 = time.time()
        executor_result = self.executor.execute(reasoner_result)
        executor_data = json.loads(executor_result)
        executor_time = time.time() - t0
        self._log(
            f"  执行完成 ({executor_time:.2f}s): "
            f"成功 {executor_data['summary']['success']}, "
            f"失败 {executor_data['summary']['failed']}, "
            f"跳过 {executor_data['summary']['skipped']}"
        )
        self._log(f"  自动修复率: {executor_data['summary']['auto_fix_rate']}")

        # 汇总
        total_time = scan_time + reasoner_time + arbiter_time + executor_time
        self._log(f"\n{'=' * 68}")
        self._log(f"  全流程完成，总耗时: {total_time:.2f}s")
        self._log(f"  预估 Token 消耗: ~{self._estimate_tokens():,}")
        self._log(f"  完成时间: {datetime.now().isoformat()}")
        self._log(f"{'=' * 68}")

        return {
            "scan": json.loads(scan_result),
            "reasoner": reasoner_data,
            "arbiter": arbiter_data,
            "executor": executor_data,
            "meta": {
                "total_time_s": total_time,
                "estimated_tokens": self._estimate_tokens(),
                "timestamp": datetime.now().isoformat(),
            },
        }

    def _log(self, msg: str):
        print(f"  {msg}")
        self.workflow_log.append({"msg": msg})

    def _estimate_tokens(self) -> int:
        stats = self.scanner._count_by_severity()
        total = sum(stats.values())
        return total * 15000 + 50000


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "."
    orch = Orchestrator(target)
    result = orch.run()

    # 保存完整报告
    output_path = "governance-report.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n完整报告已保存至: {output_path}")
