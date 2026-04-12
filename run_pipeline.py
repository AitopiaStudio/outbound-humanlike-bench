#!/usr/bin/env python3
"""
run_pipeline.py
================
外呼拟人度 Benchmark 端到端运行脚本

流程：
  Step 1  用千问 API 生成 CCO 风格和 Base 风格对话数据
  Step 2  Benchmark 评分（模型：Gemini）
  Step 3  汇总结果，输出对比报告

模型分离设计（方法论说明）：
  生成模型：Qwen（阿里云百炼，qwen-max）
  评测模型：qwen-plus（与生成模型不同版本，降低自我偏好）
  ↑ 生成与评测使用不同厂商模型，避免 LLM Judge 偏好自身输出的固有偏见。
    这是学术界 LLM-as-a-Judge 评测的推荐实践。

API Key 获取：
  千问：https://bailian.console.aliyun.com → 右上角 API-KEY
  
使用方法：
  1. 复制 .env.example 为 .env，填入 API Key
  2. pip install openai python-dotenv tqdm pydantic
  3. python run_pipeline.py --scene notification
  4. 结果保存至 outputs/ 目录

支持场景：
  --scene      notification / customerservice / returnvisit / sales
  --scene-key  指定具体业务场景 key（不指定则跑全部）
  --state-key  指定具体客户状态 key（不指定则跑全部）
  --count      每个组合生成几条（默认 3）
  --eval-only  跳过生成，只对已有数据重新评分
  --gen-only   只生成数据，不评分
"""

import os
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

# 第三方库（需要 pip install openai google-genai python-dotenv tqdm）
try:
    from openai import OpenAI   # 千问兼容 OpenAI 接口格式
except ImportError:
    raise ImportError("请先运行: pip install openai")

try:
    import google.generativeai as genai
except ImportError:
    raise ImportError("请先运行: pip install google-generativeai")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

# 导入本项目的数据合成 Prompt 模块
import sys
sys.path.insert(0, str(Path(__file__).parent))

from data_synthesis.prompts.notification_cco_prompt import (
    CCO_SYSTEM_PROMPT as NOTIF_CCO_SYS,
    BASE_SYSTEM_PROMPT as NOTIF_BASE_SYS,
    build_cco_user_prompt as notif_cco_user,
    build_base_user_prompt as notif_base_user,
    GENERATION_PLAN as NOTIF_PLAN,
    BUSINESS_SCENARIOS as NOTIF_SCENES,
    CUSTOMER_STATES as NOTIF_STATES,
)
from data_synthesis.prompts.customerservice_cco_prompt import (
    CCO_SYSTEM_PROMPT as CS_CCO_SYS,
    BASE_SYSTEM_PROMPT as CS_BASE_SYS,
    build_cco_user_prompt as cs_cco_user,
    build_base_user_prompt as cs_base_user,
    GENERATION_PLAN as CS_PLAN,
    BUSINESS_SCENARIOS as CS_SCENES,
    CUSTOMER_STATES as CS_STATES,
)
from data_synthesis.prompts.returnvisit_cco_prompt import (
    CCO_SYSTEM_PROMPT as RV_CCO_SYS,
    BASE_SYSTEM_PROMPT as RV_BASE_SYS,
    build_cco_user_prompt as rv_cco_user,
    build_base_user_prompt as rv_base_user,
    GENERATION_PLAN as RV_PLAN,
    BUSINESS_SCENARIOS as RV_SCENES,
    CUSTOMER_FEEDBACK_TYPES as RV_STATES,
)
from data_synthesis.prompts.sales_cco_prompt import (
    CCO_SYSTEM_PROMPT as SALES_CCO_SYS,
    BASE_SYSTEM_PROMPT as SALES_BASE_SYS,
    build_cco_user_prompt as sales_cco_user,
    build_base_user_prompt as sales_base_user,
    GENERATION_PLAN as SALES_PLAN,
    BUSINESS_SCENARIOS as SALES_SCENES,
    CUSTOMER_REJECTION_STATES as SALES_STATES,
)
from data_synthesis.prompts.financial_cco_prompt import (
    CCO_SYSTEM_PROMPT as FIN_CCO_SYS,
    BASE_SYSTEM_PROMPT as FIN_BASE_SYS,
    build_cco_user_prompt as fin_cco_user,
    build_base_user_prompt as fin_base_user,
    GENERATION_PLAN as FIN_PLAN,
    BUSINESS_SCENARIOS as FIN_SCENES,
    CUSTOMER_STATES as FIN_STATES,
)
from data_synthesis.prompts.insurance_cco_prompt import (
    CCO_SYSTEM_PROMPT as INS_CCO_SYS,
    BASE_SYSTEM_PROMPT as INS_BASE_SYS,
    build_cco_user_prompt as ins_cco_user,
    build_base_user_prompt as ins_base_user,
    GENERATION_PLAN as INS_PLAN,
    BUSINESS_SCENARIOS as INS_SCENES,
    CUSTOMER_STATES as INS_STATES,
)
from data_synthesis.prompts.healthcare_cco_prompt import (
    CCO_SYSTEM_PROMPT as HC_CCO_SYS,
    BASE_SYSTEM_PROMPT as HC_BASE_SYS,
    build_cco_user_prompt as hc_cco_user,
    build_base_user_prompt as hc_base_user,
    GENERATION_PLAN as HC_PLAN,
    BUSINESS_SCENARIOS as HC_SCENES,
    CUSTOMER_STATES as HC_STATES,
)
from benchmarks.scene_specific_bench import (
    get_scene_benchmark,
    get_scene_system_prompt,
    OUTPUT_FORMAT,
)


# ═══════════════════════════════════════════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════════════════════════════════════════

QWEN_MODEL_DEFAULT = "qwen3.5-flash"    # 默认生成模型（千问）
QWEN_MODEL_SALES   = "qwen-max"          # Sales 场景专用模型
GEMINI_MODEL   = "models/gemini-3-flash-preview"   # 评测模型
OUTPUT_DIR     = Path("outputs")
RETRY_LIMIT    = 3
RETRY_DELAY    = 5  # 秒

# 场景路由表
SCENE_CONFIG = {
    "notification": {
        "label":      "通知型",
        "cco_sys":    NOTIF_CCO_SYS,
        "base_sys":   NOTIF_BASE_SYS,
        "cco_user":   notif_cco_user,
        "base_user":  notif_base_user,
        "plan":       NOTIF_PLAN,
        "scenes":     NOTIF_SCENES,
        "states":     NOTIF_STATES,
        "bench_key":  "notification",
        "state_arg":  "state",   # plan 的第二个字段名
    },
    "customerservice": {
        "label":      "客服型",
        "cco_sys":    CS_CCO_SYS,
        "base_sys":   CS_BASE_SYS,
        "cco_user":   cs_cco_user,
        "base_user":  cs_base_user,
        "plan":       CS_PLAN,
        "scenes":     CS_SCENES,
        "states":     CS_STATES,
        "bench_key":  "customerservice",
        "state_arg":  "state",
    },
    "returnvisit": {
        "label":      "回访型",
        "cco_sys":    RV_CCO_SYS,
        "base_sys":   RV_BASE_SYS,
        "cco_user":   rv_cco_user,
        "base_user":  rv_base_user,
        "plan":       RV_PLAN,
        "scenes":     RV_SCENES,
        "states":     RV_STATES,
        "bench_key":  "returnvisit",
        "state_arg":  "feedback_type",
    },
    "sales": {
        "label":      "销售型",
        "cco_sys":    SALES_CCO_SYS,
        "base_sys":   SALES_BASE_SYS,
        "cco_user":   sales_cco_user,
        "base_user":  sales_base_user,
        "plan":       SALES_PLAN,
        "scenes":     SALES_SCENES,
        "states":     SALES_STATES,
        "bench_key":  "sales",    # 销售型用专项 benchmark
        "state_arg":  "rejection_state",
    },
    "financial": {
        "label": "金融行业",
        "cco_sys": FIN_CCO_SYS, "base_sys": FIN_BASE_SYS,
        "cco_user": fin_cco_user, "base_user": fin_base_user,
        "plan": FIN_PLAN, "scenes": FIN_SCENES, "states": FIN_STATES,
        "bench_key": "customerservice", "state_arg": "state",
    },
    "insurance": {
        "label": "保险行业",
        "cco_sys": INS_CCO_SYS, "base_sys": INS_BASE_SYS,
        "cco_user": ins_cco_user, "base_user": ins_base_user,
        "plan": INS_PLAN, "scenes": INS_SCENES, "states": INS_STATES,
        "bench_key": "customerservice", "state_arg": "state",
    },
    "healthcare": {
        "label": "医疗健康行业",
        "cco_sys": HC_CCO_SYS, "base_sys": HC_BASE_SYS,
        "cco_user": hc_cco_user, "base_user": hc_base_user,
        "plan": HC_PLAN, "scenes": HC_SCENES, "states": HC_STATES,
        "bench_key": "customerservice", "state_arg": "state",
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# API 客户端初始化
# ═══════════════════════════════════════════════════════════════════════════════

def init_clients():
    qwen_key   = os.getenv("QWEN_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    if not qwen_key:
        raise ValueError(
            "未找到 QWEN_API_KEY\n"
            "获取方式：https://bailian.console.aliyun.com → 右上角 API-KEY"
        )
    if not gemini_key:
        raise ValueError(
            "未找到 GEMINI_API_KEY\n"
            "获取方式：https://aistudio.google.com → Get API Key（免费）"
        )

    gen_client = OpenAI(
        api_key  = qwen_key,
        base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    genai.configure(api_key=gemini_key)
    eval_client = genai.GenerativeModel(GEMINI_MODEL)

    return gen_client, eval_client

# ═══════════════════════════════════════════════════════════════════════════════

def get_qwen_model_for_scene(scene_type: str) -> str:
    """根据场景类型返回对应的千问模型"""
    if scene_type == "sales":
        return QWEN_MODEL_SALES
    return QWEN_MODEL_DEFAULT


def generate_with_qwen(
    client,
    system_prompt: str,
    user_prompt: str,
    model: str = None,
    temperature: float = 0.8,
    max_tokens: int = 1500,
) -> str:
    """调用千问 API 生成对话，含重试逻辑（兼容 OpenAI 格式）"""
    if model is None:
        model = QWEN_MODEL_DEFAULT
    for attempt in range(RETRY_LIMIT):
        try:
            response = client.chat.completions.create(
                model       = model,
                max_tokens  = max_tokens,
                temperature = temperature,
                messages    = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_prompt},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            if attempt < RETRY_LIMIT - 1:
                print(f"    [重试 {attempt+1}/{RETRY_LIMIT}] 千问请求失败: {e}")
                time.sleep(RETRY_DELAY)
            else:
                raise RuntimeError(f"千问生成失败（已重试 {RETRY_LIMIT} 次）: {e}")


def run_generation(
    gen_client,
    scene_type: str,
    filter_scene: Optional[str] = None,
    filter_state: Optional[str] = None,
    count_per_combo: int = 3,
) -> list:
    """
    用 Claude 批量生成 CCO 和 Base 对话数据

    Returns:
        list of dict，每条包含 scene/state/type/dialog 等字段
    """
    cfg = SCENE_CONFIG[scene_type]
    results = []

    # 根据 filter 筛选生成计划
    plan = cfg["plan"]
    if filter_scene or filter_state:
        plan = [
            row for row in plan
            if (not filter_scene or row[0] == filter_scene)
            and (not filter_state or row[1] == filter_state)
        ]
        if not plan:
            print(f"⚠️  没有匹配的场景/状态组合，请检查 --scene-key 和 --state-key 参数")
            return []

    total = len(plan) * count_per_combo * 2  # CCO + Base
    done  = 0

    qwen_model = get_qwen_model_for_scene(scene_type)
    print(f"\n{'='*60}")
    print(f"Step 1  生成对话数据（模型：{qwen_model}）")
    print(f"场景：{cfg['label']}  |  组合数：{len(plan)}  |  每组：{count_per_combo}条×2类型")
    print(f"预计生成：{total} 条对话")
    print(f"{'='*60}\n")

    for row in plan:
        scenario_key, state_key, _, note = row[0], row[1], row[2], row[3]
        scene_label  = cfg["scenes"][scenario_key]["name"]
        state_info   = cfg["states"][state_key]
        state_label  = state_info["name"] if isinstance(state_info, dict) else str(state_info)

        for i in range(count_per_combo):
            # ── 生成 CCO 风格 ──────────────────────────────────────────────
            print(f"  [{done+1}/{total}] CCO  {scene_label} × {state_label} #{i+1}")
            try:
                cco_text = generate_with_qwen(
                    client        = gen_client,
                    system_prompt = cfg["cco_sys"],
                    user_prompt   = cfg["cco_user"](scenario_key, state_key),                    model         = qwen_model,                    temperature   = 0.85,
                )
                results.append({
                    "id":           f"{scene_type}_{scenario_key}_{state_key}_cco_{i}",
                    "scene_type":   scene_type,
                    "scenario_key": scenario_key,
                    "state_key":    state_key,
                    "type":         "CCO",
                    "dialog":       cco_text,
                    "note":         note,
                })
                done += 1
            except Exception as e:
                print(f"    ✗ CCO 生成失败: {e}")
                done += 1

            # ── 生成 Base 风格 ─────────────────────────────────────────────
            print(f"  [{done+1}/{total}] Base {scene_label} × {state_label} #{i+1}")
            try:
                base_text = generate_with_qwen(
                    client        = gen_client,
                    system_prompt = cfg["base_sys"],
                    user_prompt   = cfg["base_user"](scenario_key, state_key),
                    model         = qwen_model,
                    temperature   = 0.7,
                )
                results.append({
                    "id":           f"{scene_type}_{scenario_key}_{state_key}_base_{i}",
                    "scene_type":   scene_type,
                    "scenario_key": scenario_key,
                    "state_key":    state_key,
                    "type":         "Base",
                    "dialog":       base_text,
                    "note":         note,
                })
                done += 1
            except Exception as e:
                print(f"    ✗ Base 生成失败: {e}")
                done += 1

            # 避免触发速率限制
            time.sleep(1)

    print(f"\n✓ 生成完成：{len(results)}/{total} 条成功\n")
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# Step 2：Gemini 评分
# ═══════════════════════════════════════════════════════════════════════════════

def safe_parse_json(raw: str) -> dict:
    """五层容错 JSON 解析"""
    import re

    # 第一层：去 markdown 标记后直接解析
    text = re.sub(r"```json\s*", "", raw).replace("```", "").strip()
    try:
        return json.loads(text)
    except Exception:
        pass

    # 第二层：提取第一个完整 JSON 对象
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass

    # 第三层：清理 reason 字段里的非法换行和引号
    cleaned = re.sub(
        r':\s*"([^"]*?)"',
        lambda m: ': "{}"'.format(
            m.group(1).replace("\n", " ").replace("\r", "").replace('"', '\\"')
        ),
        text,
    )
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # 第四层：正则提取关键字段，构造兜底对象
    overall_m = re.search(r'"overall"\s*:\s*(\d)', text)
    veto_m    = re.search(r'"veto"\s*:\s*(true|false)', text)
    summary_m = re.search(r'"summary"\s*:\s*"([^"]{0,200})"', text)

    def get_dim_score(name):
        m = re.search(rf'"{re.escape(name)}"[^}}]*?"score"\s*:\s*(\d)', text)
        return int(m.group(1)) if m else 1

    dims_keys = re.findall(r'"(\w[\w\s]+)"\s*:\s*\{', text)
    dims_keys = [k for k in dims_keys if k not in
                 ("dimensions", "overall", "veto", "veto_reason", "summary")]

    return {
        "dimensions": {k: {"score": get_dim_score(k), "reason": "解析异常，兜底值"} for k in dims_keys},
        "overall":    int(overall_m.group(1)) if overall_m else 1,
        "veto":       veto_m.group(1) == "true" if veto_m else False,
        "veto_reason": None,
        "summary":    summary_m.group(1) if summary_m else "评分解析异常",
        "_parse_fallback": True,
    }


def evaluate_with_qwen(
    eval_client,
    dialog: str,
    dialog_type: str,
    scene_type: str,
    scenario_key: str,
    state_key: str,
    no_debias: bool = False,
) -> dict:
    """调用千问 qwen-plus 对单条对话评分，含重试逻辑"""
    cfg = SCENE_CONFIG[scene_type]

    if no_debias:
        from benchmarks.no_debias_bench import get_no_debias_prompt
        system_instr = get_no_debias_prompt(scene_type)
        dim_names = []
    else:
        dims = get_scene_benchmark(scene_type)
        dim_names = list(dims.keys())
        system_instr = get_scene_system_prompt(scene_type)

    scene_label = cfg["scenes"][scenario_key]["name"]
    state_info  = cfg["states"][state_key]
    state_label = state_info["name"] if isinstance(state_info, dict) else str(state_info)

    dim_schema = "\n".join([f'    "{d}": {{"score": 0或1或2, "reason": "不超过25字"}}' for d in dim_names])

    user_content = f"""待评估对话（{dialog_type}）：
场景：{scene_label} | 状态：{state_label}

{dialog}

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

    for attempt in range(RETRY_LIMIT):
        try:
            response = eval_client.generate_content(
                f"{system_instr}\n\n{user_content}",
                generation_config=genai.types.GenerationConfig(temperature=0.1),
            )
            raw = response.text
            return safe_parse_json(raw)
        except Exception as e:
            if attempt < RETRY_LIMIT - 1:
                print(f"    [重试 {attempt+1}/{RETRY_LIMIT}] Gemini 评分失败: {e}")
                time.sleep(RETRY_DELAY)
            else:
                return {
                    "dimensions": {},
                    "overall": -1,
                    "veto": False,
                    "veto_reason": None,
                    "summary": f"评分失败: {e}",
                    "_eval_error": True,
                }


def run_evaluation(eval_client, dialogs: list, no_debias: bool = False) -> list:
    """用 Gemini 对所有对话批量评分"""
    total   = len(dialogs)
    results = []

    print(f"\n{'='*60}")
    print(f"Step 2  Benchmark 评分（模型：{GEMINI_MODEL}）")
    print(f"待评分：{total} 条对话")
    print(f"{'='*60}\n")

    for i, d in enumerate(dialogs):
        print(f"  [{i+1}/{total}] 评分：{d['scene_type']} × {d['type']} × {d['scenario_key']}")
        eval_result = evaluate_with_qwen(
            eval_client   = eval_client,
            dialog        = d["dialog"],
            dialog_type   = d["type"],
            scene_type    = d["scene_type"],
            scenario_key  = d["scenario_key"],
            state_key     = d["state_key"],
            no_debias     = no_debias,
        )
        entry = {**d, "eval": eval_result}
        results.append(entry)

        overall = eval_result.get("overall", "?")
        veto    = "⚡Veto" if eval_result.get("veto") else ""
        fallback = " [解析降级]" if eval_result.get("_parse_fallback") else ""
        error    = " [评分失败]" if eval_result.get("_eval_error") else ""
        print(f"    ✓ 总分 {overall}/2  {veto}{fallback}{error}")

        time.sleep(1.5)  # Gemini 速率限制

    success = sum(1 for r in results if not r["eval"].get("_eval_error"))
    print(f"\n✓ 评分完成：{success}/{total} 条成功\n")
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# Step 3：汇总报告
# ═══════════════════════════════════════════════════════════════════════════════

def generate_report(results: list, scene_type: str, no_debias: bool = False) -> dict:
    """生成对比报告，计算 Base vs CCO 各维度平均分"""
    base_results = [r for r in results if r["type"] == "Base" and not r["eval"].get("_eval_error")]
    cco_results  = [r for r in results if r["type"] == "CCO"  and not r["eval"].get("_eval_error")]

    def avg_overall(arr):
        if not arr:
            return None
        return round(sum(r["eval"].get("overall", 0) for r in arr) / len(arr), 3)

    def avg_dim(arr, dim_name):
        scores = [
            r["eval"].get("dimensions", {}).get(dim_name, {}).get("score", None)
            for r in arr
        ]
        scores = [s for s in scores if s is not None]
        return round(sum(scores) / len(scores), 3) if scores else None

    def veto_count(arr):
        return sum(1 for r in arr if r["eval"].get("veto"))

    # 收集所有出现的维度名
    all_dims = set()
    for r in results:
        all_dims.update(r["eval"].get("dimensions", {}).keys())

    dim_comparison = {}
    for dim in sorted(all_dims):
        dim_comparison[dim] = {
            "base_avg": avg_dim(base_results, dim),
            "cco_avg":  avg_dim(cco_results,  dim),
            "delta":    round((avg_dim(cco_results, dim) or 0) - (avg_dim(base_results, dim) or 0), 3),
        }

    report = {
        "meta": {
            "scene_type":    scene_type,
            "generated_at":  datetime.now().isoformat(),
            "gen_model":     get_qwen_model_for_scene(scene_type),
            "eval_model":    GEMINI_MODEL,
            "debias_mode":   "disabled (ablation)" if no_debias else "enabled",
            "total_dialogs": len(results),
            "base_count":    len(base_results),
            "cco_count":     len(cco_results),
        },
        "overall_comparison": {
            "base_avg_score": avg_overall(base_results),
            "cco_avg_score":  avg_overall(cco_results),
            "delta":          round((avg_overall(cco_results) or 0) - (avg_overall(base_results) or 0), 3),
            "base_veto_count": veto_count(base_results),
            "cco_veto_count":  veto_count(cco_results),
        },
        "dimension_comparison": dim_comparison,
        "raw_results": results,
    }
    return report


def print_report_summary(report: dict):
    """在终端打印易读的结果摘要"""
    oc  = report["overall_comparison"]
    dc  = report["dimension_comparison"]
    meta = report["meta"]

    print(f"\n{'='*65}")
    print(f"评测结果摘要  |  场景：{meta['scene_type']}")
    print(f"生成模型：{meta['gen_model']}  |  评测模型：{meta['eval_model']}")
    print(f"{'='*65}")
    print(f"{'':25} {'Base':>8}  {'CCO':>8}  {'Delta':>8}")
    print(f"{'-'*65}")
    print(f"{'总分平均（满分2分）':25} {str(oc['base_avg_score']):>8}  {str(oc['cco_avg_score']):>8}  {oc['delta']:>+8.3f}")
    print(f"{'一票否决次数':25} {str(oc['base_veto_count']):>8}  {str(oc['cco_veto_count']):>8}")
    print(f"{'-'*65}")
    print("各维度对比：")
    for dim, val in dc.items():
        b = f"{val['base_avg']:.2f}" if val['base_avg'] is not None else "  —"
        c = f"{val['cco_avg']:.2f}"  if val['cco_avg']  is not None else "  —"
        d = f"{val['delta']:+.2f}"
        flag = " ★" if val["delta"] > 0.5 else ("  " if val["delta"] >= 0 else " ▼")
        print(f"  {dim:<22} {b:>6}  {c:>6}  {d:>7}{flag}")
    print(f"{'='*65}")
    print("★ = CCO 显著优于 Base（Delta > 0.5）")
    print("▼ = Base 优于 CCO（需检查 CCO prompt 设计）")


def save_outputs(report: dict, scene_type: str):
    """保存完整结果 JSON 和摘要"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 完整结果（含 raw_results）
    full_path = OUTPUT_DIR / f"{scene_type}_{ts}_full.json"
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n完整结果已保存：{full_path}")

    # 摘要（不含 raw_results，方便 README 引用）
    summary_report = {k: v for k, v in report.items() if k != "raw_results"}
    summary_path = OUTPUT_DIR / f"{scene_type}_{ts}_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_report, f, ensure_ascii=False, indent=2)
    print(f"摘要结果已保存：{summary_path}")

    return full_path, summary_path


# ═══════════════════════════════════════════════════════════════════════════════
# CLI 入口
# ═══════════════════════════════════════════════════════════════════════════════

def parse_args():
    parser = argparse.ArgumentParser(
        description="外呼拟人度 Benchmark Pipeline（千问生成 + Gemini 评测）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法：
  # 生成并评测通知型全部场景
  python run_pipeline.py --scene notification

  # 只测通知型的大促场景 × 半途打断状态，每组生成3条
  python run_pipeline.py --scene notification --scene-key ecommerce_promo --state-key mid_interrupt --count 3

  # 只评测已有数据（跳过生成）
  python run_pipeline.py --scene customerservice --eval-only --input outputs/customerservice_20250101_120000_full.json

  # 只生成数据，不评测
  python run_pipeline.py --scene sales --gen-only --count 2
        """
    )
    parser.add_argument("--scene",     required=True,
                        choices=list(SCENE_CONFIG.keys()),
                        help="场景类型")
    parser.add_argument("--scene-key", default=None,
                        help="指定具体业务场景 key（不指定则跑全部）")
    parser.add_argument("--state-key", default=None,
                        help="指定具体客户状态 key（不指定则跑全部）")
    parser.add_argument("--count",     type=int, default=10,
                        help="每个场景/状态组合生成几条（默认3）")
    parser.add_argument("--eval-only", action="store_true",
                        help="跳过生成，只评分已有数据")
    parser.add_argument("--gen-only",  action="store_true",
                        help="只生成数据，不评分")
    parser.add_argument("--input",     default=None,
                        help="--eval-only 时指定输入 JSON 文件路径")
    parser.add_argument("--no-debias", action="store_true",
                        help="消融实验模式：使用无去偏指令的基线评分，用于对比验证去偏机制有效性")
    return parser.parse_args()


def main():
    args = parse_args()

    print(f"\n外呼拟人度 Benchmark Pipeline")
    print(f"场景：{SCENE_CONFIG[args.scene]['label']}  |  "
          f"生成模型：{get_qwen_model_for_scene(args.scene)}  |  评测模型：{GEMINI_MODEL}")

    # 初始化客户端
    gen_client, eval_client = init_clients()

    dialogs = []

    # ── Step 1：生成 ────────────────────────────────────────────────────────
    if args.eval_only and args.input:
        print(f"\n跳过生成，加载已有数据：{args.input}")
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            dialogs = data
        else:
            dialogs = data.get("raw_results", data)
        print(f"已加载 {len(dialogs)} 条对话")
    else:
        dialogs = run_generation(
            gen_client     = gen_client,
            scene_type     = args.scene,
            filter_scene   = args.scene_key,
            filter_state   = args.state_key,
            count_per_combo = args.count,
        )
        if not dialogs:
            print("未生成任何数据，退出。")
            return

        # 中间结果先保存，防止评分阶段出错丢失数据
        OUTPUT_DIR.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        interim_path = OUTPUT_DIR / f"{args.scene}_{ts}_dialogs_only.json"
        with open(interim_path, "w", encoding="utf-8") as f:
            json.dump(dialogs, f, ensure_ascii=False, indent=2)
        print(f"对话数据已保存（中间结果）：{interim_path}")

    if args.gen_only:
        print("\n--gen-only 模式，跳过评分。")
        return

    # ── Step 2：评分 ────────────────────────────────────────────────────────
    results = run_evaluation(eval_client, dialogs, no_debias=args.no_debias)

    # ── Step 3：报告 ────────────────────────────────────────────────────────
    report = generate_report(results, args.scene, no_debias=args.no_debias)
    print_report_summary(report)
    save_outputs(report, args.scene)


if __name__ == "__main__":
    main()
