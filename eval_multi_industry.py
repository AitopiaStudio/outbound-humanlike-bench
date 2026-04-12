#!/usr/bin/env python3
import os, json, time, argparse, re, sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

sys.path.insert(0, str(Path(__file__).parent))
from data_synthesis.prompts.financial_cco_prompt import BUSINESS_SCENARIOS as FIN_SCENES
from data_synthesis.prompts.insurance_cco_prompt import BUSINESS_SCENARIOS as INS_SCENES
from data_synthesis.prompts.healthcare_cco_prompt import BUSINESS_SCENARIOS as HC_SCENES
from benchmarks.scene_specific_bench import get_scene_benchmark, get_scene_system_prompt, OUTPUT_FORMAT

GEMINI_MODEL = "models/gemini-3-flash-preview"
RETRY_LIMIT = 3
RETRY_DELAY = 5
OUTPUT_DIR = Path("outputs")

INDUSTRY_SCENES = {
    "financial": FIN_SCENES,
    "insurance": INS_SCENES,
    "healthcare": HC_SCENES,
}

def get_bench_type(industry: str, scenario_key: str) -> str:
    """通过 scenario_key 从 prompt 文件的 type 字段获取 benchmark 类型"""
    scenes = INDUSTRY_SCENES[industry]
    return scenes[scenario_key]["type"]

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
        "dimensions": {},
        "overall": int(overall_m.group(1)) if overall_m else 1,
        "veto": veto_m.group(1) == "true" if veto_m else False,
        "veto_reason": None,
        "summary": "解析异常",
        "_parse_fallback": True,
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

def evaluate_one(client, dialog: dict, industry: str, no_debias: bool = False) -> dict:
    scenario_key = dialog["scenario_key"]
    bench_type = get_bench_type(industry, scenario_key)
    
    # 修复：sales benchmark 需要从项目根目录加载
    import importlib, sys
    root = str(Path(__file__).parent)
    if root not in sys.path:
        sys.path.insert(0, root)
    
    # sales 场景直接用专项 benchmark 的 system prompt
    if bench_type == "sales":
        from benchmarks.sales_humanlike_bench import SALES_DIMENSIONS
        dim_names = list(SALES_DIMENSIONS.keys())
        system_instr = get_no_debias_system_prompt("sales") if no_debias else get_scene_system_prompt("sales")
    else:
        dims = get_scene_benchmark(bench_type)
        dim_names = list(dims.keys())
        system_instr = get_no_debias_system_prompt(bench_type) if no_debias else get_scene_system_prompt(bench_type)

    dim_schema = "\n".join([
        f'    "{d}": {{"score": 0或1或2, "reason": "不超过25字"}}'
        for d in dim_names
    ])

    user_content = f"""待评估对话（{dialog["type"]}）：
场景：{scenario_key} | 行业：{industry} | 状态：{dialog["state_key"]}

{dialog["dialog"]}

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
                print(f"    [重试 {attempt+1}/{RETRY_LIMIT}] 评分失败: {e}")
                time.sleep(RETRY_DELAY)
            else:
                return {
                    "dimensions": {}, "overall": -1,
                    "veto": False, "veto_reason": None,
                    "summary": f"评分失败: {e}",
                    "_eval_error": True,
                }

def generate_report(results: list, industry: str, no_debias: bool = False) -> dict:
    valid = [r for r in results if not r["eval"].get("_eval_error")]
    base_r = [r for r in valid if r["type"] == "Base"]
    cco_r  = [r for r in valid if r["type"] == "CCO"]

    def avg(arr):
        return round(sum(r["eval"].get("overall", 0) for r in arr) / len(arr), 3) if arr else None

    def avg_dim(arr, d):
        scores = [r["eval"]["dimensions"].get(d, {}).get("score") for r in arr]
        scores = [s for s in scores if s is not None]
        return round(sum(scores) / len(scores), 3) if scores else None

    all_dims = set()
    for r in valid:
        all_dims.update(r["eval"].get("dimensions", {}).keys())

    # 按 bench_type 分组统计
    bench_groups = {}
    for r in valid:
        bt = get_bench_type(industry, r["scenario_key"])
        if bt not in bench_groups:
            bench_groups[bt] = {"base": [], "cco": []}
        bench_groups[bt]["base" if r["type"] == "Base" else "cco"].append(r)

    bench_summary = {}
    for bt, grp in bench_groups.items():
        bench_summary[bt] = {
            "base_avg": avg(grp["base"]),
            "cco_avg": avg(grp["cco"]),
            "delta": round((avg(grp["cco"]) or 0) - (avg(grp["base"]) or 0), 3),
            "base_veto": sum(1 for r in grp["base"] if r["eval"].get("veto")),
            "cco_veto": sum(1 for r in grp["cco"] if r["eval"].get("veto")),
            "base_count": len(grp["base"]),
            "cco_count": len(grp["cco"]),
        }

    return {
        "meta": {
            "industry": industry,
            "generated_at": datetime.now().isoformat(),
            "eval_model": GEMINI_MODEL,
            "total": len(results),
            "valid": len(valid),
            "debias_mode": "disabled (ablation)" if no_debias else "enabled",
        },
        "overall": {
            "base_avg": avg(base_r),
            "cco_avg": avg(cco_r),
            "delta": round((avg(cco_r) or 0) - (avg(base_r) or 0), 3),
            "base_veto": sum(1 for r in base_r if r["eval"].get("veto")),
            "cco_veto": sum(1 for r in cco_r if r["eval"].get("veto")),
        },
        "by_bench_type": bench_summary,
        "raw_results": results,
    }

def print_summary(report: dict):
    m = report["meta"]
    o = report["overall"]
    print(f"\n{'='*60}")
    print(f"评测结果 | 行业：{m['industry']} | 模型：{m['eval_model']}")
    print(f"{'='*60}")
    print(f"总体：Base={o['base_avg']} CCO={o['cco_avg']} Delta={o['delta']}")
    print(f"Veto：Base={o['base_veto']}次 CCO={o['cco_veto']}次")
    print(f"\n按场景类型：")
    for bt, s in report["by_bench_type"].items():
        print(f"  {bt:15} Base={s['base_avg']} CCO={s['cco_avg']} Delta={s['delta']:+.3f} (各{s['base_count']}条)")
    print(f"{'='*60}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="dialogs_only.json 文件路径")
    parser.add_argument("--industry", required=True, choices=["financial", "insurance", "healthcare"])
    parser.add_argument("--no-debias", action="store_true", help="消融实验：使用无去偏指令")
    args = parser.parse_args()

    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("未找到 GEMINI_API_KEY")
    genai.configure(api_key=gemini_key)
    client = genai.GenerativeModel(GEMINI_MODEL)

    with open(args.input, encoding="utf-8") as f:
        dialogs = json.load(f)

    print(f"待评分：{len(dialogs)} 条 | 行业：{args.industry}")
    results = []

    for i, d in enumerate(dialogs):
        bench_type = get_bench_type(args.industry, d["scenario_key"])
        print(f"  [{i+1}/{len(dialogs)}] {d['type']} {d['scenario_key']} → {bench_type}")
        eval_result = evaluate_one(client, d, args.industry, no_debias=args.no_debias)
        results.append({**d, "bench_type": bench_type, "eval": eval_result})
        overall = eval_result.get("overall", "?")
        fallback = " [降级]" if eval_result.get("_parse_fallback") else ""
        error = " [失败]" if eval_result.get("_eval_error") else ""
        print(f"    ✓ 总分{overall}/2{fallback}{error}")
        time.sleep(1.5)

    report = generate_report(results, args.industry, no_debias=args.no_debias)
    print_summary(report)

    OUTPUT_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = OUTPUT_DIR / f"{args.industry}_{ts}_summary.json"
    summary = {k: v for k, v in report.items() if k != "raw_results"}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    full_path = OUTPUT_DIR / f"{args.industry}_{ts}_full.json"
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存：{out_path}")

if __name__ == "__main__":
    main()