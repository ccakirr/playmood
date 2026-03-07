import os
import sys
import requests
from dotenv import load_dotenv

# Proje yolu ayarı
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.Agent import DjAI

load_dotenv()

# ── Era / dönem sabitleri (orijinal inputtan tespit edilir, tag'e gönderilmez) ─

_NEW_ERA_TERMS = {
    "newschool", "new school", "new-school",
    "yeni", "modern", "fresh", "latest",
    "trending", "viral", "güncel", "çağdaş",
}

_OLD_ERA_TERMS = {
    "oldschool", "old school", "old-school",
    "eski", "classic", "klasik", "retro", "vintage", "throwback",
}

# ── Tag temizleme sabitleri (Last.fm'e gönderilmeden önce janradan çıkarılır) ──

# Sadece dönem/kalite bildiren, janra katkısı olmayan sıfatlar
_NOISE_TERMS = {
    "newschool", "new school", "new-school",
    "oldschool", "old school", "old-school",
    "yeni", "eski", "hits", "hit",
    "klasik", "classic", "modern",
    "mainstream", "fresh", "latest", "best",
    "top", "popular", "viral", "trending", "new",
}

# Türkçe/başka dillerdeki milliyet/dil ifadelerini İngilizce karşılığına eşle
_NATIONALITY_ALIASES: dict[str, str] = {
    # Türkçe
    "türkçe": "turkish", "türk": "turkish", "turk": "turkish",
    # Almanca
    "almanca": "german", "alman": "german", "deutsch": "german",
    # Fransızca
    "fransızca": "french", "fransız": "french", "français": "french",
    # İspanyolca
    "ispanyolca": "spanish", "ispanyol": "spanish",
    # İtalyanca
    "italyanca": "italian", "italyan": "italian",
    # Portekizce
    "portekizce": "portuguese", "portekizli": "portuguese",
    # Japonca
    "japonca": "japanese", "japon": "japanese",
    # Korece
    "korece": "korean", "kore": "korean",
    # Arapça
    "arapça": "arabic", "arap": "arabic",
    # Rusça
    "rusça": "russian", "rus": "russian",
    # Çince
    "çince": "chinese", "çin": "chinese",
    # Hintçe
    "hintçe": "hindi", "hint": "hindi",
}

# İngilizce milliyet sıfatları (tag'in ilk kelimesi bunlardan biri ise iyi formattadır)
_KNOWN_NATIONALITIES = {
    "turkish", "german", "french", "spanish", "italian",
    "portuguese", "japanese", "korean", "arabic", "russian",
    "chinese", "hindi", "greek", "latin", "swedish",
    "norwegian", "danish", "finnish", "polish", "dutch",
    "american", "british", "australian", "canadian",
    "brazilian", "mexican", "indian",
}


class LastFmMusicFinder:
    def __init__(self):
        self.api_key = os.getenv("LASTFM_API_KEY")
        self.base_url = "http://ws.audioscrobbler.com/2.0/"

    # ── Yardımcı: dönem tespiti ───────────────────────────────────────────────
    def _detect_era(self, genres: list, keywords: list) -> str:
        """
        Orijinal genre/keyword listesinden dönem bilgisi çıkarır.
        Temizlemeden ÖNCE çağrılmalı.
        Döner: 'new' | 'old' | 'neutral'
        """
        combined = " ".join(genres + keywords).lower()
        if any(term in combined for term in _NEW_ERA_TERMS):
            return "new"
        if any(term in combined for term in _OLD_ERA_TERMS):
            return "old"
        return "neutral"

    # ── Yardımcı: tek bir janra stringini temizle ─────────────────────────────
    def _clean_genre_tag(self, genre: str) -> str:
        """
        1. Kelime kelime böl.
        2. Türkçe/yabancı milliyet kelimelerini İngilizce karşılıklarına çevir.
        3. Gürültülü terimleri (newschool, hits, yeni …) sil.
        Sonuç boşsa orijinal dize döner.
        """
        words = genre.lower().split()
        words = [_NATIONALITY_ALIASES.get(w, w) for w in words]
        words = [w for w in words if w not in _NOISE_TERMS]
        return " ".join(words) if words else genre.lower()

    # ── Yardımcı: en iyi tag'i seç ────────────────────────────────────────────
    def _select_best_tag(self, genres: list) -> str:
        """
        Öncelik sırası:
        1. Milliyet + tür içeren tag (örn. "turkish hip hop")
        2. Sadece temizlenmiş tag
        3. "pop" (son çare)
        """
        cleaned_genres = [self._clean_genre_tag(g) for g in genres if g]

        # Milliyet + tür içerenler → en açıklayıcı
        for cg in cleaned_genres:
            parts = cg.split()
            if len(parts) >= 2 and parts[0] in _KNOWN_NATIONALITIES:
                return cg

        # İlk temizlenmiş tag
        for cg in cleaned_genres:
            if cg:
                return cg

        return "pop"

    # ── Yeni dönem: sanatçı bazlı arama ──────────────────────────────────────
    def _find_new_era_songs(self, tag: str, limit: int) -> list:
        """
        'newschool / yeni' sorguları için:
          1. tag.gettopartists  → janranın aktif sanatçıları (Çakal, Luciano …)
          2. artist.gettoptracks → her sanatçının popüler şarkıları
        Bu yöntem, istatistiksel olarak daha güncel sanatçılar ve şarkılar getirir.
        """
        n_artists = min(6, limit)
        per_artist = max(2, (limit + n_artists - 1) // n_artists)

        print(f"🆕 Yeni dönem modu: '#{tag}' için sanatçılar çekiliyor...")

        resp = requests.get(self.base_url, params={
            "method": "tag.gettopartists",
            "tag": tag,
            "api_key": self.api_key,
            "format": "json",
            "limit": n_artists,
        })
        if resp.status_code != 200:
            return []

        artists = resp.json().get("topartists", {}).get("artist", [])
        if not artists:
            return []

        song_list = []
        for artist in artists:
            artist_name = artist.get("name", "")
            if not artist_name:
                continue

            t_resp = requests.get(self.base_url, params={
                "method": "artist.gettoptracks",
                "artist": artist_name,
                "api_key": self.api_key,
                "format": "json",
                "limit": per_artist,
            })
            if t_resp.status_code != 200:
                continue

            tracks = t_resp.json().get("toptracks", {}).get("track", [])
            for track in tracks[:per_artist]:
                song_list.append({
                    "track_name": track["name"],
                    "artist_name": track["artist"]["name"],
                    "query": f"{track['name']} {track['artist']['name']} official audio",
                })
            if len(song_list) >= limit:
                break

        return song_list[:limit]

    # ── Klasik dönem / nötr: tag bazlı arama ─────────────────────────────────
    def _find_top_tracks(self, tag: str, limit: int) -> list:
        """tag.gettoptracks — tüm zamanların en popüler şarkıları (klasikler için ideal)."""
        print(f"🎵 Last.fm üzerinde '#{tag}' etiketli şarkılar aranıyor...")
        resp = requests.get(self.base_url, params={
            "method": "tag.gettoptracks",
            "tag": tag,
            "api_key": self.api_key,
            "format": "json",
            "limit": limit,
        })
        if resp.status_code != 200:
            return []
        tracks = resp.json().get("tracks", {}).get("track", [])
        return [
            {
                "track_name": t["name"],
                "artist_name": t["artist"]["name"],
                "query": f"{t['name']} {t['artist']['name']} official audio",
            }
            for t in tracks
        ]

    # ── Ana arama fonksiyonu ───────────────────────────────────────────────────
    def find_songs(self, mood_data, limit=15):
        try:
            genres  = [g.lower() for g in mood_data.get("genre", [])]
            keywords = [k.lower() for k in mood_data.get("mood_keywords", [])]

            # 1. Dönem tespiti (orijinal inputtan, temizlemeden önce)
            era = self._detect_era(genres, keywords)

            # 2. En iyi, gürültüsüz tag'i belirle
            target_tag = self._select_best_tag(genres)
            if len(target_tag) < 3:
                target_tag = self._clean_genre_tag(keywords[0]) if keywords else "pop"

            print(f"🔍 Era: {era} | Tag: #{target_tag}")

            # 3. Era'ya göre arama stratejisi
            if era == "new":
                songs = self._find_new_era_songs(target_tag, limit)
                # Yeni dönem sanatçı araması sonuç vermediyse → standart fallback
                if not songs:
                    print("⚠️ Sanatçı araması boş, standart listeye dönülüyor...")
                    songs = self._find_top_tracks(target_tag, limit)
            else:
                # old veya neutral → tüm zamanların en çok dinlenenleri
                songs = self._find_top_tracks(target_tag, limit)

            # 4. Hâlâ boşsa → milliyet kelimesini at ve tekrar dene
            if not songs and " " in target_tag:
                fallback_tag = " ".join(target_tag.split()[1:])
                print(f"⚠️ Sonuç yok, basitleştiriliyor: #{fallback_tag}")
                return self.find_songs({"genre": [fallback_tag], "mood_keywords": keywords}, limit)

            # 5. Son çare → sonun kelimesini al
            if not songs and genres:
                last_word = genres[-1].split()[-1]
                if last_word != target_tag:
                    print(f"⚠️ Son fallback: #{last_word}")
                    return self.find_songs({"genre": [last_word], "mood_keywords": []}, limit)

            return songs

        except Exception as e:
            print(f"❌ Hata: {e}")
            return []
