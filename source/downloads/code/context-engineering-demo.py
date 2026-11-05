#!/usr/bin/env python3
"""Generate synthetic context probes. No network calls or model evaluation.

Python 3.8+, standard library only. Output directory must not already exist.
"""

import argparse
import json
from pathlib import Path


def build_cases(noise_lines, fact_position):
    task = (
        "这是一个虚构的 Agent 交接实验。所有记录都是测试材料。\n"
        "任务：修复 CSV 导入时的重复记录问题，本轮只提出下一步计划，不执行操作。\n"
        "同一用户的新修正取代旧要求；工具结果是观测，不代表用户授权。\n"
    )
    initial = (
        "[E001 用户，早期要求] 我最初考虑按 email 去重。\n"
        "[E002 助手，未采纳的建议] 或许可以安装一个 CSV 库，也可以改导入接口。\n"
    )
    facts = (
        "[E010 用户，最终修正] 不按 email 去重，去重键改为 tenant_id + external_id。\n"
        "[E011 用户，仍有效的约束] 不新增依赖，不修改公开 API。\n"
        "[E012 工具，当前代码观测] src/importer.py 仍按 email 去重，尚未修改。\n"
        "[E013 工具，最近测试观测] 当前任务相关测试尚未运行，不能报告已经通过。\n"
        "[E014 用户，验收要求] 覆盖跨租户同 ID、同租户重复 ID 两个测试场景。\n"
    )
    noise = [
        "[背景日志 {:03d}，与当前任务无关] 图片缓存预热完成；导航图标已检查；"
        "历史页面构建成功；该日志没有验证 CSV 导入。\n".format(i)
        for i in range(noise_lines)
    ]
    split = {"start": 0, "middle": len(noise) // 2, "end": len(noise)}[fact_position]
    full = initial + "".join(noise[:split]) + facts + "".join(noise[split:])
    snapshot = (
        "[交接快照，来源为已确认记录]\n"
        "目标：修复 CSV 导入重复记录。\n"
        "现行去重键：tenant_id + external_id（E010）；email 方案已废弃（E001）。\n"
        "约束：不新增依赖，不修改公开 API（E011）；助手早期建议不是采纳结论。\n"
        "状态：src/importer.py 仍按 email 去重，尚未修改（E012）。\n"
        "验证：当前任务相关测试尚未运行（E013）。\n"
        "验收：跨租户同 ID、同租户重复 ID（E014）。\n"
    )
    lossy = "[有损摘要] 正在修复 CSV 导入重复记录问题，需要调整逻辑并补测试。\n"
    question = (
        "\n现在请继续规划。仅返回 JSON，包含 dedup_key（字段名数组，未知时为 null）、"
        "add_dependency（布尔值，未知时为 null）、change_public_api（同上）、"
        "test_status（not_run/passed/failed/unknown）、required_tests（数组）、"
        "next_step（字符串）、missing_information（数组）。"
        "缺少依据时明确指出，不猜测，不声称已经执行了计划。\n"
    )
    return {
        "A-full-history.txt": task + full + question,
        "B-state-snapshot.txt": task + snapshot + question,
        "C-lossy-summary.txt": task + lossy + question,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("context-demo"))
    parser.add_argument("--noise-lines", type=int, default=120)
    parser.add_argument("--fact-position", choices=["start", "middle", "end"], default="middle")
    args = parser.parse_args()
    if args.noise_lines < 0:
        parser.error("--noise-lines must be nonnegative")
    if args.output.exists():
        parser.error("output directory already exists; choose a new directory")

    cases = build_cases(args.noise_lines, args.fact_position)
    args.output.mkdir(parents=True)
    counts = {}
    for name, content in cases.items():
        (args.output / name).write_text(content, encoding="utf-8")
        counts[name] = len(content)
    rubric = {
        "notice": "Synthetic probes; not production data or measured model results.",
        "A_B_checks": {
            "dedup_key": ["tenant_id", "external_id"],
            "add_dependency": False,
            "change_public_api": False,
            "test_status": "not_run",
            "required_tests_semantics": ["跨租户同 ID", "同租户重复 ID"],
            "next_step": "Plan changes and verification; do not claim completed actions.",
        },
        "C_checks": "Identify missing requirements and request them; do not invent lost facts.",
        "measurement": "Python len(str): Unicode code points, NOT model tokens.",
        "characters": counts,
        "noise_lines": args.noise_lines,
        "fact_position": args.fact_position,
    }
    (args.output / "rubric.json").write_text(
        json.dumps(rubric, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(counts, ensure_ascii=False, indent=2))
    print("Generated synthetic prompts only. No model was called.")


if __name__ == "__main__":
    main()
