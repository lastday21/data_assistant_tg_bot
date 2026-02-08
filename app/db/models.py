import uuid
from datetime import datetime


from sqlalchemy import DateTime, ForeignKey, Index, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    creator_id: Mapped[str] = mapped_column(Text, nullable=False)
    video_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    views_count: Mapped[int] = mapped_column(Integer, nullable=False)
    likes_count: Mapped[int] = mapped_column(Integer, nullable=False)
    comments_count: Mapped[int] = mapped_column(Integer, nullable=False)
    reports_count: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    snapshots: Mapped[list["VideoSnapshot"]] = relationship(
        back_populates="video", cascade="all, delete-orphan"
    )


Index("ix_videos_creator_id", Video.creator_id)
Index("ix_videos_video_created_at", Video.video_created_at)
Index("ix_videos_views_count", Video.views_count)


class VideoSnapshot(Base):
    __tablename__ = "video_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
    )

    views_count: Mapped[int] = mapped_column(Integer, nullable=False)
    likes_count: Mapped[int] = mapped_column(Integer, nullable=False)
    comments_count: Mapped[int] = mapped_column(Integer, nullable=False)
    reports_count: Mapped[int] = mapped_column(Integer, nullable=False)

    delta_views_count: Mapped[int] = mapped_column(Integer, nullable=False)
    delta_likes_count: Mapped[int] = mapped_column(Integer, nullable=False)
    delta_comments_count: Mapped[int] = mapped_column(Integer, nullable=False)
    delta_reports_count: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    video: Mapped[Video] = relationship(back_populates="snapshots")


Index("ix_video_snapshots_video_id", VideoSnapshot.video_id)
Index("ix_video_snapshots_created_at", VideoSnapshot.created_at)
