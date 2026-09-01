"""
Persistent storage layer (Module E: DATABASE).

Uses SQLAlchemy so the same models work against SQLite (default, zero
setup, good for local/dev/demo use) or a production database such as
Postgres by simply changing DATABASE_URL in .env -- no code changes
required.

Tables implemented (per project requirements):
    users, workflows, workflow_runs, workflow_steps,
    decisions, approvals, audit_logs, reports
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./enterprise_workflow.db")

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=_connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    pass


def _uid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=_uid)
    username = Column(String, unique=True, nullable=False)
    role = Column(String, default="operator")  # operator | approver | admin
    created_at = Column(DateTime, default=datetime.utcnow)


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(String, primary_key=True, default=_uid)
    name = Column(String, nullable=False)
    objective = Column(Text, nullable=True)
    definition_json = Column(Text, nullable=False)  # serialized workflow steps
    created_at = Column(DateTime, default=datetime.utcnow)

    runs = relationship("WorkflowRun", back_populates="workflow")


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(String, primary_key=True, default=_uid)
    workflow_id = Column(String, ForeignKey("workflows.id"), nullable=False)
    query = Column(Text, nullable=False)
    user = Column(String, default="anonymous")
    status = Column(String, default="RUNNING")
    # RUNNING | COMPLETED | FAILED | PENDING_REVIEW | REJECTED | CANCELLED
    message = Column(Text, nullable=True)
    results_json = Column(Text, nullable=True)     # snapshot of results dict
    context_json = Column(Text, nullable=True)      # resumable execution context
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)

    workflow = relationship("Workflow", back_populates="runs")
    steps = relationship("WorkflowStep", back_populates="run", cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="run", cascade="all, delete-orphan")
    approvals = relationship("Approval", back_populates="run", cascade="all, delete-orphan")


class WorkflowStep(Base):
    __tablename__ = "workflow_steps"

    id = Column(String, primary_key=True, default=_uid)
    run_id = Column(String, ForeignKey("workflow_runs.id"), nullable=False)
    step_name = Column(String, nullable=False)
    step_type = Column(String, nullable=True)
    agent = Column(String, nullable=True)
    tool = Column(String, nullable=True)
    status = Column(String, default="PENDING")  # PENDING | COMPLETED | FAILED
    duration_seconds = Column(Float, default=0)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("WorkflowRun", back_populates="steps")


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(String, primary_key=True, default=_uid)
    run_id = Column(String, ForeignKey("workflow_runs.id"), nullable=False)
    decision = Column(String, nullable=False)  # APPROVE | REJECT | REVIEW | RECOMMEND
    reasoning_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("WorkflowRun", back_populates="decisions")


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(String, primary_key=True, default=_uid)
    run_id = Column(String, ForeignKey("workflow_runs.id"), nullable=False)
    status = Column(String, default="PENDING")  # PENDING | APPROVED | REJECTED
    requested_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String, nullable=True)
    comment = Column(Text, nullable=True)

    run = relationship("WorkflowRun", back_populates="approvals")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=_uid)
    run_id = Column(String, nullable=True)
    workflow_id = Column(String, nullable=True)
    user = Column(String, default="anonymous")
    step = Column(String, nullable=True)
    agent = Column(String, nullable=True)
    tool = Column(String, nullable=True)
    decision = Column(String, nullable=True)
    status = Column(String, nullable=True)
    error = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=_uid)
    run_id = Column(String, ForeignKey("workflow_runs.id"), nullable=False)
    report_type = Column(String, nullable=False)  # pdf | docx | xlsx | json
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Create all tables if they don't already exist. Safe to call repeatedly."""
    Base.metadata.create_all(bind=engine)


def get_session():
    """Yield-style session factory for use as a FastAPI dependency."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def new_session():
    """Plain (non-generator) session for use outside of FastAPI, e.g. in the executor/UI."""
    return SessionLocal()
