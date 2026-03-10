import os
import uuid
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session

# Kendi servislerini içe aktar
from services.Agent import DjAI
from services.MusicFinder import LastFmMusicFinder  # Yeni yazdığımız sınıf
from db.database import get_db
from db.models import Playlist as PlaylistModel
from db.models import User
from auth.auth_utils import get_current_user
from auth.schemas import SavePlaylistRequest, PlaylistOut

class Track(BaseModel):
    artist_name: str  # Last.fm'den gelen formata göre güncelledik
    track_name: str

class PlaylistResponse(BaseModel):
    playlist_id: str
    mood_keywords: List[str]
    tracks: List[Track]

class PlaylistRequest(BaseModel):
    prompt: str
    limit: int = 15 # Şarkı sayısı tercihi

ai = DjAI()
finder = LastFmMusicFinder()

router = APIRouter(prefix="/playlist", tags=["playlist"])

@router.post("/generate", response_model=PlaylistResponse)
def generate_playlist(request: PlaylistRequest):
    # 1. AI ile Mood Analizi (JSON olarak döner)
    mood_data = ai.send_message(request.prompt)

    if not mood_data:
        raise HTTPException(
            status_code=500,
            detail="AI mood analizi yapamadı."
        )
    
    # 2. Last.fm ile Gerçek Şarkıları Bulma
    # Artık "bok gibi" şarkılar yerine Last.fm hitleri geliyor
    songs = finder.find_songs(mood_data, limit=request.limit)

    if not songs:
        raise HTTPException(
            status_code=404,
            detail="Bu mood'a uygun hit şarkı bulunamadı."
        )

    # 3. Playlist ID Oluşturma
    playlist_id = str(uuid.uuid4())

    # YouTube router'ı ile paylaşılan veritabanı (playlists_db)
    # youtube_router bu ID'yi kullanarak şarkıları çekecek
    from routers.youtube_router import playlists_db
    
    # YouTube router'ının beklediği formata göre kaydediyoruz
    playlists_db[playlist_id] = {
        "mood": mood_data,
        "tracks": songs  # query, artist_name ve track_name içerir
    }

    return {
        "playlist_id": playlist_id,
        "mood_keywords": mood_data.get("mood_keywords", []),
        "tracks": songs
    }


# ── Persist to PostgreSQL ─────────────────────────────────────────────────────

@router.post("/save", response_model=PlaylistOut, status_code=201)
def save_playlist(
    body: SavePlaylistRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Save a generated playlist to the user's account."""
    from routers.youtube_router import playlists_db

    in_memory = playlists_db.get(body.playlist_id)
    if not in_memory:
        raise HTTPException(
            status_code=404,
            detail="Playlist not found. Generate a playlist first.",
        )

    playlist = PlaylistModel(
        user_id=current_user.id,
        playlist_name=body.playlist_name,
        prompt=body.prompt,
        tracks=in_memory.get("tracks", []),
    )
    db.add(playlist)
    db.commit()
    db.refresh(playlist)
    return playlist


@router.get("/my-playlists", response_model=List[PlaylistOut])
def my_playlists(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all playlists saved by the authenticated user, newest first."""
    return (
        db.query(PlaylistModel)
        .filter(PlaylistModel.user_id == current_user.id)
        .order_by(PlaylistModel.created_at.desc())
        .all()
    )


@router.delete("/{playlist_id}", status_code=204)
def delete_playlist(
    playlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a playlist by ID (owner only)."""
    playlist = (
        db.query(PlaylistModel)
        .filter(PlaylistModel.id == playlist_id, PlaylistModel.user_id == current_user.id)
        .first()
    )
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found.")
    db.delete(playlist)
    db.commit()


@router.get("/restore-for-youtube/{db_id}")
def restore_for_youtube(
    db_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Re-inject a saved DB playlist into the in-memory playlists_db so the
    YouTube export flow can find it via /youtube/start."""
    playlist = (
        db.query(PlaylistModel)
        .filter(PlaylistModel.id == db_id, PlaylistModel.user_id == current_user.id)
        .first()
    )
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found.")

    temp_id = str(uuid.uuid4())
    from routers.youtube_router import playlists_db
    playlists_db[temp_id] = {
        "playlist_name": playlist.playlist_name,
        "tracks": playlist.tracks,
    }
    return {"playlist_id": temp_id}