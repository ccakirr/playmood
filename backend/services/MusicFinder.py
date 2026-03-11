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

# ── Sanatçı başına maksimum şarkı sayısı ──────────────────────────────────────
MAX_SONGS_PER_ARTIST = 3

# ── Vibe mix oranı: primary tag → %70, color/expansion tag'ler → %30 ──────────
_PRIMARY_RATIO = 0.70

# ── Sıralama ağırlıkları: %80 all-time listeners + %20 playcount (güncellik) ──
_RECENT_WEIGHT = 0.20

# ── Mood keyword → yan tür genişletme tablosu ─────────────────────────────────
# Kullanıcı promptu veya mood_keywords bu kelimeleri içeriyorsa ekstra tag'ler eklenir
_MOOD_TAG_EXPANSIONS: dict[str, list[str]] = {
    "sunset":      ["dream pop", "chillwave", "lo-fi house"],
    "sunrise":     ["ambient pop", "dream pop", "indie folk"],
    "chill":       ["lo-fi", "chillhop", "downtempo"],
    "relax":       ["ambient", "lo-fi", "acoustic"],
    "sad":         ["indie folk", "post-rock", "emo"],
    "melancholy":  ["post-rock", "slowcore", "indie folk"],
    "happy":       ["indie pop", "funk", "disco"],
    "party":       ["edm", "house", "dance"],
    "focus":       ["lo-fi", "ambient", "instrumental"],
    "workout":     ["drum and bass", "hardstyle", "edm"],
    "night":       ["synthwave", "darkwave", "trip-hop"],
    "late night":  ["trip-hop", "synthwave", "lo-fi"],
    "morning":     ["acoustic folk", "indie pop", "folk"],
    "heartbreak":  ["indie folk", "singer-songwriter", "alternative"],
    "nostalgia":   ["indie pop", "dream pop", "lo-fi"],
    "summer":      ["chillwave", "surf rock", "lo-fi house"],
    "dark":        ["darkwave", "post-punk", "goth"],
    "energetic":   ["edm", "drum and bass", "punk"],
    "calm":        ["ambient", "new age", "acoustic"],
    "romantic":    ["r&b", "soul", "indie pop"],
    "drive":       ["synthwave", "indie rock", "alternative"],
    "rainy":       ["lo-fi", "post-rock", "ambient"],
}

# ── Fallback için üst tür haritası ────────────────────────────────────────────
# Bir tag yeterli sonuç vermezse bu harita üzerinden ana kategoriye yönlendirilir
_PARENT_CATEGORIES: dict[str, str] = {
    "dream pop":        "indie",
    "chillwave":        "electronic",
    "lo-fi house":      "electronic",
    "ambient pop":      "pop",
    "lo-fi":            "electronic",
    "chillhop":         "hip hop",
    "downtempo":        "electronic",
    "indie folk":       "indie",
    "post-rock":        "rock",
    "indie pop":        "pop",
    "electropop":       "pop",
    "synth-pop":        "pop",
    "synthwave":        "electronic",
    "darkwave":         "electronic",
    "trip-hop":         "electronic",
    "trap":             "hip hop",
    "drill":            "hip hop",
    "turkish hip hop":  "hip hop",
    "german hip hop":   "hip hop",
    "french hip hop":   "hip hop",
    "indie rock":       "rock",
    "alternative rock": "rock",
    "folk rock":        "rock",
    "edm":              "electronic",
    "house":            "electronic",
    "techno":           "electronic",
    "drum and bass":    "electronic",
    "dubstep":          "electronic",
    "r&b":              "soul",
    "emo":              "rock",
    "post-punk":        "rock",
    "goth":             "rock",
    "slowcore":         "indie",
    "surf rock":        "rock",
    "acoustic folk":    "folk",
    "new age":          "ambient",
    "singer-songwriter":"indie",
    "hardstyle":        "electronic",
}


# ── Tag önbellekleri ────────────────────────────────────────────────────────
# _TRACK_TAG_CACHE : (track_lower, artist_lower) → {tag_name: weight(1-100)}
# _ARTIST_TAG_CACHE: artist_lower               → {tag_name: weight(1-100)}
_TRACK_TAG_CACHE:  dict = {}
_ARTIST_TAG_CACHE: dict = {}

# ── Mood çelişki tablosu ──────────────────────────────────────────────────────
# Kullanıcı sol taraftaki terimi istiyorsa, sağdaki tag'lere sahip şarkılar atılır
_MOOD_ANTI_TAGS: dict[str, set[str]] = {
    "slow":       {"thrash metal", "death metal", "black metal", "grindcore",
                   "hardcore", "aggressive", "brutal", "noise", "fast"},
    "acoustic":   {"thrash metal", "death metal", "heavy metal", "edm",
                   "dubstep", "drum and bass", "hardstyle", "noise"},
    "calm":       {"thrash metal", "death metal", "heavy metal", "edm",
                   "dubstep", "hardcore", "grindcore", "aggressive"},
    "soft":       {"thrash metal", "death metal", "black metal", "grindcore",
                   "hardcore", "heavy metal", "aggressive"},
    "relaxing":   {"thrash metal", "death metal", "heavy metal", "edm",
                   "dubstep", "hardcore", "grindcore"},
    "ambient":    {"thrash metal", "death metal", "black metal",
                   "grindcore", "hardcore", "heavy metal"},
    "mellow":     {"thrash metal", "death metal", "heavy metal",
                   "hardcore", "grindcore", "aggressive"},
    "peaceful":   {"thrash metal", "death metal", "heavy metal",
                   "hardcore", "grindcore", "aggressive", "brutal"},
    "aggressive": {"ambient", "slowcore", "lullaby", "new age",
                   "sleep", "meditation"},
    "energetic":  {"ambient", "slowcore", "lullaby", "new age",
                   "sleep", "meditation"},
    "workout":    {"ambient", "slowcore", "lullaby", "new age",
                   "sleep", "meditation"},
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

    # ── Yardımcı: sanatçı doğrulaması ────────────────────────────────────────
    def _artist_matches_genre(self, artist_name: str, target_tag: str) -> bool:
        """
        Sanatçının Last.fm tag'lerini çekip target_tag ile uyumlu olup olmadığını
        kontrol eder. Genre ailesi eşleşmesi yeterli (örn. "rap" → "hip hop" da geçer).
        API hatası veya tag listesi boşsa True döner (eleme yapmaz).
        """
        # Hangi tag aileleri birbirinin yerine geçebilir
        _GENRE_FAMILIES: list[set] = [
            {"rap", "hip hop", "hip-hop", "hiphop", "trap", "drill"},
            {"pop", "dance pop", "electropop", "synth-pop"},
            {"rock", "indie rock", "alternative rock", "alt rock", "punk"},
            {"metal", "heavy metal", "death metal", "black metal"},
            {"electronic", "edm", "house", "techno", "trance", "electro"},
            {"r&b", "rnb", "soul", "funk"},
            {"jazz", "blues"},
            {"classical", "orchestral"},
            {"reggae", "dancehall", "reggaeton"},
        ]

        # target_tag'in ait olduğu aileyi bul
        target_words = set(target_tag.lower().split())
        target_family: set | None = None
        for family in _GENRE_FAMILIES:
            if target_words & family:
                target_family = family
                break

        if target_family is None:
            return True  # Bilinmeyen tür → eleme yapma

        artist_tags = self._fetch_artist_tags(artist_name)
        if not artist_tags:
            return True  # Veri yok → eleme yapma
        # Ağırlığa göre sıralayıp ilk 5'e bak
        top5 = {t for t, _ in sorted(artist_tags.items(), key=lambda x: -x[1])[:5]}
        return bool(top5 & target_family)

    # ── Yeni dönem: sanatçı bazlı arama ──────────────────────────────────────
    def _find_new_era_songs(self, tag: str, limit: int) -> list:
        """
        'newschool / yeni' sorguları için:
          1. tag.gettopartists  → janranın aktif sanatçıları (Çakal, Luciano …)
          2. Sanatçı doğrulaması → yanlış tür sanatçıları ele
          3. artist.gettoptracks (listeners sayısına göre sıralı) → güncel şarkılar
        """
        n_artists = min(8, limit)  # Eleme olacağı için biraz fazla çek
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

            # Sanatçı doğrulaması: tür uyumsuzsa atla
            if not self._artist_matches_genre(artist_name, tag):
                print(f"  ⛔ {artist_name} → tür uyumsuz, atlandı")
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

            # Blended score: %80 all-time listeners + %20 playcount (güncellik proxy)
            max_l = max((int(t.get("listeners", 0)) for t in tracks), default=1) or 1
            max_p = max((int(t.get("playcount",  0)) for t in tracks), default=1) or 1
            tracks_sorted = sorted(
                tracks,
                key=lambda t: (
                    (1 - _RECENT_WEIGHT) * int(t.get("listeners", 0)) / max_l
                    + _RECENT_WEIGHT    * int(t.get("playcount",  0)) / max_p
                ),
                reverse=True,
            )

            # Blended score: %80 all-time listeners + %20 playcount (güncellik proxy)
            max_l = max((int(t.get("listeners", 0)) for t in tracks), default=1) or 1
            max_p = max((int(t.get("playcount",  0)) for t in tracks), default=1) or 1
            tracks_sorted = sorted(
                tracks,
                key=lambda t: (
                    (1 - _RECENT_WEIGHT) * int(t.get("listeners", 0)) / max_l
                    + _RECENT_WEIGHT    * int(t.get("playcount",  0)) / max_p
                ),
                reverse=True,
            )

            for track in tracks_sorted[:per_artist]:
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
        """
        tag.gettoptracks — tüm zamanların en popüler şarkıları (klasikler için ideal).
        Listeners sayısına göre yeniden sıralanır.
        """
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

        # Blended score: %80 all-time listeners + %20 playcount (güncellik proxy)
        max_l = max((int(t.get("listeners", 0)) for t in tracks), default=1) or 1
        max_p = max((int(t.get("playcount",  0)) for t in tracks), default=1) or 1

        tracks_sorted = sorted(
            tracks,
            key=lambda t: (
                (1 - _RECENT_WEIGHT) * int(t.get("listeners", 0)) / max_l
                + _RECENT_WEIGHT    * int(t.get("playcount",  0)) / max_p
            ),
            reverse=True,
        )

        return [
            {
                "track_name": t["name"],
                "artist_name": t["artist"]["name"],
                "query": f"{t['name']} {t['artist']['name']} official audio",
            }
            for t in tracks_sorted
        ]

    # ── Akıllı etiket seçimi ─────────────────────────────────────────────────
    def _select_smart_tags(self, genres: list, keywords: list) -> list[str]:
        """
        DjAI'dan gelen genre + mood_keywords listelerini harmanlayarak çoklu
        Last.fm tag listesi oluşturur.

        - Ana türler temizlenerek öncelikli olarak eklenir.
        - mood_keywords içinde tablo eşleşmesi varsa sıcak yan türler de eklenir.
        - En fazla 4 farklı tag döner (API yükünü sınırlamak için).
        """
        cleaned_genres = [self._clean_genre_tag(g) for g in genres if g]
        combined_text  = " ".join(keywords).lower()

        tags: list[str] = []

        # 1. Ana temizlenmiş türleri ekle
        for cg in cleaned_genres:
            if cg and cg not in tags:
                tags.append(cg)

        # 2. Milliyet genişletmesi: "turkish psychedelic" → ayrıca "psychedelic" ekle
        for cg in cleaned_genres:
            parts = cg.split(None, 1)
            if len(parts) == 2 and parts[0] in _KNOWN_NATIONALITIES and parts[1] not in tags:
                tags.append(parts[1])

        # 3. Mood keyword'lerden yan tür genişletmesi
        for trigger, expansions in _MOOD_TAG_EXPANSIONS.items():
            if trigger in combined_text:
                for exp_tag in expansions:
                    if exp_tag not in tags:
                        tags.append(exp_tag)
                # İlk eşleşen tetikleyiciden sonra dur (aşırı genişlemeyi önle)
                break

        # 4. Maksimum 5 tag kullan (milliyet genişletmesi için 1 artırıldı)
        return tags[:5] if tags else ["pop"]

    # ── Yardımcı: şarkı etiketlerini çek ve önbellekle ─────────────────────────
    def _fetch_track_tags(self, track_name: str, artist_name: str) -> dict[str, int]:
        """
        track.gettoptags → {tag_name: weight(1-100)} sözlüğü döner.
        Sonuçlar _TRACK_TAG_CACHE'e alınır; aynı şarkı için tekrar API çağrılmaz.
        """
        cache_key = (track_name.lower(), artist_name.lower())
        if cache_key not in _TRACK_TAG_CACHE:
            try:
                resp = requests.get(self.base_url, params={
                    "method": "track.gettoptags",
                    "track": track_name,
                    "artist": artist_name,
                    "api_key": self.api_key,
                    "format": "json",
                }, timeout=3)
                if resp.status_code == 200:
                    raw = resp.json().get("toptags", {}).get("tag", [])
                    _TRACK_TAG_CACHE[cache_key] = {
                        t["name"].lower(): int(t.get("count", 1))
                        for t in raw[:15]
                    }
                else:
                    _TRACK_TAG_CACHE[cache_key] = {}
            except Exception:
                _TRACK_TAG_CACHE[cache_key] = {}
        return _TRACK_TAG_CACHE[cache_key]

    # ── Yardımcı: sanatçı etiketlerini çek ve önbellekle ─────────────────────
    def _fetch_artist_tags(self, artist_name: str) -> dict[str, int]:
        """
        artist.gettoptags → {tag_name: weight(1-100)} sözlüğü döner.
        Sonuçlar _ARTIST_TAG_CACHE'e alınır; aynı sanatçı için tekrar çağrılmaz.
        """
        key = artist_name.lower()
        if key not in _ARTIST_TAG_CACHE:
            try:
                resp = requests.get(self.base_url, params={
                    "method": "artist.gettoptags",
                    "artist": artist_name,
                    "api_key": self.api_key,
                    "format": "json",
                }, timeout=3)
                if resp.status_code == 200:
                    raw = resp.json().get("toptags", {}).get("tag", [])
                    _ARTIST_TAG_CACHE[key] = {
                        t["name"].lower(): int(t.get("count", 1))
                        for t in raw[:10]
                    }
                else:
                    _ARTIST_TAG_CACHE[key] = {}
            except Exception:
                _ARTIST_TAG_CACHE[key] = {}
        return _ARTIST_TAG_CACHE[key]

    # ── Yardımcı: şarkı tag skoru (artist_songs yeniden sıralama) ──────────────
    def _get_track_tag_score(self, track_name: str, artist_name: str, target_terms: set) -> float:
        """
        Her eşleşen terim için (tag_weight / 100) puan ekler → max 1.0 / terim.
        _find_artist_songs içinde re-rank için kullanılır.
        """
        tags = self._fetch_track_tags(track_name, artist_name)
        score = 0.0
        for term in target_terms:
            for tag_name, weight in tags.items():
                if term in tag_name or tag_name in term:
                    score += weight / 100
                    break  # her term bir kez sayılır
        return score

    # ── Sanatçı modu: sadece o sanatçının şarkıları ──────────────────────────
    def _find_artist_songs(self, artist: str, limit: int, target_terms: list | None = None) -> list:
        """
        Belirli bir sanatçının en popüler şarkılarını getirir.
        target_terms verilirse (artist_songs modu), şarkılar Last.fm tag
        eşleşmesine göre yeniden sıralanır; eşleşenler listenin başına çekilir.
        Sanatçı başına kota uygulanmaz — tüm şarkılar aynı sanatçıdan gelir.
        """
        # Yeniden sıralama için biraz fazla çek (artist_songs modunda)
        fetch_count = min(limit + 5, 20) if target_terms else limit
        print(f"🎤 Sanatçı modu: '{artist}' şarkıları çekiliyor (pool={fetch_count})...")
        resp = requests.get(self.base_url, params={
            "method": "artist.gettoptracks",
            "artist": artist,
            "api_key": self.api_key,
            "format": "json",
            "limit": fetch_count,
        })
        if resp.status_code != 200:
            return []

        tracks = resp.json().get("toptracks", {}).get("track", [])
        seen = set()
        result = []
        for track in tracks:
            if len(result) >= fetch_count:
                break
            key = track["name"].lower()
            if key in seen:
                continue
            seen.add(key)
            a_name = track.get("artist", {}).get("name", artist)
            result.append({
                "track_name": track["name"],
                "artist_name": a_name,
                "query": f"{track['name']} {a_name} official audio",
            })

        # artist_only → popülerlik sırası yeterli, doğrudan döndür
        if not target_terms:
            return result[:limit]

        # ── Tag bazlı yeniden sıralama (artist_songs modu) ──────────────────
        target_set = {t.lower() for t in target_terms if t}
        print(f"  🏷️  Tag yeniden sıralaması: {len(result)} şarkı × {target_set}")
        scored = []
        for i, song in enumerate(result):
            score = self._get_track_tag_score(song["track_name"], song["artist_name"], target_set)
            scored.append((score, i, song))

        # Yüksek skor öne, eşit skorda orijinal popülerlik sırası korunur
        scored.sort(key=lambda x: (-x[0], x[1]))
        return [s for _, _, s in scored[:limit]]

    # ── Similar vibes modu: artist.getsimilar tabanlı arama ──────────────────
    def _find_similar_artist_songs(self, artist: str, limit: int, target_tags: list | None = None) -> list:
        """
        artist.getsimilar → benzer sanatçı listesi
        Her benzer sanatçı için artist.gettoptracks → şarkılar
        target_tags verilirse, eşleşen sanatçılar öne alınır (soft priority).
        MAX_SONGS_PER_ARTIST kotası uygulanır.
        """
        print(f"🎭 Similar vibes modu: '{artist}' benzeri sanatçılar aranıyor...")
        resp = requests.get(self.base_url, params={
            "method": "artist.getsimilar",
            "artist": artist,
            "api_key": self.api_key,
            "format": "json",
            "limit": 20,
        })
        if resp.status_code != 200:
            return []

        similar_artists = resp.json().get("similarartists", {}).get("artist", [])
        if not similar_artists:
            return []

        # ── Soft priority: hedef türle eşleşen sanatçıları öne al ───────────
        # _artist_matches_genre çağrısını ilk 10 sanatçıyla sınırla (hız için)
        if target_tags:
            matching, non_matching = [], []
            for idx, sim in enumerate(similar_artists):
                sim_name = sim.get("name", "")
                if not sim_name:
                    non_matching.append(sim)
                    continue
                if idx < 10 and any(self._artist_matches_genre(sim_name, tag) for tag in target_tags[:2]):
                    matching.append(sim)
                else:
                    non_matching.append(sim)
            sorted_artists = matching + non_matching
            print(f"  ✅ Tür filtresi: {len(matching)} eşleşen / {len(non_matching)} genel sanatçı")
        else:
            sorted_artists = similar_artists

        seen_keys: set[tuple] = set()
        song_list: list[dict] = []

        for sim in sorted_artists:
            if len(song_list) >= limit:
                break
            artist_name = sim.get("name", "")
            if not artist_name:
                continue

            t_resp = requests.get(self.base_url, params={
                "method": "artist.gettoptracks",
                "artist": artist_name,
                "api_key": self.api_key,
                "format": "json",
                "limit": MAX_SONGS_PER_ARTIST + 2,
            })
            if t_resp.status_code != 200:
                continue

            tracks = t_resp.json().get("toptracks", {}).get("track", [])
            added = 0
            for track in tracks:
                if len(song_list) >= limit or added >= MAX_SONGS_PER_ARTIST:
                    break
                key = (track["name"].lower(), artist_name.lower())
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                song_list.append({
                    "track_name": track["name"],
                    "artist_name": artist_name,
                    "query": f"{track['name']} {artist_name} official audio",
                })
                added += 1

        return song_list[:limit]

    # ── Validation & Scoring Layer ──────────────────────────────────────────────
    def _validation_layer(self, songs: list[dict], keywords: list[str], genres: list[str]) -> list[dict]:
        """
        Her şarkıya +10 / -20 ağırlıklı puan verir, ardından yeniden sıralar.

        Puanlama kuralları:
          +10 × (tag_weight / 100)  — eşleşen her pozitif terim (genre / mood_keyword)
          -20 × (tag_weight / 100)  — şarkıda bulunan her anti-tag
          -15 (sabit)               — istenen milliyet sanatçı tag'lerinde yoksa

        Sonuç < -10 olan şarkılar atılır; kalanlar puana göre büyükten küçüğe sıralanır.
        Sanatçı başına kota değiştirilmez — bu katman yalnızca sıralamayı düzenler.
        """
        if not songs:
            return songs

        pos_terms = {k.lower() for k in keywords} | {g.lower() for g in genres}

        # İstenen milliyet ön ekleri (örn. "turkish", "french")
        requested_nationalities = {
            g.split()[0]
            for g in genres
            if g.split() and g.split()[0] in _KNOWN_NATIONALITIES
        }

        # Anti-tag seti: pozitif terimlerden çelişki tablosuna göre üret
        anti_tags: set[str] = set()
        for term in pos_terms:
            anti_tags |= _MOOD_ANTI_TAGS.get(term, set())

        print(
            f"🎯 Scoring {len(songs)} songs"
            + (f" | nationalities: {requested_nationalities}" if requested_nationalities else "")
            + (f" | anti: {anti_tags}" if anti_tags else "")
        )

        scored: list[tuple[float, int, dict]] = []

        for idx, song in enumerate(songs):
            track_tags = self._fetch_track_tags(song["track_name"], song["artist_name"])
            score = 0.0

            # ── +10 × weight/100 per matching positive term ────────────────────
            for term in pos_terms:
                for tag_name, weight in track_tags.items():
                    if term in tag_name or tag_name in term:
                        score += 10 * (weight / 100)
                        break  # her terim bir kez sayılır

            # ── -20 × weight/100 per conflicting anti-tag ─────────────────────
            for anti in anti_tags:
                if anti in track_tags:
                    score -= 20 * (track_tags[anti] / 100)

            # ── Milliyet penaltısı: sanatçı o ülkeden değilse -15 ─────────────
            if requested_nationalities:
                artist_tags = self._fetch_artist_tags(song["artist_name"])
                artist_tag_names = set(artist_tags.keys())
                for nationality in requested_nationalities:
                    if not any(nationality in t for t in artist_tag_names):
                        score -= 15

            scored.append((score, idx, song))

        # Puan < -10 → gerçekten uyumsuz, at
        pre = len(scored)
        scored = [(s, i, song) for s, i, song in scored if s > -10]
        removed = pre - len(scored)
        if removed:
            print(f"  🗑️  {removed} şarkı elendi (skor ≤ -10), {len(scored)} kaldı")

        # Yüksek puan öne; eşit puanda orijinal sıra (idx) tiebreak
        scored.sort(key=lambda x: (-x[0], x[1]))
        return [s for _, _, s in scored]

    # ── Ana arama fonksiyonu ───────────────────────────────────────────────────
    def find_songs(self, mood_data, limit=15):
        try:
            mode   = mood_data.get("mode", "mood_only")
            artist = mood_data.get("artist")

            # ── Sanatçı modları ────────────────────────────────────────────────
            if mode in ("artist_only", "artist_songs") and artist:
                if mode == "artist_songs":
                    # Sanatçının şarkılarını genre + mood_keywords'e göre yeniden sırala
                    target_terms = (
                        [g.lower() for g in mood_data.get("genre", [])]
                        + [k.lower() for k in mood_data.get("mood_keywords", [])]
                    )
                    songs = self._find_artist_songs(artist, limit, target_terms=target_terms or None)
                else:
                    # artist_only: popülerlik sırası yeterli
                    songs = self._find_artist_songs(artist, limit)
                if songs:
                    return songs
                print(f"⚠️ '{artist}' Last.fm'de bulunamadı, mood bazlı aramaya geçiliyor...")

            # ── Similar vibes modu ─────────────────────────────────────────────
            # Sanatçının vibe'ına benzeyen DİĞER sanatçıların şarkıları
            elif mode == "similar_vibes" and artist:
                # Hedef taglar: AI'nin belirlediği ana janralar (temizlenmiş)
                target_tags = [self._clean_genre_tag(g) for g in mood_data.get("genre", []) if g]
                songs = self._find_similar_artist_songs(artist, limit, target_tags=target_tags or None)
                if songs:
                    return songs
                print(f"⚠️ '{artist}' için benzer sanatçı bulunamadı, tag bazlı aramaya geçiliyor...")

            # ── mood_only veya yukarıdaki fallback'ler ─────────────────────────
            genres   = [g.lower() for g in mood_data.get("genre", [])]
            keywords = [k.lower() for k in mood_data.get("mood_keywords", [])]

            # 1. Dönem tespiti (orijinal inputtan, temizlemeden önce)
            era = self._detect_era(genres, keywords)

            # 2. Akıllı çoklu tag seçimi
            smart_tags  = self._select_smart_tags(genres, keywords)
            primary_tag = smart_tags[0] if smart_tags else "pop"
            color_tags  = smart_tags[1:]  # expansion / yan tür tag'leri

            print(f"🔍 Era: {era} | Primary: #{primary_tag} | Color: {color_tags}")

            # ── Yardımcı: belirli bir tag için ham şarkı listesi çek ──────────
            def _fetch(tag: str, n: int) -> list:
                if era == "new":
                    result = self._find_new_era_songs(tag, n)
                    return result if result else self._find_top_tracks(tag, n)
                return self._find_top_tracks(tag, n)

            # ── Sanatçı kotası uygulayarak havuzları hedefe dolduran closure ──
            seen_keys:     set[tuple]      = set()
            artist_counts: dict[str, int]  = {}
            filtered_songs: list[dict]     = []

            def _admit(songs: list, target: int) -> None:
                count = 0
                for song in songs:
                    if count >= target:
                        break
                    key = (song["track_name"].lower(), song["artist_name"].lower())
                    if key in seen_keys:
                        continue
                    a = song["artist_name"].lower()
                    if artist_counts.get(a, 0) >= MAX_SONGS_PER_ARTIST:
                        continue
                    seen_keys.add(key)
                    artist_counts[a] = artist_counts.get(a, 0) + 1
                    filtered_songs.append(song)
                    count += 1

            # 3. Pool size: limitin 3 katını topla, validation'dan sonra limit'e indir
            pool_size = min(limit * 3, 45)

            # 4. Slot dağılımı — hibrit tespiti
            # AI 2+ janra verdiyse her birine eşit slot; tek janrada %70/%30
            ai_genre_tags  = [self._clean_genre_tag(g) for g in genres if g]
            expansion_tags = [t for t in smart_tags if t not in ai_genre_tags]

            if len(ai_genre_tags) >= 2:
                # ── Dengeli hibrit: her AI janrasına eşit slot ────────────────
                per_slot  = pool_size // len(ai_genre_tags)
                remainder = pool_size % len(ai_genre_tags)
                print(f"⚖️  Hibrit mod: {ai_genre_tags} → {per_slot} slot/janra (pool={pool_size})")
                for idx, tag in enumerate(ai_genre_tags):
                    slot = per_slot + (1 if idx < remainder else 0)
                    _admit(_fetch(tag, slot * 2), slot)
                # Kalan slotları expansion tag'lerle doldur
                for et in expansion_tags:
                    if len(filtered_songs) >= pool_size:
                        break
                    _admit(_fetch(et, (pool_size - len(filtered_songs)) * 2),
                           pool_size - len(filtered_songs))
            else:
                # ── Tekil primary + expansion: %70 / %30 ─────────────────────
                primary_target = round(pool_size * _PRIMARY_RATIO) if color_tags else pool_size
                color_target   = pool_size - primary_target

                primary_raw = _fetch(primary_tag, max(primary_target * 2, 30))
                color_raw: list[dict] = []
                if color_tags:
                    per_color = max(round(color_target * 2 / len(color_tags)), 10)
                    for ct in color_tags:
                        color_raw.extend(_fetch(ct, per_color))

                _admit(primary_raw, primary_target)   # %70 primer
                _admit(color_raw,   color_target)      # %30 color

                # Toplam hâlâ yetersizse kalan slotları primary'den tamamla
                if len(filtered_songs) < pool_size:
                    _admit(primary_raw, pool_size - len(filtered_songs))

            # 6. Fallback — limit'ten az sonuç varsa ana kategoriye yükselt
            if len(filtered_songs) < limit:
                fallback_tags: list[str] = []
                for tag in smart_tags:
                    parent = _PARENT_CATEGORIES.get(tag)
                    if parent and parent not in smart_tags and parent not in fallback_tags:
                        fallback_tags.append(parent)

                for fb_tag in fallback_tags:
                    if len(filtered_songs) >= limit:
                        break
                    print(f"⚠️ {len(filtered_songs)} sonuç yetersiz (<{limit}), fallback: #{fb_tag}")
                    _admit(_fetch(fb_tag, limit * 2), limit - len(filtered_songs))

            # 7. Hâlâ boşsa → milliyet/sıfat ön ekini at ve tekrar dene
            if not filtered_songs and " " in primary_tag:
                fallback_tag = " ".join(primary_tag.split()[1:])
                print(f"⚠️ Sonuç yok, tag basitleştiriliyor: #{fallback_tag}")
                return self.find_songs({"genre": [fallback_tag], "mood_keywords": keywords}, limit)

            # 8. Son çare → genre listesinin son kelimesi
            if not filtered_songs and genres:
                last_word = genres[-1].split()[-1]
                if last_word != primary_tag:
                    print(f"⚠️ Son fallback: #{last_word}")
                    return self.find_songs({"genre": [last_word], "mood_keywords": []}, limit)

            # 9. Validation Layer: anti-tag filtresi + mood keyword re-rank
            filtered_songs = self._validation_layer(filtered_songs, keywords, ai_genre_tags)

            return filtered_songs[:limit]

        except Exception as e:
            print(f"❌ Hata: {e}")
            return []
