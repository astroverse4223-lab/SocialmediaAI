from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, subqueryload
from typing import Optional, List, Dict, Any
from datetime import datetime

from .models import Base, Project, Transcript, GeneratedContent, Template, ExportHistory


class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False}
        )
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)

    def initialize(self):
        Base.metadata.create_all(self.engine)
        self._seed_default_templates()

    def get_session(self) -> Session:
        return self.SessionLocal()

    # ──────────────────── PROJECTS ────────────────────

    def create_project(self, youtube_url: str, title: str = "Untitled",
                       video_id: str = "", **kwargs) -> Project:
        with self.get_session() as session:
            project = Project(
                youtube_url=youtube_url,
                title=title,
                video_id=video_id,
                **kwargs
            )
            session.add(project)
            session.commit()
            session.refresh(project)
            return project

    def update_project(self, project_id: int, **kwargs) -> Optional[Project]:
        with self.get_session() as session:
            project = session.get(Project, project_id)
            if project:
                for k, v in kwargs.items():
                    setattr(project, k, v)
                project.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(project)
            return project

    def get_project(self, project_id: int) -> Optional[Project]:
        with self.get_session() as session:
            return (
                session.query(Project)
                .options(
                    subqueryload(Project.content_items),
                    subqueryload(Project.transcript),
                    subqueryload(Project.exports),
                )
                .filter(Project.id == project_id)
                .first()
            )

    def get_all_projects(self, limit: int = 100, offset: int = 0,
                         search: str = "") -> List[Project]:
        with self.get_session() as session:
            query = session.query(Project).options(
                subqueryload(Project.content_items),
                subqueryload(Project.exports),
            )
            if search:
                query = query.filter(
                    Project.title.ilike(f"%{search}%") |
                    Project.channel.ilike(f"%{search}%")
                )
            return query.order_by(Project.created_at.desc()).offset(offset).limit(limit).all()

    def get_recent_projects(self, limit: int = 6) -> List[Project]:
        with self.get_session() as session:
            return (
                session.query(Project)
                .options(
                    subqueryload(Project.content_items),
                    subqueryload(Project.exports),
                )
                .order_by(Project.updated_at.desc())
                .limit(limit)
                .all()
            )

    def delete_project(self, project_id: int) -> bool:
        with self.get_session() as session:
            project = session.get(Project, project_id)
            if project:
                session.delete(project)
                session.commit()
                return True
            return False

    def toggle_favorite(self, project_id: int) -> bool:
        with self.get_session() as session:
            project = session.get(Project, project_id)
            if project:
                project.is_favorite = not project.is_favorite
                session.commit()
                return project.is_favorite
            return False

    def get_project_count(self) -> int:
        with self.get_session() as session:
            return session.query(Project).count()

    # ──────────────────── TRANSCRIPTS ────────────────────

    def save_transcript(self, project_id: int, content: str,
                        timestamped: str = "", language: str = "en") -> Transcript:
        with self.get_session() as session:
            existing = session.query(Transcript).filter_by(project_id=project_id).first()
            word_count = len(content.split())
            if existing:
                existing.content = content
                existing.timestamped_content = timestamped
                existing.language = language
                existing.word_count = word_count
                existing.char_count = len(content)
                session.commit()
                session.refresh(existing)
                return existing
            transcript = Transcript(
                project_id=project_id,
                content=content,
                timestamped_content=timestamped,
                language=language,
                word_count=word_count,
                char_count=len(content),
            )
            session.add(transcript)
            session.commit()
            session.refresh(transcript)
            return transcript

    def get_transcript(self, project_id: int) -> Optional[Transcript]:
        with self.get_session() as session:
            return session.query(Transcript).filter_by(project_id=project_id).first()

    # ──────────────────── GENERATED CONTENT ────────────────────

    def save_content(self, project_id: int, content_type: str,
                     content: str, content_subtype: str = "",
                     ai_provider: str = "", model: str = "",
                     tokens_used: int = 0, prompt_tokens: int = 0) -> GeneratedContent:
        with self.get_session() as session:
            existing = session.query(GeneratedContent).filter_by(
                project_id=project_id,
                content_type=content_type,
                content_subtype=content_subtype
            ).first()
            if existing:
                existing.content = content
                existing.ai_provider = ai_provider
                existing.model = model
                existing.tokens_used = tokens_used
                existing.prompt_tokens = prompt_tokens
                existing.created_at = datetime.utcnow()
                session.commit()
                session.refresh(existing)
                return existing
            item = GeneratedContent(
                project_id=project_id,
                content_type=content_type,
                content_subtype=content_subtype,
                content=content,
                ai_provider=ai_provider,
                model=model,
                tokens_used=tokens_used,
                prompt_tokens=prompt_tokens,
            )
            session.add(item)
            session.commit()
            session.refresh(item)
            return item

    def get_content(self, project_id: int, content_type: str,
                    content_subtype: str = "") -> Optional[GeneratedContent]:
        with self.get_session() as session:
            return session.query(GeneratedContent).filter_by(
                project_id=project_id,
                content_type=content_type,
                content_subtype=content_subtype
            ).first()

    def get_all_content_for_project(self, project_id: int) -> List[GeneratedContent]:
        with self.get_session() as session:
            return (
                session.query(GeneratedContent)
                .filter_by(project_id=project_id)
                .order_by(GeneratedContent.created_at.asc())
                .all()
            )

    def get_total_content_count(self) -> int:
        with self.get_session() as session:
            return session.query(GeneratedContent).count()

    def get_total_tokens_used(self) -> int:
        with self.get_session() as session:
            result = session.query(GeneratedContent).all()
            return sum(r.tokens_used or 0 for r in result)

    # ──────────────────── TEMPLATES ────────────────────

    def get_all_templates(self) -> List[Template]:
        with self.get_session() as session:
            return session.query(Template).order_by(Template.is_builtin.desc(), Template.name).all()

    def save_template(self, name: str, content_type: str, user_prompt_template: str,
                      system_prompt: str = "", description: str = "") -> Template:
        with self.get_session() as session:
            tmpl = Template(
                name=name,
                content_type=content_type,
                user_prompt_template=user_prompt_template,
                system_prompt=system_prompt,
                description=description,
                is_builtin=False,
            )
            session.add(tmpl)
            session.commit()
            session.refresh(tmpl)
            return tmpl

    def delete_template(self, template_id: int) -> bool:
        with self.get_session() as session:
            tmpl = session.get(Template, template_id)
            if tmpl and not tmpl.is_builtin:
                session.delete(tmpl)
                session.commit()
                return True
            return False

    # ──────────────────── EXPORT HISTORY ────────────────────

    def save_export(self, project_id: int, fmt: str, content_types: str,
                    file_path: str, file_size: int = 0) -> ExportHistory:
        with self.get_session() as session:
            export = ExportHistory(
                project_id=project_id,
                format=fmt,
                content_types=content_types,
                file_path=file_path,
                file_size=file_size,
            )
            session.add(export)
            session.commit()
            session.refresh(export)
            return export

    # ──────────────────── STATS ────────────────────

    def get_dashboard_stats(self) -> Dict[str, Any]:
        with self.get_session() as session:
            project_count = session.query(Project).count()
            content_count = session.query(GeneratedContent).count()
            blog_count = session.query(GeneratedContent).filter(
                GeneratedContent.content_type.like("blog%")
            ).count()
            social_count = session.query(GeneratedContent).filter(
                GeneratedContent.content_type.in_([
                    "twitter_thread", "linkedin_post", "facebook_post",
                    "instagram_captions", "tiktok_content"
                ])
            ).count()
            total_tokens = sum(
                r.tokens_used or 0
                for r in session.query(GeneratedContent).all()
            )
            return {
                "project_count": project_count,
                "content_count": content_count,
                "blog_count": blog_count,
                "social_count": social_count,
                "total_tokens": total_tokens,
            }

    # ──────────────────── SEED DATA ────────────────────

    def _seed_default_templates(self):
        with self.get_session() as session:
            if session.query(Template).filter_by(is_builtin=True).count() > 0:
                return
            defaults = [
                Template(
                    name="MrBeast Style", content_type="blog", style="entertainment",
                    description="High-energy, exciting, curiosity-driven content",
                    system_prompt="You are a content writer specializing in high-energy, "
                                  "exciting YouTube-style content. Use short sentences, "
                                  "exclamation points, and create intense curiosity gaps.",
                    user_prompt_template="Write a MrBeast-style blog post about: {transcript}",
                    is_builtin=True,
                ),
                Template(
                    name="Alex Hormozi Style", content_type="blog", style="business",
                    description="Direct, value-packed, no-fluff business content",
                    system_prompt="You are writing in the style of Alex Hormozi: direct, "
                                  "value-dense, no fluff, business-focused. Use short "
                                  "paragraphs and bold claims backed by logic.",
                    user_prompt_template="Write business content based on: {transcript}",
                    is_builtin=True,
                ),
                Template(
                    name="Educational Guide", content_type="blog", style="educational",
                    description="Step-by-step educational format",
                    system_prompt="You are an educational content expert. Write clear, "
                                  "structured guides that are easy to understand. Use "
                                  "numbered steps, examples, and helpful analogies.",
                    user_prompt_template="Create an educational guide from: {transcript}",
                    is_builtin=True,
                ),
                Template(
                    name="Podcast Show Notes", content_type="podcast", style="podcast",
                    description="Professional podcast show notes template",
                    system_prompt="You write professional podcast show notes. Include "
                                  "timestamps, key quotes, guest info, and resources.",
                    user_prompt_template="Create podcast show notes for: {transcript}",
                    is_builtin=True,
                ),
            ]
            for t in defaults:
                session.add(t)
            session.commit()
