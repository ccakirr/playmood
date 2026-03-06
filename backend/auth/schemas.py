from pydantic import BaseModel, EmailStr, field_validator
from typing import Any, List, Optional
from datetime import datetime


# ── Auth ────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters.")
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Playlist ──────────────────────────────────────────────────────────────────
class SavePlaylistRequest(BaseModel):
    playlist_id: str          # in-memory key from /playlist/generate
    playlist_name: str
    prompt: str


class PlaylistOut(BaseModel):
    id: int
    playlist_name: str
    prompt: str
    tracks: List[Any]
    created_at: datetime

    model_config = {"from_attributes": True}
