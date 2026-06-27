from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False, default="Untitled Project")
    youtube_url = Column(String(500), nullable=False)
    video_id = Column(String(50), index=True)
    channel = Column(String(200))
    duration = Column(Integer, default=0)
    views = Column(Integer, default=0)
    thumbnail_url = Column(String(500))
    description = Column(Text)
    publish_date = Column(String(50))
    language = Column(String(10), default="en")
    tags = Column(String(1000))
    folder = Column(String(200), default="")
    is_favorite = Column(Boolean, default=False)
    status = Column(String(50), default="pending")
    note = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    transcript = relationship(
        "Transcript", back_populates="project",
        uselist=False, cascade="all, delete-orphan"
    )
    content_items = relationship(
        "GeneratedContent", back_populates="project",
        cascade="all, delete-orphan"
    )
    exports = relationship(
        "ExportHistory", back_populates="project",
        cascade="all, delete-orphan"
    )

    @property
    def content_count(self) -> int:
        return len(self.content_items)

    @property
    def duration_str(self) -> str:
        s = self.duration or 0
        h = s // 3600
        m = (s % 3600) // 60
        sec = s % 60
        if h:
            return f"{h}:{m:02d}:{sec:02d}"
        return f"{m}:{sec:02d}"


class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    content = Column(Text)
    timestamped_content = Column(Text)
    language = Column(String(10))
    word_count = Column(Integer, default=0)
    char_count = Column(Integer, default=0)
    is_edited = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="transcript")


class GeneratedContent(Base):
    __tablename__ = "generated_content"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    content_type = Column(String(100), nullable=False)
    content_subtype = Column(String(100), default="")
    content = Column(Text)
    ai_provider = Column(String(50))
    model = Column(String(100))
    tokens_used = Column(Integer, default=0)
    prompt_tokens = Column(Integer, default=0)
    is_edited = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="content_items")


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    content_type = Column(String(100))
    style = Column(String(100))
    system_prompt = Column(Text)
    user_prompt_template = Column(Text)
    description = Column(String(500))
    is_builtin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ExportHistory(Base):
    __tablename__ = "export_history"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    format = Column(String(20))
    content_types = Column(String(500))
    file_path = Column(String(1000))
    file_size = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="exports")
