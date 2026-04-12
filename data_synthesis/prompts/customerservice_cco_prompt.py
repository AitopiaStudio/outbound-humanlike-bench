#!/usr/bin/env python3
"""
客服型场景 CCO 风格数据合成 Prompt
======================================
场景特征：
  - 客户主动拨入，CCO 被动承接
  - 核心挑战：将书面 FAQ / 专业术语转化为客户能听懂的口语表达
  - 客户情绪复杂，需要先稳情绪再解决问题

与通知型的根本差异：
  - 通知型：CCO 掌握主动权，按计划说完信息
  - 客服型：客户掌握主动权，CCO 必须先"听懂"再"转化"再"输出"
  - 拟人化难点不在于"怎么说"，而在于"有没有真正理解客户问的是什么"

覆盖问题类型（4类）：
  1. 订单类   订单失效原因 + 后续处理流程（多信息点串联）
  2. 规则类   平台现有规则的具体内容解释
  3. 数据类   专业名词解释（转化率、同行对比等）
  4. 投诉类   客户认为规则不合理，有明显情绪

客户情绪状态（4种，按频率排序）：
  A. 焦急型   有问题要立刻解决，语速快，容易打断
  B. 困惑型   不懂，需要解释，可能要解释不止一遍
  C. 质疑型   对规则或结果有异议，有情绪，需要先安抚
  D. 追问型   理解了一个点还想继续深挖，问题一个接一个
"""

from typing import Dict, Any

# ═══════════════════════════════════════════════════════════════════════════════
# PART 1: 场景配置
# ═══════════════════════════════════════════════════════════════════════════════

BUSINESS_SCENARIOS: Dict[str, Any] = {

    # ── 场景1：订单类 · 订单失效原因+后续流程（多信息点）────────────────────
    "order_invalid": {
        "name": "订单失效原因及处理流程",
        "type": "order",
        "faq_content": {
            "原因": "订单超过48小时未付款系统自动关闭；或商品库存不足被平台自动取消；或买家/卖家手动取消",
            "流程": "失效订单无法恢复，需重新下单；若是库存问题商家会在3个工作日内联系买家；退款（如有预付）原路退回1-3工作日",
            "注意": "失效订单不影响账户信用分，不会有任何处罚"
        },
        "human_explanation": {
            "原因口语化": "就是说您这个订单可能是超时没付款被系统自动关了，或者商家那边库存不够了",
            "流程口语化": "失效的订单没办法恢复，您需要重新下一个。退款的话如果有预付，原路退回去就行，一般1到3天",
            "安抚": "这个不影响您的账户，放心"
        },
        "multi_info_points": True,
        "info_count": 2
    },

    # ── 场景2：规则类 · 平台规则解释───────────────────────────────────────────
    "platform_rules": {
        "name": "平台活动报名规则解释",
        "type": "rules",
        "faq_content": {
            "报名条件": "店铺综合评分≥4.6分，近30天无严重违规记录，商品库存≥10件，参与品类需与店铺主营一致",
            "审核时间": "提交后24-48小时内完成审核，节假日顺延",
            "未通过原因": "最常见：库存不足、评分不达标、品类不符"
        },
        "human_explanation": {
            "条件口语化": "简单说就是您店铺评分得到4.6以上，最近没有被处罚过，然后这个商品库存得有10件以上",
            "审核口语化": "提交了一般一两天就出结果，赶上节假日可能会晚一点",
            "未通过口语化": "没过的话大部分是库存不够或者评分差一点点，您可以在后台看一下具体原因"
        },
        "multi_info_points": True,
        "info_count": 3
    },

    # ── 场景3：数据类 · 专业名词解释（转化率+同行对比）──────────────────────
    "data_explanation": {
        "name": "转化率及同行对比数据解释",
        "type": "data",
        "faq_content": {
            "转化率定义": "商品转化率=成交订单数/商品访客数×100%，反映访客转化为买家的比例",
            "同行均值": "平台根据相同类目、相近价格带、相近月销量的店铺计算行业均值，每周更新",
            "偏低原因": "常见原因：主图点击率低、详情页跳出率高、价格竞争力不足、评价质量差"
        },
        "human_explanation": {
            "转化率口语化": "就是说100个人看了您这个商品，最后有几个人下单，这个比例就是转化率。比如100个人看，5个人买，就是5%",
            "同行口语化": "平台会把跟您差不多的店——同类目、差不多价位的——的转化率平均一下，作为参考",
            "偏低口语化": "转化率低的话，一般是主图不够吸引人，或者进来看了觉得价格不值，就走了"
        },
        "multi_info_points": True,
        "info_count": 2,
        "has_analogy": True  # 这类场景CCO必须用类比解释
    },

    # ── 场景4：投诉类 · 客户对规则有情绪──────────────────────────────────────
    "rule_complaint": {
        "name": "规则申诉及情绪安抚",
        "type": "complaint",
        "faq_content": {
            "申诉条件": "违规处罚后7天内可发起申诉，需提供证明材料，申诉成功率约30%",
            "申诉流程": "商家后台→违规记录→申诉→上传材料→等待审核（3-5工作日）",
            "不可申诉": "部分严重违规（售假、欺诈）不支持申诉"
        },
        "human_explanation": {
            "安抚话术": "您的心情我理解，这种情况确实让人着急",
            "申诉口语化": "您可以去后台的违规记录那里，有个申诉的按钮，把相关证明上传上去，一般3到5天出结果",
            "预期管理": "申诉的话我也跟您说实话，通过率不是特别高，但您有证明材料的话还是值得试一下"
        },
        "multi_info_points": False,
        "requires_emotion_first": True  # 必须先处理情绪再解决问题
    }
}

CUSTOMER_STATES = {
    "anxious": {
        "name": "焦急型",
        "frequency": "高频",
        "desc": "有问题要立刻解决，语速快，可能在CCO说到一半就打断追问，希望得到明确答案而非模糊回复",
        "behavior": "客户开口就直奔问题，中途可能打断，CCO需要先让客户把话说完，再简短给出明确答案",
        "trap": "AI陷阱：给出冗长的解释反而让焦急型客户更烦躁"
    },
    "confused": {
        "name": "困惑型",
        "frequency": "高频",
        "desc": "不懂平台规则或专业术语，需要用类比或举例解释，可能需要解释不止一遍",
        "behavior": "客户会说'我不太明白''什么意思'，CCO需要换一种更简单的方式重新解释",
        "trap": "AI陷阱：用更多专业术语解释专业术语，越解释越乱"
    },
    "skeptical": {
        "name": "质疑型",
        "frequency": "高频",
        "desc": "对规则结果有异议，认为平台规则不合理，有明显情绪，需要先稳情绪再讲道理",
        "behavior": "客户会说'这不公平''凭什么'，CCO必须先表示理解，不能立刻讲规则，否则会激化情绪",
        "trap": "AI陷阱：直接引用规则条文，完全忽视情绪，导致客户更激动"
    },
    "inquisitive": {
        "name": "追问型",
        "frequency": "低频",
        "desc": "理解能力强，但好奇心重，每个答案后面还有下一个问题，CCO需要保持耐心和节奏",
        "behavior": "客户每次得到解释后会继续追问细节，CCO需要判断哪些值得继续解释，哪些可以引导自行查看",
        "trap": "AI陷阱：对每个追问都给出同等长度的详细解释，导致对话无法结束"
    }
}


# ═══════════════════════════════════════════════════════════════════════════════
# PART 2: CCO 风格 System Prompt
# ═══════════════════════════════════════════════════════════════════════════════

CCO_SYSTEM_PROMPT = """你是专门生成【真实人类客服CCO风格】电话对话的专家。

客服型场景的根本逻辑：
客户打进来 → CCO先听懂客户真正在问什么 → 把书面答案转化成口语 → 用客户能听懂的方式说出来

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【硬性规则：违反即触发Veto】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【单轮长度限制】每轮CCO回复严格不超过50字。
客户在电话里无法消化长段内容，真人客服会说一段停一下。
说完一个要点后必须给客户说话的机会，或者问"您明白了吗"。

【FAQ必须口语化】绝对不能直接念FAQ原文。
必须用"就是说""说白了""打个比方"引出解释，用数字举例。
✅ "就是说100个人看您商品，5个买了，就是5%的转化率"
❌ "转化率是指成交订单数除以访客数所得的百分比"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【客服型最核心的拟人化挑战：FAQ 口语化】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

这是真人CCO和AI最大的区别所在。

❌ AI的典型失误（直接念FAQ）：
客户："为什么我的转化率低？"
AI："您好，根据平台数据显示，商品转化率是指成交订单数与商品访客数的比值，
    影响转化率的因素主要包括：1.主图点击率 2.详情页停留时长 3.价格竞争力..."

✅ 真人CCO的方式（先理解，再类比，再给方向）：
CCO："转化率低啊...简单说就是，100个人看了您这个商品，最后有几个买的，
     这个比例就是转化率。您这个数据低，一般是主图不够吸引人，或者进来
     看了觉得价格不合适就走了。您现在大概是什么水平？"

真人口语化解释的三个关键技巧：
1. 先用"就是说""简单讲""说白了"把书面内容转口语
2. 立刻跟一个具体的类比或例子（数字举例最有效）
3. 解释完主动确认客户听懂了（"您明白我意思吗？"）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【情绪处理：不同客户状态的应对方式】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

焦急型客户：
  ✅ 先让客户说完，立刻给明确答案，不解释太多
  ❌ 长篇大论解释背景，客户更烦

困惑型客户：
  ✅ 换更简单的类比重新解释，问"这样说您懂了吗"
  ❌ 用更多术语解释术语

质疑型客户（最难）：
  ✅ 第一句必须是共情："您这个情况确实让人着急/我理解您的感受"
  ✅ 然后才能讲规则，且要用"但是我们这边..."而非直接引用条文
  ❌ 直接引用规则条文，完全忽视情绪

追问型客户：
  ✅ 回答完后主动给出"下一步"引导，减少无效追问
  ❌ 对每个问题都给同等详细的回答，对话永远结束不了

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【真人CCO必须具备的语言特征】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 先复述/确认客户问题（真人会先理解再回答）
   "您是说订单被关掉了，对吧？" / "您问的是转化率为什么低，是吗？"

2. 口语化解释的标志词
   "就是说" / "简单讲" / "说白了就是" / "您可以这样理解"

3. 类比举例
   "打个比方" / "就好比" / "比如说100个人进来，5个买了，那就是5%"

4. 自然停顿与犹豫（查系统、思考时）
   "嗯...让我看一下" / "您稍等，我查一下您的订单"

5. 主动确认理解
   "您明白我意思吗？" / "这样说您懂了吗？" / "您还有什么不清楚的？"

6. 省略主语、短句
   "进后台看一下" / "对，就是那个" / "查到了"

7. 倒装追补
   "处理完了这个" / "退款没问题的这个"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【绝对禁止】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- 直接念FAQ原文：长句、术语密集、像在背课文
- 条目化回答：1.xxx 2.xxx 3.xxx
- 忽视情绪直接讲规则（质疑型客户场景）
- 开头客套："您好，感谢您致电XX客服"
- 结尾客套："祝您生活愉快，再见"
- 用更多术语解释术语

【输出格式】只输出对话，不要任何说明：
[客户]: xxx
[CCO]: xxx
"""


# ═══════════════════════════════════════════════════════════════════════════════
# PART 3: Base 模型对比 System Prompt
# ═══════════════════════════════════════════════════════════════════════════════

BASE_SYSTEM_PROMPT = """你是一个智能客服系统，负责接听客户来电并解答问题。
根据给定的场景和FAQ内容，生成一段客服对话。
格式：[客户]: xxx  [客服]: xxx"""


# ═══════════════════════════════════════════════════════════════════════════════
# PART 4: 动态 User Prompt 构建
# ═══════════════════════════════════════════════════════════════════════════════

def build_faq_text(scenario: dict) -> str:
    """将 FAQ 内容格式化为 prompt 文本"""
    faq = scenario["faq_content"]
    return "\n".join([f"  【{k}】{v}" for k, v in faq.items()])


def build_human_explanation_text(scenario: dict) -> str:
    """将口语化解释参考格式化为 prompt 文本"""
    exp = scenario["human_explanation"]
    return "\n".join([f"  {k}：{v}" for k, v in exp.items()])


def build_cco_user_prompt(scenario_key: str, state_key: str) -> str:
    scenario = BUSINESS_SCENARIOS[scenario_key]
    state = CUSTOMER_STATES[state_key]

    turns_guide = {
        "anxious":    "6-10轮，客户说话快，CCO回答要简短直接，避免长篇解释",
        "confused":   "10-16轮，可能需要换方式解释2次，耐心引导",
        "skeptical":  "8-14轮，第一轮CCO必须是共情，不能直接讲规则",
        "inquisitive": "12-18轮，客户会持续追问，CCO需要适时引导去自助查询"
    }

    multi_info_note = ""
    if scenario.get("multi_info_points"):
        multi_info_note = f"""
【多信息点串联要求】
这个场景需要解释 {scenario["info_count"]} 个信息点。
串联时禁止用"第一、第二"，改用口语过渡词：
  "还有一个" / "对了" / "另外" / "说完这个，还有一点"
"""

    analogy_note = ""
    if scenario.get("has_analogy"):
        analogy_note = """
【类比解释要求】
这是数据类问题，CCO必须用具体数字举例：
  ✅ "比如100个人看，5个下单，就是5%的转化率"
  ❌ "转化率是成交量除以访客量的百分比"（直接定义，客户听不懂）
"""

    emotion_note = ""
    if scenario.get("requires_emotion_first"):
        emotion_note = """
【情绪优先要求】
投诉类场景：CCO第一句话必须是共情，绝对不能直接讲规则！
  ✅ "您这个情况确实让人着急，我理解"
  ❌ "根据平台规定，违规处罚后7天内可发起申诉..."（冷漠，会激化情绪）
"""

    return f"""场景：{scenario["name"]}（{scenario["type"]}类问题）
CCO角色：电商平台客服专员

【客户情绪状态】
类型：{state["name"]}（{state["frequency"]}场景）
描述：{state["desc"]}
行为特征：{state["behavior"]}
⚠️ 注意陷阱：{state["trap"]}

【FAQ 原始内容（书面版，不能直接念）】
{build_faq_text(scenario)}

【口语化表达参考（CCO应该这样说）】
{build_human_explanation_text(scenario)}
{multi_info_note}{analogy_note}{emotion_note}
【对话轮次】{turns_guide[state_key]}

关键提醒：
- 客户先开口，CCO先听懂再回答
- FAQ内容必须转化为口语，不能直接念原文
- 根据客户情绪状态调整应对策略

现在开始生成对话（客户先说）："""


def build_base_user_prompt(scenario_key: str, state_key: str) -> str:
    scenario = BUSINESS_SCENARIOS[scenario_key]
    state = CUSTOMER_STATES[state_key]
    faq_simple = "\n".join([f"{k}：{v}" for k, v in scenario["faq_content"].items()])

    return f"""场景：{scenario["name"]}
客服类型：电商平台客服
客户情绪：{state["name"]} - {state["desc"]}

FAQ参考内容：
{faq_simple}

生成对话（客户先说）：
[客户]: xxx
[客服]: xxx"""


# ═══════════════════════════════════════════════════════════════════════════════
# PART 5: 批量生成计划
# ═══════════════════════════════════════════════════════════════════════════════

GENERATION_PLAN = [
    # (场景, 客户状态, 生成数量, 说明)
    # 焦急型+困惑型优先，因为频率最高
    ("order_invalid",    "anxious",    4, "订单失效·焦急型·高频"),
    ("order_invalid",    "confused",   4, "订单失效·困惑型·高频"),
    ("order_invalid",    "skeptical",  3, "订单失效·质疑型·高频"),

    ("platform_rules",   "confused",   4, "规则解释·困惑型·高频"),
    ("platform_rules",   "skeptical",  3, "规则解释·质疑型·高频"),
    ("platform_rules",   "anxious",    3, "规则解释·焦急型·高频"),

    ("data_explanation", "confused",   4, "数据解释·困惑型·类比关键"),
    ("data_explanation", "inquisitive",3, "数据解释·追问型·低频"),
    ("data_explanation", "anxious",    3, "数据解释·焦急型"),

    ("rule_complaint",   "skeptical",  4, "投诉申诉·质疑型·情绪最复杂"),
    ("rule_complaint",   "anxious",    3, "投诉申诉·焦急型"),
    ("rule_complaint",   "inquisitive",2, "投诉申诉·追问型"),
]
# 合计：CCO风格 40条 + Base风格 40条 = 80条客服型对话


def print_plan_summary():
    print("=" * 65)
    print("客服型场景 数据生成计划")
    print("=" * 65)
    total = 0
    for scene, state, count, note in GENERATION_PLAN:
        sname = BUSINESS_SCENARIOS[scene]["name"]
        sstate = CUSTOMER_STATES[state]["name"]
        print(f"  {sname} × {sstate}: {count}条  [{note}]")
        total += count
    print("-" * 65)
    print(f"  CCO风格合计：{total}条")
    print(f"  Base风格合计：{total}条")
    print(f"  总计：{total * 2}条")
    print()
    print("核心设计意图：")
    print("  · FAQ口语化：Base模型会直接念FAQ原文，CCO会类比+举例转化")
    print("  · 情绪处理：质疑型场景测试CCO能否先共情再讲规则")
    print("  · 术语解释：数据类场景测试CCO能否用数字举例而非术语定义")
    print("  · 多信息串联：订单/规则类测试能否用口语过渡词而非1.2.3.")
    print("=" * 65)


# ═══════════════════════════════════════════════════════════════════════════════
# PART 6: 使用示例
# ═══════════════════════════════════════════════════════════════════════════════

def demo():
    print("【CCO风格 System Prompt（节选）】")
    print("-" * 60)
    print(CCO_SYSTEM_PROMPT[:600] + "...[截断]")

    print("\n\n【示例 CCO User Prompt：数据解释 × 困惑型客户】")
    print("-" * 60)
    print(build_cco_user_prompt("data_explanation", "confused"))

    print("\n\n【对比用 Base User Prompt：相同场景，无拟人指令】")
    print("-" * 60)
    print(build_base_user_prompt("data_explanation", "confused"))

    print("\n\n【生成计划摘要】")
    print_plan_summary()

    print("\n\n【接入 LLM API 的调用方式（与通知型相同）】")
    print("-" * 60)
    print("""
import os, json
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL")
)

results = []
for scenario_key, state_key, count, _ in GENERATION_PLAN:
    for i in range(count):

        # CCO 风格（含拟人指令）
        cco = client.chat.completions.create(
            model=os.getenv("LLM_MODEL_NAME"),
            messages=[
                {"role": "system", "content": CCO_SYSTEM_PROMPT},
                {"role": "user",   "content": build_cco_user_prompt(scenario_key, state_key)}
            ],
            temperature=0.85
        )

        # Base 对比（无任何拟人指令）
        base = client.chat.completions.create(
            model=os.getenv("LLM_MODEL_NAME"),
            messages=[
                {"role": "system", "content": BASE_SYSTEM_PROMPT},
                {"role": "user",   "content": build_base_user_prompt(scenario_key, state_key)}
            ],
            temperature=0.7
        )

        results.append({
            "id": f"{scenario_key}_{state_key}_{i}",
            "scenario": scenario_key,
            "state": state_key,
            "type": "CCO",
            "dialog": cco.choices[0].message.content
        })
        results.append({
            "id": f"{scenario_key}_{state_key}_{i}_base",
            "scenario": scenario_key,
            "state": state_key,
            "type": "Base",
            "dialog": base.choices[0].message.content
        })

with open("data_synthesis/outputs/customerservice_dialogs.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"完成，共 {len(results)} 条对话")
""")


if __name__ == "__main__":
    demo()
