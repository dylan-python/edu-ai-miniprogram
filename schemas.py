from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

# ====== Student ======
class StudentCreate(BaseModel):
    name: str
    grade: str
    class_name: Optional[str] = None
    school: Optional[str] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    avatar_url: Optional[str] = None

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    grade: Optional[str] = None
    class_name: Optional[str] = None
    school: Optional[str] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    avatar_url: Optional[str] = None

class StudentResponse(BaseModel):
    id: int
    name: str
    grade: str
    class_name: Optional[str] = None
    school: Optional[str] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}

# ====== Daily Check-in ======
class CheckinCreate(BaseModel):
    student_id: int
    mood: Optional[str] = None
    subjects_today: Optional[str] = None
    homework_done: Optional[str] = None
    difficulties: Optional[str] = None
    extracurricular: Optional[str] = None
    sleep_hours: Optional[float] = None
    notes: Optional[str] = None
    checkin_date: Optional[date] = None

class CheckinResponse(BaseModel):
    id: int
    student_id: int
    checkin_date: date
    mood: Optional[str] = None
    subjects_today: Optional[str] = None
    homework_done: Optional[str] = None
    difficulties: Optional[str] = None
    extracurricular: Optional[str] = None
    sleep_hours: Optional[float] = None
    notes: Optional[str] = None
    ai_conversation: Optional[list] = None
    ai_summary: Optional[str] = None
    ai_suggestion: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}

# ====== Exam ======
class QuestionItem(BaseModel):
    question: str
    student_answer: Optional[str] = None
    correct_answer: Optional[str] = None
    is_correct: Optional[bool] = None
    score: Optional[float] = None
    max_score: Optional[float] = None
    category: Optional[str] = None  # 知识点分类

class ExamCreate(BaseModel):
    student_id: int
    subject: str
    exam_name: Optional[str] = None
    score: Optional[float] = None
    total_score: Optional[float] = None
    exam_date: date
    questions: Optional[List[QuestionItem]] = None

class ExamResponse(BaseModel):
    id: int
    student_id: int
    subject: str
    exam_name: Optional[str] = None
    score: Optional[float] = None
    total_score: Optional[float] = None
    exam_date: date
    questions: Optional[list] = None
    analysis: Optional[dict] = None
    weaknesses: Optional[str] = None
    suggestions: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}

# ====== Guidance ======
class GuidanceCreate(BaseModel):
    student_id: int
    category: str = "general"
    title: Optional[str] = None
    content: str
    source: Optional[str] = None

class GuidanceResponse(BaseModel):
    id: int
    student_id: int
    date: date
    category: str
    title: Optional[str] = None
    content: str
    ai_generated: int
    source: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}

# ====== AI Chat ======
class AIChatRequest(BaseModel):
    student_id: int
    message: str
    context_type: str = "checkin"  # checkin / exam / guidance / free
    session_data: Optional[dict] = None

class AIChatResponse(BaseModel):
    reply: str
    structured_data: Optional[dict] = None
    suggestions: Optional[List[str]] = None
