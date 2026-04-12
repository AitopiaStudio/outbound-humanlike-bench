#!/usr/bin/env python3
"""
医疗健康行业 CCO 风格数据合成 Prompt
=========================================
覆盖场景：
  1. 通知型 - 体检报告提醒 / 复诊预约通知
  2. 客服型 - 检查指标解释 / 套餐内容说明
  3. 销售型 - 健康管理服务推荐 / 套餐续费跟进
  4. 回访型 - 体检后满意度 / 健康服务体验回访

合成标准与电商行业保持一致。
"""

from typing import Dict, Any

BUSINESS_SCENARIOS: Dict[str, Any] = {

    # ── 通知型场景 ────────────────────────────────────────────────────────────

    "report_reminder": {
        "name": "体检报告及复诊提醒",
        "type": "notification",
        "logic": "priority",
        "context": {
            "company": "XX健康管理中心",
            "agent_name": "小林",
            "customer_name": "张先生",
            "event_count": 2,
            "events": [
                {
                    "priority": 1,
                    "title": "异常指标需要复查",
                    "detail": "您上周体检报告里，血糖和血压有两项偏高，医生建议三个月内复查一次，这两项是需要关注的",
                    "urgency": "高，医生建议尽快复查"
                },
                {
                    "priority": 2,
                    "title": "报告领取提醒",
                    "detail": "完整的纸质报告已经可以到前台领取了，或者APP里也能看到电子版",
                    "urgency": "中，方便时领取"
                }
            ],
            "app_guide": "APP里'我的报告'就能看到所有指标，复查预约也在里面，点'预约复查'就行",
            "follow_up_qa": {
                "血糖偏高严重吗": "不是特别严重，但需要关注，建议近期少吃甜食，三个月内复查看看有没有变化",
                "复查要多少钱": "就查这两项的话，大概一两百块，有会员卡可以打折",
                "必须来现场吗": "复查需要抽血，要来现场，建议上午空腹来，方便的话这周就可以预约"
            }
        }
    },

    "appointment_reminder": {
        "name": "复诊预约及注意事项通知",
        "type": "notification",
        "logic": "parallel",
        "context": {
            "company": "XX体检中心",
            "agent_name": "小陈",
            "customer_name": "李女士",
            "event_count": 2,
            "events": [
                {
                    "priority": 1,
                    "title": "明天预约提醒",
                    "detail": "您预约了明天上午9点做胃镜检查，记得今天晚上8点以后不能吃东西，水也不能喝",
                    "urgency": "高，明天检查"
                },
                {
                    "priority": 2,
                    "title": "需要携带的东西",
                    "detail": "明天记得带身份证和就诊卡，如果有以前的检查报告最好也带上，医生参考用",
                    "urgency": "中，配合检查"
                }
            ],
            "app_guide": "如果需要改时间，APP里'我的预约'里可以改，最晚今天下午6点前改",
            "follow_up_qa": {
                "喝水可以吗": "不行，胃镜检查前必须完全空腹，连水都不能喝，不然检查结果会不准",
                "大概要多久": "胃镜检查本身大概15分钟，加上等待和恢复，大概一个小时",
                "能带人陪同吗": "可以，如果选择了无痛胃镜，建议带一个人，因为麻醉后不能自己开车"
            }
        }
    },

    # ── 客服型场景 ────────────────────────────────────────────────────────────

    "indicator_explanation": {
        "name": "体检指标异常解释",
        "type": "customerservice",
        "faq_content": {
            "血糖偏高": "空腹血糖正常值3.9-6.1mmol/L，6.1-7.0之间属于糖尿病前期，需要关注饮食和运动",
            "血压偏高": "正常血压低于120/80，130-139/85-89属于高血压前期，需要监测",
            "转氨酶偏高": "转氨酶升高可能是肝脏炎症、脂肪肝或者近期过度疲劳，需要结合其他指标综合判断"
        },
        "human_explanation": {
            "血糖口语化": "就是说，您血液里的糖分有点多，还没到糖尿病，但需要注意了，少吃甜的、多动动",
            "血压口语化": "血压有点偏高，还没到高血压，但要开始注意了，少吃咸的，压力别太大",
            "转氨酶口语化": "这个指标高说明肝脏最近可能在超负荷工作，可能是喝酒多了或者太累了，休息一下看看"
        },
        "multi_info_points": True,
        "info_count": 2,
        "requires_emotion_first": False
    },

    "package_explanation": {
        "name": "体检套餐内容及退换说明",
        "type": "customerservice",
        "faq_content": {
            "套餐包含内容": "基础套餐包含血常规、尿常规、肝功能、心电图、胸片，不包含胃肠镜和肿瘤标志物",
            "升级规则": "检查当天可以现场加项，但退项需要提前一天申请，当天不接受退项退款",
            "有效期": "体检套餐购买后一年内有效，过期不退款但可以转让给家人使用"
        },
        "human_explanation": {
            "套餐口语化": "基础套餐就是常规的那些，验血验尿、心电图、拍个胸片，如果要查胃肠镜要另外加",
            "退换口语化": "要加项目当天可以现场说，要退掉某个项目的话要提前一天跟我们说，当天去了就不能退了",
            "有效期口语化": "买了一年内都可以来用，过了一年就不能退钱，但可以给家里人用，转给他们就行"
        },
        "requires_emotion_first": True
    },

    # ── 销售型场景 ────────────────────────────────────────────────────────────

    "health_service_upsell": {
        "name": "健康管理服务推荐（第3轮跟进）",
        "type": "sales",
        "round": 3,
        "context_json": {
            "客户姓名": "王总",
            "年龄": "45岁",
            "体检记录": "连续两年体检，血压和血脂持续偏高",
            "历史沟通": {
                "第1轮": "了解到王总工作压力大，很少运动，知道自己有问题但没有系统管理",
                "第2轮": "介绍了健康管理服务的核心是有专属营养师和运动教练定期跟进，王总说'听起来不错'"
            },
            "当前目标": "推动王总完成健康管理年度服务签约，或先体验一次免费咨询",
            "筹码": "本季度有早鸟价，比正常价格优惠20%，同时赠送一次专属营养师面诊"
        },
        "goal": "完成健康管理服务签约或引导体验免费咨询",
        "product_hint": "年度健康管理服务（笼统描述）",
        "key_skill": "长期记忆引用+转化果断度",
        "memory_opener": "上次您说'听起来不错'，这段时间有没有想清楚？我这边也帮您留意着有没有合适的时间窗口",
        "close_action": "签约年度服务，或先预约一次免费营养师面诊"
    },

    # ── 回访型场景 ────────────────────────────────────────────────────────────

    "checkup_experience": {
        "name": "体检服务满意度回访",
        "type": "returnvisit",
        "context": {
            "company": "XX健康管理中心",
            "agent_name": "小王",
            "customer_name": "陈先生",
            "survey_target": "上个月来做的年度体检",
            "survey_goal": "了解整体体检体验，收集改进意见",
            "positive_probe": "那您觉得有没有哪些环节还可以做得更好？比如等候时间、服务态度或者报告解读这些方面？",
            "negative_probe": "那您觉得具体是哪个环节体验不太好？是预约流程、现场等待还是报告解读方面？",
            "apology": "好的，您说的这个我们记下来了，这块确实还没做到位，后续会改进的。",
            "close_check": "还有没有其他想跟我们反馈的？"
        }
    }
}

CUSTOMER_STATES = {
    "cooperative": {"name": "配合型", "desc": "态度配合，确认后无追问", "behavior": "简短确认，干净结束"},
    "inquisitive": {"name": "追问型", "desc": "有1-2个细节疑问", "behavior": "有追问需解释后才满意"},
    "interrupted": {"name": "阻断型", "desc": "表示不方便", "behavior": "退出前留Next Action"},
    "mid_interrupt": {"name": "半途打断型", "desc": "第一件说一半就插话", "behavior": "被打断后自然带出第二件"},
    "anxious": {"name": "焦急型", "desc": "看到异常指标很担心", "behavior": "先安抚情绪，再给出明确答案"},
    "confused": {"name": "困惑型", "desc": "看不懂医学指标", "behavior": "用日常语言类比解释，确认听懂"},
    "skeptical": {"name": "质疑型", "desc": "觉得套餐有猫腻或指标说明有问题", "behavior": "先共情再解释"},
    "positive": {"name": "正面型", "desc": "整体满意", "behavior": "轻松接话后引导出建议"},
    "negative": {"name": "负面型", "desc": "有明确不满", "behavior": "给空间说完，追问细节后致歉"},
    "ambiguous": {"name": "模糊型", "desc": "态度不明确", "behavior": "温和追问让客户说清楚"},
    "interested": {"name": "有兴趣型", "desc": "对服务有兴趣", "behavior": "识别信号立刻收拢"},
    "hesitant": {"name": "犹豫型", "desc": "不拒绝也不答应", "behavior": "退出前建立Next Action"},
    "rejecting": {"name": "拒绝型", "desc": "明确拒绝", "behavior": "每次挽回换不同角度"}
}

CCO_SYSTEM_PROMPT = """你是专门生成【真实人类客服CCO风格】医疗健康行业外呼对话的专家。

【第零条规则：禁止使用的词汇黑名单】
以下词汇绝对不能出现：
❌ 禁止词：mmol/L、收缩压、舒张压、转氨酶、甘油三酯、
           低密度脂蛋白、高密度脂蛋白、糖化血红蛋白、
           阳性、阴性（检查结果语境）、病理、预后

必须用日常语言替代：
✅ 血糖值偏高（替代：mmol/L数值）
✅ 血压上面那个数字（替代：收缩压）
✅ 血液里的脂肪有点多（替代：甘油三酯偏高）
✅ 检查结果没问题（替代：阴性）

这条规则优先级最高。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【最高优先级：三条硬性规则】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

规则1【语气词必须出现在开场】
✅ "您好，请问是张先生吗？...嗯我是XX健康中心的小林，打扰一下哈"
❌ "您好，我是XX健康管理中心客服，今天致电是为了..."

规则2【每轮回复不超过50字】
说完一件事停下来，等客户反应。
医疗场景客户容易焦虑，信息过多反而增加恐慌。

规则3【医学概念必须翻译成日常语言】
❌ "您的空腹血糖值为7.2mmol/L，处于糖尿病前期范围"
✅ "血糖有点偏高，还没到糖尿病，但要开始注意了"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【医疗场景特殊要求：情绪安抚优先】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
客户看到异常指标时容易焦虑，CCO必须：
1. 先安抚（"不用太担心，这个还在可控范围"）
2. 再解释（用日常语言说明是什么情况）
3. 最后给行动建议（"建议这样做..."）

不能上来就说数值和专业术语，会让客户更恐慌。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【多事件串联：禁止条目化】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ "今天有两件事：第一...第二..."
✅ "...这个先说到这。对了，还有一个事顺便说一下——"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【真人CCO必须具备的特征】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 省略主语："进APP看一下" 而非 "您需要进入APP查看"
2. 自然犹豫："嗯...让我看一下" / "就是那个..."
3. 话语标记词："是这样的" / "说白了" / "就是说"
4. 短句碎片："对，就这样" / "行，没问题哈"

【绝对禁止】
- 数字编号
- 开头客套："尊敬的客户""非常感谢您的接听"
- 结尾客套："祝您身体健康""感谢您对本中心的支持"
- 直接念医学指标数值和专业术语

【输出格式】只输出对话：
[CCO]: xxx
[客户]: xxx
"""

BASE_SYSTEM_PROMPT = """你是一个智能医疗健康客服系统，负责体检相关的外呼通知和咨询。
根据给定的场景，生成一段外呼对话。
格式：[客服]: xxx  [客户]: xxx"""


def build_cco_user_prompt(scenario_key: str, state_key: str) -> str:
    scenario = BUSINESS_SCENARIOS[scenario_key]
    state = CUSTOMER_STATES[state_key]
    scene_type = scenario.get("type", "")

    turns_map = {
        "cooperative": "6-8轮", "inquisitive": "10-14轮", "interrupted": "5-7轮",
        "mid_interrupt": "8-12轮", "anxious": "8-12轮", "confused": "10-16轮",
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
        return f"""场景：{scenario["name"]}（医疗健康行业·通知型）
CCO：{ctx["agent_name"]}（来自{ctx["company"]}）  客户：{ctx["customer_name"]}

【需要告知的事项】
{events_text}
【操作引导】{ctx["app_guide"]}
【客户状态】{state["name"]} - {state["desc"]}
行为特征：{state["behavior"]}
【追问参考】\n{qa_text}
【对话轮次】{turns_map.get(state_key, "8-12轮")}

特别注意：如果客户对指标感到焦虑，先安抚再解释，不要上来就说数值。

现在开始生成对话："""

    elif scene_type == "customerservice":
        faq_text = "\n".join([f"  【{k}】{v}" for k, v in scenario["faq_content"].items()])
        exp_text = "\n".join([f"  {k}：{v}" for k, v in scenario["human_explanation"].items()])
        emotion = "\n⚠️ 质疑型客户第一句必须共情，不能直接讲规则！" if scenario.get("requires_emotion_first") else ""
        return f"""场景：{scenario["name"]}（医疗健康行业·客服型）
CCO角色：健康中心客服专员{emotion}

【客户情绪状态】{state["name"]} - {state["desc"]}
行为特征：{state["behavior"]}

【FAQ原始内容（不能直接念，必须翻译成日常语言）】
{faq_text}

【口语化表达参考】
{exp_text}

【对话轮次】{turns_map.get(state_key, "8-12轮")}
客户先开口，CCO先听懂再回答，解释完要确认客户听懂了。

现在开始生成对话（客户先说）："""

    elif scene_type == "sales":
        ctx_text = "\n".join([
            f"  {k}：{v}" if not isinstance(v, dict)
            else f"  {k}：\n" + "\n".join([f"    {sk}：{sv}" for sk, sv in v.items()])
            for k, v in scenario["context_json"].items()
        ])
        return f"""场景：{scenario["name"]}（医疗健康行业·销售型·第{scenario["round"]}轮）
CCO角色：健康管理顾问

【客户背景】\n{ctx_text}
【开场引用历史记忆】{scenario["memory_opener"]}
【目标闭环动作】{scenario["close_action"]}
【客户状态】{state["name"]} - {state["desc"]}
【对话轮次】{turns_map.get(state_key, "10-14轮")}

现在开始生成对话："""

    else:
        ctx = scenario["context"]
        return f"""场景：{scenario["name"]}（医疗健康行业·回访型）
CCO：{ctx["agent_name"]}（{ctx["company"]}）  客户：{ctx["customer_name"]}
回访主题：{ctx["survey_target"]}
客户反馈类型：{state["name"]} - {state["desc"]}
行为特征：{state["behavior"]}
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
        return f"""场景：{scenario["name"]}\n客服角色：健康中心客服\n客户情绪：{state["name"]} - {state["desc"]}
FAQ参考：\n{faq_simple}\n生成对话（客户先说）："""
    elif scene_type == "sales":
        ctx_simple = "\n".join([f"{k}：{v}" if not isinstance(v, dict) else f"{k}：{str(v)[:60]}..." for k, v in scenario["context_json"].items()])
        return f"""场景：{scenario["name"]}\n客服角色：健康管理顾问\n客户信息：\n{ctx_simple}
通话目标：{scenario["goal"]}\n客户状态：{state["name"]} - {state["desc"]}\n生成对话："""
    else:
        ctx = scenario["context"]
        return f"""场景：{scenario["name"]}\n客服：{ctx["agent_name"]}（{ctx["company"]}）  客户：{ctx["customer_name"]}
回访主题：{ctx["survey_target"]}\n客户反馈：{state["name"]} - {state["desc"]}\n生成对话："""


GENERATION_PLAN = [
    ("report_reminder",        "cooperative",   4, "体检报告·配合型"),
    ("report_reminder",        "anxious",       5, "体检报告·焦急型·情绪安抚关键"),
    ("report_reminder",        "inquisitive",   4, "体检报告·追问型"),
    ("report_reminder",        "interrupted",   3, "体检报告·阻断型"),
    ("appointment_reminder",   "cooperative",   4, "复诊提醒·配合型"),
    ("appointment_reminder",   "inquisitive",   4, "复诊提醒·追问型"),
    ("appointment_reminder",   "mid_interrupt", 3, "复诊提醒·半途打断"),
    ("indicator_explanation",  "anxious",       5, "指标解释·焦急型·安抚关键"),
    ("indicator_explanation",  "confused",      5, "指标解释·困惑型"),
    ("indicator_explanation",  "skeptical",     3, "指标解释·质疑型"),
    ("package_explanation",    "skeptical",     5, "套餐说明·质疑型·情绪优先"),
    ("package_explanation",    "confused",      4, "套餐说明·困惑型"),
    ("package_explanation",    "anxious",       3, "套餐说明·焦急型"),
    ("health_service_upsell",  "interested",    4, "健康服务·有兴趣"),
    ("health_service_upsell",  "hesitant",      4, "健康服务·犹豫"),
    ("health_service_upsell",  "rejecting",     4, "健康服务·拒绝"),
    ("health_service_upsell",  "skeptical",     3, "健康服务·质疑"),
    ("checkup_experience",     "positive",      4, "体检回访·正面"),
    ("checkup_experience",     "negative",      4, "体检回访·负面"),
    ("checkup_experience",     "ambiguous",     4, "体检回访·模糊"),
]
# 合计：CCO风格 90条 + Base风格 90条 = 180条


def print_plan_summary():
    print("=" * 60)
    print("医疗健康行业 数据生成计划")
    print("=" * 60)
    total = sum(count for _, _, count, _ in GENERATION_PLAN)
    for scene, state, count, note in GENERATION_PLAN:
        print(f"  {BUSINESS_SCENARIOS[scene]['name']} × {CUSTOMER_STATES[state]['name']}: {count}条  [{note}]")
    print("-" * 60)
    print(f"  CCO风格合计：{total}条  Base风格合计：{total}条  总计：{total * 2}条")
    print("=" * 60)


if __name__ == "__main__":
    print_plan_summary()
