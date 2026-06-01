"""
EduAI — 小学生 AI 学习辅导微信小程序后端
基于 FastAPI + SQLite + AI（DeepSeek/GLM/DashScope）
"""
import os
import sys
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# 将 routers 目录加入路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db
from routers import students, checkin, exams, guidance


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 EduAI 后端启动中...")
    await init_db()
    logger.info("✅ 数据库初始化完成")
    yield
    logger.info("👋 EduAI 后端关闭")


app = FastAPI(
    title="EduAI - 小学生 AI 学习辅导",
    description="AI 驱动的每日打卡、考试分析、个性化指导",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(students.router)
app.include_router(checkin.router)
app.include_router(exams.router)
app.include_router(guidance.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "EduAI"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
