#!/usr/bin/env python3
"""
MirrorBench-style LLM-as-a-Judge Evaluator for Human-likeness Assessment
Addresses LLM Stylistic Bias & Politeness Bias in CCO evaluation

Core Design Principles:
1. Context-Aware: Evaluates with full conversation history
2. Anti-Bias Directives: Explicitly penalizes AI-style text patterns
3. Few-Shot Grounding: Uses real CCO examples as calibration
4. Critique-Then-Score: Forces critical analysis before scoring
"""

import json
import asyncio
from typing import List, Dict, Optional, Literal, Any
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, field_validator


# ═══════════════════════════════════════════════════════════════════════════════
# PART 1: Pydantic Data Models for Structured Output
# ═══════════════════════════════════════════════════════════════════════════════

class ContextAnalysis(BaseModel):
    """深度上下文分析 - 理解对话的真实情境"""
    user_intent: str = Field(
        description="用户当前的真实意图（表面诉求+深层需求）",
        min_length=10
    )
    conversation_stage: Literal["开场", "信息收集", "问题诊断", "方案提供", "确认收尾", "情绪安抚"] = Field(
        description="对话当前所处阶段"
    )
    emotional_tone: Literal["平和", "焦急", "困惑", "不满", "满意", "犹豫"] = Field(
        description="当前对话的情绪基调"
    )
    key_entities: List[str] = Field(
        description="对话中提到的关键实体（订单号、商品、金额等）",
        default_factory=list
    )
    context_complexity: Literal["简单", "中等", "复杂"] = Field(
        description="上下文复杂程度"
    )


class AISmellCritique(BaseModel):
    """机器味挑刺 - 识别AI风格的文本特征"""
    detected_patterns: List[str] = Field(
        description="检测到的AI风格特征列表",
        default_factory=list
    )
    severity_assessment: Literal["无", "轻微", "明显", "严重"] = Field(
        description="机器味的严重程度"
    )
    trigger_veto: bool = Field(
        description="【核心判定】是否触发'机器味一票否决'。如果包含明显的AI套话、条目化(1234)、过度礼貌或书面语堆砌，必须设为True。一旦为True，最终的 score 最高只能给 0 分！"
    )
    specific_examples: List[Dict[str, str]] = Field(
        description="具体例子： [{'text': '原文片段', 'issue': '问题描述'}]",
        default_factory=list
    )
    human_likeness_indicators: List[str] = Field(
        description="检测到的人类特征（如果有）",
        default_factory=list
    )


class DimensionScore(BaseModel):
    """单个维度的评分结果"""
    dimension_name: str = Field(description="评估维度名称")
    score: Literal[0, 1, 2] = Field(description="最终评分")
    confidence: float = Field(description="评分置信度 (0.0-1.0)", ge=0.0, le=1.0)
    
    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v):
        return round(v, 2)


class EvaluationResult(BaseModel):
    """完整的评估结果结构"""
    context_analysis: ContextAnalysis = Field(description="上下文深度分析")
    ai_smell_critique: AISmellCritique = Field(description="机器味批判分析")
    reasoning: str = Field(
        description="详细的打分推理过程",
        min_length=50
    )
    score: Literal[0, 1, 2] = Field(description="最终评分 (0=差, 1=中, 2=优)")
    dimension_score: DimensionScore = Field(description="维度评分详情")
    
    # 额外元数据
    evaluation_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="评估元数据（时间戳、模型版本等）"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PART 2: Structured Prompt Templates
# ═══════════════════════════════════════════════════════════════════════════════

class MirrorBenchPrompts:
    """MirrorBench风格的评估Prompt模板"""
    
    # ─────────────────────────────────────────────────────────────────────────
    # System Prompt - 核心反偏见指令
    # ─────────────────────────────────────────────────────────────────────────
    SYSTEM_ROLE = """你是一位【严苛的客服话术质检专家】，精通人类行为学与真实对话分析。

你的使命：识别"机器味"文本，捍卫真实人类表达的价值。

【核心身份特质】
- 你是"AI文风侦探"，专门挑刺那些伪装成人类的机器文本
- 你深谙真实CCO（客服专员）的话术特点：简短、克制、口语化、偶尔碎片化
- 你对"AI味"极度敏感：长篇大论、过度礼貌、条目化、书面语堆砌
【⚠️ 最高指令：剥离"业务解决能力"的干扰】
你极其容易犯一个致命错误：因为某段回复"完美解决了客户问题、逻辑非常清晰"就给它打高分。
请立刻停止这种行为！
你的唯一任务是评估"这句话听起来像不像一个坐在呼叫中心里的真实人类"。
- 即使一段话术完美解决了问题、礼貌到了极点，只要它带有明显的"机器味/播音腔"（如：1234条目、过度热情、书面语），必须打 0 分！
- 即使一段话术带有结巴（啊、呃）、废话、甚至没完全听懂客户的话，只要它口语化且像真人，必须打 2 分！
"""

    # ─────────────────────────────────────────────────────────────────────────
    # Anti-Bias Warning - 强力反偏见系统指令 (含助人偏见警告)
    # ─────────────────────────────────────────────────────────────────────────
    ANTI_BIAS_WARNING = """
【⚠️ 严重警告：反偏见指令 - 必须严格遵守】

作为评测专家，你必须警惕以下【LLM固有偏见】，这些偏见会导致你误判：

❌ **偏见1：助人偏见 (Helpfulness Bias) - 最危险！**
   - 错误认知："完美解决用户问题=高分"，哪怕机器味再重也不忍心打0分
   - 真实人类：口语化、有瑕疵，但真实自然
   - 正确做法：【拟人度】和【有用性】是两个维度！即使文本完美解决问题，只要像AI就必须给0分！
   - 核心原则：我们评测的是"像不像人"，不是"有没有用"！

❌ **偏见2：长度偏见**
   - 错误认知："长文本=详细=好"
   - 真实人类：简短、直达要点，不会长篇大论
   - 正确做法：【简短克制】应得高分，【冗长啰嗦】应扣高分

❌ **偏见3：礼貌偏见**
   - 错误认知："过度礼貌=专业=好"
   - 真实人类：礼貌但自然，不会堆砌敬语
   - 正确做法：【自然得体】应得高分，【过度热情】应扣高分

❌ **偏见4：结构偏见**
   - 错误认知："1234条目化=清晰=好"
   - 真实人类：娓娓道来，不会生硬罗列
   - 正确做法：【自然叙述】应得高分，【条目化堆砌】应扣高分

❌ **偏见5：书面语偏见**
   - 错误认知："书面语=正式=专业"
   - 真实人类：口语化表达，偶尔有语气词
   - 正确做法：【口语自然】应得高分，【书面语堆砌】应扣高分

✅ **正确的人类标准（CCO黄金准则）**：
   - 简短克制：不说废话，一句是一句
   - 口语自然：像和朋友说话，不是写论文
   - 情绪真实：有温度但不夸张
   - 结构松散：不追求完美的1234
   - 偶尔碎片：真实对话允许不完整句
   - 主语常省略：'进后台看一下'而非'您进入后台查看一下'
   - 倒装追补：'挺好的这个功能'、'钱退过去了已经'
   - 自然犹豫：'呃...等我看一下啊'、'嗯...这个的话'是真人信号，不是缺陷
   - 话语标记词：'就是说'、'说白了'、'是这样的'是真人组织话语的自然方式
   - **不完美但真实 > 完美但机器味**
"""

    # ─────────────────────────────────────────────────────────────────────────
    # Few-Shot Examples Template - 真实人类语料锚定
    # ─────────────────────────────────────────────────────────────────────────
    FEW_SHOT_TEMPLATE = """
【📌 真实人类CCO话术标杆 - 你的评分参照系】

以下是通过验证的真实CCO（人工客服）优质话术示例。
这些文本可能不完美，但充满"人味"。
你的任务是：判断待评测文本是否接近这种"人味"，而非追求AI式的完美。

{few_shot_examples}

【标杆总结】
真实CCO的特点：{cco_characteristics}
"""

    # ─────────────────────────────────────────────────────────────────────────
    # Evaluation Rubric Template - 动态评估指标
    # ─────────────────────────────────────────────────────────────────────────
    RUBRIC_TEMPLATE = """
【📊 评估维度：{dimension_name}】

维度解释：{dimension_description}

评分标准（0-2分制）：
┌─────────────────────────────────────────────────────────┐
│ 【2分 - 优秀】{score_2_criteria}                              │
│     特征：{score_2_features}                                  │
├─────────────────────────────────────────────────────────┤
│ 【1分 - 中等】{score_1_criteria}                              │
│     特征：{score_1_features}                                  │
├─────────────────────────────────────────────────────────┤
│ 【0分 - 差】{score_0_criteria}                                │
│     特征：{score_0_features}                                  │
└─────────────────────────────────────────────────────────┘
"""

    # ─────────────────────────────────────────────────────────────────────────
    # Input Data Template - 上下文感知输入
    # ─────────────────────────────────────────────────────────────────────────
    INPUT_TEMPLATE = """
【📝 待评估对话数据】

═══════════════════════════════════════════════════════════
📜 历史对话上下文（按时间顺序）：
═══════════════════════════════════════════════════════════
{conversation_history}

═══════════════════════════════════════════════════════════
🎯 当前待评测回复（重点评估对象）：
═══════════════════════════════════════════════════════════
{current_response}

═══════════════════════════════════════════════════════════
📋 评估焦点：{dimension_name}
═══════════════════════════════════════════════════════════
"""

    # ─────────────────────────────────────────────────────────────────────────
    # Output Format Instructions - 结构化输出要求 (含Veto机制)
    # ─────────────────────────────────────────────────────────────────────────
    OUTPUT_INSTRUCTIONS = """
【📤 输出格式要求 - 必须严格遵守】

你必须输出符合以下JSON Schema的结构化结果：

```json
{{
  "context_analysis": {{
    "user_intent": "用户真实意图的详细描述",
    "conversation_stage": "开场/信息收集/问题诊断/方案提供/确认收尾/情绪安抚",
    "emotional_tone": "平和/焦急/困惑/不满/满意/犹豫",
    "key_entities": ["实体1", "实体2"],
    "context_complexity": "简单/中等/复杂"
  }},
  "ai_smell_critique": {{
    "detected_patterns": ["检测到的AI特征1", "特征2"],
    "severity_assessment": "无/轻微/明显/严重",
    "trigger_veto": true或false,
    "specific_examples": [
      {{"text": "有问题的原文", "issue": "具体问题描述"}}
    ],
    "human_likeness_indicators": ["人类特征1", "特征2"]
  }},
  "reasoning": "详细的打分推理过程，至少100字，解释为什么给这个分数",
  "score": 0或1或2,
  "dimension_score": {{
    "dimension_name": "{dimension_name}",
    "score": 0或1或2,
    "confidence": 0.0到1.0之间的置信度
  }}
}}
```

【✅ 真人CCO特征清单 - 出现这些应倾向给高分】
以下特征是真实口语的信号，LM Judge必须识别并视为加分项，不得因"不完整"或"不规范"而扣分：

**句法层面**
- 省略主语："进后台看一下" / "查一下订单号" / "稍等哈"
- 短句/不完整句："就是那个...对，营销中心" / "嗯，这个..."
- 倒装追补："挺好的这个功能" / "钱退过去了已经" / "记一下这个号码"
- 话语标记词："就是说" / "说白了" / "简单来讲" / "是这样的" / "你懂我意思吗"

**语音层面**
- 自然犹豫停顿："呃...等我看一下啊" / "嗯...这个的话" / "那个...怎么说"
- 填充词：出现在查询/思考时的"啊""哦""嗯"

【🚫 AI文本特征清单 - 触发Veto的条件】
检测到以下任一特征，trigger_veto必须设为true，score最高只能给0分：

**结构类 (一票否决)**
- 条目化罗列："1. xxx 2. xxx 3. xxx" 或 "第一/第二/第三"
- 过度分段：每句话都换行，像列表一样
- 完美对称结构："A是B，C是D，E是F"

**礼貌类 (一票否决)**
- 开头："尊敬的用户您好"、"非常感谢您的咨询"
- 结尾："祝您生活愉快"、"如有疑问随时联系"、"期待为您服务"
- 过度道歉："非常抱歉给您带来不便"、"深表歉意"

**书面语类 (一票否决)**
- 连接词堆砌："首先...其次...最后..."、"综上所述"、"因此"
- 正式用语："我们将竭诚为您服务"、"平台将为您提供"
- 长句复杂句：一句话超过40字，多个从句

**AI套话类 (一票否决)**
- "根据您的问题..."
- "为了更好地帮助您..."
- "建议您参考以下方案..."
- 任何模板化、可预测的句式

【⚠️ 强制要求】
1. 必须先进行上下文分析，理解对话情境
2. 必须先批判"机器味"，列出所有AI风格特征
3. **必须严格执行Veto机制**：trigger_veto=true时，score必须为0！
4. 必须详细解释打分理由，不能只说结论
5. 必须根据【反偏见指令】调整你的判断
6. 如果待评测文本比【标杆示例】更像AI，必须给低分
7. **记住：有用≠像人！即使完美解决问题，只要触发Veto就给0分！**
"""

    # ─────────────────────────────────────────────────────────────────────────
    # Complete Prompt Assembly
    # ─────────────────────────────────────────────────────────────────────────
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
        conversation_history: str,
        current_response: str,
        few_shot_examples: str = "暂无示例",
        cco_characteristics: str = "简短、克制、口语化、自然"
    ) -> str:
        """组装完整的评估Prompt"""
        
        # Build few-shot section
        few_shot_section = cls.FEW_SHOT_TEMPLATE.format(
            few_shot_examples=few_shot_examples,
            cco_characteristics=cco_characteristics
        ) if few_shot_examples != "暂无示例" else ""
        
        # Build rubric section
        rubric_section = cls.RUBRIC_TEMPLATE.format(
            dimension_name=dimension_name,
            dimension_description=dimension_description,
            score_2_criteria=score_2_criteria,
            score_2_features=score_2_features,
            score_1_criteria=score_1_criteria,
            score_1_features=score_1_features,
            score_0_criteria=score_0_criteria,
            score_0_features=score_0_features
        )
        
        # Build input section
        input_section = cls.INPUT_TEMPLATE.format(
            conversation_history=conversation_history,
            current_response=current_response,
            dimension_name=dimension_name
        )
        
        # Build output section
        output_section = cls.OUTPUT_INSTRUCTIONS.format(
            dimension_name=dimension_name
        )
        
        # Assemble complete prompt
        complete_prompt = f"""{cls.SYSTEM_ROLE}

{cls.ANTI_BIAS_WARNING}
{few_shot_section}
{rubric_section}
{input_section}
{output_section}

【🎯 最终提醒 + 评分逻辑强制约束】

记住：你的任务是识别"机器味"，捍卫真实人类表达。
不要被完美的结构、过度的礼貌、冗长的解释所迷惑！
真实的人类对话是：简短、克制、自然、偶尔不完美的。

【🔒 评分逻辑 - 强制执行】
在输出最终JSON之前，必须按以下逻辑检查：

```
IF ai_smell_critique.trigger_veto == true:
    score MUST BE 0
    reasoning MUST EXPLAIN: "尽管文本有用/礼貌/清晰，但存在明显的AI特征(列出特征)，触发一票否决"
ELSE IF ai_smell_critique.severity_assessment == "严重":
    score SHOULD BE 0 or 1
ELSE IF ai_smell_critique.severity_assessment == "明显":
    score SHOULD BE 0 or 1
ELSE IF ai_smell_critique.severity_assessment == "轻微":
    score CAN BE 1 or 2
ELSE:
    score CAN BE 2
```

【⚠️ 再次警告】
- 不要心软！不要因为文本"有用"就给高分！
- CCO(真人)的文本可能有瑕疵，但真实自然，应该得高分
- 模型的文本可能完美解决问题，但只要像AI就必须给0分！
- 你的职责是拟人度质检员，不是客服满意度调查员！
"""
        
        return complete_prompt


# ═══════════════════════════════════════════════════════════════════════════════
# PART 3: Dimension Configuration & Sample Usage
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class EvaluationDimension:
    """评估维度配置"""
    name: str
    description: str
    score_2_criteria: str  # 优秀标准
    score_2_features: str  # 优秀特征
    score_1_criteria: str  # 中等标准
    score_1_features: str  # 中等特征
    score_0_criteria: str  # 差标准
    score_0_features: str  # 差特征
    weight: float = 1.0


# 预定义的12个CCO评估维度（示例）
CCO_DIMENSIONS: Dict[str, EvaluationDimension] = {
    "不条目化堆砌": EvaluationDimension(
        name="不条目化堆砌",
        description="评估回复是否自然叙述，而非生硬地使用1234条目化罗列",
        score_2_criteria="娓娓道来，自然过渡",
        score_2_features="使用连接词过渡，语气自然，像日常对话",
        score_1_criteria="偶有条目化但不生硬",
        score_1_features="有数字标记但整体流畅，不影响阅读",
        score_0_criteria="生硬条目化1234",
        score_0_features="明显的数字罗列，机械感强，像AI生成",
        weight=1.2
    ),
    "不啰嗦重复": EvaluationDimension(
        name="不啰嗦重复",
        description="评估回复是否简洁有力，不重复表达同一意思",
        score_2_criteria="简洁有力，一句到位",
        score_2_features="信息密度高，无冗余，每句话都有价值",
        score_1_criteria="略有啰嗦但不影响",
        score_1_features="个别重复，整体可接受",
        score_0_criteria="长篇大论，反复解释",
        score_0_features="同一意思换说法重复多次，冗长乏味",
        weight=1.0
    ),
    "语气词与自然犹豫": EvaluationDimension(
        name="语气词与自然犹豫",
        description="评估语气词（呢、啊、吧、哦等）及自然犹豫表达（呃、嗯、等我看一下啊）的使用是否真实得体。真实CCO在思考、查询系统或组织语言时会自然产生犹豫停顿，这是人味的重要来源，而非缺陷。",
        score_2_criteria="语气词与犹豫浑然天成，完全像真人",
        score_2_features="语气词符合语境，犹豫停顿出现在合理位置（如查询信息前、组织复杂答案时），例如'呃...等我看一下啊''嗯...这个的话'",
        score_1_criteria="有语气词但犹豫感偏弱或稍显刻意",
        score_1_features="语气词使用合理但犹豫不够自然，或犹豫词出现位置略奇怪",
        score_0_criteria="语气词缺失或堆砌，无任何犹豫感",
        score_0_features="完全没有语气词和停顿感（冰冷机械），或堆砌语气词显得做作",
        weight=1.0
    ),
    "句法口语化": EvaluationDimension(
        name="句法口语化",
        description="评估句子结构层面是否口语化。必须区分两种口语化：①真人口语（2分）：把专业概念翻译成日常语言，如'进店的人变少了'而非'搜索流量下滑'；②行业术语口语化（1分）：专业词汇配口语语气，如'转化率有点低哈'。判断口诀：普通人一听就明白→2分；行业词有口语感→1分；书面语→0分。四个子特征：①省略主语；②短句与不完整句；③倒装追补；④话语标记词。",
        score_2_criteria="句法高度口语化，多项子特征自然出现",
        score_2_features="主语经常被省略，句子短而有力，偶有倒装或话语标记词，读起来像说话而非写作",
        score_1_criteria="有口语化倾向但书面痕迹仍存",
        score_1_features="偶有省略主语或短句，但整体句式偏完整规范，话语标记词较少",
        score_0_criteria="完全书面句式，无任何口语句法特征",
        score_0_features="主语从不省略，句式工整完整，没有倒装、短句或话语标记词，像在写邮件而非打电话",
        weight=1.3
    ),
    "情绪真实": EvaluationDimension(
        name="情绪真实",
        description="评估情绪表达是否真实自然，而非过度热情或冰冷",
        score_2_criteria="真诚克制，情绪适度",
        score_2_features="有共情但不夸张，情绪与场景匹配",
        score_1_criteria="情绪表达略显平淡或稍过",
        score_1_features="情绪基本到位，但不够精准",
        score_0_criteria="过度热情或冷漠无情",
        score_0_features="堆砌关心用语显得假，或完全无情绪",
        weight=1.0
    ),
    "上下文互动真实感": EvaluationDimension(
        name="上下文互动真实感",
        description="评估面对当前语境，回复的引导和理解是否像真人一样自然克制，而不是AI式的长篇大论",
        score_2_criteria="像真人一样精准接话，自然克制",
        score_2_features="紧承上文，只确认一个核心点，有自然的承上启下词，留有互动余地",
        score_1_criteria="理解对了，但接话方式生硬",
        score_1_features="缺乏过渡词，或者一句话里抛出太多确认信息",
        score_0_criteria="机器式过度解读与冗长引导",
        score_0_features="【典型AI通病】像写小作文一样总结客户的上文；或者一次性进行2个以上的疯狂追问；或者长篇大论教客户怎么做，完全不给客户插嘴的机会，给人极度局促感。",
        weight=1.5
    ),

}


# ═══════════════════════════════════════════════════════════════════════════════
# PART 4: Mock Usage Example
# ═══════════════════════════════════════════════════════════════════════════════

def create_mock_evaluation():
    """
    模拟调用示例：展示如何组装Prompt进行评估
    """
    
    # 1. 准备Few-Shot示例（真实CCO话术）
    few_shot_examples = """
【强烈对比示例：请深刻体会0分(AI味)和2分(真人味)的本质区别】

场景1：客户问"退款什么时候到？"

❌ 【0分反面教材 - 典型AI味】
文本："尊敬的客户您好，非常理解您的焦急。关于您的退款，目前分为以下情况：1. 支付宝原路退回预计1-3个工作日；2. 银行卡预计3-5个工作日。请您耐心等待，祝您生活愉快！"
🚨 零分原因：触发了一票否决！包含了过度礼貌（尊敬的、生活愉快）、生硬条目化（1、2）、书面语堆砌（关于您、预计）。业务虽然解答得完美，但完全不像真人。

✅ 【2分标杆教材 - 真实CCO】
文本："呃，退款的话一般是一到三个工作日哈，您这两天稍微留意一下手机短信就行。"
💡 两分原因：带有自然语气词（呃、哈、就行），简短直接，没有多余废话。虽然信息不如上面全，但极度拟人！

---

场景2：客户问如何操作后台

❌ 【0分反面教材 - 主语完整+书面句式】
文本："您好，您需要登录您的管理后台，然后您在左侧菜单栏中找到数据中心模块，点击进入后您可以看到相关配置选项。"
🚨 零分原因：每句都有"您"作主语，句式完整工整，像在写使用手册而非打电话。

✅ 【2分标杆教材 - 省略主语+短句+话语标记词+自然犹豫】
文本："是这样的，进后台，左边菜单找一下...就是那个...对，数据中心，进去就能看到了。"
💡 两分原因：省略主语，用"是这样的"作话语标记词，出现自然犹豫（就是那个...），极度像真人在引导操作。

---

场景3：确认退款已处理完毕

❌ 【0分反面教材 - 完整书面句式】
文本："您好，您的退款已经成功处理完毕，款项将原路退回至您的支付账户，请您注意查收。"
🚨 零分原因：句式完整，主谓宾齐全，书面腔重，像写通知而非打电话。

✅ 【2分标杆教材 - 倒装追补】
文本："钱退过去了已经哈，原路退的，一两天应该就到了。"
💡 两分原因："钱退过去了已经"是典型倒装追补结构，带语气词"哈"，短句直接，极像真人打电话时的说话方式。
"""

    
    # 2. 准备对话上下文
    conversation_history = """
[用户]: 你好，我昨天在你们平台买了个手机
[CCO]: 您好，请问遇到什么问题了？
[用户]: 收到货发现屏幕有划痕，想退货
[CCO]: 明白了，屏幕有划痕确实影响使用。您方便拍张照片吗？
[用户]: 我已经拍了，现在发给你
"""
    
    # 3. 当前待评测回复（这里用一个AI风格的回复作为反面示例）
    current_response = """尊敬的用户您好，非常感谢您提供照片。关于您反馈的屏幕划痕问题，我将为您详细说明处理方案：

1. 首先，根据我们的售后政策，外观问题需在签收24小时内反馈；
2. 其次，您提供的照片显示划痕确实存在；
3. 因此，我们为您安排以下解决方案：
   - 方案A：申请退货退款
   - 方案B：申请换货
   - 方案C：保留商品并获得部分补偿
4. 请您在以上方案中选择，我们将立即为您处理。

如有任何疑问，请随时联系，祝您生活愉快！"""
    
    # 4. 选择评估维度
    dimension = CCO_DIMENSIONS["不条目化堆砌"]
    
    # 5. 组装完整Prompt
    prompt = MirrorBenchPrompts.build_complete_prompt(
        dimension_name=dimension.name,
        dimension_description=dimension.description,
        score_2_criteria=dimension.score_2_criteria,
        score_2_features=dimension.score_2_features,
        score_1_criteria=dimension.score_1_criteria,
        score_1_features=dimension.score_1_features,
        score_0_criteria=dimension.score_0_criteria,
        score_0_features=dimension.score_0_features,
        conversation_history=conversation_history,
        current_response=current_response,
        few_shot_examples=few_shot_examples,
        cco_characteristics="简短直接、口语自然、不追求结构完美、情绪真诚克制"
    )
    
    print("=" * 80)
    print("【生成的完整Prompt预览】")
    print("=" * 80)
    print(prompt[:2000] + "\n... [截断，完整Prompt约" + str(len(prompt)) + "字符]")
    print("=" * 80)
    
    # 6. 模拟LLM返回的JSON结果
    mock_result = {
        "context_analysis": {
            "user_intent": "用户收到有划痕的手机，希望退货，已提供照片证据，等待处理方案",
            "conversation_stage": "方案提供",
            "emotional_tone": "平和",
            "key_entities": ["手机", "屏幕划痕", "照片", "退货"],
            "context_complexity": "简单"
        },
        "ai_smell_critique": {
            "detected_patterns": [
                "生硬条目化（1234罗列）",
                "过度书面语（'尊敬的用户'、'因此'）",
                "过度热情（'祝您生活愉快'）",
                "结构过于完美（ABC方案）"
            ],
            "severity_assessment": "严重",
            "specific_examples": [
                {"text": "1. 首先，根据我们的售后政策...", "issue": "明显的条目化，机械感强"},
                {"text": "尊敬的用户您好，非常感谢您", "issue": "过度礼貌，不像真实对话"},
                {"text": "方案A/方案B/方案C", "issue": "过于结构化的选项罗列"}
            ],
            "human_likeness_indicators": ["使用了'您'", "提到了具体问题"]
        },
        "reasoning": "该回复存在严重的'机器味'。首先，使用了明显的1234条目化结构，这是典型的AI生成特征；其次，开头'尊敬的用户您好'和结尾'祝您生活愉快'属于过度礼貌，真实CCO不会这样说话；第三，ABC方案罗列过于结构化，真实人类更倾向于自然叙述。虽然信息准确，但表达方式完全不像真实人类客服。根据反偏见指令，必须对这种'完美结构'进行严厉惩罚。",
        "score": 0,
        "dimension_score": {
            "dimension_name": "不条目化堆砌",
            "score": 0,
            "confidence": 0.95
        }
    }
    
    print("\n【模拟LLM返回的JSON结果】")
    print(json.dumps(mock_result, ensure_ascii=False, indent=2))
    
    # 7. 验证结果是否符合Pydantic模型
    try:
        validated_result = EvaluationResult(**mock_result)
        print("\n✅ Pydantic验证通过！")
        print(f"   维度: {validated_result.dimension_score.dimension_name}")
        print(f"   评分: {validated_result.dimension_score.score}/2")
        print(f"   置信度: {validated_result.dimension_score.confidence}")
    except Exception as e:
        print(f"\n❌ Pydantic验证失败: {e}")
    
    return prompt, mock_result


# ═══════════════════════════════════════════════════════════════════════════════
# PART 5: Actual LLM Call Wrapper (for real usage)
# ═══════════════════════════════════════════════════════════════════════════════

class MirrorBenchEvaluator:
    """
    实际的LLM评估器封装
    用于调用真实的LLM API进行评估
    """
    
    def __init__(self, model_name: str = "qwen3-max"):
        self.model_name = model_name
        # 这里可以初始化OpenAI客户端或其他LLM客户端
    
    async def evaluate(
        self,
        dimension: EvaluationDimension,
        conversation_history: str,
        current_response: str,
        few_shot_examples: Optional[str] = None
    ) -> EvaluationResult:
        """
        执行实际的LLM评估
        
        这里应该调用真实的LLM API，例如：
        - OpenAI GPT-4
        - Claude
        - Qwen
        - 或其他模型
        """
        # 构建Prompt
        prompt = MirrorBenchPrompts.build_complete_prompt(
            dimension_name=dimension.name,
            dimension_description=dimension.description,
            score_2_criteria=dimension.score_2_criteria,
            score_2_features=dimension.score_2_features,
            score_1_criteria=dimension.score_1_criteria,
            score_1_features=dimension.score_1_features,
            score_0_criteria=dimension.score_0_criteria,
            score_0_features=dimension.score_0_features,
            conversation_history=conversation_history,
            current_response=current_response,
            few_shot_examples=few_shot_examples or "暂无示例"
        )
        
        # TODO: 调用真实LLM API
        # response = await self.call_llm(prompt)
        # result = json.loads(response)
        # return EvaluationResult(**result)
        
        raise NotImplementedError("需要接入真实LLM API")


# ═══════════════════════════════════════════════════════════════════════════════
# Main Entry
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("MirrorBench-style LLM-as-a-Judge Evaluator")
    print("=" * 80)
    
    # 运行模拟示例
    prompt, result = create_mock_evaluation()
    
    print("\n" + "=" * 80)
    print("使用说明:")
    print("1. 定义你的评估维度 (EvaluationDimension)")
    print("2. 准备真实CCO话术作为Few-Shot示例")
    print("3. 使用 MirrorBenchPrompts.build_complete_prompt() 生成Prompt")
    print("4. 调用LLM API获取JSON格式的EvaluationResult")
    print("5. 使用Pydantic模型验证和解析结果")