#!/usr/bin/env python3
"""
批量评分脚本：对已生成的 financial、healthcare、insurance 对话数据进行评分
使用客服型 Benchmark（所有三个场景的 bench_key 都是 customerservice）
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# 导入必要的库和函数
sys.path.insert(0, str(Path(__file__).parent))

from run_pipeline import (
    SCENE_CONFIG,
    init_clients,
    generate_report,
    print_report_summary,
    save_outputs,
    RETRY_LIMIT,
    RETRY_DELAY,
    safe_parse_json,
)
import google.generativeai as genai


def evaluate_industry_scenes(eval_client, dialogs: list, scene_type: str, no_debias: bool = False) -> list:
    """
    为 financial、healthcare、insurance 场景评分
    这些场景使用 customerservice 的评分标准
    """
    from benchmarks.scene_specific_bench import get_scene_system_prompt, get_scene_benchmark, OUTPUT_FORMAT
    
    # 确定用于评分的 bench_key
    bench_scene = SCENE_CONFIG[scene_type]["bench_key"]
    
    total = len(dialogs)
    results = []
    
    print(f"\n{'='*60}")
    print(f"Step 2  Benchmark 评分（模型：Gemini）")
    print(f"场景: {SCENE_CONFIG[scene_type]['label']}")
    print(f"评分标准: {SCENE_CONFIG[bench_scene]['label']}")
    print(f"待评分: {total} 条对话")
    print(f"{'='*60}\n")
    
    # 获取评分标准（基于 bench_scene）
    if no_debias:
        from benchmarks.no_debias_bench import get_no_debias_prompt
        system_instr = get_no_debias_prompt(bench_scene)
        dim_names = []
    else:
        dims = get_scene_benchmark(bench_scene)
        dim_names = list(dims.keys())
        system_instr = get_scene_system_prompt(bench_scene)
    
    for i, d in enumerate(dialogs):
        print(f"  [{i+1}/{total}] 评分: {d['scene_type']} x {d['type']} x {d['scenario_key']}")
        
        # 获取场景标签和状态标签（从原始 scene_type）
        cfg = SCENE_CONFIG[scene_type]
        scene_label = cfg["scenes"][d["scenario_key"]]["name"]
        state_info = cfg["states"][d["state_key"]]
        state_label = state_info["name"] if isinstance(state_info, dict) else str(state_info)
        
        # 构建评分提示
        dim_schema = "\n".join([f'    "{d}": {{"score": 0或1或2, "reason": "不超过25字"}}' for d in dim_names])
        
        user_content = f"""待评估对话（{d['type']}）：
场景：{scene_label} | 状态：{state_label}

{d['dialog']}

{OUTPUT_FORMAT}
维度列表（只评这些维度，key名称必须完全一致）：
{{
  "dimensions": {{
{dim_schema}
  }},
  "overall": 0或1或2,
  "veto": true或false,
  "veto_reason": "触发了哪个维度的Veto，未触发写null",
  "summary": "2句总评不超过50字"
}}"""
        
        # 调用 Gemini 进行评分
        for attempt in range(RETRY_LIMIT):
            try:
                response = eval_client.generate_content(
                    f"{system_instr}\n\n{user_content}",
                    generation_config=genai.types.GenerationConfig(temperature=0.1),
                )
                raw = response.text
                eval_result = safe_parse_json(raw)
                break
            except Exception as e:
                if attempt < RETRY_LIMIT - 1:
                    print(f"    [重试 {attempt+1}/{RETRY_LIMIT}] Gemini 评分失败: {e}")
                    time.sleep(RETRY_DELAY)
                else:
                    eval_result = {
                        "dimensions": {},
                        "overall": -1,
                        "veto": False,
                        "veto_reason": None,
                        "summary": f"评分失败: {e}",
                        "_eval_error": True,
                    }
        
        entry = {**d, "eval": eval_result}
        results.append(entry)
        
        overall = eval_result.get("overall", "?")
        veto = "⚡Veto" if eval_result.get("veto") else ""
        fallback = " [解析降级]" if eval_result.get("_parse_fallback") else ""
        error = " [评分失败]" if eval_result.get("_eval_error") else ""
        print(f"    ✓ 总分 {overall}/2  {veto}{fallback}{error}")
        
        time.sleep(1.5)  # Gemini 速率限制
    
    success = sum(1 for r in results if not r["eval"].get("_eval_error"))
    print(f"\n✓ 评分完成: {success}/{total} 条成功\n")
    return results


def main():
    """主函数：对三个场景的数据进行评分"""
    
    # 需要评分的三个场景及其输入文件
    scenes_to_eval = [
        ("financial", "outputs/financial_20260408_234804_dialogs_only.json"),
        ("healthcare", "outputs/healthcare_20260408_031704_dialogs_only.json"),
        ("insurance", "outputs/insurance_all_dialogs.json"),
    ]
    
    # 初始化客户端
    print("初始化 API 客户端...")
    gen_client, eval_client = init_clients()
    
    # 对每个场景进行评分
    for scene_type, input_file in scenes_to_eval:
        input_path = Path(input_file)
        
        if not input_path.exists():
            print(f"\n⚠️  文件不存在: {input_file}，跳过")
            continue
        
        print(f"\n{'='*70}")
        print(f"评分场景: {SCENE_CONFIG[scene_type]['label']} ({scene_type})")
        print(f"输入文件: {input_file}")
        print(f"{'='*70}")
        
        # 读取对话数据
        with open(input_path, 'r', encoding='utf-8') as f:
            dialogs = json.load(f)
        
        print(f"已加载 {len(dialogs)} 条对话")
        
        # 执行评分
        results = evaluate_industry_scenes(eval_client, dialogs, scene_type, no_debias=False)
        
        # 生成报告
        report = generate_report(results, scene_type, no_debias=False)
        
        # 打印摘要
        print_report_summary(report)
        
        # 保存输出
        full_path, summary_path = save_outputs(report, scene_type)
        
        print(f"\n✓ {scene_type} 评分完成")
    
    print(f"\n{'='*70}")
    print("所有场景评分完成！")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
