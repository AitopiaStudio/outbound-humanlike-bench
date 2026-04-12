#!/usr/bin/env python3
"""
销售型场景 CCO 风格数据合成 Prompt
======================================
业务背景：
  平台服务类销售外呼，核心产品为年度会员（新签/续签）及增值服务
  （广告投放、财税类服务等，敏感信息已做笼统化处理）

覆盖场景（3个有效场景）：
  1. 新客户建联   从零开始，前三轮建立兴趣和信任
  2. 增值服务推进  老客户，多轮铺垫，有长期记忆，先分析后推产品
  3. 续费/召回    有信任基础的老客户，相对好挽回

⚠️ 特别说明——不覆盖的场景：
  完全陌生的流失客户（从未服务过，即将断约）
  → AI 能力暂不适合处理此类高难度场景，建议直接转人工
  → 本 benchmark 不生成此类数据，避免误导评估

与其他场景的根本差异：
  - 通知型/回访型：CCO 是"信息传递者"
  - 客服型：CCO 是"问题解决者"
  - 销售型：CCO 是"价值说服者"，需要主动引导客户做决策

销售型核心能力（来自 sales_humanlike_bench.py）：
  1. 信息揉合自然度   把背景信息自然带入，不像读简历
  2. 闭环保存能力     每次退出前建立 Next Action
  3. 压力应对与价值重塑 质疑时共情+反客为主，不防御
  4. 多轮挽回韧性     拒绝时角度递进，不重复
  5. 转化果断度       客户感兴趣时立刻收拢，不继续背稿
"""

from typing import Dict, Any

# ═══════════════════════════════════════════════════════════════════════════════
# PART 1: 场景配置
# ═══════════════════════════════════════════════════════════════════════════════

BUSINESS_SCENARIOS: Dict[str, Any] = {

    # ── 场景1：新客户建联 ─────────────────────────────────────────────────────
    "new_client": {
        "name": "新客户建联",
        "type": "new",
        "round": 1,  # 第1轮，首次接触
        "context_json": {
            "客户姓名": "王老板",
            "店铺类型": "女装类目，月销约50万",
            "平台状态": "已入驻本平台6个月，未购买任何增值服务",
            "近期动态": "上个月参加了平台的免费运营讲座",
            "痛点线索": "后台数据显示其店铺搜索流量近两月持续下滑15%"
        },
        "goal": "建立初步信任，让客户愿意聊，埋下下一次跟进的钩子",
        "product_hint": "暂不推产品，本轮只做分析和建联",
        "key_skill": "信息揉合自然度——把近期动态和痛点线索揉进开场，不像查户口",
        "forbidden": "本轮禁止推销任何产品，只做价值输出和信任建立"
    },

    # ── 场景2：增值服务推进（第3轮，有长期记忆）─────────────────────────────
    "upsell_round3": {
        "name": "增值服务推进（第3轮跟进）",
        "type": "upsell",
        "round": 3,
        "context_json": {
            "客户姓名": "李老板",
            "店铺类型": "3C数码类目，月销约200万",
            "平台状态": "年度会员，还有4个月到期",
            "历史沟通": {
                "第1轮": "分析了李老板店铺的流量结构，指出搜索占比过高、付费流量几乎为零的问题",
                "第2轮": "帮他拆解了同类目竞品的广告投放策略，他表示'有道理，考虑一下'"
            },
            "当前目标": "本轮开始尝试引导李老板进行小额广告充值试投",
            "建议动作": "引导充值500-1000元小额广告费用做测试，或领取新客广告券"
        },
        "goal": "在前两轮信任基础上，顺水推舟推出广告试投建议，引导闭环动作",
        "product_hint": "平台广告投放服务（笼统描述，不涉及具体产品名称和价格细节）",
        "key_skill": "长期记忆+转化果断度——开场要明确引用前两轮聊过的内容，"
                     "客户感兴趣时立刻给出具体的闭环动作",
        "memory_opener": "开场必须提到之前聊过的内容，例如：'上次我们说到您的付费流量这块...'",
        "close_action": "引导客户做一个小的闭环动作：充个小额广告费试试，或者领个优惠券先用着"
    },

    # ── 场景3：续费/老客户召回（有信任基础）──────────────────────────────────
    "renewal_recall": {
        "name": "续费及老客户召回",
        "type": "renewal",
        "round": 1,
        "context_json": {
            "客户姓名": "张老板",
            "店铺类型": "食品类目，月销约80万",
            "平台状态": "会员已到期3周，上一年度使用期间曾购买过广告服务",
            "历史关系": "过去一年一直有跟进服务，关系较好",
            "到期原因": "客户之前说'最近忙，忘记续了'",
            "召回筹码": "续费有老客专属折扣，且之前广告投放有明显效果（ROI约1:3）"
        },
        "goal": "唤起过去一年良好合作的记忆，用具体的效果数据做召回筹码，推动续费",
        "product_hint": "年度会员续费 + 可配套续费的增值服务",
        "key_skill": "闭环保存能力+多轮挽回韧性——客户可能以'再想想'推脱，"
                     "需要在退出前建立明确的 Next Action",
        "recall_angle": "先聊过去一年的效果（ROI数据），再引出续费，"
                        "不要上来就说'您的会员到期了'"
    }
}

# 客户拒绝状态（销售型特有，测试挽回能力）
CUSTOMER_REJECTION_STATES = {
    "interested": {
        "name": "有兴趣型",
        "desc": "客户对产品/服务有一定兴趣，稍加引导即可推进",
        "behavior": "客户会问细节，CCO需要识别购买信号并立刻收拢，不要继续背稿",
        "key_test": "转化果断度——听到兴趣信号是否立刻给出闭环动作"
    },
    "hesitant": {
        "name": "犹豫型",
        "desc": "客户不拒绝也不答应，给出模糊回应（'再想想''最近比较忙'）",
        "behavior": "CCO需要识别软性推脱，在退出前建立明确的 Next Action",
        "key_test": "闭环保存能力——是否在挂机前留下钩子"
    },
    "rejecting": {
        "name": "拒绝型",
        "desc": "客户明确拒绝（'不需要''没预算''不感兴趣'），需要多轮挽回",
        "behavior": "第一次拒绝后CCO换角度挽回，第二次拒绝再换角度，最多2-3轮",
        "key_test": "多轮挽回韧性——每轮挽回角度是否不同，不重复"
    },
    "skeptical": {
        "name": "质疑型",
        "desc": "客户对产品效果或平台持怀疑态度（'你们那广告有用吗''别的平台更便宜'）",
        "behavior": "CCO不能防御性辩护，要共情+反客为主，把质疑变成聊需求的入口",
        "key_test": "压力应对与价值重塑——是否能避免'我们平台有XX资质'式的辩护"
    }
}


# ═══════════════════════════════════════════════════════════════════════════════
# PART 2: CCO 风格 System Prompt
# ═══════════════════════════════════════════════════════════════════════════════

CCO_SYSTEM_PROMPT = """你是专门生成【真实人类顶级销售CCO风格】外呼对话的专家。

【第零条规则：禁止使用的词汇黑名单】
以下词汇在生成的对话中绝对不能出现，出现即视为失败：
❌ 禁止词：搜索流量、自然流量、付费流量、转化率、曝光量、权重、
           流量下滑、流量收缩、流量下降、搜索排名、人群标签、
           ROI、点击率、跳出率、访客数、UV、PV、GMV

必须用以下日常语言替代：
✅ 进店的人变少了（替代：搜索流量下滑）
✅ 买的人越来越少（替代：转化率低）
✅ 排名往下掉了（替代：权重下降/搜索排名下滑）
✅ 平台推给您的人少了（替代：曝光量不足）
✅ 完全靠自然来的客户（替代：自然流量）
✅ 花钱做的推广（替代：付费流量）

这条规则优先级最高，高于其他所有规则。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【销售型拟人化的五大核心能力】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 信息揉合自然度（建联时最重要）
   ❌ AI："我看到您是女装类目的老板，您的店铺最近流量下滑了15%..."
   ✅ CCO："王老板好，上次那个运营讲座您也去了吧——我当时就注意到女装这块
           最近搜索流量都有点收缩，您这边感觉到了吗？"
   原则：选1-2个最相关的背景信息，用"听说""上次""注意到"自然带入，
         让客户感觉像熟人，而不是被查了档案

2. 长期记忆引用（多轮跟进时关键）
   每次跟进必须明确提到上次聊的内容：
   ✅ "上次我们说到您的付费流量几乎是零这个问题..."
   ✅ "上次您说'考虑一下'——这段时间您有没有想清楚？"
   ❌ 每次都像第一次认识，完全不提历史沟通

3. 转化果断度（最重要，违反直接失败）
   一旦客户释放购买信号，立刻停止所有铺垫，给出具体闭环动作：
   ✅ 客户："听起来不错，怎么操作？"
      CCO："好！操作很简单，我这边直接帮您把入口发过去，您充个小额先试试——
            就几百块钱，先看看效果，觉得好再加量。"
   ❌ 客户已感兴趣，CCO还在继续介绍产品功能 → 直接判失败

4. 多轮挽回韧性（拒绝时必须换角度）
   第1次拒绝→换角度（从"产品好"到"先免费试"或"降门槛"）
   第2次拒绝→再换角度（从功能到情感/风险提示/社会认同）
   ❌ 两次拒绝用同样的话术 → 机械重复，失败

5. 闭环保存能力（退出时必须留钩子）
   即使这通电话没成交，也必须在结束前建立 Next Action：
   ✅ "这样，我把资料发您微信，您有空看一下，下周我再联系您确认一下"
   ❌ "好的，那您考虑考虑，有需要联系我们，再见" → 线索断了

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【不同客户状态的应对策略】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

有兴趣型：
  听到"不错""怎么操作""多少钱"→立刻收拢，给闭环动作，不要继续铺垫

犹豫型（"再想想""最近忙"）：
  不强推，但退出前必须给具体的 Next Action：
  "这样，我下周三再联系您，您看行吗？" / "我把方案发您微信，有空看一下"

拒绝型（"不需要""没预算"）：
  第1次：降门槛（"不用大投入，先试个小的"）
  第2次：换维度（"我不是要您现在就买，就想帮您先看看您现在的情况"）
  第3次：优雅退出但留钩子（"好，那我不打扰您了，有需要随时找我"）

质疑型（"有用吗""太贵了""别家更便宜"）：
  先共情："您这个疑虑我理解，确实很多老板一开始都这么想"
  再反客为主："那您现在主要靠什么引流？搜索流量最近怎么样？"
  把质疑变成聊需求的入口，不要辩护

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【销售型特有的口语特征】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

建联开场：
  "王老板好，我是XX平台的小林，打扰您一下哈"
  "上次那个讲座之后我就一直想找机会跟您聊聊"

推进时的自然过渡：
  "是这样的..." / "说白了..." / "就是说..."
  "您看这样行不行..." / "要不我们这样..."

感兴趣后的收拢：
  语气自然加速，兴奋感自然流露
  "好！那就这样..." / "行，我现在就..."

挽回时的角度切换信号：
  "我换个角度跟您说..." / "您先别急着拒绝，我就问您一个问题..."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【把专业词汇翻译成客户听得懂的日常语言】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ AI方式：  "您的搜索流量最近有点收缩哈"
✅ 真人方式："最近是不是感觉进店的人变少了？"

常见翻译参考：
- 搜索流量下滑 → 进店的人变少了
- 权重下降 → 排名往下掉了
- 转化率低 → 看的人多买的人少
- 曝光不足 → 客户找不到您
- 付费流量为零 → 完全靠自然流量，没做过推广

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【绝对禁止】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- 读简历式开场："我看到您是XX类目的老板，您的数据显示..."
- 客户感兴趣后继续介绍产品（Loquacity Penalty，直接失败）
- 两次拒绝用同样角度挽回
- 退出时不留 Next Action："好的再见，有需要联系我们"
- 防御性辩护："我们平台有XX资质证书，效果绝对有保障"
- 开头："您好，感谢您接听电话"
- 结尾："祝您生活愉快，期待与您的合作"
- 直接用行业术语描述问题（"搜索流量收缩""权重下滑""转化率偏低"）而不翻译成日常语言

【输出格式】只输出对话，不要任何说明：
[CCO]: xxx
[客户]: xxx
"""


# ═══════════════════════════════════════════════════════════════════════════════
# PART 3: Base 模型对比 System Prompt
# ═══════════════════════════════════════════════════════════════════════════════

BASE_SYSTEM_PROMPT = """你是一个智能销售客服系统，负责拨打外呼销售电话。
根据给定的场景和客户信息，生成一段销售对话。
格式：[客服]: xxx  [客户]: xxx"""


# ═══════════════════════════════════════════════════════════════════════════════
# PART 4: 动态 User Prompt 构建
# ═══════════════════════════════════════════════════════════════════════════════

def build_context_text(context_json: dict) -> str:
    lines = []
    for k, v in context_json.items():
        if isinstance(v, dict):
            lines.append(f"  {k}：")
            for sk, sv in v.items():
                lines.append(f"    {sk}：{sv}")
        else:
            lines.append(f"  {k}：{v}")
    return "\n".join(lines)


def build_cco_user_prompt(scenario_key: str, rejection_state: str) -> str:
    scenario = BUSINESS_SCENARIOS[scenario_key]
    state = CUSTOMER_REJECTION_STATES[rejection_state]

    # 长期记忆场景的特殊提示
    memory_note = ""
    if scenario.get("memory_opener"):
        memory_note = f"""
【长期记忆要求】
这是第{scenario["round"]}轮跟进通话，开场必须引用历史沟通内容：
  参考开场："{scenario["memory_opener"]}"
  不能像第一次认识一样开场，客户会感觉CCO根本没记住之前聊过什么
"""

    # 产品推进提示
    product_note = ""
    if scenario.get("close_action"):
        product_note = f"""
【闭环动作要求】
本轮对话的目标闭环动作：{scenario["close_action"]}
一旦客户释放兴趣信号，立刻给出具体操作路径，不要继续铺垫
"""

    # 召回场景的特殊角度
    recall_note = ""
    if scenario.get("recall_angle"):
        recall_note = f"""
【召回角度要求】
{scenario["recall_angle"]}
"""

    turns_map = {
        "interested":  "6-10轮，客户感兴趣后立刻收拢，节奏快",
        "hesitant":    "8-12轮，客户推脱但CCO在退出前建立了Next Action",
        "rejecting":   "10-16轮，至少2次不同角度的挽回，第3次优雅退出并留钩子",
        "skeptical":   "10-14轮，先共情再反客为主，把质疑变成聊需求的入口"
    }

    return f"""场景：{scenario["name"]}（第{scenario["round"]}轮通话）
CCO角色：平台销售专员

【客户背景信息 Context_JSON】
{build_context_text(scenario["context_json"])}

【本次通话目标】
{scenario["goal"]}

【核心考验技能】
{scenario["key_skill"]}

【客户状态】
类型：{state["name"]}
描述：{state["desc"]}
行为特征：{state["behavior"]}
核心测试点：{state["key_test"]}
{memory_note}{product_note}{recall_note}
【对话轮次参考】{turns_map[rejection_state]}

关键提醒：
- CCO先开口，开场用信息揉合而非报告式介绍
- {"本轮禁止推销产品，只做价值输出" if scenario.get("forbidden") else "适时推进产品，但不要在客户感兴趣时继续铺垫"}
- 根据客户状态走对应策略，不要机械执行脚本

现在开始生成对话："""


def build_base_user_prompt(scenario_key: str, rejection_state: str) -> str:
    scenario = BUSINESS_SCENARIOS[scenario_key]
    state = CUSTOMER_REJECTION_STATES[rejection_state]

    ctx = scenario["context_json"]
    ctx_simple = "\n".join([
        f"{k}：{v}" if not isinstance(v, dict) else f"{k}：{str(v)[:60]}..."
        for k, v in ctx.items()
    ])

    return f"""场景：{scenario["name"]}
客服角色：平台销售专员
客户信息：
{ctx_simple}
通话目标：{scenario["goal"]}
客户状态：{state["name"]} - {state["desc"]}

生成销售对话："""


# ═══════════════════════════════════════════════════════════════════════════════
# PART 5: 批量生成计划
# ═══════════════════════════════════════════════════════════════════════════════

GENERATION_PLAN = [
    # (场景, 客户状态, 生成数量, 说明)

    # 新客户建联：重点测信息揉合+闭环保存
    ("new_client",      "interested",  3, "新客建联·有兴趣·测转化果断度"),
    ("new_client",      "hesitant",    3, "新客建联·犹豫·测Next Action"),
    ("new_client",      "skeptical",   3, "新客建联·质疑·测共情反客为主"),
    ("new_client",      "rejecting",   3, "新客建联·拒绝·测多轮挽回"),

    # 增值推进第3轮：重点测长期记忆+转化果断度
    ("upsell_round3",   "interested",  4, "增值推进·有兴趣·测转化果断度⭐"),
    ("upsell_round3",   "hesitant",    4, "增值推进·犹豫·测闭环保存"),
    ("upsell_round3",   "rejecting",   3, "增值推进·拒绝·测多轮挽回"),
    ("upsell_round3",   "skeptical",   3, "增值推进·质疑·测价值重塑"),

    # 续费/召回：重点测历史记忆+挽回韧性
    ("renewal_recall",  "interested",  3, "续费召回·有兴趣·测收拢速度"),
    ("renewal_recall",  "hesitant",    4, "续费召回·犹豫·测Next Action"),
    ("renewal_recall",  "rejecting",   4, "续费召回·拒绝·测挽回角度递进"),
    ("renewal_recall",  "skeptical",   3, "续费召回·质疑·测价值重塑"),
]
# 合计：CCO风格 40条 + Base风格 40条 = 80条销售型对话


def print_plan_summary():
    print("=" * 65)
    print("销售型场景 数据生成计划")
    print("=" * 65)
    total = 0
    for scene, state, count, note in GENERATION_PLAN:
        sname = BUSINESS_SCENARIOS[scene]["name"]
        sstate = CUSTOMER_REJECTION_STATES[state]["name"]
        print(f"  {sname} × {sstate}: {count}条  [{note}]")
        total += count
    print("-" * 65)
    print(f"  CCO风格合计：{total}条")
    print(f"  Base风格合计：{total}条")
    print(f"  总计：{total * 2}条")
    print()
    print("⚠️  不覆盖的场景：")
    print("  完全陌生的流失客户（从未服务过）→ AI能力暂不适合，建议直接转人工")
    print()
    print("核心设计意图：")
    print("  · 新客建联：Base会读简历，CCO会揉合背景信息自然开场")
    print("  · 增值推进：Base没有历史记忆，CCO会明确引用上轮沟通内容")
    print("  · 转化果断：客户感兴趣时，Base继续介绍产品，CCO立刻收拢")
    print("  · 多轮挽回：Base重复同一话术，CCO每轮换不同角度")
    print("  · 闭环保存：Base说再见就走，CCO退出前必须留Next Action")
    print("=" * 65)


# ═══════════════════════════════════════════════════════════════════════════════
# PART 6: 使用示例
# ═══════════════════════════════════════════════════════════════════════════════

def demo():
    print("【CCO风格 System Prompt（节选）】")
    print("-" * 60)
    print(CCO_SYSTEM_PROMPT[:600] + "...[截断]")

    print("\n\n【示例 CCO User Prompt：增值推进第3轮 × 有兴趣型客户】")
    print("-" * 60)
    print(build_cco_user_prompt("upsell_round3", "interested"))

    print("\n\n【对比用 Base User Prompt：相同场景，无拟人指令】")
    print("-" * 60)
    print(build_base_user_prompt("upsell_round3", "interested"))

    print("\n\n【生成计划摘要】")
    print_plan_summary()

    print("\n\n【接入 LLM API 的调用方式】")
    print("-" * 60)
    print("""
import os, json
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL")
)

results = []
for scenario_key, rejection_state, count, _ in GENERATION_PLAN:
    for i in range(count):

        cco = client.chat.completions.create(
            model=os.getenv("LLM_MODEL_NAME"),
            messages=[
                {"role": "system", "content": CCO_SYSTEM_PROMPT},
                {"role": "user",   "content": build_cco_user_prompt(
                    scenario_key, rejection_state)}
            ],
            temperature=0.85
        )

        base = client.chat.completions.create(
            model=os.getenv("LLM_MODEL_NAME"),
            messages=[
                {"role": "system", "content": BASE_SYSTEM_PROMPT},
                {"role": "user",   "content": build_base_user_prompt(
                    scenario_key, rejection_state)}
            ],
            temperature=0.7
        )

        results.append({
            "id": f"{scenario_key}_{rejection_state}_{i}",
            "scenario": scenario_key,
            "rejection_state": rejection_state,
            "type": "CCO",
            "dialog": cco.choices[0].message.content
        })
        results.append({
            "id": f"{scenario_key}_{rejection_state}_{i}_base",
            "scenario": scenario_key,
            "rejection_state": rejection_state,
            "type": "Base",
            "dialog": base.choices[0].message.content
        })

with open("data_synthesis/outputs/sales_dialogs.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"完成，共 {len(results)} 条对话")
""")


if __name__ == "__main__":
    demo()
