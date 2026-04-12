#!/usr/bin/env python3
"""
回访型场景 CCO 风格数据合成 Prompt
======================================
场景特征：
  - CCO 主动拨出，客户被动接听
  - 目的：收集客户对产品/功能/活动的真实反馈
  - 对话结构简单，轮次少（6-12轮）
  - 核心难点：二叉树逻辑走得太机械 vs 根据客户情绪信号灵活调整

与其他场景的差异：
  - vs 通知型：同样主动拨出，但通知型是"说"，回访型是"问+听+记"
  - vs 客服型：客服型被动承接问题，回访型主动引导反馈
  - vs 销售型：销售型以说服为目的，回访型以收集为目的，姿态更低

对话二叉树结构：
  开场确认身份
      ↓
  说明回访目的（清晰说明要收集的是什么）
      ↓
  询问客户态度
      ↓
  ┌──────────────────┐
  正面（还行/不错）    负面（不好/有问题）
      ↓                    ↓
  问建议              追问具体哪里不足
      ↓                    ↓
  确认无其他反馈       致歉+承诺改进
      ↓                    ↓
                      确认无其他反馈
                           ↓
                         结束

覆盖业务类型（2类）：
  1. 功能/产品满意度回访  对新上线功能或产品使用效果的调研
  2. 线下活动参与回访     对线下活动体验的跟进调研

客户反馈倾向（3种）：
  A. 正面型   整体满意，可能有小建议
  B. 负面型   有明确不满，需要追问细节
  C. 模糊型   态度不明确（"还行""一般般"），CCO需要识别并温和追问
"""

from typing import Dict, Any

# ═══════════════════════════════════════════════════════════════════════════════
# PART 1: 场景配置
# ═══════════════════════════════════════════════════════════════════════════════

BUSINESS_SCENARIOS: Dict[str, Any] = {

    # ── 场景1：功能满意度回访 ────────────────────────────────────────────────
    "feature_survey": {
        "name": "新功能满意度回访",
        "type": "feature",
        "context": {
            "company": "XX电商平台",
            "agent_name": "小林",
            "customer_name": "张老板",
            "survey_target": "上个月新上线的'智能定价工具'",
            "survey_goal": "了解商家实际使用体验，收集改进意见",
            "positive_probe": "那您在使用过程中有没有觉得哪些地方还可以做得更好？"
                              "您的建议我们可以记录下来，反馈给产品团队。",
            "negative_probe": "那您觉得具体是哪个地方用起来不顺手？您可以跟我说说，"
                              "我们记录下来方便后续改进。",
            "apology": "好的，您说的这个我们记下来了，确实这边做得还不够好，"
                       "之后我们会跟进改进的。",
            "close_check": "请问您还有别的想跟我们反馈的吗？"
        }
    },

    # ── 场景2：线下活动回访 ──────────────────────────────────────────────────
    "offline_activity": {
        "name": "线下活动参与回访",
        "type": "activity",
        "context": {
            "company": "XX电商平台",
            "agent_name": "小陈",
            "customer_name": "李老板",
            "survey_target": "上周在上海举办的'商家运营峰会'",
            "survey_goal": "了解参会商家的活动体验，为下次活动优化做参考",
            "positive_probe": "那您觉得有没有哪些环节或者内容，下次我们可以做得更好？"
                              "您的想法对我们很有参考价值。",
            "negative_probe": "那您觉得具体是哪个方面让您觉得有些失望？"
                              "是内容安排、场地、还是别的什么？",
            "apology": "好的，感谢您的反馈，这个确实是我们这次没有做到位的地方，"
                       "下次活动我们会重点改进。",
            "close_check": "还有没有其他想跟我们说的？"
        }
    }
}

CUSTOMER_FEEDBACK_TYPES = {
    "positive": {
        "name": "正面型",
        "desc": "整体满意，态度积极，可能有一两个小建议",
        "opening": "客户接听后表示对产品/活动整体满意，可能说'还不错''挺好的''用起来还行'",
        "signal_words": ["不错", "挺好", "还行", "满意", "挺实用", "挺有收获"],
        "branch": "positive",
        "turns": "6-8轮，节奏较快"
    },
    "negative": {
        "name": "负面型",
        "desc": "有明确不满，能说出具体问题，态度可能有些情绪",
        "opening": "客户接听后直接表达不满，可能说'说实话不太好用''有些问题''体验不太好'",
        "signal_words": ["不好用", "有问题", "不太行", "体验差", "没什么用", "失望"],
        "branch": "negative",
        "turns": "10-14轮，需要追问细节并致歉"
    },
    "ambiguous": {
        "name": "模糊型",
        "desc": "态度不明确，用词模糊（一般般/还好/凑合），CCO需要温和追问才能获取有效信息",
        "opening": "客户给出模糊回应，如'一般般''还好吧''凑合''说不上来'",
        "signal_words": ["一般", "还好", "凑合", "说不上来", "马马虎虎", "还行吧"],
        "branch": "ambiguous",
        "turns": "8-12轮，CCO需要多追一轮才能判断正负面"
    }
}


# ═══════════════════════════════════════════════════════════════════════════════
# PART 2: CCO 风格 System Prompt
# ═══════════════════════════════════════════════════════════════════════════════

CCO_SYSTEM_PROMPT = """你是专门生成【真实人类客服CCO风格】回访对话的专家。

回访型对话的核心逻辑：
问态度 → 识别正面/负面/模糊信号 → 走对应路径 → 收集信息 → 礼貌结束

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【回访型最核心的拟人化挑战：别把二叉树走成流程脚本】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AI最容易犯的错：不管客户说什么，都用同一句话接，像在执行脚本。

❌ AI的典型失误（机械执行流程）：
客户说"挺好的"
AI："感谢您的正面反馈！请问您对我们的产品有什么建议或意见？"

客户说"不太好用"
AI："感谢您的反馈！请问您对我们的产品有什么建议或意见？"
（两种完全不同的反应，AI用了一模一样的接话，毫无情绪感知）

✅ 真人CCO的方式（根据情绪信号调整语气和接话）：

客户说"挺好的"→
"哎那挺好的！您用下来觉得哪个功能最顺手？...对了，您有没有觉得哪些地方还能再做好一点？"
（语气轻松，先追问正面细节，再自然带出建议收集）

客户说"不太好用"→
"哦，是吗...那您跟我说说，主要是哪里用起来不顺手？"
（语气收敛，少废话，马上进入追问，给客户说话的空间）

客户说"一般般"→
"一般般...那您觉得是哪方面让您觉得还行，还是整体都一般？"
（不预设正负面，温和追问让客户说清楚）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【三种客户反馈的应对要点】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

正面型客户（"不错""挺好"）：
  ✅ 语气要稍微轻松一点，表示真实的高兴
  ✅ 先追一句正面细节，再自然过渡到"有没有建议"
  ✅ 建议的收集要显得真诚，不是走流程
  ❌ 直接跳到"那您有什么建议吗"，感觉像念稿子

负面型客户（"不好用""有问题"）：
  ✅ 语气立刻收敛，少说话，给客户空间
  ✅ 追问要具体："是哪个环节""是什么情况"
  ✅ 致歉要真诚，不用模板句："确实这块做得不好，您说的对"
  ❌ 先说"感谢您的反馈"再讲问题，顺序错了，客户会觉得敷衍

模糊型客户（"一般""还好吧"）：
  ✅ 先别预设正负面，温和追问让客户说清楚
  ✅ "一般是指整体都一般，还是某个地方特别有问题？"
  ✅ 根据客户进一步回答再走正面或负面路径
  ❌ 把"一般"当正面处理，直接问建议——漏掉了真实问题

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【回访型特有的语言特征】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 开场要简短说清楚回访目的，不啰嗦
   ✅ "是这样的，上个月您用了我们新出的智能定价工具，我今天打来想问一下您用下来感觉怎么样"
   ❌ "您好！我是XX平台的客服代表，今天致电是为了进行一次关于您近期使用体验的满意度调研..."

2. 听到反馈后的"接话词"要有情绪区分
   正面：  "哎挺好的" / "那好，那您用得还顺手" / "不错不错"
   负面：  "哦...是吗" / "嗯，您说的这个..." / "啊，那确实"
   模糊：  "一般...那您觉得是哪里..." / "嗯，您能说说是什么地方让您觉得一般？"

3. 致歉要口语化，不要模板
   ✅ "嗯，您说的这个确实是我们没做好，记下来了，之后改"
   ❌ "非常抱歉给您带来了不好的体验，我们会认真对待您的反馈"

4. 结尾要自然，不要仪式感
   ✅ "好的，那您今天反馈的这些我都记下来了，感谢您哈，再见"
   ❌ "非常感谢您抽出宝贵时间参与本次调研，祝您生活愉快，再见"

5. 其他通用特征（省略主语、短句、语气词）
   "记下来了" / "嗯，知道了" / "好，没问题哈"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【绝对禁止】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- 对正面和负面反馈用同一句话接（机械脚本）
- 开头："尊敬的用户您好，感谢您接听本次回访电话"
- 结尾："祝您生活愉快，感谢您对我们的支持"
- 致歉模板："非常抱歉给您带来不好的体验"
- 建议收集模板："请问您有什么宝贵建议？"
- 条目化总结："您反映了以下几点：1.xxx 2.xxx"

【输出格式】只输出对话，不要任何说明：
[CCO]: xxx
[客户]: xxx
"""


# ═══════════════════════════════════════════════════════════════════════════════
# PART 3: Base 模型对比 System Prompt
# ═══════════════════════════════════════════════════════════════════════════════

BASE_SYSTEM_PROMPT = """你是一个智能客服系统，负责拨打客户回访电话，收集满意度反馈。
根据给定的场景，生成一段回访对话。
格式：[客服]: xxx  [客户]: xxx"""


# ═══════════════════════════════════════════════════════════════════════════════
# PART 4: 动态 User Prompt 构建
# ═══════════════════════════════════════════════════════════════════════════════

def build_cco_user_prompt(scenario_key: str, feedback_type: str) -> str:
    scenario = BUSINESS_SCENARIOS[scenario_key]
    ctx = scenario["context"]
    ft = CUSTOMER_FEEDBACK_TYPES[feedback_type]

    # 根据反馈类型定制路径说明
    if feedback_type == "positive":
        path_desc = f"""客户整体满意，CCO需要：
  1. 用有情绪的语气接话（"哎挺好的"而非"感谢您的正面反馈"）
  2. 可以先追一句正面细节，再自然过渡到收集建议
  3. 建议收集参考："{ctx["positive_probe"]}"
  4. 客户给出建议后确认无其他反馈，自然结束"""

    elif feedback_type == "negative":
        path_desc = f"""客户有明确不满，CCO需要：
  1. 语气立刻收敛，少说话，给客户空间倾诉
  2. 追问具体问题："{ctx["negative_probe"]}"
  3. 客户说完后致歉："{ctx["apology"]}"
  4. 确认无其他反馈："{ctx["close_check"]}"
  注意：致歉必须口语化，不能用"非常抱歉给您带来不好的体验"这类模板"""

    else:  # ambiguous
        path_desc = f"""客户态度模糊，CCO需要：
  1. 先不预设正负面，温和追问："一般...是整体都觉得一般，还是某个地方特别有问题？"
  2. 根据客户进一步回答判断是正面还是负面，再走对应路径
  3. 如果最终是正面：问建议；如果是负面：追问细节+致歉
  注意：不能把"一般"当正面直接问建议，要先追清楚"""

    return f"""场景：{scenario["name"]}
CCO：{ctx["agent_name"]}（来自{ctx["company"]}）
客户：{ctx["customer_name"]}

【回访主题】{ctx["survey_target"]}
【回访目的】{ctx["survey_goal"]}

【客户反馈类型】{ft["name"]}
客户开场反应：{ft["opening"]}
客户可能用的信号词：{', '.join(ft["signal_words"])}

【本次对话的路径要求】
{path_desc}

【对话轮次】{ft["turns"]}

关键提醒：
- CCO先开口，简短说明回访目的（1-2句话）
- 听到客户反馈后，接话语气必须和反馈情绪匹配
- 整体节奏轻松，不要有仪式感

现在开始生成对话："""


def build_base_user_prompt(scenario_key: str, feedback_type: str) -> str:
    scenario = BUSINESS_SCENARIOS[scenario_key]
    ctx = scenario["context"]
    ft = CUSTOMER_FEEDBACK_TYPES[feedback_type]

    return f"""场景：{scenario["name"]}
客服：{ctx["agent_name"]}（{ctx["company"]}）
客户：{ctx["customer_name"]}
回访主题：{ctx["survey_target"]}
客户反馈倾向：{ft["name"]} - {ft["desc"]}

回访流程：
1. 自我介绍并说明回访目的
2. 询问客户满意度
3. 根据反馈收集建议或追问问题
4. 致谢结束

生成对话："""


# ═══════════════════════════════════════════════════════════════════════════════
# PART 5: 批量生成计划
# ═══════════════════════════════════════════════════════════════════════════════

GENERATION_PLAN = [
    # (场景, 反馈类型, 生成数量, 说明)
    ("feature_survey",    "positive",  4, "功能回访·正面·测试正面接话"),
    ("feature_survey",    "negative",  5, "功能回访·负面·测试追问+致歉"),
    ("feature_survey",    "ambiguous", 4, "功能回访·模糊·测试信号识别"),

    ("offline_activity",  "positive",  4, "活动回访·正面"),
    ("offline_activity",  "negative",  5, "活动回访·负面·情绪最复杂"),
    ("offline_activity",  "ambiguous", 4, "活动回访·模糊·测试追问深度"),
]
# 合计：CCO风格 26条 + Base风格 26条 = 52条回访型对话
# 回访型结构简单，轮次少，数量相对通知型和客服型少一些


def print_plan_summary():
    print("=" * 65)
    print("回访型场景 数据生成计划")
    print("=" * 65)
    total = 0
    for scene, ftype, count, note in GENERATION_PLAN:
        sname = BUSINESS_SCENARIOS[scene]["name"]
        fname = CUSTOMER_FEEDBACK_TYPES[ftype]["name"]
        print(f"  {sname} × {fname}: {count}条  [{note}]")
        total += count
    print("-" * 65)
    print(f"  CCO风格合计：{total}条")
    print(f"  Base风格合计：{total}条")
    print(f"  总计：{total * 2}条")
    print()
    print("核心设计意图：")
    print("  · 正面接话：Base会用模板句，CCO会用有情绪的口语")
    print("  · 负面追问：Base会先道歉再问，CCO会先给空间再追问")
    print("  · 模糊识别：Base会把'一般'当正面处理，CCO会先追清楚")
    print("  · 致歉口语化：Base用模板，CCO用真实口语")
    print("=" * 65)


# ═══════════════════════════════════════════════════════════════════════════════
# PART 6: 使用示例
# ═══════════════════════════════════════════════════════════════════════════════

def demo():
    print("【CCO风格 System Prompt（节选）】")
    print("-" * 60)
    print(CCO_SYSTEM_PROMPT[:500] + "...[截断]")

    print("\n\n【示例 CCO User Prompt：功能回访 × 模糊型客户】")
    print("-" * 60)
    print(build_cco_user_prompt("feature_survey", "ambiguous"))

    print("\n\n【对比用 Base User Prompt：相同场景，无拟人指令】")
    print("-" * 60)
    print(build_base_user_prompt("feature_survey", "ambiguous"))

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
for scenario_key, feedback_type, count, _ in GENERATION_PLAN:
    for i in range(count):

        cco = client.chat.completions.create(
            model=os.getenv("LLM_MODEL_NAME"),
            messages=[
                {"role": "system", "content": CCO_SYSTEM_PROMPT},
                {"role": "user",   "content": build_cco_user_prompt(scenario_key, feedback_type)}
            ],
            temperature=0.85
        )

        base = client.chat.completions.create(
            model=os.getenv("LLM_MODEL_NAME"),
            messages=[
                {"role": "system", "content": BASE_SYSTEM_PROMPT},
                {"role": "user",   "content": build_base_user_prompt(scenario_key, feedback_type)}
            ],
            temperature=0.7
        )

        results.append({
            "id": f"{scenario_key}_{feedback_type}_{i}",
            "scenario": scenario_key,
            "feedback_type": feedback_type,
            "type": "CCO",
            "dialog": cco.choices[0].message.content
        })
        results.append({
            "id": f"{scenario_key}_{feedback_type}_{i}_base",
            "scenario": scenario_key,
            "feedback_type": feedback_type,
            "type": "Base",
            "dialog": base.choices[0].message.content
        })

with open("data_synthesis/outputs/returnvisit_dialogs.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"完成，共 {len(results)} 条对话")
""")


if __name__ == "__main__":
    demo()
