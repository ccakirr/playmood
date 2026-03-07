import os
import sys
import requests
from dotenv import load_dotenv

# Proje yolu ayarı
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.Agent import DjAI

load_dotenv()

# ── Tag temizleme sabitleri ────────────────────────────────────────────────────

# Dönem/popülarite bildiren, janra katkısı olmayan gürültülü terimler
_NOISE_TERMS = {
    "newschool", "new school", "new-school",
    "oldschool", "old school", "old-school",
    "yeni", "eski", "hits", "hit",
    "klasik", "classic", "modern", "underground",
    "mainstream", "fresh", "latest", "best",
    "top", "popular", "viral", "trending",
    "trap", "new",  # "trap" gibi alt-türler de çoğu zaman Last.fm'de sonuç vermez
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

    # ── Yardımcı: tek bir janra stringini temizle ─────────────────────────────
    def _clean_genre_tag(self, genre: str) -> str:
        """
        1. Kelime kelime böl.
        2. Türkçe/yabancı milliyet kelimelerini İngilizce karşılıklarına çevir.
        3. Gürültülü terimleri (newschool, hits, yeni …) sil.
        Sonuç boşsa orijinal dize döner.
        """
        words = genre.lower().split()
        # Milliyet kısaltmalarını normalize et
        words = [_NATIONALITY_ALIASES.get(w, w) for w in words]
        # Gürültü terimlerini çıkar
        words = [w for w in words if w not in _NOISE_TERMS]
        return " ".join(words) if words else genre.lower()

    # ── Yardımcı: en iyi tag'i seç ────────────────────────────────────────────
    def _select_best_tag(self, genres: list) -> str:
        """
        Öncelik sırası:
        1. Milliyet + tür içeren tag (örn. "turkish hip hop") — en açıklayıcı
        2. Sadece milliyet içeren tag (örn. "turkish pop")
        3. İlk temizlenmiş tag
        4. "pop" (son çare)
        """
        cleaned_genres = [self._clean_genre_tag(g) for g in genres if g]

        # 1. Milliyet + tür içerenler
        for cg in cleaned_genres:
            parts = cg.split()
            if len(parts) >= 2 and parts[0] in _KNOWN_NATIONALITIES:
                return cg

        # 2. Sadece milliyet içerenler veya ilk temizlenmiş
        for cg in cleaned_genres:
            if cg:
                return cg

        return "pop"

    # ── Ana arama fonksiyonu ───────────────────────────────────────────────────
    def find_songs(self, mood_data, limit=15):
        try:
            genres = [g.lower() for g in mood_data.get('genre', [])]
            keywords = [k.lower() for k in mood_data.get('mood_keywords', [])]

            # En iyi tag'i belirle (gürültü temizlenmiş, milliyet normallanmış)
            target_tag = self._select_best_tag(genres)

            # Tag hâlâ çok kısaysa keyword'lerden destek al
            if len(target_tag) < 3:
                target_tag = self._clean_genre_tag(keywords[0]) if keywords else "pop"

            print(f"🎵 Last.fm üzerinde '#{target_tag}' etiketli şarkılar aranıyor...")

            params = {
                "method": "tag.gettoptracks",
                "tag": target_tag,
                "api_key": self.api_key,
                "format": "json",
                "limit": limit,
            }

            response = requests.get(self.base_url, params=params)

            if response.status_code != 200:
                return []

            data = response.json()
            tracks = data.get('tracks', {}).get('track', [])

            # FALLBACK 1: Milliyet + tür varsa → sadece tür ile tekrar dene
            if not tracks and " " in target_tag:
                simplified_tag = " ".join(target_tag.split()[1:])  # milliyet kelimesini at
                print(f"⚠️ Sonuç yok, basitleştiriliyor: #{simplified_tag}")
                return self.find_songs({"genre": [simplified_tag]}, limit)

            # FALLBACK 2: Hiç sonuç gelmezse son kelimeyi al (örn. "hip hop" → "hip hop")
            if not tracks and genres:
                last_word = genres[-1].split()[-1]
                if last_word != target_tag:
                    print(f"⚠️ Son fallback: #{last_word}")
                    return self.find_songs({"genre": [last_word]}, limit)

            song_list = []
            for track in tracks:
                song_list.append({
                    "track_name": track['name'],
                    "artist_name": track['artist']['name'],
                    "query": f"{track['name']} {track['artist']['name']} official audio",
                })

            return song_list

        except Exception as e:
            print(f"❌ Hata: {e}")
            return []
