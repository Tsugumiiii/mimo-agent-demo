# Multi-Agent Code Governance System

多 Agent 协作的代码质量自动化治理系统 —— 用于 MiMo Token Plan 申请的技术演示项目。

## 架构概览

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐
│  Scanner    │────▶│  Reasoner    │────▶│  Arbiter    │────▶│  Executor   │
│  Agent      │     │  Agent       │     │  Agent      │     │  Agent      │
│  代码扫描    │     │  长链推理     │     │  冲突仲裁    │     │  执行修复    │
└─────────────┘     └──────────────┘     └─────────────┘     └─────────────┘
       │                    │                    │                   │
       ▼                    ▼                    ▼                   ▼
  结构化问题清单        带优先级的            冲突已解决          成功/失败/
  (JSON)               修复计划             的修复方案           回退报告
                         │                    │                   │
                         └────────────────────┴───────────────────┘
                                          │
                                          ▼
                                   人机协同检查点
                                  （高风险项人工Review）
```

## Agent 职责

| Agent | 职责 | 输入 | 输出 |
|-------|------|------|------|
| **Scanner** | 遍历代码仓库，基于规则库扫描问题 | 代码仓库路径 | 结构化问题清单 (JSON) |
| **Reasoner** | 多步长链推理：根因诊断 → 影响面评估 → 风险评级 → 优先级排序 | Scanner 输出 | 带优先级的修复计划 |
| **Arbiter** | 检测修复方案冲突，做出最优决策 | Reasoner 输出 | 冲突仲裁结果 |
| **Executor** | 执行修复、自动生成 PR、运行测试验证、失败回退 | Reasoner + Arbiter 输出 | 执行结果报告 |

## 规则库

- `deprecated-api` — 检测废弃 API 调用 (`.subscribe()`, `.toPromise()`)
- `hardcoded-secret` — 检测硬编码密钥/密码
- `circular-dependency` — 检测潜在循环依赖
- `missing-error-handling` — 检测缺少错误处理的异步调用
- `naming-convention` — 检测命名规范问题
- `unused-import` — 检测未使用的导入

## 快速运行

```bash
# 运行演示（自动创建包含 15+ 问题的模拟代码库）
python demo.py

# 扫描指定目录
python orchestrator.py /path/to/your/project
```

## 预期输出

```
====================================================================
  多 Agent 代码质量自动化治理系统
  Multi-Agent Code Governance System v1.0
====================================================================
  Phase 1/4: Scanner Agent 启动 — 扫描代码仓库
    扫描完成 (0.03s): 遍历 5 个文件, 发现 15 个问题
    严重性分布: {"critical": 3, "high": 4, "medium": 3, "low": 5}
  Phase 2/4: Reasoner Agent 启动 — 长链推理分析
    推理完成 (0.01s): 推理链路: Scanner输出 → 根因诊断 → 影响面评估 → 风险评级 → 优先级排序
    可自动修复: 5, 需人工审查: 10
  Phase 3/4: Arbiter Agent 启动 — 冲突检测与仲裁
    仲裁完成 (0.00s): 检测到 2 个冲突，已全部仲裁完毕
  Phase 4/4: Executor Agent 启动 — 执行修复与验证
    执行完成 (0.01s): 成功 6, 失败 1, 跳过 8
    自动修复率: 40.0%
====================================================================
  全流程完成，总耗时: 0.06s
  预估 Token 消耗: ~275,000
====================================================================
```

## 技术栈

- Python 3.9+
- Claude Agent SDK (via Claude Code)
- 多 Agent 编排模式 (消息队列 + 人机协同检查点)

## License

MIT
