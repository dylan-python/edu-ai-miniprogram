from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import Student, Exam
from schemas import ExamCreate, ExamResponse
from ai_service import analyze_exam

router = APIRouter(prefix="/api/exams", tags=["exams"])

@router.post("/", response_model=ExamResponse)
async def create_exam(data: ExamCreate, db: AsyncSession = Depends(get_db)):
    exam = Exam(
        student_id=data.student_id,
        subject=data.subject,
        exam_name=data.exam_name,
        score=data.score,
        total_score=data.total_score,
        exam_date=data.exam_date,
        questions=[q.model_dump() for q in data.questions] if data.questions else None,
    )

    # AI 分析
    if data.questions:
        result = await db.execute(select(Student).where(Student.id == data.student_id))
        student = result.scalar_one_or_none()
        if student:
            analysis = await analyze_exam(
                student_name=student.name,
                grade=student.grade,
                subject=data.subject,
                exam_name=data.exam_name or "考试",
                score=data.score or 0,
                total_score=data.total_score or 100,
                questions=[q.model_dump() for q in data.questions],
            )
            exam.analysis = analysis
            if analysis.get("weaknesses"):
                exam.weaknesses = "\n".join(
                    f"{w.get('name','')}（{w.get('severity','')}）"
                    for w in analysis["weaknesses"]
                )
            if analysis.get("study_plan") or analysis.get("parent_advice"):
                parts = []
                if analysis.get("study_plan"):
                    parts.append(f"学习计划：{analysis['study_plan']}")
                if analysis.get("parent_advice"):
                    parts.append(f"家长建议：{analysis['parent_advice']}")
                exam.suggestions = "\n\n".join(parts)

    db.add(exam)
    await db.commit()
    await db.refresh(exam)
    return exam

@router.get("/student/{student_id}", response_model=list[ExamResponse])
async def get_student_exams(student_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Exam)
        .where(Exam.student_id == student_id)
        .order_by(Exam.exam_date.desc())
    )
    return result.scalars().all()

@router.get("/{exam_id}", response_model=ExamResponse)
async def get_exam(exam_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Exam).where(Exam.id == exam_id))
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(404, "考试记录不存在")
    return exam
