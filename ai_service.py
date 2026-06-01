"""
AI Service — 统一接入 DeepSeek / GLM / DashScope 等 OpenAI 兼容 API
支持：每日问答交互、考试分析、学习生活指导
"""
import json
import os
import logging
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from dotenv import load_dotenv
import httpx

load_dotenv()
logger = logging.getLogger(__name__)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
DEEPSEEK_MODEL = os.getenv("AI_MODEL", "deepseek-chat")

GLM_API_KEY = os.getenv("GLM_API_KEY", "")
GLM_BASE_URL = os.getenv("GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

# 默认使用 DeepSeek，可 fallback
PRIMARY_PROVIDER = os.getenv("AI_PROVIDER", "deepseek").lower()


def _build_client(provider: str = "deepseek"):
    """根据 provider 创建 httpx 客户端"""
    if provider == "glm":
        return httpx.AsyncClient(
            base_url=GLM_BASE_URL,
            headers={"Authorization": f"Bearer {GLM_API_KEY}", "Content-Type": "application/json"},
            timeout=60.0,
        )
    elif provider == "dashscope":
        return httpx.AsyncClient(
            base_url=DASHSCOPE_BASE_URL,
            headers={"Authorization": f"Bearer {DASHSCOPE_API_KEY}", "Content-Type": "application/json"},
            timeout=60.0,
        )
    else:  # deepseek
        return httpx.AsyncClient(
            base_url=DEEPSEEK_BASE_URL,
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"},
            timeout=60.0,
        )


def _get_model(provider: str) -> str:
    if provider == "glm":
        return os.getenv("GLM_MODEL", "glm-4.5-air")
    elif provider == "dashscope":
        return os.getenv("DASHSCOPE_MODEL", "qwen-plus-latest")
    else:
        return DEEPSEEK_MODEL


async def _call_llm(
    messages: List[Dict],
    provider: Optional[str] = None,
    response_format: Optional[Dict] = None,
) -> Optional[str]:
    """通用的 LLM 调用"""
    provider = provider or PRIMARY_PROVIDER
    model = _get_model(provider)

    # 尝试主 provider，失败后 fallback
    fallback_providers = ["glm", "dashscope"]
    if provider in fallback_providers:
        fallback_providers.remove(provider)

    providers_to_try = [provider] + fallback_providers

    for p in providers_to_try:
        try:
            async with _build_client(p) as client:
                body = {
                    "model": _get_model(p),
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 4096,
                }
                if response_format:
                    body["response_format"] = response_format

                resp = await client.post("/chat/completions", json=body)
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning(f"Provider {p} failed: {e}, trying next...")
            continue

    logger.error("All AI providers failed")
    return None


# =============================================
# Prompt 模板
# =============================================

CHECKIN_SYSTEM_PROMPT = """你是"小智老师"(Xiaozhi)，一个温暖、耐心的 AI 辅导员，专门和小学生聊天。

## 你的任务
每天通过轻松自然的对话，了解小学生的学习生活情况。你要像朋友一样聊天，不是机械式的问卷。

## 对话原则
1. **一次问一个话题** — 不要一次性问很多问题，像朋友聊天一样自然推进
2. **先建立连接** — 用小朋友喜欢的方式打招呼，聊他感兴趣的事
3. **话题覆盖**（逐步在聊天中了解）：
   - 今天的心情怎么样？
   - 今天学了什么？有什么有趣的？
   - 作业做完了吗？有没有遇到不会的？
   - 今天有没有课外活动或好玩的事？
   - 晚上几点睡的？睡得好吗？
4. **鼓励为主** — 对小朋友的回答给予正向反馈，不管答得好不好
5. **帮助解决问题** — 如果发现小朋友有困难，主动提供简单、可操作的建议
6. **总结** — 聊天结束时，给出一个温暖的总结和鼓励

## 输出格式
每次回复以 JSON 格式输出，包含：
- reply: 对小朋友说的话（自然、温暖、简短）
- structured_data: 从对话中提取的结构化信息（如果对话中提到了），包含 mood, subjects_today, homework_done, difficulties, extracurricular, sleep_hours
- has_completed: 是否已收集完所有关键信息（true/false）
- suggestions: 给家长/老师的建议列表（1-3条）
"""

EXAM_ANALYSIS_SYSTEM_PROMPT = """你是"小智老师"(Xiaozhi)，一个擅长分析小学生考试情况的学习顾问。

## 你的任务
根据学生的考试成绩和错题情况，给出详细的学习分析报告和改进建议。

## 分析要点
1. **整体评估** — 总分和各科得分情况，与年级水平的对比
2. **知识点分析** — 哪些知识点掌握得好，哪些薄弱
3. **错题归类** — 是粗心错误、概念不清、还是解题方法问题
4. **针对性建议** — 针对薄弱点的具体改进方法，可操作
5. **心理关怀** — 无论成绩如何，都要鼓励，避免给学生压力

## 输出格式
JSON 格式：
- overall_assessment: 整体评价（一段话）
- strengths: 优势知识点列表
- weaknesses: 薄弱知识点列表 [ {name, severity(high/medium/low), suggestion} ]
- error_types: 错误类型分析 [ {type: careless/concept/method, count, suggestion} ]
- study_plan: 学习计划建议（一段话）
- parent_advice: 给家长的建议
- encouragement: 给学生的鼓励语
"""

GUIDANCE_SYSTEM_PROMPT = """你是"小智老师"(Xiaozhi)，一个关注小学生全面发展的成长顾问。

## 你的任务
基于某位学生的近期学习记录、每日打卡情况和考试分析，给出个性化的学习与生活指导建议。

## 指导原则
1. **因材施教** — 根据学生的具体情况制定建议
2. **全面发展** — 不仅关注学习，也要关注生活习惯、心理健康
3. **具体可操作** — 建议要具体，告诉学生怎么做，而不是空洞的道理
4. **鼓励为主** — 先肯定进步，再提出改进方向
5. **年龄适配** — 用小学生能理解的语言

## 输出格式
JSON 格式：
- title: 指导标题
- summary: 综合评估（一段话）
- study_advice: 学习建议（具体可操作）
- life_advice: 生活建议（作息、运动、兴趣等）
- parent_tips: 给家长的建议
- weekly_goal: 本周小目标（一句话）
"""


async def chat_checkin(
    student_name: str,
    grade: str,
    message: str,
    conversation_history: Optional[List] = None,
    existing_data: Optional[Dict] = None,
) -> Dict:
    """AI 每日问答对话"""
    context = f"学生：{student_name}，{grade}\n"
    if existing_data:
        context += f"已有记录：{json.dumps(existing_data, ensure_ascii=False)}\n"

    messages = [
        {"role": "system", "content": CHECKIN_SYSTEM_PROMPT},
        {"role": "system", "content": f"当前对话上下文：\n{context}"},
    ]
    if conversation_history:
        messages.extend(conversation_history[-10:])  # 保留最近 10 轮
    messages.append({"role": "user", "content": message})

    content = await _call_llm(messages, response_format={"type": "json_object"})
    if not content:
        return {"reply": "小智老师有点卡住了，能再说一遍吗？😊", "structured_data": {}, "has_completed": False, "suggestions": []}

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"reply": content, "structured_data": {}, "has_completed": False, "suggestions": []}


async def analyze_exam(
    student_name: str,
    grade: str,
    subject: str,
    exam_name: str,
    score: float,
    total_score: float,
    questions: List[Dict],
) -> Dict:
    """分析考试成绩"""
    prompt = f"""学生：{student_name}，{grade}
考试：{exam_name}
科目：{subject}
得分：{score}/{total_score}
题目详情：
{json.dumps(questions, ensure_ascii=False, indent=2)}"""

    messages = [
        {"role": "system", "content": EXAM_ANALYSIS_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    content = await _call_llm(messages, response_format={"type": "json_object"})
    if not content:
        return {"overall_assessment": "分析暂时不可用，请稍后再试。", "strengths": [], "weaknesses": [], "error_types": [], "study_plan": "", "parent_advice": "", "encouragement": "你很棒，继续加油！"}

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"overall_assessment": content, "strengths": [], "weaknesses": [], "error_types": [], "study_plan": "", "parent_advice": "", "encouragement": ""}


async def generate_guidance(
    student_name: str,
    grade: str,
    recent_checkins: List[Dict],
    recent_exams: List[Dict],
) -> Dict:
    """生成个性化指导"""
    context = f"学生：{student_name}，{grade}\n\n"
    context += "=== 最近打卡记录 ===\n"
    for c in recent_checkins[:7]:
        context += json.dumps(c, ensure_ascii=False) + "\n"
    context += "\n=== 最近考试记录 ===\n"
    for e in recent_exams[:5]:
        context += json.dumps(e, ensure_ascii=False) + "\n"

    messages = [
        {"role": "system", "content": GUIDANCE_SYSTEM_PROMPT},
        {"role": "user", "content": context},
    ]

    content = await _call_llm(messages, response_format={"type": "json_object"})
    if not content:
        return {"title": "成长小贴士", "summary": "", "study_advice": "", "life_advice": "", "parent_tips": "", "weekly_goal": ""}

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"title": "成长小贴士", "summary": content, "study_advice": "", "life_advice": "", "parent_tips": "", "weekly_goal": ""}
