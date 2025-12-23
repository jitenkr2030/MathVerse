from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class UserRole(enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"
    CREATOR = "creator"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    avatar_url = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    enrollments = relationship("Enrollment", back_populates="user")
    progress = relationship("Progress", back_populates="user")
    quiz_attempts = relationship("QuizAttempt", back_populates="user")
    payments = relationship("Payment", back_populates="user")

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    thumbnail_url = Column(String)
    level = Column(String)  # primary, secondary, senior_secondary, undergraduate, postgraduate
    subject = Column(String)
    price = Column(Float, default=0.0)
    is_free = Column(Boolean, default=True)
    is_published = Column(Boolean, default=False)
    creator_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User")
    lessons = relationship("Lesson", back_populates="course")
    enrollments = relationship("Enrollment", back_populates="course")

class Lesson(Base):
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    content = Column(Text)
    order_index = Column(Integer, default=0)
    course_id = Column(Integer, ForeignKey("courses.id"))
    video_url = Column(String)
    video_duration = Column(Integer)  # seconds
    animation_scene_path = Column(String)
    animation_class = Column(String)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    course = relationship("Course", back_populates="lessons")
    quizzes = relationship("Quiz", back_populates="lesson")
    progress = relationship("Progress", back_populates="lesson")

class Quiz(Base):
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    time_limit = Column(Integer)  # minutes
    passing_score = Column(Float, default=70.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    lesson = relationship("Lesson", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz")
    attempts = relationship("QuizAttempt", back_populates="quiz")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    question_text = Column(Text, nullable=False)
    question_type = Column(String)  # multiple_choice, true_false, text
    options = Column(Text)  # JSON string for multiple choice options
    correct_answer = Column(Text)
    explanation = Column(Text)
    points = Column(Float, default=1.0)
    order_index = Column(Integer, default=0)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="questions")

class Enrollment(Base):
    __tablename__ = "enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    progress_percentage = Column(Float, default=0.0)
    
    # Relationships
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

class Progress(Base):
    __tablename__ = "progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    is_completed = Column(Boolean, default=False)
    completion_percentage = Column(Float, default=0.0)
    watch_time = Column(Integer, default=0)  # seconds
    last_position = Column(Integer, default=0)  # seconds
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="progress")
    lesson = relationship("Lesson", back_populates="progress")

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    score = Column(Float)
    total_points = Column(Float)
    percentage = Column(Float)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    answers = Column(Text)  # JSON string of user answers
    
    # Relationships
    user = relationship("User", back_populates="quiz_attempts")
    quiz = relationship("Quiz", back_populates="attempts")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    amount = Column(Float)
    currency = Column(String, default="USD")
    status = Column(String)  # pending, completed, failed, refunded
    payment_method = Column(String)
    stripe_payment_intent_id = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="payments")
    course = relationship("Course")