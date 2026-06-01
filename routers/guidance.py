import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import Student, Guidance, DailyCheckin, Exam
from schemas import GuidanceCreate, GuidanceResponse
from ai_service import generate_guidance

router = APIRouter(prefix="/api/guidance", tags=["guidance"])

@router.post("/", response_model=GuidanceResponse)
async def create_guidance(data: GuidanceCreate, db: AsyncSession = Depends(get_db)):
    guidance = Guidance(**data.model_dump())
    db.add(guidance)
    await db.commit()
    await db.refresh(guidance)
    return guidance

@router.post("/ai-generate/{student_id}", response_model=dict)
async def ai_generate_guidance(student_id: int, db: AsyncSession = Depends(get_db)):
    """AI 自动生成个性化指导"""
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(404, "学生不存在")

    # 获取最近打卡和考试记录
    checkin_result = await db.execute(
        select(DailyCheckin)
        .where(DailyCheckin.student_id == student_id)
        .order_by(DailyCheckin.checkin_date.desc())
        .limit(14)
    )
    exam_result = await db.execute(
        select(Exam)
        .where(Exam.student_id == student_id)
        .order_by(Exam.exam_date.desc())
        .limit(10)
    )

    recent_checkins = []
    for c in checkin_result.scalars().all():
        recent_checkins.append({
            "date": str(c.checkin_date),
            "mood": c.mood,
            "subjects": c.subjects_today,
            "homework": c.homework_done,
            "difficulties": c.difficulties,
            "ai_summary": c.ai_summary,
        })

    recent_exams = []
    for e in exam_result.scalars().all():
        recent_exams.append({
            "date": str(e.exam_date),
            "subject": e.subject,
            "exam_name": e.exam_name,
            "score": e.score,
            "total": e.total_score,
            "weaknesses": e.weaknesses,
        })

    guidance_data = await generate_guidance(
        student_name=student.name,
        grade=student.grade,
        recent_checkins=recent_checkins,
        recent_exams=recent_exams,
    )

    # 保存到数据库
    guidance = Guidance(
        student_id=student_id,
        category="general",
        title=guidance_data.get("title", "成长指导"),
        content=json.dumps(guidance_data, ensure_ascii=False),
        source="ai_auto",
    )
    db.add(guidance)
    await db.commit()
    await db.refresh(guidance)

    return guidance_data

@router.get("/{student_id}", response_model=list[GuidanceResponse])
async def get_student_guidance(student_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Guidance)
        .where(Guidance.student_id == student_id)
        .order_by(Guidance.date.desc())
        .limit(20)
    )
    return result.scalars().all()
