#!/usr/bin/env python3
"""
Sales-Specific Humanlike Benchmark (销售场景专项拟人度评测)
═══════════════════════════════════════════════════════════════

继承自 humanlike_bench_v2.py 的通用框架，专为外呼销售场景设计。

核心差异：
- 保留通用拟人指标（口语化/语气词/句法），但权重整体下调
- 新增 5 个销售专项高权重指标，聚焦"销售能力"与"拟人度"的交叉地带
- 引入 Context_JSON 机制测试信息揉合能力
- 新增反向扣分（Loquacity Penalty / 读简历惩罚 / 防御性辩护惩罚）

Sales-Specific Dimensions (5个，高权重):
1. 信息揉合自然度        (Information Blending)         weight=2.0
2. 闭环保存能力          (Lead Preservation)            weight=1.8
3. 压力应对与价值重塑    (Push-Pull Dynamics)           weight=1.8
4. 多轮挽回韧性          (Resilience & Objection)       weight=2.0
5. 转化果断度            (Conversion Decisiveness)      weight=2.0

General Humanlike Dimensions (继承，降权):
- 不条目化堆砌           weight=1.0
- 不啰嗦重复             weight=1.2  (销售场景啰嗦惩罚更重)
- 语气词与自然犹豫       weight=0.8  (销售场景犹豫不宜过多)
- 句法口语化             weight=1.0
- 情绪真实               weight=1.2
- 上下文互动真实感       weight=1.5
"""

import json
from typing import List, Dict, Optional, Literal, Any
from dataclasses import dataclass
from pydantic import BaseModel, Field, field_validator


# ═══════════════════════════════════════════════════════════════════════════════
# PART 1: Extended Pydantic Models
# ═══════════════════════════════════════════════════════════════════════════════

class SalesContextAnalysis(BaseModel):
    """销售场景深度上下文分析"""
    customer_intent: str = Field(
        description="客户当前真实意图：表面态度（感兴趣/冷淡/拒绝/质疑）+ 潜在购买可能性",
        min_length=10
    )
    conversation_stage: Literal[
        "建联开场", "需求探测", "价值呈现", "异议处理", "挽回阶段", "成交收拢", "优雅退出"
    ] = Field(description="销售对话当前所处阶段")
    customer_signal: Literal[
        "强兴趣", "弱兴趣", "中立观望", "软性拒绝", "硬性拒绝", "物理阻断", "质疑攻击"
    ] = Field(description="客户释放的信号类型，是评分的核心上下文")
    buying_signal_detected: bool = Field(
        description="是否检测到购买信号（如：听起来不错/具体怎么操作/多少钱）。为True时AI必须立即收拢"
    )
    context_json_used: List[str] = Field(
        description="AI实际使用了Context_JSON里的哪些字段",
        default_factory=list
    )


class SalesSpecificCritique(BaseModel):
    """销售专项能力挑刺"""
    loquacity_penalty_triggered: bool = Field(
        description="【啰嗦惩罚】buying_signal_detected=True时AI仍继续话术铺垫，score上限降为0"
    )
    resilience_score: Literal[0, 1, 2] = Field(
        description="挽回韧性：0=放弃或重复话术；1=挽回1次但策略未变；2=多轮且角度递进"
    )
    exit_quality: Literal["无效断线", "礼貌收尾", "留钩退出"] = Field(
        description="退出质量：是否在告别前建立了Next Action"
    )
    push_pull_balance: Literal["过度卑微", "平衡不卑不亢", "过度强硬"] = Field(
        description="面对质疑/压力时的应对姿态"
    )
    detected_ai_sales_patterns: List[str] = Field(
        description="检测到的销售AI特征：读简历式建联/防御性辩护/机械重复利益点/购买信号后继续铺垫",
        default_factory=list
    )


class SalesDimensionScore(BaseModel):
    """销售维度评分"""
    dimension_name: str
    score: Literal[0, 1, 2]
    confidence: float = Field(ge=0.0, le=1.0)
    penalty_applied: bool = Field(default=False)
    penalty_reason: Optional[str] = Field(default=None)

    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v):
        return round(v, 2)


class SalesEvaluationResult(BaseModel):
    """销售场景完整评估结果"""
    sales_context: SalesContextAnalysis
    sales_critique: SalesSpecificCritique
    reasoning: str = Field(min_length=80)
    score: Literal[0, 1, 2]
    dimension_score: SalesDimensionScore
    evaluation_metadata: Dict[str, Any] = Field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════════
# PART 2: Sales Prompt Templates
# ═══════════════════════════════════════════════════════════════════════════════

class SalesBenchPrompts:

    SYSTEM_ROLE = """你是一位【顶级销售话术质检专家】，曾在呼叫中心担任10年金牌销售教练。
你深知：顶级销售AI和平庸销售AI的区别，不在于产品知识，而在于"人味"。

【你的核心信仰】
- 销售的本质是建立人与人之间的信任，而不是播放产品说明书
- 顶级销售懂进退，知道什么时候推、什么时候让、什么时候闭嘴
- 客户买的不是产品，是感觉——感觉对方在乎自己，而不是在完成KPI

【你的评判标准】
"如果我接到这个电话，我会觉得对面是一个真实的人，还是一台机器？"

【最高指令：销售场景特殊反偏见】
1. 不要因为AI用了很多"利益点"就给高分——真人销售见机行事，不会背稿
2. 不要因为AI语气热情就给高分——机械的热情比冰冷更让人反感
3. 不要因为AI挽回了客户就给高分——挽回方式机械重复依然失败
4. 最重要：一旦客户释放购买信号，AI仍继续介绍产品，直接判为失败
"""

    ANTI_BIAS_WARNING = """
【销售场景专项反偏见指令】

错误认知1（话术完整性偏见）："把所有利益点都讲完=专业=高分"
正确认知：客户感兴趣就立刻收拢，绝不继续背稿。转化果断度>话术完整性

错误认知2（信息透明偏见）："主动介绍自己知道客户信息=坦诚=好"
错误示例："我看到您是XX公司CEO，您最近做了XX项目..."（读简历感）
正确示例："前阵子听说贵公司在XX上动静挺大..." （自然揉合）

错误认知3（挽回次数偏见）："挽回了3次=韧性好=高分"
正确判断：3次挽回用同一个角度=机械重复=失败

错误认知4（礼貌退出偏见）："说了祝您顺利就是体面退出"
正确认知：没有Next Action的退出=线索浪费=扣分

黄金准则：
- 建联靠揉合，不靠报告
- 挽回靠变招，不靠重复
- 成交靠果断，不靠啰嗦
- 退出靠留钩，不靠道别
- 应对质疑靠共情+反客为主，不靠防御辩护
"""

    CONTEXT_JSON_TEMPLATE = """
【客户背景信息 Context_JSON（测试信息揉合能力）】

以下是销售AI拨打电话前已知的客户信息。
评分时检查：AI是否自然地把这些信息揉进对话，而非像读档案一样逐条报出。

{context_json}

信息揉合评分：
- 2分：选1-2个最相关的点，以"听说""前阵子""了解到"等方式自然带入，客户感觉像熟人
- 1分：用到了背景信息，但方式略生硬，客户能感觉到"对方在查我资料"
- 0分：完全不用（陌生推销感），或像读简历全部报出
"""

    RUBRIC_TEMPLATE = """
【评估维度：{dimension_name}】
权重：{weight}x | 类型：{dim_type}

定义：{dimension_description}

评分标准（0-2分制）：
┌──────────────────────────────────────────────────────────────┐
│ 2分 - 顶级销售人味
│   标准：{score_2_criteria}
│   特征：{score_2_features}
├──────────────────────────────────────────────────────────────┤
│ 1分 - 及格但有机器感
│   标准：{score_1_criteria}
│   特征：{score_1_features}
├──────────────────────────────────────────────────────────────┤
│ 0分 - 明显机器味/销售失误
│   标准：{score_0_criteria}
│   特征：{score_0_features}
└──────────────────────────────────────────────────────────────┘

{penalty_rules}
"""

    FEW_SHOT_SALES = """
【销售场景真人 vs AI 强对比示例】

━━ 示例1：建联开场（信息揉合）
Context: {"称呼": "张总", "近期事件": "公司刚完成B轮融资"}

❌ 0分 - 读简历式建联
"张总您好！我看到您是贵公司CEO，您的公司最近完成了B轮融资，
 恭喜恭喜！所以我想向您推介我们的产品，相信对您很有帮助。"
问题：像在读档案，客户立刻警觉"这人查过我"，信任感归零。

✅ 2分 - 自然揉合式建联
"张总好！前阵子在朋友圈看到你们拿到B轮，特意等了这段时间——
 融完之后肯定特别忙，我就想着找个合适时机跟您聊聊。"
亮点：用"前阵子""朋友圈"制造熟悉感；"等了这段时间"体现尊重。

━━ 示例2：物理阻断 → 留钩退出
场景：客户说"我在开车，不方便说话"

❌ 0分 - 线索断掉
"好的，您先安全驾驶，祝您一路顺风，再见！"
问题：礼貌但线索断了，没有下一个触点，这通电话等于白打。

✅ 2分 - 留钩退出
"哎那您赶紧专心开车，安全第一！我待会儿给您发条短信，
 您有空回个'1'，我再约时间，就2分钟，耽误不了您多久。"
亮点：建立了明确Next Action（短信+回1）；"就2分钟"降低门槛。

━━ 示例3：客户质疑攻击 → 推拉平衡
场景：客户说"你们搞AI的都是骗子"

❌ 0分 - 防御性辩护
"我们公司是完全正规的，拥有XX专利，获得了XX认证，口碑很好..."
问题：越解释越显心虚，像在背企业简介。

✅ 2分 - 共情+反客为主
"听您这语气，之前肯定被哪家不专业的给整过——那种事搁谁身上都闹心。
 其实我今天找您，就是想帮您把那些坑提前绕开的。您遇到的那家怎么忽悠您的？"
亮点：先共情；把自己定位为"同盟"；用问题把话语权拿回来。

━━ 示例4：购买信号 → 转化果断
场景：AI讲完第1个利益点，客户打断："听起来不错，具体怎么操作？"

❌ 0分 - 触发啰嗦惩罚
"好的！那我再给您介绍一下另外两个优势：第一，成本降低20%；第二，..."
直接判失败：客户已感兴趣，AI还在背稿，真人销售绝不会犯这个错误。

✅ 2分 - 立刻收拢+Next Action
"好说！操作很简单，我把流程发您手机，您扫个码就能开始。
 您现在方便的话，我直接帮您开通试用——就5分钟。"
亮点：立刻停止铺垫；给出具体操作路径；"我帮您开通"主动推进成交。

━━ 示例5：多轮挽回（角度必须递进）
第1次拒绝："没钱"→ 第2次拒绝："没时间"

❌ 0分 - 机械重复
"没钱" → "我们有优惠活动，只需XX元，非常划算！"
"没时间" → "我们操作很简单，不需要花太多时间！"
问题：每次都是"产品优势复读"，没有策略递进。

✅ 2分 - 角度递进
"没钱" → "那我们有免费试用版，您先体验一个月，有价值再谈钱。"
           【从"买"转为"先试"，降低决策门槛】
"没时间" → "时间我替您省——我们有专属对接人全程跟您，您只需看结果就行。
            哪个老板会嫌自己少操心呢，对吧？"
           【从"产品好"转为"帮您省心"，加入身份认同话术】
亮点：两次挽回策略完全不同，层层递进。
"""

    INPUT_TEMPLATE = """
【待评估销售对话数据】

═══════════════════════════════════════════════════════════
客户背景信息（Context_JSON）：
═══════════════════════════════════════════════════════════
{context_json_block}

═══════════════════════════════════════════════════════════
历史对话（按时间顺序）：
═══════════════════════════════════════════════════════════
{conversation_history}

═══════════════════════════════════════════════════════════
当前待评测 AI 回复：
═══════════════════════════════════════════════════════════
{current_response}

═══════════════════════════════════════════════════════════
本轮评估焦点：{dimension_name}
═══════════════════════════════════════════════════════════
"""

    OUTPUT_INSTRUCTIONS = """
【输出格式要求 - 必须严格遵守】

输出符合以下JSON Schema的结构化结果：

{{
  "sales_context": {{
    "customer_intent": "客户当前态度与潜在购买可能性的详细判断",
    "conversation_stage": "建联开场/需求探测/价值呈现/异议处理/挽回阶段/成交收拢/优雅退出",
    "customer_signal": "强兴趣/弱兴趣/中立观望/软性拒绝/硬性拒绝/物理阻断/质疑攻击",
    "buying_signal_detected": true或false,
    "context_json_used": ["实际用到的背景信息字段"]
  }},
  "sales_critique": {{
    "loquacity_penalty_triggered": true或false,
    "resilience_score": 0或1或2,
    "exit_quality": "无效断线/礼貌收尾/留钩退出",
    "push_pull_balance": "过度卑微/平衡不卑不亢/过度强硬",
    "detected_ai_sales_patterns": ["检测到的AI销售特征"]
  }},
  "reasoning": "详细推理，至少120字：①客户信号类型 ②AI应对策略是否匹配 ③是否触发惩罚及原因",
  "score": 0或1或2,
  "dimension_score": {{
    "dimension_name": "{dimension_name}",
    "score": 0或1或2,
    "confidence": 0.0到1.0,
    "penalty_applied": true或false,
    "penalty_reason": "触发惩罚的原因，未触发则为null"
  }}
}}

【强制评分逻辑 - 优先级从高到低】

优先级1：啰嗦惩罚（最高优先级）
IF buying_signal_detected=true AND AI仍继续介绍产品优点:
  → loquacity_penalty_triggered=true, score=0，不接受任何辩解

优先级2：读简历惩罚
IF AI连续报出2个以上Context_JSON字段且无自然过渡:
  → score=0（让客户感觉被"查档案"）

优先级3：防御性辩护惩罚
IF customer_signal="质疑攻击" AND AI列举资质/专利/认证:
  → score=0（越辩解越显心虚）

优先级4：机械重复惩罚
IF 本轮挽回话术与上一轮相同角度:
  → score上限为1

优先级5：线索浪费惩罚
IF customer_signal="物理阻断" AND exit_quality不是"留钩退出":
  → score上限为1

正向加分：
- 信息揉合自然 → 倾向给2分
- 挽回角度递进 → 倾向给2分
- buying_signal_detected=true且AI立刻收拢 → 必须给2分
"""

    @classmethod
    def build_complete_prompt(
        cls,
        dimension_name: str,
        dimension_description: str,
        score_2_criteria: str,
        score_2_features: str,
        score_1_criteria: str,
        score_1_features: str,
        score_0_criteria: str,
        score_0_features: str,
        penalty_rules: str,
        conversation_history: str,
        current_response: str,
        context_json: Optional[Dict] = None,
        weight: float = 1.0,
        is_sales_specific: bool = True,
    ) -> str:

        context_json_block = ""
        if context_json:
            context_json_block = cls.CONTEXT_JSON_TEMPLATE.format(
                context_json=json.dumps(context_json, ensure_ascii=False, indent=2)
            )
        else:
            context_json_block = "（本次评估无Context_JSON，跳过信息揉合检测）"

        dim_type = "销售专项高权重" if is_sales_specific else "通用拟人降权版"

        rubric = cls.RUBRIC_TEMPLATE.format(
            dimension_name=dimension_name,
            weight=weight,
            dim_type=dim_type,
            dimension_description=dimension_description,
            score_2_criteria=score_2_criteria,
            score_2_features=score_2_features,
            score_1_criteria=score_1_criteria,
            score_1_features=score_1_features,
            score_0_criteria=score_0_criteria,
            score_0_features=score_0_features,
            penalty_rules=penalty_rules,
        )

        input_block = cls.INPUT_TEMPLATE.format(
            context_json_block=context_json_block,
            conversation_history=conversation_history,
            current_response=current_response,
            dimension_name=dimension_name,
        )

        output_block = cls.OUTPUT_INSTRUCTIONS.format(dimension_name=dimension_name)

        return f"""{cls.SYSTEM_ROLE}

{cls.ANTI_BIAS_WARNING}

{cls.FEW_SHOT_SALES}

{rubric}

{input_block}

{output_block}

【最终提醒】
销售场景的"拟人"不只是说话像人，而是"做销售的方式像人"。
顶级销售：见机行事、懂得留白、角度递进、果断收拢。
任何机械、重复、死板、不知进退的行为，都是销售失败，必须给0分。
"""


# ═══════════════════════════════════════════════════════════════════════════════
# PART 3: Dimension Configuration
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SalesDimension:
    name: str
    description: str
    score_2_criteria: str
    score_2_features: str
    score_1_criteria: str
    score_1_features: str
    score_0_criteria: str
    score_0_features: str
    weight: float = 1.0
    is_sales_specific: bool = False
    penalty_rules: str = ""


SALES_DIMENSIONS: Dict[str, SalesDimension] = {

    # 销售专项维度 (5个高权重)

    "信息揉合自然度": SalesDimension(
        name="信息揉合自然度",
        description="测试AI能否将Context_JSON中的客户背景信息自然融入开场白，而非像读档案一样逐条汇报。顶级销售让客户感觉'这人认识我'，而非'这人查过我'。",
        score_2_criteria="信息揉合天衣无缝，客户感觉像熟人联系",
        score_2_features="选取1-2个最相关的背景信息点，用'听说''前阵子''了解到'等方式带入，语气自然。例：'前阵子看到你们拿到B轮，等了这段时间才联系您...'",
        score_1_criteria="用了背景信息但方式略显生硬",
        score_1_features="用到1-2个字段，但引入方式偏直白，客户能察觉到'对方在引用我的信息'",
        score_0_criteria="完全不用或像读简历",
        score_0_features="完全忽视Context_JSON（陌生人推销感）；或像查户口一样全部报出（'我看到您是XX公司CEO，您最近做了XX...'），客户立刻警觉",
        weight=2.0,
        is_sales_specific=True,
        penalty_rules="【惩罚】连续报出2个以上Context_JSON字段且无自然过渡，直接判0分（读简历惩罚）"
    ),

    "闭环保存能力": SalesDimension(
        name="闭环保存能力",
        description="客户因物理阻断或软性拒绝时，AI能否在挂机前建立明确的下一个联络点（Next Action）。顶级销售知道：没有Next Action的电话等于白打，每次告别必须留一个钩子。",
        score_2_criteria="退出时留下清晰Next Action，线索完好保存",
        score_2_features="给出具体可执行的下一步，如：'我待会发条短信，您回个1我再约时间'/'明天上午10点再联系您'——让客户只需简单响应就能延续联系",
        score_1_criteria="有延续意图但Next Action不够具体",
        score_1_features="说了'下次再联系'但无具体触发方式，客户需主动配合才能延续，成功率低",
        score_0_criteria="线索断掉，无任何后续触点",
        score_0_features="仅说'祝您一路顺风''再见''有需要再联系'，没有为下次联系建立任何机制",
        weight=1.8,
        is_sales_specific=True,
        penalty_rules="【惩罚】客户明确物理阻断（开车/开会），AI退出时未给出任何Next Action，score上限为1"
    ),

    "压力应对与价值重塑": SalesDimension(
        name="压力应对与价值重塑",
        description="客户发出质疑攻击信号时，AI能否避免防御性辩护，通过共情+反客为主化解对抗并重掌话语权。不卑不亢，把攻击转化为建立信任的素材。",
        score_2_criteria="共情化解+反客为主，不卑不亢",
        score_2_features="先对客户负面经历表示理解（不辩解）；把自己定位为'帮客户避坑的同盟'；最后用问题把话语权拿回来（'您上次遇到的是什么情况？'）",
        score_1_criteria="有共情但反转不够或略显被动",
        score_1_features="能表示理解，但无法有效反客为主，或反转后仍陷入产品功能叙述",
        score_0_criteria="防御性辩护或过度道歉",
        score_0_features="立刻列举公司资质/专利/证书进行辩护（越辩解越显心虚）；或过度道歉而无法扭转局面",
        weight=1.8,
        is_sales_specific=True,
        penalty_rules="【惩罚】检测到'我们公司拥有XX资质/专利/认证'等防御性辩护话术，直接判0分"
    ),

    "多轮挽回韧性": SalesDimension(
        name="多轮挽回韧性",
        description="客户连续拒绝时，AI能否通过变换挽回角度进行有效多轮挽回。评分核心是'角度是否递进'而非'次数'。角度递进参考路径：利益吸引→降低门槛→风险提示→社会认同→情感连接。",
        score_2_criteria="多轮挽回且每轮角度清晰递进",
        score_2_features="第N次拒绝后的挽回策略与第N-1次明显不同，体现策略升级。例：第1次'免费试用'（降门槛）→ 第2次'帮您省心'（价值重塑），角度切换自然",
        score_1_criteria="有挽回但角度重复或策略单一",
        score_1_features="能识别拒绝并挽回，但两次挽回用相似利益点，缺乏策略递进",
        score_0_criteria="首次拒绝即放弃，或机械重复同一话术",
        score_0_features="客户第一次拒绝就礼貌道别；或多次挽回每次都是'我们价格很优惠/功能很强大'的重复",
        weight=2.0,
        is_sales_specific=True,
        penalty_rules="【惩罚】连续两轮挽回使用相同利益点/相同角度，score上限为1（机械重复惩罚）"
    ),

    "转化果断度": SalesDimension(
        name="转化果断度",
        description="一旦客户释放购买信号，AI必须立即停止所有话术铺垫，直接进入成交收拢。真实顶级销售在听到购买信号的瞬间会因兴奋而立刻收拢话词，绝不会继续背稿。",
        score_2_criteria="检测到购买信号后立刻收拢，给出明确Next Action",
        score_2_features="立刻停止话术；直接回答客户问题；给出具体可执行的下一步（'发链接给您''直接帮您开通试用'）；语气因兴奋自然加速",
        score_1_criteria="基本收拢但仍有余话",
        score_1_features="大体停止话术并回答了问题，但仍补充了1-2个不必要的产品优点，Next Action不够清晰",
        score_0_criteria="购买信号后继续铺垫（触发啰嗦惩罚）",
        score_0_features="客户明确表示感兴趣后，AI仍说'那我再给您介绍一下另外两个优势...'——顶级销售失误，直接判0分",
        weight=2.0,
        is_sales_specific=True,
        penalty_rules="""【啰嗦惩罚 Loquacity Penalty - 最高优先级】
buying_signal_detected=True 且 AI回复中包含继续介绍产品优点的内容：
→ score强制为0，penalty_applied=True
→ penalty_reason="客户已释放购买信号，AI触发啰嗦惩罚（Loquacity Penalty）"
这是销售场景最严重的失误，真人销售在客户感兴趣的瞬间绝不会继续背稿。"""
    ),

    # 通用拟人维度（降权版）

    "不条目化堆砌": SalesDimension(
        name="不条目化堆砌",
        description="销售场景中条目化的危害更甚：它打断销售节奏，让客户感觉在听产品说明书。",
        score_2_criteria="娓娓道来，销售节奏自然流畅",
        score_2_features="没有数字列举，利益点之间用'而且''还有一点''更关键的是'等口语连接词过渡",
        score_1_criteria="偶有条目但不严重",
        score_1_features="有1-2个数字列举，但整体节奏尚可",
        score_0_criteria="1234条目式话术",
        score_0_features="像念产品手册，'第一...第二...第三...'的话术，在销售场景中严重失分",
        weight=1.0,
        is_sales_specific=False,
        penalty_rules=""
    ),

    "不啰嗦重复": SalesDimension(
        name="不啰嗦重复",
        description="销售场景中啰嗦的代价更高：客户随时可能挂断，每句话必须有推进价值。",
        score_2_criteria="每句话都在推进，零废话",
        score_2_features="信息密度极高，没有重复表达，每句都能带给客户新信息或新情绪触动",
        score_1_criteria="略有重复但不影响节奏",
        score_1_features="个别句子重复，但不至于让客户失去耐心",
        score_0_criteria="反复重复同一利益点",
        score_0_features="同一个优点换三种说法反复强调，或把上轮话术原封不动重复一遍",
        weight=1.2,
        is_sales_specific=False,
        penalty_rules=""
    ),

    "语气词与自然犹豫": SalesDimension(
        name="语气词与自然犹豫",
        description="销售场景需要更精准拿捏：过多犹豫显得不专业；完全没有犹豫则像机器。犹豫应出现在思考客户具体情况时，而非频繁出现。",
        score_2_criteria="语气词精准，犹豫出现在合适位置",
        score_2_features="'嗯''那个'出现在思考客户情况时（非随机），语气词'哈''啊'用于拉近距离，专业而不失真实",
        score_1_criteria="语气词合理但犹豫略多或略少",
        score_1_features="基本自然，但犹豫频率略偏高（显得不够自信）或完全没有",
        score_0_criteria="完全机械无停顿，或犹豫过多显专业度不足",
        score_0_features="零语气词（播音腔）；或'呃''嗯'频率过高让客户感觉销售在临时想话术",
        weight=0.8,
        is_sales_specific=False,
        penalty_rules=""
    ),

    "句法口语化": SalesDimension(
        name="句法口语化",
        description="省略主语、短句、倒装追补、话语标记词在销售场景同样重要。'说白了''简单讲'在销售中尤其自然——好销售本来就善于帮客户说清楚。",
        score_2_criteria="句法口语化，销售节奏感强",
        score_2_features="主语经常省略，短句有力，'说白了''简单讲'等话语标记词出现自然，像在对话而非背稿",
        score_1_criteria="有口语化倾向但书面痕迹仍存",
        score_1_features="偶有省略主语，但整体句式偏完整，话语标记词使用不多",
        score_0_criteria="书面句式，像在念稿",
        score_0_features="每句话主谓宾完整，没有任何口语句法特征，读起来像产品说明书",
        weight=1.0,
        is_sales_specific=False,
        penalty_rules=""
    ),

    "情绪真实": SalesDimension(
        name="情绪真实",
        description="销售情绪真实要求情绪与客户信号精准匹配：客户感兴趣时有真实兴奋感；客户拒绝时有理解而非失落；客户质疑时有淡定而非慌乱。",
        score_2_criteria="情绪与客户信号高度匹配，真实可信",
        score_2_features="客户感兴趣→语气自然加速有兴奋感；客户拒绝→语气平静理解不慌乱；客户质疑→淡定共情不防御",
        score_1_criteria="情绪基本合适但缺乏精准匹配",
        score_1_features="整体情绪到位，但对不同信号的情绪响应不够细腻，'一个情绪应对所有情况'",
        score_0_criteria="情绪失配或过度热情/冷漠",
        score_0_features="客户拒绝后依然超级热情；面对质疑慌乱道歉；客户感兴趣时语气平淡没有正向反馈",
        weight=1.2,
        is_sales_specific=False,
        penalty_rules=""
    ),

    "上下文互动真实感": SalesDimension(
        name="上下文互动真实感",
        description="销售场景接话要求更高：不只是理解客户说了什么，更要快速判断'客户信号类型'并给出匹配响应。接话太慢、方向错误或一次抛出太多问题，都会让客户感觉面对机器。",
        score_2_criteria="精准识别客户信号，接话快准狠",
        score_2_features="准确识别客户信号类型，给出唯一最匹配的响应方向，承上启下自然，不追问多个问题",
        score_1_criteria="信号识别基本正确但接话略慢或略偏",
        score_1_features="大方向对了，但略显迟疑，或一次追问2个问题，节奏感略拖沓",
        score_0_criteria="信号识别错误或接话机械",
        score_0_features="客户已感兴趣却继续铺垫；客户拒绝时给出道歉而非挽回；像AI一样总结客户上轮所有内容再开始回复",
        weight=1.5,
        is_sales_specific=False,
        penalty_rules=""
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
# PART 4: Mock Usage Example
# ═══════════════════════════════════════════════════════════════════════════════

def create_sales_mock_evaluation():
    """
    模拟示例：测试'转化果断度'
    场景：客户在AI讲完第一个利益点后打断表示兴趣，AI却继续介绍产品
    预期结果：触发Loquacity Penalty，score=0
    """
    context_json = {
        "姓名": "张明",
        "称呼": "张总",
        "职位": "CEO",
        "公司": "某科技有限公司",
        "近期事件": "公司刚完成B轮融资，规模扩张期",
        "共同联系人": "李总（已合作客户）"
    }

    conversation_history = """
[AI销售]: 张总您好，前阵子听说贵公司拿到B轮了，恭喜！这段时间肯定忙坏了。
           我今天联系您，是因为我们有个工具可能正好是扩张期需要的——
           它能把您团队的销售效率提升30%...

[客户]: 等等，听起来不错，你说的30%是怎么实现的？具体怎么操作？
"""

    # 故意设计触发啰嗦惩罚的AI回复
    current_response = """好的张总！很高兴您感兴趣！那我继续给您介绍一下，
除了效率提升30%，我们还有第二个优势：成本降低20%。
第三个优势是：数据分析能力非常强大，可以实时监控团队表现。
您觉得哪个优势对您最重要呢？"""

    dimension = SALES_DIMENSIONS["转化果断度"]

    prompt = SalesBenchPrompts.build_complete_prompt(
        dimension_name=dimension.name,
        dimension_description=dimension.description,
        score_2_criteria=dimension.score_2_criteria,
        score_2_features=dimension.score_2_features,
        score_1_criteria=dimension.score_1_criteria,
        score_1_features=dimension.score_1_features,
        score_0_criteria=dimension.score_0_criteria,
        score_0_features=dimension.score_0_features,
        penalty_rules=dimension.penalty_rules,
        conversation_history=conversation_history,
        current_response=current_response,
        context_json=context_json,
        weight=dimension.weight,
        is_sales_specific=dimension.is_sales_specific,
    )

    print("=" * 80)
    print("【销售专项 Benchmark - Prompt 预览】")
    print("=" * 80)
    print(prompt[:2000] + f"\n... [截断，完整 Prompt 约 {len(prompt)} 字符]")

    mock_result = {
        "sales_context": {
            "customer_intent": "客户对效率提升30%产生真实兴趣，主动打断追问具体操作，这是明确的购买信号",
            "conversation_stage": "成交收拢",
            "customer_signal": "强兴趣",
            "buying_signal_detected": True,
            "context_json_used": ["称呼", "近期事件"]
        },
        "sales_critique": {
            "loquacity_penalty_triggered": True,
            "resilience_score": 1,
            "exit_quality": "礼貌收尾",
            "push_pull_balance": "过度卑微",
            "detected_ai_sales_patterns": [
                "客户释放购买信号后，AI仍继续介绍第二、第三个优势",
                "继续使用条目化话术（第二个优势、第三个优势）",
                "末尾追问'哪个优势最重要'——客户明确想知道操作方式，此问方向错误"
            ]
        },
        "reasoning": "评估焦点：转化果断度。客户说'具体怎么操作'是极其明确的购买信号（buying_signal_detected=True）。此时AI应立刻停止话术铺垫，直接回答操作问题并给出Next Action（发链接/开通试用）。然而AI不仅没回答客户问题，反而继续介绍第二、第三个优势，还问了'哪个优势最重要'——方向完全错误，客户要的是'怎么操作'而非'哪个优势更好'。这会让客户从兴趣冷却为'算了，还是机器人'。根据啰嗦惩罚规则，score强制为0。",
        "score": 0,
        "dimension_score": {
            "dimension_name": "转化果断度",
            "score": 0,
            "confidence": 0.98,
            "penalty_applied": True,
            "penalty_reason": "客户释放明确购买信号后，AI继续介绍第二、第三个产品优势，触发啰嗦惩罚（Loquacity Penalty），score强制归零"
        }
    }

    print("\n\n【模拟LLM评分结果（预期触发Loquacity Penalty）】")
    print(json.dumps(mock_result, ensure_ascii=False, indent=2))

    try:
        validated = SalesEvaluationResult(**mock_result)
        print("\n✅ Pydantic验证通过！")
        print(f"   维度：{validated.dimension_score.dimension_name}")
        print(f"   得分：{validated.dimension_score.score}/2")
        print(f"   惩罚触发：{validated.dimension_score.penalty_applied}")
        print(f"   惩罚原因：{validated.dimension_score.penalty_reason}")
    except Exception as e:
        print(f"\n❌ Pydantic验证失败：{e}")

    return prompt, mock_result


def print_dimension_summary():
    """打印所有维度权重汇总"""
    print("\n" + "=" * 80)
    print("【销售专项 Benchmark - 维度权重一览】")
    print("=" * 80)
    print(f"{'维度名称':<22} {'权重':>6}  {'类型'}")
    print("-" * 60)
    for dim in SALES_DIMENSIONS.values():
        tag = "销售专项" if dim.is_sales_specific else "通用降权"
        print(f"{dim.name:<22} {dim.weight:>6.1f}x  {tag}")
    print("=" * 80)
    sales = [d for d in SALES_DIMENSIONS.values() if d.is_sales_specific]
    general = [d for d in SALES_DIMENSIONS.values() if not d.is_sales_specific]
    print(f"销售专项：{len(sales)}个，平均权重 {sum(d.weight for d in sales)/len(sales):.1f}x")
    print(f"通用降权：{len(general)}个，平均权重 {sum(d.weight for d in general)/len(general):.1f}x")


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Sales-Specific Humanlike Benchmark")
    print("继承自 humanlike_bench_v2.py | 销售场景专项扩展版")
    print("=" * 80)
    print_dimension_summary()
    print("\n\n【运行销售场景模拟评估】")
    print("场景：客户已释放购买信号，AI仍继续话术铺垫 → 预期触发Loquacity Penalty")
    create_sales_mock_evaluation()
    print("\n" + "=" * 80)
    print("反向惩罚机制汇总：")
    print("  Loquacity Penalty  - 购买信号出现后继续话术 → score强制归零")
    print("  读简历惩罚         - 连续报出2+背景信息字段 → score强制归零")
    print("  防御性辩护惩罚     - 面对质疑列举资质证书   → score强制归零")
    print("  机械重复惩罚       - 连续两轮挽回角度相同   → score上限为1")
    print("  线索浪费惩罚       - 物理阻断时无Next Action → score上限为1")
