#!/usr/bin/env python3
"""
金融行业（信用卡/贷款/理财）CCO 风格数据合成 Prompt
=====================================================
覆盖场景：
  1. 通知型 - 账单提醒 / 额度调整通知 / 还款提醒
  2. 客服型 - 利率解释 / 还款规则 / 账单异议
  3. 销售型 - 信用卡增值权益推荐 / 贷款产品跟进
  4. 回访型 - 新功能满意度 / 服务体验回访

合成标准与电商行业保持一致：
  - Base：模型直接输出，无任何拟人化指令
  - CCO：含完整拟人化指令，包含黑名单词汇约束
"""

from typing import Dict, Any

# ═══════════════════════════════════════════════════════════════════════════════
# PART 1: 场景配置
# ═══════════════════════════════════════════════════════════════════════════════

BUSINESS_SCENARIOS: Dict[str, Any] = {

    # ── 通知型场景 ────────────────────────────────────────────────────────────

    "bill_reminder": {
        "name": "信用卡账单及还款提醒",
        "type": "notification",
        "logic": "parallel",
        "context": {
            "company": "XX银行信用卡中心",
            "agent_name": "小李",
            "customer_name": "张先生",
            "event_count": 2,
            "events": [
                {
                    "priority": 1,
                    "title": "本期账单提醒",
                    "detail": "本月账单金额3,847元，最后还款日是下周五，错过会产生利息和滞纳金",
                    "urgency": "高，下周五截止"
                },
                {
                    "priority": 2,
                    "title": "分期优惠告知",
                    "detail": "3000元以上可以申请免息分期，最长12期，现在办理本月账单可以用",
                    "urgency": "中，本月有效"
                }
            ],
            "app_guide": "手机银行APP首页点'我的账单'，分期申请在账单详情里",
            "follow_up_qa": {
                "最低还款是多少": "最低还款是384元，但建议全额还，不然剩下的部分会按日计息",
                "分期手续费多少": "手续费按月0.6%，12期的话每月大概多还18块，比逾期利息划算很多",
                "能不能延期": "延期会产生逾期费用，影响信用记录，建议这几天先把最低还款还上"
            }
        }
    },

    "quota_adjustment": {
        "name": "额度调整及权益变更通知",
        "type": "notification",
        "logic": "parallel",
        "context": {
            "company": "XX银行信用卡中心",
            "agent_name": "小王",
            "customer_name": "李女士",
            "event_count": 2,
            "events": [
                {
                    "priority": 1,
                    "title": "临时额度到期",
                    "detail": "上个月申请的5000元临时额度今天到期，额度会从18000恢复到13000，如果有未还款项会影响使用",
                    "urgency": "高，今天到期"
                },
                {
                    "priority": 2,
                    "title": "永久额度提升机会",
                    "detail": "根据您的用卡记录，现在可以申请永久额度提升，预计可以涨到16000，需要在APP里提交申请",
                    "urgency": "中，本月有效"
                }
            ],
            "app_guide": "APP里'我的卡'→'额度管理'→'申请提额'，审核一般1个工作日",
            "follow_up_qa": {
                "临时额度还完才能用吗": "临时额度到期后，如果有用到临时额度部分的欠款，需要先还掉才能正常使用固定额度",
                "提额会查征信吗": "会做一次软查询，不影响征信评分，放心申请",
                "提额成功率高吗": "您的还款记录很好，通过率比较高，具体额度审核后才能确定"
            }
        }
    },

    # ── 客服型场景 ────────────────────────────────────────────────────────────

    "interest_explanation": {
        "name": "利率及计息规则解释",
        "type": "customerservice",
        "faq_content": {
            "日利率计算": "信用卡分期年利率约15%-18%，折算日利率约0.04%-0.05%，按未还款余额每天计算",
            "免息期规则": "最长56天免息期，从账单日到还款日，全额还款才能享受，最低还款会失去免息资格",
            "逾期影响": "逾期会产生每日万分之五的利息，同时上报征信，影响后续贷款和信用卡申请"
        },
        "human_explanation": {
            "利率口语化": "就是说，你欠了1000块，每天大概要多还4毛钱的利息，一个月差不多12块",
            "免息期口语化": "简单说就是，你这个月刷了钱，只要在下个月还款日之前全部还清，这段时间是不收利息的",
            "逾期口语化": "逾期最麻烦的不是那点利息，是会被记到征信里，以后买房贷款都可能受影响"
        },
        "multi_info_points": True,
        "info_count": 2
    },

    "bill_dispute": {
        "name": "账单异议及争议处理",
        "type": "customerservice",
        "faq_content": {
            "争议申请条件": "发现异常消费后60天内可以发起争议，需要提供消费时间、金额、商户信息",
            "处理流程": "提交争议后银行会联系商户核实，一般7-15个工作日出结果，期间可以暂不还争议金额",
            "常见原因": "盗刷、重复扣款、商户未退款等，需要根据具体情况提供不同材料"
        },
        "human_explanation": {
            "争议口语化": "就是说你看到一笔不认识的消费，可以告诉我们，我们帮你去找商家核实，核实期间这笔钱你可以先不还",
            "流程口语化": "您这边提交一下，我们那边大概一两周会有结果，如果确认是误扣，钱会直接退回来",
            "材料口语化": "主要就是说清楚什么时候、扣了多少、您当时在哪，有截图更好，没有也行"
        },
        "requires_emotion_first": True
    },

    # ── 销售型场景 ────────────────────────────────────────────────────────────

    "rights_upsell": {
        "name": "信用卡增值权益推荐（第3轮跟进）",
        "type": "sales",
        "round": 3,
        "context_json": {
            "客户姓名": "陈总",
            "职位": "私营业主",
            "用卡情况": "持卡3年，月均消费2万以上，主要用于商务消费",
            "历史沟通": {
                "第1轮": "介绍了白金卡的机场贵宾室权益，陈总表示'有点兴趣但不急'",
                "第2轮": "帮他算了一下，按他的消费习惯，升级白金卡每年能省差不多3000块的差旅费用"
            },
            "当前目标": "推动陈总完成白金卡升级申请，或者至少领取一次免费体验权益",
            "筹码": "本月升级白金卡免首年年费，同时赠送一次机场接送机服务"
        },
        "goal": "在前两轮信任基础上完成白金卡升级，或引导体验权益",
        "product_hint": "信用卡白金卡升级（笼统描述，不涉及具体产品细节）",
        "key_skill": "长期记忆引用+转化果断度",
        "memory_opener": "上次我们算过，按您的差旅频率，升级之后每年能省不少，您那边考虑得怎么样了？",
        "close_action": "引导完成升级申请，或先领取一次免费权益体验"
    },

    # ── 回访型场景 ────────────────────────────────────────────────────────────

    "app_feature_survey": {
        "name": "手机银行新功能满意度回访",
        "type": "returnvisit",
        "context": {
            "company": "XX银行",
            "agent_name": "小张",
            "customer_name": "王先生",
            "survey_target": "上个月新上线的'智能还款提醒'功能",
            "survey_goal": "了解用户实际使用体验，收集改进意见",
            "positive_probe": "那您觉得这个功能有没有哪些地方还可以做得更好？您的建议我们可以反馈给产品团队。",
            "negative_probe": "那您觉得具体是哪里用起来不顺手？您可以跟我说说，我们记录下来改进。",
            "apology": "好的，您说的这个我们记下来了，这块确实还没做到位，后续会跟进改进的。",
            "close_check": "请问您还有别的想跟我们反馈的吗？"
        }
    }
}

CUSTOMER_STATES = {
    "cooperative": {
        "name": "配合型",
        "desc": "态度配合，确认信息后无追问，简短结束",
        "behavior": "对两件事分别简短确认，不深挖细节"
    },
    "inquisitive": {
        "name": "追问型",
        "desc": "对其中一件事有1-2个细节疑问",
        "behavior": "听完第一件事后配合，但对第二件事会追问细节"
    },
    "interrupted": {
        "name": "阻断型",
        "desc": "CCO说完第一件事后表示不方便，需要判断是否简短提及第二件",
        "behavior": "CCO需在退出前建立明确的Next Action"
    },
    "mid_interrupt": {
        "name": "半途打断型",
        "desc": "第一件事说到一半就插话，CCO接话后自然带出第二件",
        "behavior": "测试被打断后能否流畅带出第二件事"
    },
    "anxious": {
        "name": "焦急型",
        "desc": "有问题要立刻解决，语速快，容易打断",
        "behavior": "直奔问题，中途可能打断，需要简短给出明确答案"
    },
    "confused": {
        "name": "困惑型",
        "desc": "不懂金融术语，需要用类比解释",
        "behavior": "会说'我不太明白'，需要换更简单的方式重新解释"
    },
    "skeptical": {
        "name": "质疑型",
        "desc": "对规则或利率有异议，有情绪",
        "behavior": "必须先共情再讲规则，直接讲规则会激化情绪"
    },
    "positive": {
        "name": "正面型",
        "desc": "整体满意，可能有小建议",
        "behavior": "语气积极，CCO用轻松语气接话后引导出建议"
    },
    "negative": {
        "name": "负面型",
        "desc": "有明确不满，能说出具体问题",
        "behavior": "CCO语气收敛，给客户空间说完，再追问细节并致歉"
    },
    "ambiguous": {
        "name": "模糊型",
        "desc": "态度不明确，用词模糊",
        "behavior": "CCO不预设正负面，温和追问让客户说清楚"
    },
    "interested": {
        "name": "有兴趣型",
        "desc": "对产品有兴趣，稍加引导即可推进",
        "behavior": "CCO识别购买信号立刻收拢，不要继续背稿"
    },
    "hesitant": {
        "name": "犹豫型",
        "desc": "不拒绝也不答应，给出模糊回应",
        "behavior": "CCO在退出前建立明确的Next Action"
    },
    "rejecting": {
        "name": "拒绝型",
        "desc": "明确拒绝，需要多轮挽回",
        "behavior": "每次挽回换不同角度，不重复"
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# PART 2: CCO 风格 System Prompt
# ═══════════════════════════════════════════════════════════════════════════════

CCO_SYSTEM_PROMPT = """你是专门生成【真实人类客服CCO风格】金融行业外呼对话的专家。

【第零条规则：禁止使用的词汇黑名单】
以下词汇在生成的对话中绝对不能出现，出现即视为失败：
❌ 禁止词：日利率、年化利率、征信评分、授信额度、风控、
           逾期率、坏账率、资产配置、理财产品收益率、
           AUM、ROI、LTV、NPL

必须用以下日常语言替代：
✅ 每天多还几毛钱（替代：日利率）
✅ 影响以后贷款买房（替代：影响征信）
✅ 银行给你的可以用的钱（替代：授信额度）
✅ 还款记录（替代：征信记录）

这条规则优先级最高，高于其他所有规则。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【最高优先级：三条硬性规则】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

规则1【语气词必须出现在开场】
开场前两句话必须有语气词或停顿。
✅ "您好，请问是张先生吗？...嗯我是XX银行信用卡中心的小李，打扰一下哈"
❌ "您好，我是XX银行客服代表，今天致电是为了告知您..."

规则2【每轮回复不超过50字】
说完一件事就停，等客户反应，不能一口气说完所有内容。

规则3【专业概念必须翻译成日常语言】
❌ "您的免息期即将结束，建议全额还款以避免产生利息"
✅ "下周五之前把钱还上，这段时间是不收利息的，过了就开始算钱了"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【多事件串联：禁止条目化】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ "今天联系您有两件事：第一，您的账单...第二，关于分期..."
✅ "...账单这边就是这样哈。对了，还有一个事顺便说一下——"

串联用语：
- "还有一个事" / "对了，顺便跟您说" / "说完这个，另外还有"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【真人CCO必须具备的特征】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 省略主语："进APP看一下" 而非 "您需要进入APP查看"
2. 自然犹豫："嗯...让我看一下" / "就是那个...对，那个选项"
3. 话语标记词："是这样的" / "说白了" / "就是说"
4. 短句碎片："对，就这样" / "行，没问题哈"
5. 倒装追补："退回去了已经" / "发短信了我"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【绝对禁止】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- 数字编号："第一""其次""1.""2."
- 开头客套："尊敬的客户""非常感谢您的接听"
- 结尾客套："祝您生活愉快""感谢您对我行的支持"
- 书面语："根据您的账户信息""我行将为您处理"
- 直接使用金融术语而不翻译成日常语言

【输出格式】只输出对话，不要任何说明：
[CCO]: xxx
[客户]: xxx
"""

# ═══════════════════════════════════════════════════════════════════════════════
# PART 3: Base 模型对比 System Prompt
# ═══════════════════════════════════════════════════════════════════════════════

BASE_SYSTEM_PROMPT = """你是一个智能金融客服系统，负责处理银行信用卡相关的外呼通知和咨询。
根据给定的场景，生成一段外呼对话。
格式：[客服]: xxx  [客户]: xxx"""

# ═══════════════════════════════════════════════════════════════════════════════
# PART 4: 动态 User Prompt 构建
# ═══════════════════════════════════════════════════════════════════════════════

def build_events_text(scenario: dict) -> str:
    ctx = scenario["context"]
    logic = scenario["logic"]
    events = ctx["events"]
    logic_desc = "并列关系：两件事同等重要，都需要告知" if logic == "parallel" else "优先级关系：第一件最紧急，客户有意愿再说第二件"
    events_text = f"事件逻辑：{logic_desc}\n\n"
    for e in events:
        events_text += f"事项{e['priority']}（{e['title']}，紧急度：{e['urgency']}）：\n  {e['detail']}\n\n"
    return events_text


def build_cco_user_prompt(scenario_key: str, state_key: str) -> str:
    scenario = BUSINESS_SCENARIOS[scenario_key]
    state = CUSTOMER_STATES[state_key]
    scene_type = scenario.get("type", "")

    turns_map = {
        "cooperative": "6-8轮，简短结束",
        "inquisitive": "10-14轮，有追问",
        "interrupted": "5-7轮，退出前留Next Action",
        "mid_interrupt": "8-12轮，被打断后自然带出第二件",
        "anxious": "6-10轮，简短直接给答案",
        "confused": "10-16轮，可能需要换方式解释2次",
        "skeptical": "8-14轮，第一句必须是共情",
        "positive": "6-8轮，轻松语气",
        "negative": "10-14轮，追问细节并致歉",
        "ambiguous": "8-12轮，先追清楚再走路径",
        "interested": "6-10轮，感兴趣后立刻收拢",
        "hesitant": "8-12轮，退出前留Next Action",
        "rejecting": "10-16轮，至少2次不同角度挽回"
    }

    scene_type = scenario.get("type", "")

    if scene_type == "notification":
        ctx = scenario["context"]
        return f"""场景：{scenario["name"]}（金融行业·通知型）
CCO：{ctx["agent_name"]}（来自{ctx["company"]}）
客户：{ctx["customer_name"]}

【需要告知的事项（共{ctx["event_count"]}件）】
{build_events_text(scenario)}
【操作引导路径】
{ctx["app_guide"]}

【客户状态】{state["name"]} - {state["desc"]}
行为特征：{state["behavior"]}

【追问参考答案】
{"".join([f'  客户问"{q}"→回答：{a}' + chr(10) for q, a in ctx["follow_up_qa"].items()])}
【对话轮次】{turns_map.get(state_key, "8-12轮")}

现在开始生成对话："""

    elif scene_type == "customerservice":
        faq_text = "\n".join([f"  【{k}】{v}" for k, v in scenario["faq_content"].items()])
        exp_text = "\n".join([f"  {k}：{v}" for k, v in scenario["human_explanation"].items()])
        emotion_note = "\n⚠️ 情绪优先：质疑型客户第一句必须是共情，不能直接讲规则！" if scenario.get("requires_emotion_first") else ""
        return f"""场景：{scenario["name"]}（金融行业·客服型）
CCO角色：银行信用卡客服专员

【客户情绪状态】{state["name"]} - {state["desc"]}
行为特征：{state["behavior"]}
{emotion_note}

【FAQ原始内容（不能直接念）】
{faq_text}

【口语化表达参考（CCO应该这样说）】
{exp_text}

【对话轮次】{turns_map.get(state_key, "8-12轮")}
客户先开口，CCO先听懂再回答。

现在开始生成对话（客户先说）："""

    elif scene_type == "sales":
        ctx_text = "\n".join([
            f"  {k}：{v}" if not isinstance(v, dict)
            else f"  {k}：\n" + "\n".join([f"    {sk}：{sv}" for sk, sv in v.items()])
            for k, v in scenario["context_json"].items()
        ])
        return f"""场景：{scenario["name"]}（金融行业·销售型·第{scenario["round"]}轮）
CCO角色：银行客户经理

【客户背景 Context_JSON】
{ctx_text}

【本次通话目标】{scenario["goal"]}
【开场引用历史记忆】{scenario["memory_opener"]}
【目标闭环动作】{scenario["close_action"]}

【客户状态】{state["name"]} - {state["desc"]}
核心测试：{state["behavior"]}

【对话轮次】{turns_map.get(state_key, "10-14轮")}

现在开始生成对话："""

    else:  # returnvisit
        ctx = scenario["context"]
        return f"""场景：{scenario["name"]}（金融行业·回访型）
CCO：{ctx["agent_name"]}（来自{ctx["company"]}）
客户：{ctx["customer_name"]}

【回访主题】{ctx["survey_target"]}
【回访目的】{ctx["survey_goal"]}

【客户反馈类型】{state["name"]} - {state["desc"]}
行为特征：{state["behavior"]}

【对话轮次】{turns_map.get(state_key, "6-10轮")}

现在开始生成对话："""


def build_base_user_prompt(scenario_key: str, state_key: str) -> str:
    scenario = BUSINESS_SCENARIOS[scenario_key]
    state = CUSTOMER_STATES[state_key]
    scene_type = scenario.get("type", "")

    if scene_type == "notification":
        ctx = scenario["context"]
        events_simple = "\n".join([
            f"事项{e['priority']}：{e['title']} - {e['detail'][:50]}..."
            for e in ctx["events"]
        ])
        return f"""场景：{scenario["name"]}
客服：{ctx["agent_name"]}（{ctx["company"]}）  客户：{ctx["customer_name"]}
客户状态：{state["desc"]}
需告知事项：\n{events_simple}
操作引导：{ctx["app_guide"]}
生成对话："""

    elif scene_type == "customerservice":
        faq_simple = "\n".join([f"{k}：{v}" for k, v in scenario["faq_content"].items()])
        return f"""场景：{scenario["name"]}
客服角色：银行信用卡客服
客户情绪：{state["name"]} - {state["desc"]}
FAQ参考：\n{faq_simple}
生成对话（客户先说）："""

    elif scene_type == "sales":
        ctx_simple = "\n".join([
            f"{k}：{v}" if not isinstance(v, dict) else f"{k}：{str(v)[:60]}..."
            for k, v in scenario["context_json"].items()
        ])
        return f"""场景：{scenario["name"]}
客服角色：银行客户经理
客户信息：\n{ctx_simple}
通话目标：{scenario["goal"]}
客户状态：{state["name"]} - {state["desc"]}
生成对话："""

    else:
        ctx = scenario["context"]
        return f"""场景：{scenario["name"]}
客服：{ctx["agent_name"]}（{ctx["company"]}）  客户：{ctx["customer_name"]}
回访主题：{ctx["survey_target"]}
客户反馈倾向：{state["name"]} - {state["desc"]}
生成对话："""


# ═══════════════════════════════════════════════════════════════════════════════
# PART 5: 批量生成计划（目标约350条对话）
# ═══════════════════════════════════════════════════════════════════════════════

GENERATION_PLAN = [
    # 通知型
    ("bill_reminder",      "cooperative",   4, "账单提醒·配合型"),
    ("bill_reminder",      "inquisitive",   4, "账单提醒·追问型"),
    ("bill_reminder",      "interrupted",   3, "账单提醒·阻断型"),
    ("bill_reminder",      "mid_interrupt", 4, "账单提醒·半途打断"),
    ("quota_adjustment",   "cooperative",   4, "额度通知·配合型"),
    ("quota_adjustment",   "inquisitive",   4, "额度通知·追问型"),
    ("quota_adjustment",   "interrupted",   3, "额度通知·阻断型"),

    # 客服型
    ("interest_explanation","anxious",      4, "利率解释·焦急型"),
    ("interest_explanation","confused",     5, "利率解释·困惑型·类比关键"),
    ("interest_explanation","skeptical",    4, "利率解释·质疑型"),
    ("bill_dispute",        "anxious",      4, "账单争议·焦急型"),
    ("bill_dispute",        "skeptical",    5, "账单争议·质疑型·情绪优先"),
    ("bill_dispute",        "confused",     3, "账单争议·困惑型"),

    # 销售型
    ("rights_upsell",      "interested",    4, "权益推荐·有兴趣·测转化果断"),
    ("rights_upsell",      "hesitant",      4, "权益推荐·犹豫·测Next Action"),
    ("rights_upsell",      "rejecting",     4, "权益推荐·拒绝·测多轮挽回"),
    ("rights_upsell",      "skeptical",     3, "权益推荐·质疑·测价值重塑"),

    # 回访型
    ("app_feature_survey", "positive",      4, "功能回访·正面"),
    ("app_feature_survey", "negative",      4, "功能回访·负面"),
    ("app_feature_survey", "ambiguous",     4, "功能回访·模糊·信号识别"),
]
# 合计：CCO风格 88条 + Base风格 88条 = 176条


def print_plan_summary():
    print("=" * 60)
    print("金融行业 数据生成计划")
    print("=" * 60)
    total = sum(count for _, _, count, _ in GENERATION_PLAN)
    for scene, state, count, note in GENERATION_PLAN:
        sname = BUSINESS_SCENARIOS[scene]["name"]
        sstate = CUSTOMER_STATES[state]["name"]
        print(f"  {sname} × {sstate}: {count}条  [{note}]")
    print("-" * 60)
    print(f"  CCO风格合计：{total}条")
    print(f"  Base风格合计：{total}条")
    print(f"  总计：{total * 2}条")
    print("=" * 60)


if __name__ == "__main__":
    print_plan_summary()
    print("\n示例 CCO User Prompt：账单提醒 × 半途打断型")
    print("-" * 60)
    print(build_cco_user_prompt("bill_reminder", "mid_interrupt"))
