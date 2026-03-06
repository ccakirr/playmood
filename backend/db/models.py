from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy import JSON
from datetime import datetime, timezone
from db.database import Base


class User(Base):
    __tablename__ = "users"

    id             = Column(Integer, primary_key=True, index=True)
    email          = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at     = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    playlists = relationship("Playlist", back_populates="owner", cascade="all, delete-orphan")


class Playlist(Base):
    __tablename__ = "playlists"

    id            = Column(Integer, primary_key=True, index=True)
    user_id       = Column(Integer, ForeignKey("users.id"), nullable=False)
    playlist_name = Column(String, nullable=False)
    prompt        = Column(Text, nullable=False)
    tracks        = Column(JSON, nullable=False, default=list)
    created_at    = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="playlists")
