"""
MathVerse Backend API - Quizzes Module
=======================================
Quiz and assessment endpoints.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload
import json

from app.database import get_db
from app.models import Quiz, Question, QuizAttempt, User, Lesson, UserRole
from app.schemas import (
    QuizCreate, QuizUpdate, QuizResponse, QuizDetailResponse,
    QuizAttemptCreate, QuizAttemptResponse, QuestionCreate, QuestionResponse,
    MessageResponse, ErrorResponse
)
from app.dependencies import get_current_user, get_or_404


router = APIRouter()


@router.get("/", response_model=List[QuizResponse])
async def get_quizzes(
    lesson_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get all quizzes, optionally filtered by lesson.
    """
    query = select(Quiz)
    
    if lesson_id:
        query = query.where(Quiz.lesson_id == lesson_id)
    
    quizzes = db.execute(query.order_by(Quiz.created_at.desc())).scalars().all()
    
    return quizzes


@router.get("/{quiz_id}", response_model=QuizDetailResponse)
async def get_quiz(
    quiz_id: int,
    current_user: Optional[User] = None,
    db: Session = Depends(get_db)
):
    """
    Get quiz details with questions.
    """
    quiz = db.execute(
        select(Quiz)
        .options(joinedload(Quiz.questions))
        .where(Quiz.id == quiz_id)
    ).unique().scalar_one_or_none()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Sort questions by order_index
    questions = sorted(quiz.questions, key=lambda q: q.order_index)
    
    question_responses = []
    for q in questions:
        options = None
        if q.options:
            try:
                options = json.loads(q.options)
            except json.JSONDecodeError:
                options = None
        
        question_responses.append(QuestionResponse(
            id=q.id,
            quiz_id=q.quiz_id,
            question_text=q.question_text,
            question_type=q.question_type,
            options=options,
            explanation=q.explanation,
            points=q.points,
            order_index=q.order_index
        ))
    
    return QuizDetailResponse(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        lesson_id=quiz.lesson_id,
        time_limit=quiz.time_limit,
        passing_score=quiz.passing_score,
        created_at=quiz.created_at,
        questions=question_responses
    )


@router.get("/{quiz_id}/preview", response_model=QuizResponse)
async def get_quiz_preview(
    quiz_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get quiz without correct answers (for taking the quiz).
    """
    quiz = db.execute(
        select(Quiz).where(Quiz.id == quiz_id)
    ).scalar_one_or_none()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Get question count
    questions_count = db.execute(
        select(func.count(Question.id)).where(Question.quiz_id == quiz_id)
    ).scalar() or 0
    
    return QuizResponse(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        lesson_id=quiz.lesson_id,
        time_limit=quiz.time_limit,
        passing_score=quiz.passing_score,
        created_at=quiz.created_at
    )


@router.post("/", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def create_quiz(
    quiz_data: QuizCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new quiz (creator only).
    """
    if current_user.role not in [UserRole.TEACHER, UserRole.CREATOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only creators can create quizzes"
        )
    
    # Verify lesson exists
    lesson = await get_or_404(Lesson, quiz_data.lesson_id, db, "Lesson not found")
    
    quiz = Quiz(
        title=quiz_data.title,
        description=quiz_data.description,
        lesson_id=quiz_data.lesson_id,
        time_limit=quiz_data.time_limit,
        passing_score=quiz_data.passing_score
    )
    
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    
    # Create questions if provided
    for question_data in quiz_data.questions:
        options_json = None
        if question_data.options:
            options_json = json.dumps([
                {"id": opt.id, "text": opt.text, "is_correct": opt.is_correct}
                for opt in question_data.options
            ])
        
        question = Question(
            quiz_id=quiz.id,
            question_text=question_data.question_text,
            question_type=question_data.question_type.value if hasattr(question_data.question_type, 'value') else question_data.question_type,
            options=options_json,
            correct_answer=question_data.correct_answer,
            explanation=question_data.explanation,
            points=question_data.points,
            order_index=question_data.order_index
        )
        db.add(question)
    
    db.commit()
    
    return quiz


@router.put("/{quiz_id}", response_model=QuizResponse)
async def update_quiz(
    quiz_id: int,
    quiz_data: QuizUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a quiz (creator only).
    """
    quiz = await get_or_404(Quiz, quiz_id, db, "Quiz not found")
    
    update_data = quiz_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(quiz, field, value)
    
    db.commit()
    db.refresh(quiz)
    
    return quiz


@router.delete("/{quiz_id}", response_model=MessageResponse)
async def delete_quiz(
    quiz_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a quiz (creator only).
    """
    quiz = await get_or_404(Quiz, quiz_id, db, "Quiz not found")
    
    db.delete(quiz)
    db.commit()
    
    return MessageResponse(
        message="Quiz deleted successfully",
        detail=f"Quiz '{quiz.title}' has been deleted"
    )


# ==================== QUESTIONS ====================

@router.post("/{quiz_id}/questions", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def add_question(
    quiz_id: int,
    question_data: QuestionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a question to a quiz (creator only).
    """
    quiz = await get_or_404(Quiz, quiz_id, db, "Quiz not found")
    
    options_json = None
    if question_data.options:
        options_json = json.dumps([
            {"id": opt.id, "text": opt.text, "is_correct": opt.is_correct}
            for opt in question_data.options
        ])
    
    question = Question(
        quiz_id=quiz_id,
        question_text=question_data.question_text,
        question_type=question_data.question_type.value if hasattr(question_data.question_type, 'value') else question_data.question_type,
        options=options_json,
        correct_answer=question_data.correct_answer,
        explanation=question_data.explanation,
        points=question_data.points,
        order_index=question_data.order_index
    )
    
    db.add(question)
    db.commit()
    db.refresh(question)
    
    return question


# ==================== QUIZ ATTEMPTS ====================

@router.post("/{quiz_id}/attempt", response_model=QuizAttemptResponse)
async def submit_quiz_attempt(
    quiz_id: int,
    attempt_data: QuizAttemptCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a quiz attempt and get results.
    """
    quiz = db.execute(
        select(Quiz)
        .options(joinedload(Quiz.questions))
        .where(Quiz.id == quiz_id)
    ).unique().scalar_one_or_none()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Get all questions
    questions = quiz.questions
    
    # Calculate score
    total_points = 0
    earned_points = 0
    correct_answers = {}
    
    for question in questions:
        total_points += question.points
        
        user_answer = attempt_data.answers.get(str(question.id))
        correct_answer = question.correct_answer
        
        correct_answers[str(question.id)] = {
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": user_answer == correct_answer,
            "points": question.points,
            "explanation": question.explanation
        }
        
        if user_answer == correct_answer:
            earned_points += question.points
    
    percentage = (earned_points / total_points * 100) if total_points > 0 else 0
    passed = percentage >= quiz.passing_score
    
    # Create attempt record
    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz_id,
        score=earned_points,
        total_points=total_points,
        percentage=percentage,
        completed_at=datetime.utcnow(),
        answers=json.dumps(correct_answers)
    )
    
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    
    return QuizAttemptResponse(
        id=attempt.id,
        user_id=attempt.user_id,
        quiz_id=attempt.quiz_id,
        score=earned_points,
        total_points=total_points,
        percentage=percentage,
        passed=passed,
        started_at=attempt.started_at,
        completed_at=attempt.completed_at,
        answers=correct_answers
    )


@router.get("/{quiz_id}/attempts", response_model=List[QuizAttemptResponse])
async def get_quiz_attempts(
    quiz_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's attempts for a quiz.
    """
    attempts = db.execute(
        select(QuizAttempt)
        .where(
            and_(
                QuizAttempt.user_id == current_user.id,
                QuizAttempt.quiz_id == quiz_id
            )
        )
        .order_by(QuizAttempt.started_at.desc())
    ).scalars().all()
    
    results = []
    for attempt in attempts:
        answers = {}
        if attempt.answers:
            try:
                answers = json.loads(attempt.answers)
            except json.JSONDecodeError:
                pass
        
        results.append(QuizAttemptResponse(
            id=attempt.id,
            user_id=attempt.user_id,
            quiz_id=attempt.quiz_id,
            score=attempt.score,
            total_points=attempt.total_points,
            percentage=attempt.percentage,
            passed=attempt.percentage >= 70 if attempt.percentage else False,
            started_at=attempt.started_at,
            completed_at=attempt.completed_at,
            answers=answers
        ))
    
    return results


@router.get("/{quiz_id}/best-attempt")
async def get_best_attempt(
    quiz_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's best attempt for a quiz.
    """
    best_attempt = db.execute(
        select(QuizAttempt)
        .where(
            and_(
                QuizAttempt.user_id == current_user.id,
                QuizAttempt.quiz_id == quiz_id,
                QuizAttempt.completed_at.isnot(None)
            )
        )
        .order_by(QuizAttempt.percentage.desc())
        .limit(1)
    ).scalar_one_or_none()
    
    if not best_attempt:
        return {"message": "No attempts yet", "best_attempt": None}
    
    return {
        "best_attempt": {
            "id": best_attempt.id,
            "score": best_attempt.score,
            "total_points": best_attempt.total_points,
            "percentage": best_attempt.percentage,
            "completed_at": best_attempt.completed_at
        }
    }
