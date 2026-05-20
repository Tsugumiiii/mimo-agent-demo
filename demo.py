"""
演示脚本 —— 创建模拟代码库并运行完整的 4-Agent 工作流，
生成可以直接截图提交的终端输出。
"""
import os
import sys
import tempfile
from pathlib import Path


def create_demo_codebase(base_dir: str):
    """创建一个包含典型代码问题的模拟代码库"""
    files = {
        "src/auth/login.py": '''
import os
from typing import Optional
import { something }
import { unused_thing }

api_key = "sk-1234567890abcdef1234567890abcdef"

class UserAuth:
    def login(self, username, password):
        result = self._validate(username, password).subscribe()
        return result

    async def refresh_token(self):
        token = await self._fetch_new_token()
        return token

    async def logout(self):
        result = await self._invalidate_session()

    def _validate(self, username, password):
        secret = "my-secret-key-12345"
        return True
''',
        "src/services/payment.py": '''
from ..models.order import Order
from ..auth.login import UserAuth
import requests

class PaymentService:
    def process(self, order_id):
        order = Order.find(order_id).toPromise()
        result = self._charge(order)
        return result

    def _charge(self, order):
        password = "payment-gateway-secret-98765"
        return {"status": "ok"}

    def refund(self, order_id):
        resp = requests.post("https://api.payment.com/refund")
        return resp.json()
''',
        "src/utils/helpers.py": '''
import re
import json
from typing import Any, Dict

def format_response(data, FormatType):
    result = json.dumps(data)
    return result

def parse_input(raw_input):
    import { heavy_lib }
    return raw_input.strip()

def fetch_user_data(user_id):
    resp = requests.get(f"https://api.example.com/users/{user_id}")
    return resp.json()

class data_processor:
    def process(self, items):
        return [item.upper() for item in items]

class user_repository:
    def find_by_email(self, email):
        token = "ghp_abc123def456ghi789jkl012mno345pqr678"
        return None
''',
        "src/models/order.py": '''
from ..services.payment import PaymentService

class Order:
    def __init__(self, order_id):
        self.id = order_id

    @staticmethod
    def find(order_id):
        return Order(order_id)

    def process_payment(self):
        service = PaymentService()
        result = service.process(self.id).subscribe()
        return result

    def cancel(self):
        self.process_payment().waitFor("cancelled")
''',
        "tests/test_auth.py": '''
from src.auth.login import UserAuth

def test_login():
    auth = UserAuth()
    result = auth.login("user", "pass")
    assert result is True
''',
    }

    for filepath, content in files.items():
        full_path = Path(base_dir) / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
        print(f"  创建: {filepath}")

    print(f"  已创建 {len(files)} 个文件，包含 15+ 预设代码问题\n")


def main():
    print("=" * 68)
    print("  MiMo Token Plan 申请演示")
    print("  多 Agent 代码质量自动化治理系统")
    print("=" * 68)
    print()

    # 创建临时代码库
    demo_dir = tempfile.mkdtemp(prefix="mimo-demo-")
    print(f"[1] 创建模拟代码库: {demo_dir}")
    create_demo_codebase(demo_dir)

    # 运行多 Agent 编排器
    print("[2] 启动多 Agent 协作工作流\n")

    # 添加当前目录到 path 以确保导入正常
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    from orchestrator import Orchestrator

    orch = Orchestrator(demo_dir)
    result = orch.run()

    # 输出适合截图的摘要
    print("\n")
    print("*" * 68)
    print("  成果总结")
    print("*" * 68)
    scan = result["scan"]["summary"]
    exec_s = result["executor"]["summary"]
    print(f"  扫描文件数:    {scan['total_files_scanned']}")
    print(f"  发现问题数:    {scan['total_issues']}")
    print(f"  自动修复成功:  {exec_s['success']}")
    print(f"  自动修复失败:  {exec_s['failed']}")
    print(f"  跳过(需人工):  {exec_s['skipped']}")
    print(f"  自动修复率:    {exec_s['auto_fix_rate']}")
    print(f"  预估 Token 消耗: ~{result['meta']['estimated_tokens']:,}")
    print(f"  总耗时:        {result['meta']['total_time_s']:.2f}s")
    print("*" * 68)
    print()
    print("  可用证据材料:")
    print(f"    1. 终端运行日志（上方输出）")
    print(f"    2. 完整治理报告: governance-report.json")
    print(f"    3. 项目源码: {os.path.dirname(os.path.abspath(__file__))}")
    print()

    # 清理
    import shutil
    shutil.rmtree(demo_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
