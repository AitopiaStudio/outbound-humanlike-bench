# OutboundHumanlike-Bench

> **首个面向 AI 外呼场景的拟人度评测框架**，覆盖销售坐席与客服坐席，支持四个行业，内置 LLM Judge 去偏机制与真人录音验证。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org)
[![Eval Model: Gemini](https://img.shields.io/badge/Eval-Gemini_Flash-orange.svg)](https://deepmind.google)
[![Gen Model: Qwen](https://img.shields.io/badge/Gen-Qwen--Max%2FFlash-purple.svg)](https://qwen.ai)

---

## 为什么需要这个框架

AI 外呼系统正在大规模落地，但现有评测方法存在三个根本性问题：

| 问题 | 具体表现 |
|------|---------|
| **人工评测不可扩展** | 成本高、主观性强、无法覆盖多行业多场景 |
| **通用指标失效** | BLEU、ROUGE 等指标无法识别「播音腔」「条目化」等 AI 特征 |
| **LLM Judge 自带偏见** | 未经干预的大模型会把「结构完整、表达礼貌」的 AI 话术评为高分，恰恰掩盖了机器味 |

本框架针对第三个问题设计了系统性去偏机制，并通过消融实验验证：**去偏后区分度提升 91–99%，不去偏则基线与风格对齐数据无法区分。**

---

## 三个核心亮点

###  场景专项评分体系
针对外呼场景的两类坐席、四种子类型设计独立的评分维度，通过对电商、金融、保险、医疗的行业通用性验证的外呼拟人指标：

- **销售坐席**：信息揉合自然度、转化果断度、多轮挽回韧性、闭环保存能力、压力应对与价值重塑
- **客服坐席**：通知型 / 咨询解答型 / 回访型，各有专属 Veto 触发条件与维度权重

### LLM-AS-A-JUDGE 去偏机制
基于四个原则消除 LLM Judge 的系统性偏见：

- **Critique-then-Score**：强制上下文分析 → 机器味挑刺 → 推理说明 → 打分，三步 Cross Validation 后才得出分数
- **五类偏见显式压制**：助人偏见 / 长度偏见 / 礼貌偏见 / 结构偏见 / 书面语偏见，逐一在 Prompt 中显式纠正
- **Few-Shot 真实锚定**：嵌入真实 CCO 话术正反对比，以真人表达为参照系而非 AI 完美答案
- **Veto 一票否决**：检测到播音腔开场、条目化、套话结尾等 AI 特征，该条对话总分直接归零

###  真人录音多层验证
引入真实外呼录音（164 条，覆盖四行业），验证 Benchmark 对不同拟人度层级的排序能力。

---

## 核心结果

> 满分 2.0 分。真人最佳录音定义：同一行业 × 类型 × 客户状态下多条同样录音取最高分，剔除ASR问题导致的低分；AI风格对齐是通过设计业务场景下的拟人化prompt，AI通过上下文产出的高质量拟人风格对话；基线模型是给同样的场景设定与上下文，基模产出的对话。

### 客服坐席（通知型 42% / 咨询解答型 33% / 回访型 25% 加权）

| 评测对象 | 本框架（去除 LLM Judge 偏见） | 消融对照组（含 LLM Judge 偏见） |
|---------|:---:|:---:|
| 基线模型（无拟人指令） | 0.36 | 1.93 |
| AI 风格对齐 | 1.95 | 1.98 |
| 真人录音（最佳） | 1.95 | 1.90 |

### 销售坐席

| 评测对象 | 本框架（去除 LLM Judge 偏见） | 消融对照组（含 LLM Judge 偏见） |
|---------|:---:|:---:|
| 基线模型（无拟人指令） | 0.59 | 1.88 |
| AI 风格对齐 | 1.93 | 1.99 |
| 真人录音（最佳） | 1.89 | 1.83 |

**结论：** 本框架中三类数据呈清晰梯级分布（基线 → AI 风格对齐 → 真人最佳），消融对照组中三者挤压在 1.80–2.00 区间完全无法区分。去偏机制是框架有效性的前提，而非可选项。

---

## 跨行业稳定性

### 客服坐席

| 行业 | 基线模型 | AI 拟人风格对齐 | 真人最佳 |
|------|:---:|:---:|:---:|
| 电商 | 0.43 | 1.95 | 2.00 |
| 金融 | 0.46 | 1.93 | 2.00 |
| 保险 | 0.37 | 1.93 | 2.00 |
| 医疗健康 | 0.40 | 1.92 | 1.78 |

### 销售坐席

| 行业 | 基线模型 | AI 拟人风格对齐 | 真人最佳 |
|------|:---:|:---:|:---:|
| 电商 | 0.59 | 1.93 | 2.00 |
| 金融 | 1.40 | 1.95 | 2.00 |
| 保险 | 1.85 | 2.00 | 2.00 |
| 医疗健康 | 1.20 | 2.00 | 1.50 |

Benchmark 在四个行业中均保持稳定的区分能力，客服坐席跨行业一致性尤为突出。

---

## 框架覆盖范围

```
OutboundHumanlike-Bench
│
├── 销售坐席
│   └── 销售型
│       ├── 专项维度（×5）：信息揉合自然度 · 转化果断度 · 多轮挽回韧性
│       │                   闭环保存能力 · 压力应对与价值重塑
│       └── 通用维度（×6）：语气词 · 口语化 · 情绪真实 · 上下文互动
│                           不啰嗦 · 不条目化
│
└── 客服坐席
    ├── 通知型（42%）   → Veto：播音腔开场 / 条目化堆砌
    ├── 咨询解答型（33%）→ Veto：单轮超长 / FAQ 直接念稿
    └── 回访型（25%）   → Veto：负面信号走正面路径

行业：电商 · 金融 · 保险 · 医疗健康
评分：0 / 1 / 2 三档，Veto 触发则直接归零
```

---

## 快速上手

### 环境配置

```bash
git clone https://github.com/your-username/outbound-humanlike-bench.git
cd outbound-humanlike-bench
pip install -r requirements.txt
cp .env.example .env   # 填入 QWEN_API_KEY 和 GEMINI_API_KEY
```

### 生成 + 评测（端到端）

```bash
# 客服坐席——通知型，生成 10 条并评分
python run_pipeline.py --scene notification --count 10

# 销售坐席，仅生成
python run_pipeline.py --scene sales --gen-only --count 10

# 多行业评测（金融行业）
python eval_multi_industry.py \
  --input outputs/financial_dialogs_only.json \
  --industry financial
```

### 消融实验对照

```bash
# 无去偏版本，验证去偏机制的贡献
python eval_multi_industry.py \
  --input outputs/financial_dialogs_only.json \
  --industry financial \
  --no-debias
```

### 真人录音评分

```bash
python eval_human_recording.py \
  --input outputs/human_corrected.json \
  --tag corrected
```

---

## 项目结构

```
outbound-humanlike-bench/
├── benchmarks/
│   ├── humanlike_bench_v2.py      # MirrorBench 风格核心评分框架
│   ├── scene_specific_bench.py    # 四场景专项 Benchmark
│   ├── sales_humanlike_bench.py   # 销售坐席专项维度
│   └── no_debias_bench.py         # 消融实验基线（无去偏）
│
├── data_synthesis/
│   └── prompts/                   # 各行业数据生成 Prompt
│       ├── financial_cco_prompt.py
│       ├── insurance_cco_prompt.py
│       ├── healthcare_cco_prompt.py
│       └── ...
│
├── run_pipeline.py                # 端到端：生成 + 评测
├── eval_multi_industry.py         # 多行业评测脚本
├── eval_human_recording.py        # 真人录音评测脚本
│
├── outputs/                       # 评测结果输出目录
├── docs/
│   └── report.md                  # 完整技术报告
└── .env.example
```

---

## 技术报告

完整实验设计、维度得分、消融实验数据与局限性分析，见 **[report.md](report.md)**。

---

## 引用

```bibtex
@misc{outbound-humanlike-bench-2026,
  title   = {OutboundHumanlike-Bench: A Scene-Specific Benchmark for
             Evaluating Human-likeness in AI Outbound Calls},
  year    = {2026},
  url     = {https://github.com/your-username/outbound-humanlike-bench}
}
```

---

## License

MIT License · 数据与代码完整开源
