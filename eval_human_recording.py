#!/usr/bin/env python3
"""
eval_human_recording.py
评测真人录音数据，支持 ASR 矫正版和未矫正版
用法：
  python eval_human_recording.py --input outputs/human_corrected.json --tag corrected
  python eval_human_recording.py --input outputs/human_uncorrected.json --tag uncorrected
"""
import os, json, time, argparse, re, sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai
sys.path.insert(0, str(Path(__file__).parent))
from benchmarks.scene_specific_bench import get_scene_benchmark, get_scene_system_prompt, OUTPUT_FORMAT

GEMINI_MODEL = "models/gemini-3-flash-preview"
RETRY_LIMIT = 3
RETRY_DELAY = 5
OUTPUT_DIR = Path("outputs")

def safe_parse_json(raw: str) -> dict:
    text = re.sub(r"```json\s*", "", raw).replace("```", "").strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    overall_m = re.search(r'"overall"\s*:\s*(\d)', text)
    veto_m = re.search(r'"veto"\s*:\s*(true|false)', text)
    return {
        "dimensions": {}, "overall": int(overall_m.group(1)) if overall_m else 1,
        "veto": veto_m.group(1) == "true" if veto_m else False,
        "veto_reason": None, "summary": "解析异常", "_parse_fallback": True,
    }

def get_no_debias_system_prompt(bench_type: str) -> str:
    """无去偏版本：保留维度结构，去掉所有偏见压制指令、Veto机制、惩罚规则"""
    prompts = {
        "notification": """你是客服话术质检专家，请对以下通知型外呼对话中客服的回复评分。

评分标准：评估回复是否清晰传达了通知内容、表达是否自然、与客户互动是否流畅。
对每个维度打分（0-2分）：2=优秀，1=一般，0=较差。
只输出JSON，不要其他文字，reason不超过25字。""",

        "customerservice": """你是客服话术质检专家，请对以下客服型外呼对话中客服的回复评分。

评分标准：评估回复是否清晰解答客户问题、表达是否自然流畅、互动是否得当。
对每个维度打分（0-2分）：2=优秀，1=一般，0=较差。
只输出JSON，不要其他文字，reason不超过25字。""",

        "sales": """你是销售话术质检专家，请对以下销售型外呼对话中销售的回复评分。

评分标准：评估回复是否专业有效、表达是否自然、销售策略是否得当。
对每个维度打分（0-2分）：2=优秀，1=一般，0=较差。
只输出JSON，不要其他文字，reason不超过25字。""",

        "returnvisit": """你是客服话术质检专家，请对以下回访型外呼对话中客服的回复评分。

评分标准：评估回复是否有效收集反馈、表达是否自然、对客户信号的识别是否准确。
对每个维度打分（0-2分）：2=优秀，1=一般，0=较差。
只输出JSON，不要其他文字，reason不超过25字。""",
    }
    return prompts.get(bench_type, prompts["customerservice"])

def evaluate_one(client, record: dict, no_debias: bool = False) -> dict:
    bench_type = record["bench_type"]
    dims = get_scene_benchmark(bench_type)
    dim_names = list(dims.keys())
    system_instr = get_no_debias_system_prompt(bench_type) if no_debias else get_scene_system_prompt(bench_type)
    
    dim_schema = "\n".join([
        f'    "{d}": {{"score": 0或1或2, "reason": "不超过25字"}}'
        for d in dim_names
    ])
    
    # 评分用完整对话（含上下文），但说明只对客服部分评分
    user_content = f"""待评估对话（真人录音·{record.get("asr_type","corrected")}）：
行业：{record["industry"]} | 场景：{record["scene_type"]} | 细分：{record["scenario_name"]}

完整对话（含上下文）：
{record["dialog"]}

注意：只对上面对话中【客服/销售】说的部分进行评分，客户/豆包扮演的部分不评分。

{OUTPUT_FORMAT}
维度列表：
{{
  "dimensions": {{
{dim_schema}
  }},
  "overall": 0或1或2,
  "veto": true或false,
  "veto_reason": "触发了哪个维度的Veto，未触发写null",
  "summary": "2句总评不超过50字"
}}"""

    full_prompt = f"{system_instr}\n\n{user_content}"
    
    for attempt in range(RETRY_LIMIT):
        try:
            response = client.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(temperature=0.1),
            )
            return safe_parse_json(response.text)
        except Exception as e:
            if attempt < RETRY_LIMIT - 1:
                print(f"    [重试 {attempt+1}/{RETRY_LIMIT}] {e}")
                time.sleep(RETRY_DELAY)
            else:
                return {
                    "dimensions": {}, "overall": -1, "veto": False,
                    "veto_reason": None, "summary": f"失败: {e}", "_eval_error": True,
                }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--tag", default="corrected", choices=["corrected", "uncorrected"])
    parser.add_argument("--no-debias", action="store_true", help="消融实验：使用无去偏指令")
    args = parser.parse_args()

    gemini_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=gemini_key)
    client = genai.GenerativeModel(GEMINI_MODEL)

    with open(args.input, encoding="utf-8") as f:
        records = json.load(f)

    print(f"待评分：{len(records)} 条 | 类型：{args.tag}")
    results = []

    for i, r in enumerate(records):
        print(f"  [{i+1}/{len(records)}] {r['industry']} {r['scene_type']} {r['scenario_name'][:15]}")
        eval_result = evaluate_one(client, r, no_debias=args.no_debias)
        results.append({**r, "eval": eval_result})
        overall = eval_result.get("overall", "?")
        fb = " [降级]" if eval_result.get("_parse_fallback") else ""
        err = " [失败]" if eval_result.get("_eval_error") else ""
        print(f"    ✓ 总分{overall}/2{fb}{err}")
        time.sleep(1.5)

    valid = [r for r in results if not r["eval"].get("_eval_error")]
    by_bench = {}
    for r in valid:
        bt = r["bench_type"]
        by_bench.setdefault(bt, []).append(r)

    def avg(arr):
        return round(sum(r["eval"].get("overall", 0) for r in arr) / len(arr), 3) if arr else None

    print(f"\n{'='*55}")
    print(f"真人录音评测结果 | ASR版本：{args.tag}")
    print(f"{'='*55}")
    print(f"总体均分：{avg(valid)} | 有效条数：{len(valid)}/{len(results)}")
    print(f"Veto次数：{sum(1 for r in valid if r['eval'].get('veto'))}")
    print(f"\n按场景类型：")
    for bt, arr in by_bench.items():
        print(f"  {bt:15} 均分={avg(arr)} 条数={len(arr)} Veto={sum(1 for r in arr if r['eval'].get('veto'))}")
    print(f"\n按行业：")
    by_ind = {}
    for r in valid:
        by_ind.setdefault(r["industry"], []).append(r)
    for ind, arr in by_ind.items():
        print(f"  {ind:8} 均分={avg(arr)} 条数={len(arr)}")
    print(f"{'='*55}")

    report = {
        "meta": {"asr_tag": args.tag, "generated_at": datetime.now().isoformat(),
                 "eval_model": GEMINI_MODEL, "total": len(results), "valid": len(valid),
                 "debias_mode": "disabled (ablation)" if args.no_debias else "enabled"},
        "overall_avg": avg(valid),
        "veto_count": sum(1 for r in valid if r['eval'].get('veto')),
        "by_bench_type": {bt: {"avg": avg(arr), "count": len(arr),
                               "veto": sum(1 for r in arr if r['eval'].get('veto'))}
                          for bt, arr in by_bench.items()},
        "by_industry": {ind: {"avg": avg(arr), "count": len(arr)}
                        for ind, arr in by_ind.items()},
        "raw_results": results,
    }

    OUTPUT_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = OUTPUT_DIR / f"human_{args.tag}_{ts}_summary.json"
    summary = {k: v for k, v in report.items() if k != "raw_results"}
    with open(out, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    full_out = OUTPUT_DIR / f"human_{args.tag}_{ts}_full.json"
    with open(full_out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存：{out}")

if __name__ == "__main__":
    main()