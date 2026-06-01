from sqlalchemy import Column, Integer, String, Float, Text, Date, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, date
from database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    grade = Column(String(20), nullable=False, comment="年级，如 一年级、二年级")
    class_name = Column(String(20), nullable=True, comment="班级")
    school = Column(String(100), nullable=True)
    parent_name = Column(String(50), nullable=True)
    parent_phone = Column(String(20), nullable=True)
    avatar_url = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    checkins = relationship("DailyCheckin", back_populates="student", cascade="all, delete-orphan")
    exams = relationship("Exam", back_populates="student", cascade="all, delete-orphan")
    guidance = relationship("Guidance", back_populates="student", cascade="all, delete-orphan")

class DailyCheckin(Base):
    __tablename__ = "daily_checkins"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    checkin_date = Column(Date, default=date.today, nullable=False)
    mood = Column(String(20), nullable=True, comment="心情：开心/一般/不开心")
    subjects_today = Column(Text, nullable=True, comment="今天学的科目，逗号分隔")
    homework_done = Column(String(10), nullable=True, comment="作业完成情况：全部完成/部分完成/未完成")
    difficulties = Column(Text, nullable=True, comment="遇到的困难")
    extracurricular = Column(Text, nullable=True, comment="课外活动")
    sleep_hours = Column(Float, nullable=True, comment="睡眠小时数")
    notes = Column(Text, nullable=True, comment="学生自由备注")
    ai_conversation = Column(JSON, nullable=True, comment="AI 对话记录")
    ai_summary = Column(Text, nullable=True, comment="AI 生成的每日总结")
    ai_suggestion = Column(Text, nullable=True, comment="AI 建议")
    created_at = Column(DateTime, default=datetime.now)

    student = relationship("Student", back_populates="checkins")

class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject = Column(String(30), nullable=False, comment="科目：语文/数学/英语等")
    exam_name = Column(String(100), nullable=True, comment="考试名称")
    score = Column(Float, nullable=True)
    total_score = Column(Float, nullable=True)
    exam_date = Column(Date, nullable=False)
    questions = Column(JSON, nullable=True, comment="题目列表 [{question, answer, correct, score, category}]")
    analysis = Column(JSON, nullable=True, comment="AI 分析结果")
    weaknesses = Column(Text, nullable=True, comment="薄弱知识点")
    suggestions = Column(Text, nullable=True, comment="提升建议")
    created_at = Column(DateTime, default=datetime.now)

    student = relationship("Student", back_populates="exams")

class Guidance(Base):
    __tablename__ = "guidance"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    date = Column(Date, default=date.today, nullable=False)
    category = Column(String(20), nullable=False, comment="类型: study/life/general")
    title = Column(String(100), nullable=True)
    content = Column(Text, nullable=False, comment="指导内容")
    ai_generated = Column(Integer, default=1, comment="是否 AI 生成")
    source = Column(String(50), nullable=True, comment="来源: checkin/exam/manual")
    created_at = Column(DateTime, default=datetime.now)

    student = relationship("Student", back_populates="guidance")
