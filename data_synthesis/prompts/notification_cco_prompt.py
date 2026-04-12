#!/usr/bin/env python3
"""
通知型场景 CCO 风格数据合成 Prompt v2
========================================
更新说明（v2）：
  - 所有场景升级为 2-3 件并列事项，真实还原多事件通话场景
  - 新增「优先级关系」场景（风险提示 + 后续排查），模拟先急后缓的通话逻辑
  - CCO prompt 明确教授多事件的口语化串联方式
  - Base prompt 保持极简，让模型自然暴露条目化倾向
  - 客户状态重新设计，增加「半途打断」状态提升区分度

核心设计目的：
  在多事件场景下，Base 模型会本能地使用"第一/其次/最后"等条目化结构，
  而 CCO 风格会用口语过渡词自然串联。这才是「不条目化堆砌」维度真正的区分场景。

覆盖场景（4类）：
  1. 并列-电商大促报名      2件并列任务需同时完成
  2. 并列-账户安全+操作引导  2件并列但有轻重之分
  3. 并列-会员权益到期+续费  2件并列（通知+行动引导）
  4. 优先级-风险提示+排查指引 先急后缓，2件有明显优先级

客户状态（4种）：
  A. 配合型    直接配合，确认即结束
  B. 追问型    对其中一件事有细节疑问
  C. 阻断型    当前不方便，需留下核心信息后优雅退出
  D. 半途打断型 听到第一件事就插话，CCO需灵活接话再带出第二件事
"""

from typing import Dict, Any

# ═══════════════════════════════════════════════════════════════════════════════
# PART 1: 场景配置（全部升级为多事件）
# ═══════════════════════════════════════════════════════════════════════════════

BUSINESS_SCENARIOS: Dict[str, Any] = {

    # ── 场景1：并列关系 · 电商大促报名（2件并列任务）──────────────────────
    "ecommerce_promo": {
        "name": "大促活动报名通知",
        "logic": "parallel",  # 并列关系
        "context": {
            "company": "XX电商平台运营中心",
            "agent_name": "小林",
            "customer_name": "陈老板",
            "event_count": 2,
            "events": [
                {
                    "priority": 1,
                    "title": "主会场报名",
                    "detail": "双十一主会场报名截止明天晚上12点，需要在商家后台'营销活动'里提交报名，审核一般2小时",
                    "urgency": "高，明天截止"
                },
                {
                    "priority": 2,
                    "title": "满减券设置",
                    "detail": "报名主会场的同时要配套设置满减券，在'优惠工具'里选'平台大促满减'，建议设个满200减20的",
                    "urgency": "中，配套动作"
                }
            ],
            "app_guide": "商家后台→营销活动→双十一报名，满减券在旁边的'优惠工具'里",
            "follow_up_qa": {
                "截止时间能延吗": "这个平台统一截止的，延不了，您今天有空就先提交一下哈",
                "满减券必须设吗": "不是强制的，但设了会提升曝光权重，建议还是设一个",
                "审核没通过怎么办": "审核不通过会有站内信说明原因，您可以修改后重新提交"
            }
        }
    },

    # ── 场景2：并列关系 · 账户安全通知（2件并列，有轻重之分）──────────────
    "account_security": {
        "name": "账户安全提醒",
        "logic": "parallel",
        "context": {
            "company": "XX银行风控中心",
            "agent_name": "小张",
            "customer_name": "刘女士",
            "event_count": 2,
            "events": [
                {
                    "priority": 1,
                    "title": "异常登录提醒",
                    "detail": "您的账户昨晚11点有一笔异地登录记录，登录地是广州，想确认一下是不是您本人操作的",
                    "urgency": "高，需先确认"
                },
                {
                    "priority": 2,
                    "title": "密码修改建议",
                    "detail": "如果不是您本人操作，建议您尽快在APP里修改一下登录密码，同时把绑定手机号也核对一遍",
                    "urgency": "中，视第一件确认结果而定"
                }
            ],
            "app_guide": "APP→我的→账户安全→修改密码，顺便在'绑定信息'里核对一下手机号",
            "follow_up_qa": {
                "是我自己登的": "那就好，您平时注意不要在公共网络登录，我就不打扰您了哈",
                "不是我操作的": "那您现在方便的话先冻结一下账户，APP里有一键冻结，我等您操作",
                "怎么冻结": "APP首页右上角有个盾牌图标，点进去就能看到账户冻结的选项"
            }
        }
    },

    # ── 场景3：并列关系 · 会员到期+续费引导（2件并列）──────────────────────
    "membership_expiry": {
        "name": "会员权益到期及续费通知",
        "logic": "parallel",
        "context": {
            "company": "XX视频平台会员中心",
            "agent_name": "小王",
            "customer_name": "李先生",
            "event_count": 2,
            "events": [
                {
                    "priority": 1,
                    "title": "权益即将到期",
                    "detail": "您的年度会员还有3天到期，到期后4K画质和离线下载这两个功能会关掉",
                    "urgency": "中，3天后到期"
                },
                {
                    "priority": 2,
                    "title": "续费优惠窗口",
                    "detail": "现在续费有个老用户专属价，年费从198降到148，这个价格只有到期前3天才有，过了就没了",
                    "urgency": "高，限时优惠"
                }
            ],
            "app_guide": "APP右下角'我的'→'会员中心'→续费，优惠价格在那里能直接看到",
            "follow_up_qa": {
                "不续费会怎样": "4K和下载功能会关掉，已下载的内容还在，不会删",
                "只想续半年": "现在只有年费的优惠，半年费没有这个折扣，年费算下来更划算",
                "可以退款吗": "续费之后是不支持退款的，您确认要续再操作哈"
            }
        }
    },

    # ── 场景4：优先级关系 · 风险提示+排查指引（先急后缓）──────────────────
    "risk_alert": {
        "name": "店铺风险提示及排查指引",
        "logic": "priority",  # 优先级关系
        "context": {
            "company": "XX电商平台商家服务中心",
            "agent_name": "小陈",
            "customer_name": "赵老板",
            "event_count": 2,
            "events": [
                {
                    "priority": 1,
                    "title": "店铺违规风险提示",
                    "detail": "您店铺有一个商品描述被系统标记了，有违规风险，如果48小时内不处理可能会影响店铺评分",
                    "urgency": "高，48小时内需处理"
                },
                {
                    "priority": 2,
                    "title": "后续排查建议",
                    "detail": "除了这个商品，建议您把近期上架的新品也检查一遍，主要看主图和标题有没有夸大宣传的词，"
                              "平台最近对这块查得比较严",
                    "urgency": "中，预防性动作，不紧急但重要"
                }
            ],
            "app_guide": "商家后台→违规记录→找到标记商品→点处理，修改描述后重新提交审核",
            "follow_up_qa": {
                "哪个商品被标记了": "您后台违规记录里能看到具体是哪一条，一般是标题或者主图的问题",
                "影响会有多大": "48小时不处理的话店铺健康分会扣，扣够了会影响搜索权重",
                "怎么排查其他商品": "重点看标题里有没有'第一''最好''100%'这类词，这些最容易被标记"
            }
        }
    }
}

CUSTOMER_STATES = {
    "cooperative": {
        "name": "配合型",
        "desc": "客户态度配合，听完两件事都表示了解，无深度追问，简短结束",
        "behavior": "客户会对两件事分别简短确认，不深挖细节，整体通话干净利落"
    },
    "inquisitive": {
        "name": "追问型",
        "desc": "客户对其中一件事（通常是第二件或更重要的那件）有1-2个细节疑问",
        "behavior": "客户听完第一件事后配合，但听到第二件事时会问一两个细节，CCO解答后才满意结束"
    },
    "interrupted": {
        "name": "阻断型",
        "desc": "客户在CCO说完第一件事后就表示当前不方便，CCO需要判断第二件是否必须说、如何简短交代后优雅退出",
        "behavior": "CCO需要在退出前判断第二件事的紧急程度，紧急的简短说完，不紧急的可以告知后续跟进方式"
    },
    "mid_interrupt": {
        "name": "半途打断型",
        "desc": "客户在CCO说第一件事的过程中就插话（追问或表达意见），CCO需要先处理插话再自然带出第二件事",
        "behavior": "测试CCO能否在被打断后流畅地接话，并在合适时机用口语方式过渡到第二件事，"
                    "而不是机械地说'接下来说第二点'"
    }
}


# ═══════════════════════════════════════════════════════════════════════════════
# PART 2: CCO 风格 System Prompt（核心：多事件口语化串联）
# ═══════════════════════════════════════════════════════════════════════════════

CCO_SYSTEM_PROMPT = """你是专门生成【真实人类客服CCO风格】外呼对话的专家。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【最高优先级：三条硬性规则，违反即失败】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

规则1【语气词必须出现在开场】
开场前两句话必须有语气词或停顿，否则客户会把你当机器人挂断。
✅ "您好，请问是XX吗？...嗯我是XX公司的小林，打扰一下哈"
❌ "您好，我是XX公司客服代表，今天致电是为了通知您..." （播音腔，直接失败）

规则2【每轮回复不超过40字】
说完一件事就停，等客户反应，不能把所有内容一口气说完。
真人打电话不会说完所有事才停，说一段停一下是本能。

规则3【每个信息只说一遍】
确认完一件事立刻进下一步，不反复强调，不重复同一意思。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【多事件串联：真人 vs AI 的根本区别】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ AI的典型失误（直接判0分）：
"我今天联系您主要有两件事：第一，您的账单金额为2847元；
 第二，您的会员权益将于3天后到期。请您知悉。"

✅ 真人CCO的方式（说完一件，自然带出另一件）：
"...账单这边就是这个情况哈。对了，还有一个事顺便跟您说一下——
 您的会员好像3天后就到期了，我看了一下，您这个级别有个续费优惠..."

真人串联多件事的口语方式（必须从以下选择，禁止用"第一第二"）：
- "还有一个事" / "对了，顺便说一下" / "另外还有件事"
- "说完这个，还有一个情况想跟您提一下"
- "这个先放一边，有个更重要的事"（优先级场景）
- "您先处理这个，还有一个配套的动作"（并列任务场景）
- "就这两件事，一个是...一个是..."（简短总结时可用，但不能用数字）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【真人CCO必须具备的其他特征】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 省略主语
   错："您需要在商家后台点击营销活动进行报名"
   对："进后台，营销活动那里，点报名就行"

2. 自然犹豫（在查信息、思考时出现）
   "嗯...让我看一下" / "就是那个...对，那个入口" / "呃，这个的话"

3. 话语标记词
   "是这样的" / "说白了" / "就是说" / "您懂我意思吗"

4. 短句/不完整句
   "对，就这样" / "嗯，到了" / "行，没问题哈"

5. 倒装追补
   "处理完了这个" / "发您短信了我" / "简单这个操作"

6. 被打断后自然接话（半途打断场景）
   客户插话后，先回应客户的话，再用"对了""说回来""还有一个事"等自然带回主题

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【绝对禁止】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- 任何数字编号："第一""其次""1.""2."
- 任何条目化过渡："首先...然后...最后..."
- 开头客套："尊敬的""非常感谢您的接听"
- 结尾客套："祝您生活愉快""如有疑问随时联系我们"
- 书面语："根据系统显示""我们将为您处理"
- 完美对称句式："A是B，C是D，E是F"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【输出格式】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
严格按格式，只输出对话，不要任何说明：
[CCO]: xxx
[客户]: xxx
"""


# ═══════════════════════════════════════════════════════════════════════════════
# PART 3: Base 模型对比 System Prompt（极简，不加任何拟人指令）
# ═══════════════════════════════════════════════════════════════════════════════

BASE_SYSTEM_PROMPT = """你是一个智能外呼客服系统。
根据给定的场景，生成一段外呼通知对话。
格式：[客服]: xxx  [客户]: xxx"""


# ═══════════════════════════════════════════════════════════════════════════════
# PART 4: 动态 User Prompt 构建
# ═══════════════════════════════════════════════════════════════════════════════

def build_events_text(scenario: dict) -> str:
    """将多事件配置转成 prompt 文本"""
    ctx = scenario["context"]
    logic = scenario["logic"]
    events = ctx["events"]

    if logic == "parallel":
        logic_desc = "并列关系：这两件事需要同时告知，没有明显的先后顺序，但第一件相对更紧急"
    else:
        logic_desc = "优先级关系：第一件事最紧急，必须先说；客户有意愿听的情况下再带出第二件事"

    events_text = f"事件逻辑：{logic_desc}\n\n"
    for e in events:
        events_text += f"事件{e['priority']}（{e['title']}，紧急度：{e['urgency']}）：\n"
        events_text += f"  {e['detail']}\n\n"
    return events_text


def build_qa_text(scenario: dict) -> str:
    """将 QA 配置转成 prompt 文本"""
    qa = scenario["context"]["follow_up_qa"]
    return "\n".join([f'  如果客户问"{q}"，回答：{a}' for q, a in qa.items()])


def build_cco_user_prompt(scenario_key: str, state_key: str) -> str:
    scenario = BUSINESS_SCENARIOS[scenario_key]
    state = CUSTOMER_STATES[state_key]
    ctx = scenario["context"]

    turns_guide = {
        "cooperative": "6-8轮，两件事都说完，客户简短确认后结束",
        "inquisitive": "10-14轮，第二件事会有1-2个追问，解答后才结束",
        "interrupted": "5-7轮，CCO判断第二件事紧急度后决定是否强行简短提及",
        "mid_interrupt": "8-12轮，客户在第一件事中途插话，CCO接话后自然带出第二件事"
    }

    return f"""场景：{scenario["name"]}
CCO：{ctx["agent_name"]}（来自{ctx["company"]}）
客户：{ctx["customer_name"]}

【需要告知的事项（共{ctx["event_count"]}件）】
{build_events_text(scenario)}
【操作引导路径】
{ctx["app_guide"]}

【客户状态】
类型：{state["name"]}
描述：{state["desc"]}
行为要求：{state["behavior"]}

【追问参考答案】
{build_qa_text(scenario)}

【对话轮次要求】
{turns_guide[state_key]}

关键提醒：
- 串联两件事时，禁止说"第一件事...第二件事"，用口语过渡词
- {"第一件事更紧急，说完必须带出第二件" if scenario["logic"]=="parallel" else "优先处理第一件，客户愿意听再说第二件"}
- 被客户打断时，先回应客户，再找时机自然带回

现在开始生成对话："""


def build_base_user_prompt(scenario_key: str, state_key: str) -> str:
    scenario = BUSINESS_SCENARIOS[scenario_key]
    state = CUSTOMER_STATES[state_key]
    ctx = scenario["context"]
    events = ctx["events"]

    events_simple = "\n".join([
        f"事项{e['priority']}：{e['title']} - {e['detail'][:50]}..."
        for e in events
    ])

    return f"""场景：{scenario["name"]}
客服：{ctx["agent_name"]}（{ctx["company"]}）
客户：{ctx["customer_name"]}
客户状态：{state["desc"]}

需要告知的事项：
{events_simple}

操作引导：{ctx["app_guide"]}

生成对话："""


# ═══════════════════════════════════════════════════════════════════════════════
# PART 5: 批量生成计划
# ═══════════════════════════════════════════════════════════════════════════════

# 优先覆盖"半途打断"和"阻断型"，因为这两种场景对多事件串联能力要求最高
GENERATION_PLAN = [
    # (场景, 客户状态, 生成数量, 说明)
    ("ecommerce_promo",   "mid_interrupt", 3, "并列任务·半途打断·最高区分度"),
    ("ecommerce_promo",   "inquisitive",   3, "并列任务·追问型"),
    ("ecommerce_promo",   "cooperative",   2, "并列任务·配合型"),
    ("ecommerce_promo",   "interrupted",   2, "并列任务·阻断型"),

    ("account_security",  "mid_interrupt", 3, "账户安全·半途打断"),
    ("account_security",  "inquisitive",   3, "账户安全·追问型"),
    ("account_security",  "cooperative",   2, "账户安全·配合型"),
    ("account_security",  "interrupted",   2, "账户安全·阻断型"),

    ("membership_expiry", "inquisitive",   3, "会员续费·追问型"),
    ("membership_expiry", "cooperative",   2, "会员续费·配合型"),
    ("membership_expiry", "interrupted",   2, "会员续费·阻断型"),

    ("risk_alert",        "mid_interrupt", 3, "风险提示·半途打断·优先级场景"),
    ("risk_alert",        "inquisitive",   3, "风险提示·追问型"),
    ("risk_alert",        "cooperative",   2, "风险提示·配合型"),
    ("risk_alert",        "interrupted",   2, "风险提示·阻断型"),
]
# 合计：CCO风格 37条 + Base风格 37条 = 74条通知型对话


def print_plan_summary():
    print("=" * 65)
    print("通知型场景 v2 数据生成计划")
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
    print("设计意图：")
    print("  · 所有场景含 2 件需告知事项，强迫模型在多事件组织上做选择")
    print("  · Base 模型面对多事件会本能条目化，CCO 用口语过渡词串联")
    print("  · 「半途打断」场景：测试被中断后能否自然带出第二件事")
    print("  · 「阻断型」场景：测试能否判断紧急度后决定是否强行提及第二件")
    print("=" * 65)


# ═══════════════════════════════════════════════════════════════════════════════
# PART 6: 使用示例
# ═══════════════════════════════════════════════════════════════════════════════

def demo():
    print("【CCO风格 System Prompt（节选）】")
    print("-" * 60)
    print(CCO_SYSTEM_PROMPT[:600] + "...[截断]")

    print("\n\n【示例 CCO User Prompt：大促报名 × 半途打断型】")
    print("-" * 60)
    print(build_cco_user_prompt("ecommerce_promo", "mid_interrupt"))

    print("\n\n【对比用 Base User Prompt：相同场景，无任何拟人指令】")
    print("-" * 60)
    print(build_base_user_prompt("ecommerce_promo", "mid_interrupt"))

    print("\n\n【生成计划摘要】")
    print_plan_summary()

    print("\n\n【接入 LLM API 的调用方式】")
    print("-" * 60)
    print("""
import os, json
from openai import OpenAI   # Qwen/Claude 同理，改 base_url

client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL")
)

results = []
for scenario_key, state_key, count, _ in GENERATION_PLAN:
    for i in range(count):

        # CCO 风格
        cco = client.chat.completions.create(
            model=os.getenv("LLM_MODEL_NAME"),
            messages=[
                {"role": "system", "content": CCO_SYSTEM_PROMPT},
                {"role": "user",   "content": build_cco_user_prompt(scenario_key, state_key)}
            ],
            temperature=0.85
        )

        # Base 对比（无拟人指令）
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

with open("data_synthesis/outputs/notification_v2_dialogs.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"完成，共 {len(results)} 条对话")
""")


if __name__ == "__main__":
    demo()
