from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class QuizResult(Base):
    __tablename__ = "quiz_results"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    q1_answer = Column(String(50), nullable=False)
    q2_answer = Column(String(50), nullable=False)
    q3_answer = Column(String(50), nullable=False)
    q4_answer = Column(String(50), nullable=False)
    q5_answer = Column(String(50), nullable=False)

    score = Column(JSON, nullable=False)
    recommendation = Column(String(50), nullable=False)

    ai_advice = relationship("AIAdvice", back_populates="quiz_result", uselist=False)


class AIAdvice(Base):
    __tablename__ = "ai_advices"

    id = Column(Integer, primary_key=True)
    quiz_result_id = Column(Integer, ForeignKey("quiz_results.id"), nullable=False)
    content = Column(Text, nullable=False)

    quiz_result = relationship("QuizResult", back_populates="ai_advice")
