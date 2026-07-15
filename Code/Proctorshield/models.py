from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from Proctorshield import db, login_manager
from flask import current_app
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Table, Column, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Association tables
teaches = Table('teaches', db.Model.metadata,
    Column('student_id', Integer, ForeignKey('student.id'), primary_key=True),
    Column('teacher_id', Integer, ForeignKey('teacher.id'), primary_key=True))

submits_assign = Table('submits_assign', db.Model.metadata,
    Column('student_id', Integer, ForeignKey('student.id'), primary_key=True),
    Column('assignment_id', Integer, ForeignKey('assignment.id'), primary_key=True),
    Column('time_submitted', DateTime, nullable=False, default=datetime.utcnow),
    Column('marks', Integer))

submits_quiz = Table('submits_quiz', db.Model.metadata,
    Column('student_id', Integer, ForeignKey('student.id'), primary_key=True),
    Column('quiz_id', Integer, ForeignKey('quiz.id'), primary_key=True),
    Column('time_submitted', DateTime, nullable=False, default=datetime.utcnow),
    Column('marks', Integer))

quiz_assigned_students = Table('quiz_assigned_students', db.Model.metadata,
    Column('student_id', Integer, ForeignKey('student.id'), primary_key=True),
    Column('quiz_id', Integer, ForeignKey('quiz.id'), primary_key=True))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    student: Mapped[Optional["Student"]] = relationship(back_populates="user", uselist=False)
    teacher: Mapped[Optional["Teacher"]] = relationship(back_populates="user", uselist=False)

    def get_reset_token(self):
        s = Serializer(current_app.config["SECRET_KEY"])
        return s.dumps({"user_id": self.id})
    
    @staticmethod
    def verify_reset_token(token, expire_sec=600):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token, max_age=expire_sec)['user_id']    
        except:
            return None
        return User.query.get(user_id)
    
    def __repr__(self):
        return f"User {self.id}, {self.name}, {self.email}"


class Student(db.Model):
    __tablename__ = 'student'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))

    user: Mapped["User"] = relationship(back_populates="student")
    profile_photo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    submitted_assignment: Mapped[List["Assignment"]] = relationship(
        secondary=submits_assign,
        back_populates="submitted_by"
    )
    submitted_quiz: Mapped[List["Quiz"]] = relationship(
        secondary=submits_quiz,
        back_populates="submitted_by"
    )


class Teacher(db.Model):
    __tablename__ = 'teacher'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))

    user: Mapped["User"] = relationship(back_populates="teacher")
    
    assignment_created: Mapped[List["Assignment"]] = relationship(back_populates="created_by")
    quiz_created: Mapped[List["Quiz"]] = relationship(back_populates="created_by")
    
    students: Mapped[List["Student"]] = relationship(
        secondary=teaches,
        backref="taught_by"
    )


class Assignment(db.Model):
    __tablename__ = 'assignment'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(30), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    time_created: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    teacher_id: Mapped[int] = mapped_column(ForeignKey('teacher.id'))
    marks: Mapped[Optional[int]] = mapped_column(Integer)

    created_by: Mapped["Teacher"] = relationship(back_populates="assignment_created")
    questions: Mapped[List["Assignment_Questions"]] = relationship(back_populates="assignment")
    submitted_by: Mapped[List["Student"]] = relationship(
        secondary=submits_assign,
        back_populates="submitted_assignment"
    )


class Assignment_Questions(db.Model):
    __tablename__ = 'assignment_questions'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    question_desc: Mapped[str] = mapped_column(String(700), nullable=False)
    marks: Mapped[Optional[int]] = mapped_column(Integer)
    photo_uri: Mapped[Optional[str]] = mapped_column(String(30))
    option_1: Mapped[str] = mapped_column(String(400), nullable=False)
    option_2: Mapped[str] = mapped_column(String(400), nullable=False)
    option_3: Mapped[str] = mapped_column(String(400), nullable=False)
    option_4: Mapped[str] = mapped_column(String(400), nullable=False)
    assignment_id: Mapped[int] = mapped_column(ForeignKey('assignment.id'))

    assignment: Mapped["Assignment"] = relationship(back_populates="questions")


class Quiz(db.Model):
    __tablename__ = 'quiz'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(30), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    duration: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    attempts_allowed: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    results_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    time_created: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    teacher_id: Mapped[int] = mapped_column(ForeignKey('teacher.id'))
    marks: Mapped[Optional[int]] = mapped_column(Integer)

    created_by: Mapped["Teacher"] = relationship(back_populates="quiz_created")
    questions: Mapped[List["Quiz_Questions"]] = relationship(back_populates="quiz")
    submitted_by: Mapped[List["Student"]] = relationship(
        secondary=submits_quiz,
        back_populates="submitted_quiz"
    )
    assigned_students: Mapped[List["Student"]] = relationship(
        secondary=quiz_assigned_students,
        backref="assigned_quizzes"
    )


class Quiz_Questions(db.Model):
    __tablename__ = 'quiz_questions'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    question_desc: Mapped[str] = mapped_column(String(700), nullable=False)
    marks: Mapped[Optional[int]] = mapped_column(Integer)
    photo_uri: Mapped[Optional[str]] = mapped_column(String(30))
    option_1: Mapped[str] = mapped_column(String(400), nullable=False)
    option_2: Mapped[str] = mapped_column(String(400), nullable=False)
    option_3: Mapped[str] = mapped_column(String(400), nullable=False)
    option_4: Mapped[str] = mapped_column(String(400), nullable=False)
    quiz_id: Mapped[int] = mapped_column(ForeignKey('quiz.id'))

    quiz: Mapped["Quiz"] = relationship(back_populates="questions")


class ProctorLog(db.Model):
    __tablename__ = 'proctor_log'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('student.id'), nullable=False)
    quiz_id: Mapped[int] = mapped_column(ForeignKey('quiz.id'), nullable=False)
    tab_switches: Mapped[int] = mapped_column(default=0)
    fullscreen_exits: Mapped[int] = mapped_column(default=0)
    face_missing: Mapped[int] = mapped_column(default=0)
    multiple_faces: Mapped[int] = mapped_column(default=0)
    look_away: Mapped[int] = mapped_column(default=0)
    noise_violations: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(String(20), default="Clean")
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    attempts_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # AI anomaly tracking
    ai_anomaly_score: Mapped[float] = mapped_column(Float, default=0.0)
    ai_risk_diagnostics: Mapped[Optional[str]] = mapped_column(String(1000), default="")
    screen_recording: Mapped[Optional[str]] = mapped_column(Text)
    camera_recording: Mapped[Optional[str]] = mapped_column(Text)

    student: Mapped["Student"] = relationship(backref=db.backref('proctor_logs', lazy=True))
    quiz: Mapped["Quiz"] = relationship(backref=db.backref('proctor_logs', lazy=True))
    snapshots: Mapped[List["SuspiciousSnapshot"]] = relationship(back_populates="proctor_log", cascade="all, delete-orphan")


class ExamFingerprint(db.Model):
    __tablename__ = 'exam_fingerprint'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('student.id'), nullable=False)
    quiz_id: Mapped[int] = mapped_column(ForeignKey('quiz.id'), nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(255))
    screen_resolution: Mapped[Optional[str]] = mapped_column(String(50))
    os_platform: Mapped[Optional[str]] = mapped_column(String(50))
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    student: Mapped["Student"] = relationship(backref=db.backref('fingerprints', lazy=True))
    quiz: Mapped["Quiz"] = relationship(backref=db.backref('fingerprints', lazy=True))


class SuspiciousSnapshot(db.Model):
    __tablename__ = 'suspicious_snapshot'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    proctor_log_id: Mapped[int] = mapped_column(ForeignKey('proctor_log.id'), nullable=False)
    violation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    image_path: Mapped[str] = mapped_column(String(200), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    proctor_log: Mapped["ProctorLog"] = relationship(back_populates="snapshots")
