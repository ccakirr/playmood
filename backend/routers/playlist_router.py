import os
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

# Kendi servislerini içe aktar
from services.Agent import DjAI
from services.MusicFinder import LastFmMusicFinder  # Yeni yazdığımız sınıf

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