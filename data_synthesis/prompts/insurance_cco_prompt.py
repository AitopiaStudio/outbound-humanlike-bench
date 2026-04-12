#!/usr/bin/env python3
"""
保险行业 CCO 风格数据合成 Prompt
=====================================
覆盖场景：
  1. 通知型 - 保单续期提醒 / 理赔进度通知
  2. 客服型 - 保障条款解释 / 理赔材料说明
  3. 销售型 - 增值险种推荐 / 续期跟进
  4. 回访型 - 投保后满意度 / 理赔体验回访

合成标准与电商行业保持一致。
"""

from typing import Dict, Any

BUSINESS_SCENARIOS: Dict[str, Any] = {

    # ── 通知型场景 ────────────────────────────────────────────────────────────

    "renewal_reminder": {
        "name": "保单续期及权益提醒",
        "type": "notification",
        "logic": "priority",
        "context": {
            "company": "XX人寿保险",
            "agent_name": "小陈",
            "customer_name": "刘女士",
            "event_count": 2,
            "events": [
                {
                    "priority": 1,
                    "title": "保单即将到期",
                    "detail": "您的意外险下周五到期，到期后保障自动终止，期间发生意外就没有赔付了",
                    "urgency": "高，下周五到期"
                },
                {
                    "priority": 2,
                    "title": "续期优惠",
                    "detail": "现在续期有老客户专属折扣，同等保障比新客便宜15%，而且不需要重新体检",
                    "urgency": "中，到期前有效"
                }
            ],
            "app_guide": "APP里'我的保单'→找到这份意外险→点续期，或者直接告诉我您要续，我帮您办",
            "follow_up_qa": {
                "不续期会怎样": "保障直接断掉，期间出了什么事就没有保险公司赔了，建议提前几天续上",
                "续期保费一样吗": "保费会根据年龄有小幅调整，但老客折扣基本能抵消，实际差不多",
                "可以换别的险种吗": "可以，但换了就算新投保，需要重新核保，这份续期不需要，更方便"
            }
        }
    },

    "claim_progress": {
        "name": "理赔进度及材料补充通知",
        "type": "notification",
        "logic": "priority",
        "context": {
            "company": "XX财险",
            "agent_name": "小王",
            "customer_name": "赵先生",
            "event_count": 2,
            "events": [
                {
                    "priority": 1,
                    "title": "材料补充紧急通知",
                    "detail": "您上次提交的理赔材料里，医院的诊断证明缺少医生签字，需要补一份，不然审核没法继续",
                    "urgency": "高，影响理赔进度"
                },
                {
                    "priority": 2,
                    "title": "理赔预计时间告知",
                    "detail": "材料补齐后，大概5个工作日内出审核结果，通过后3个工作日内打款到您绑定的银行卡",
                    "urgency": "中，流程说明"
                }
            ],
            "app_guide": "补充材料可以在APP'理赔进度'里直接上传照片，也可以到就近网点重新盖章",
            "follow_up_qa": {
                "还差什么材料": "主要就是诊断证明上需要医生手写签名和日期，照片拍清楚上传就行",
                "多久能收到钱": "材料齐了之后5个工作日审核，通过了3个工作日打款，大概一周多",
                "可以快一点吗": "审核流程是固定的，但您材料越快补齐，整体就越快，建议今天就去补一下"
            }
        }
    },

    # ── 客服型场景 ────────────────────────────────────────────────────────────

    "coverage_explanation": {
        "name": "保障范围及免责条款解释",
        "type": "customerservice",
        "faq_content": {
            "免责条款": "酒后驾车、故意伤害、战争、核辐射等情况不在保障范围内，自然灾害和意外事故在保障内",
            "等待期": "重疾险一般有90-180天等待期，等待期内发生的疾病不赔，意外险无等待期",
            "理赔条件": "需要提供医院诊断证明、费用清单、本人身份证，住院的话还需要住院小结"
        },
        "human_explanation": {
            "免责口语化": "就是说，喝了酒开车出了事，保险公司是不赔的。正常出门遇到意外，是赔的",
            "等待期口语化": "等待期就像是试用期，刚买的前三个月，如果发现病了，这段时间的不赔，三个月之后买保险才真正生效",
            "理赔口语化": "就是去医院拿几张纸：诊断书、花费明细，再加上身份证，拍照片发给我们就行"
        },
        "multi_info_points": True,
        "info_count": 2,
        "requires_emotion_first": False
    },

    "claim_guidance": {
        "name": "理赔流程及材料指导",
        "type": "customerservice",
        "faq_content": {
            "理赔流程": "出险后5天内报案，提交材料后5-10个工作日审核，审核通过3个工作日打款",
            "所需材料": "诊断证明（需医生签字）、医疗费用明细、住院小结（如有）、本人身份证和银行卡",
            "注意事项": "发票和收据要保留原件，APP上传照片要清晰，模糊的会被退回"
        },
        "human_explanation": {
            "流程口语化": "出了事先跟我们说一声，然后把医院给的那几张纸拍照发给我们，我们审完就打钱给你",
            "材料口语化": "主要就是医生写的诊断书、你花了多少钱的清单，加上身份证，就这几样",
            "注意口语化": "那些票据和收据的原件别扔，拍照也行但要拍清楚，拍虚了我们这边看不清楚会退回来"
        },
        "requires_emotion_first": True
    },

    # ── 销售型场景 ────────────────────────────────────────────────────────────

    "additional_coverage": {
        "name": "增值险种推荐（第3轮跟进）",
        "type": "sales",
        "round": 3,
        "context_json": {
            "客户姓名": "林总",
            "职业": "自由职业者",
            "现有保单": "意外险，年保费800元，已投保2年",
            "历史沟通": {
                "第1轮": "了解到林总经常出差，目前只有基础意外险，没有医疗险",
                "第2轮": "帮他算了一下，如果住院一次花费3万，现有保险只能报销意外部分，自费比例很高"
            },
            "当前目标": "推荐附加住院医疗险，引导完成投保或至少获得报价确认",
            "筹码": "老客户投保附加险有折扣，而且不需要重新体检"
        },
        "goal": "在前两轮信任基础上完成附加险投保，或引导获取报价",
        "product_hint": "住院医疗附加险（笼统描述）",
        "key_skill": "长期记忆引用+转化果断度",
        "memory_opener": "上次我们说到，您要是住院了，现在的保险自费部分还是挺多的，您那边有没有考虑补一个医疗险？",
        "close_action": "引导完成报价查询或直接投保申请"
    },

    # ── 回访型场景 ────────────────────────────────────────────────────────────

    "claim_experience": {
        "name": "理赔体验满意度回访",
        "type": "returnvisit",
        "context": {
            "company": "XX保险",
            "agent_name": "小林",
            "customer_name": "周先生",
            "survey_target": "上个月完成的一次医疗理赔",
            "survey_goal": "了解理赔全程体验，收集改进意见",
            "positive_probe": "那整个过程有没有哪些地方您觉得我们还可以做得更好？您的反馈对我们很重要。",
            "negative_probe": "那您觉得具体是哪个环节让您觉得不太满意？是材料提交、审核速度还是别的什么？",
            "apology": "好的，您说的这个我们记下来了，这块确实还有改进空间，之后会跟进优化的。",
            "close_check": "还有没有别的想跟我们说的？"
        }
    }
}

CUSTOMER_STATES = {
    "cooperative": {"name": "配合型", "desc": "态度配合，确认信息后无追问，简短结束", "behavior": "简短确认，不深挖"},
    "inquisitive": {"name": "追问型", "desc": "对其中一件事有1-2个细节疑问", "behavior": "有追问需解释后才满意"},
    "interrupted": {"name": "阻断型", "desc": "表示不方便，需要退出前留Next Action", "behavior": "CCO需在退出前建立联系点"},
    "mid_interrupt": {"name": "半途打断型", "desc": "第一件说到一半就插话", "behavior": "被打断后自然带出第二件"},
    "anxious": {"name": "焦急型", "desc": "出险或到期很着急，需要快速解决", "behavior": "直接给答案，不要长篇解释"},
    "confused": {"name": "困惑型", "desc": "不懂保险条款，需要类比解释", "behavior": "用日常例子解释，解释后确认听懂了"},
    "skeptical": {"name": "质疑型", "desc": "觉得理赔被拒不合理，有情绪", "behavior": "必须先共情再解释"},
    "positive": {"name": "正面型", "desc": "整体满意，可能有小建议", "behavior": "轻松接话后引导出建议"},
    "negative": {"name": "负面型", "desc": "有明确不满", "behavior": "给空间说完，追问细节后致歉"},
    "ambiguous": {"name": "模糊型", "desc": "态度不明确", "behavior": "温和追问让客户说清楚"},
    "interested": {"name": "有兴趣型", "desc": "对产品有兴趣", "behavior": "识别信号立刻收拢"},
    "hesitant": {"name": "犹豫型", "desc": "不拒绝也不答应", "behavior": "退出前建立Next Action"},
    "rejecting": {"name": "拒绝型", "desc": "明确拒绝", "behavior": "每次挽回换不同角度"}
}

CCO_SYSTEM_PROMPT = """你是专门生成【真实人类客服CCO风格】保险行业外呼对话的专家。

【第零条规则：禁止使用的词汇黑名单】
以下词汇绝对不能出现：
❌ 禁止词：保额、免赔额、赔付率、核保、承保、续保率、
           理赔率、风险敞口、精算、保险密度、保险深度

必须用日常语言替代：
✅ 保险赔多少钱（替代：保额）
✅ 超过多少钱才开始赔（替代：免赔额）
✅ 审核（替代：核保/承保）
✅ 续保（替代：续期）

这条规则优先级最高。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【最高优先级：三条硬性规则】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

规则1【语气词必须出现在开场】
✅ "您好，请问是刘女士吗？...嗯我是XX保险的小陈，打扰一下哈"
❌ "您好，我是XX保险客服，今天致电是为了告知您..."

规则2【每轮回复不超过50字】
说完一件事停下来，等客户反应。

规则3【专业概念翻译成日常语言】
❌ "您的保单即将到期，届时保障将自动终止"
✅ "您的保险下周就到期了，到期之后出了什么事就没人赔了"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【多事件串联：禁止条目化】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ "今天有两件事：第一...第二..."
✅ "...这个先说到这。对了，还有一个事顺便跟您说一下——"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【真人CCO必须具备的特征】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 省略主语："进APP看一下" 而非 "您需要进入APP查看"
2. 自然犹豫："嗯...让我看一下" / "就是那个..."
3. 话语标记词："是这样的" / "说白了" / "就是说"
4. 短句碎片："对，就这样" / "行，没问题哈"
5. 倒装追补："材料补了已经" / "发你了我"

【绝对禁止】
- 数字编号："第一""其次""1.""2."
- 开头客套："尊敬的客户""非常感谢您的接听"
- 结尾客套："祝您生活愉快""感谢您对本公司的支持"
- 直接使用保险术语而不翻译

【输出格式】只输出对话：
[CCO]: xxx
[客户]: xxx
"""

BASE_SYSTEM_PROMPT = """你是一个智能保险客服系统，负责保险相关的外呼通知和咨询。
根据给定的场景，生成一段外呼对话。
格式：[客服]: xxx  [客户]: xxx"""


def build_cco_user_prompt(scenario_key: str, state_key: str) -> str:
    scenario = BUSINESS_SCENARIOS[scenario_key]
    state = CUSTOMER_STATES[state_key]
    scene_type = scenario.get("type", "")

    turns_map = {
        "cooperative": "6-8轮", "inquisitive": "10-14轮", "interrupted": "5-7轮",
        "mid_interrupt": "8-12轮", "anxious": "6-10轮", "confused": "10-16轮",
        "skeptical": "8-14轮", "positive": "6-8轮", "negative": "10-14轮",
        "ambiguous": "8-12轮", "interested": "6-10轮", "hesitant": "8-12轮",
        "rejecting": "10-16轮"
    }

    if scene_type == "notification":
        ctx = scenario["context"]
        events = ctx["events"]
        logic_desc = "优先级关系：第一件最紧急" if scenario["logic"] == "priority" else "并列关系：两件事同等重要"
        events_text = f"事件逻辑：{logic_desc}\n\n"
        for e in events:
            events_text += f"事项{e['priority']}（{e['title']}，紧急度：{e['urgency']}）：\n  {e['detail']}\n\n"
        qa_text = "\n".join([f"  客户问\"{q}\"→回答：{a}" for q, a in ctx["follow_up_qa"].items()])
        return f"""场景：{scenario["name"]}（保险行业·通知型）
CCO：{ctx["agent_name"]}（来自{ctx["company"]}）  客户：{ctx["customer_name"]}

【需要告知的事项】
{events_text}
【操作引导】{ctx["app_guide"]}
【客户状态】{state["name"]} - {state["desc"]}
【追问参考】\n{qa_text}
【对话轮次】{turns_map.get(state_key, "8-12轮")}

现在开始生成对话："""

    elif scene_type == "customerservice":
        faq_text = "\n".join([f"  【{k}】{v}" for k, v in scenario["faq_content"].items()])
        exp_text = "\n".join([f"  {k}：{v}" for k, v in scenario["human_explanation"].items()])
        emotion = "\n⚠️ 质疑型客户第一句必须共情，不能直接讲规则！" if scenario.get("requires_emotion_first") else ""
        return f"""场景：{scenario["name"]}（保险行业·客服型）
CCO角色：保险客服专员{emotion}

【客户情绪状态】{state["name"]} - {state["desc"]}
行为特征：{state["behavior"]}

【FAQ原始内容（不能直接念）】
{faq_text}

【口语化表达参考】
{exp_text}

【对话轮次】{turns_map.get(state_key, "8-12轮")}
客户先开口。现在开始生成对话（客户先说）："""

    elif scene_type == "sales":
        ctx_text = "\n".join([
            f"  {k}：{v}" if not isinstance(v, dict)
            else f"  {k}：\n" + "\n".join([f"    {sk}：{sv}" for sk, sv in v.items()])
            for k, v in scenario["context_json"].items()
        ])
        return f"""场景：{scenario["name"]}（保险行业·销售型·第{scenario["round"]}轮）
CCO角色：保险客户经理

【客户背景】\n{ctx_text}
【开场引用历史】{scenario["memory_opener"]}
【目标闭环动作】{scenario["close_action"]}
【客户状态】{state["name"]} - {state["desc"]}
【对话轮次】{turns_map.get(state_key, "10-14轮")}

现在开始生成对话："""

    else:
        ctx = scenario["context"]
        return f"""场景：{scenario["name"]}（保险行业·回访型）
CCO：{ctx["agent_name"]}（{ctx["company"]}）  客户：{ctx["customer_name"]}
回访主题：{ctx["survey_target"]}
客户反馈类型：{state["name"]} - {state["desc"]}
【对话轮次】{turns_map.get(state_key, "6-10轮")}

现在开始生成对话："""


def build_base_user_prompt(scenario_key: str, state_key: str) -> str:
    scenario = BUSINESS_SCENARIOS[scenario_key]
    state = CUSTOMER_STATES[state_key]
    scene_type = scenario.get("type", "")

    if scene_type == "notification":
        ctx = scenario["context"]
        events_simple = "\n".join([f"事项{e['priority']}：{e['title']} - {e['detail'][:50]}..." for e in ctx["events"]])
        return f"""场景：{scenario["name"]}\n客服：{ctx["agent_name"]}（{ctx["company"]}）  客户：{ctx["customer_name"]}
客户状态：{state["desc"]}\n需告知事项：\n{events_simple}\n操作引导：{ctx["app_guide"]}\n生成对话："""
    elif scene_type == "customerservice":
        faq_simple = "\n".join([f"{k}：{v}" for k, v in scenario["faq_content"].items()])
        return f"""场景：{scenario["name"]}\n客服角色：保险客服\n客户情绪：{state["name"]} - {state["desc"]}
FAQ参考：\n{faq_simple}\n生成对话（客户先说）："""
    elif scene_type == "sales":
        ctx_simple = "\n".join([f"{k}：{v}" if not isinstance(v, dict) else f"{k}：{str(v)[:60]}..." for k, v in scenario["context_json"].items()])
        return f"""场景：{scenario["name"]}\n客服角色：保险客户经理\n客户信息：\n{ctx_simple}
通话目标：{scenario["goal"]}\n客户状态：{state["name"]} - {state["desc"]}\n生成对话："""
    else:
        ctx = scenario["context"]
        return f"""场景：{scenario["name"]}\n客服：{ctx["agent_name"]}（{ctx["company"]}）  客户：{ctx["customer_name"]}
回访主题：{ctx["survey_target"]}\n客户反馈：{state["name"]} - {state["desc"]}\n生成对话："""


GENERATION_PLAN = [
    ("renewal_reminder",    "cooperative",   4, "续期提醒·配合型"),
    ("renewal_reminder",    "inquisitive",   4, "续期提醒·追问型"),
    ("renewal_reminder",    "interrupted",   3, "续期提醒·阻断型"),
    ("renewal_reminder",    "mid_interrupt", 4, "续期提醒·半途打断"),
    ("claim_progress",      "anxious",       4, "理赔通知·焦急型"),
    ("claim_progress",      "inquisitive",   4, "理赔通知·追问型"),
    ("claim_progress",      "interrupted",   3, "理赔通知·阻断型"),
    ("coverage_explanation","confused",      5, "条款解释·困惑型"),
    ("coverage_explanation","anxious",       4, "条款解释·焦急型"),
    ("coverage_explanation","skeptical",     4, "条款解释·质疑型"),
    ("claim_guidance",      "anxious",       4, "理赔指导·焦急型"),
    ("claim_guidance",      "skeptical",     5, "理赔指导·质疑型·情绪优先"),
    ("claim_guidance",      "confused",      3, "理赔指导·困惑型"),
    ("additional_coverage", "interested",    4, "增值险·有兴趣"),
    ("additional_coverage", "hesitant",      4, "增值险·犹豫"),
    ("additional_coverage", "rejecting",     4, "增值险·拒绝·多轮挽回"),
    ("additional_coverage", "skeptical",     3, "增值险·质疑"),
    ("claim_experience",    "positive",      4, "理赔回访·正面"),
    ("claim_experience",    "negative",      4, "理赔回访·负面"),
    ("claim_experience",    "ambiguous",     4, "理赔回访·模糊"),
]
# 合计：CCO风格 88条 + Base风格 88条 = 176条


def print_plan_summary():
    print("=" * 60)
    print("保险行业 数据生成计划")
    print("=" * 60)
    total = sum(count for _, _, count, _ in GENERATION_PLAN)
    for scene, state, count, note in GENERATION_PLAN:
        print(f"  {BUSINESS_SCENARIOS[scene]['name']} × {CUSTOMER_STATES[state]['name']}: {count}条  [{note}]")
    print("-" * 60)
    print(f"  CCO风格合计：{total}条  Base风格合计：{total}条  总计：{total * 2}条")
    print("=" * 60)


if __name__ == "__main__":
    print_plan_summary()
