from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from database import get_db
from models import Student, DailyCheckin
from schemas import CheckinCreate, CheckinResponse, AIChatRequest
from ai_service import chat_checkin

router = APIRouter(prefix="/api/checkin", tags=["checkin"])

@router.post("/", response_model=CheckinResponse)
async def create_checkin(data: CheckinCreate, db: AsyncSession = Depends(get_db)):
    checkin = DailyCheckin(**data.model_dump(exclude_unset=True))
    db.add(checkin)
    await db.commit()
    await db.refresh(checkin)
    return checkin

@router.post("/ai-chat", response_model=dict)
async def ai_checkin_chat(req: AIChatRequest, db: AsyncSession = Depends(get_db)):
    """AI 对话式每日打卡"""
    result = await db.execute(select(Student).where(Student.id == req.student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(404, "学生不存在")

    session_data = req.session_data or {}

    reply = await chat_checkin(
        student_name=student.name,
        grade=student.grade,
        message=req.message,
        conversation_history=session_data.get("conversation_history"),
        existing_data=session_data.get("existing_data"),
    )

    return {
        "reply": reply.get("reply", ""),
        "structured_data": reply.get("structured_data", {}),
        "has_completed": reply.get("has_completed", False),
        "suggestions": reply.get("suggestions", []),
    }

@router.get("/history/{student_id}", response_model=list[CheckinResponse])
async def get_checkin_history(student_id: int, days: int = 30, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(DailyCheckin)
        .where(DailyCheckin.student_id == student_id)
        .order_by(DailyCheckin.checkin_date.desc())
        .limit(days)
    )
    return result.scalars().all()

@router.get("/today/{student_id}")
async def get_today_checkin(student_id: int, db: AsyncSession = Depends(get_db)):
    today = date.today()
    result = await db.execute(
        select(DailyCheckin).where(
            DailyCheckin.student_id == student_id,
            DailyCheckin.checkin_date == today,
        )
    )
    checkin = result.scalar_one_or_none()
    if not checkin:
        return None
    return CheckinResponse.model_validate(checkin)
