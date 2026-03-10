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

        try:
            resp = requests.get(self.base_url, params={
                "method": "artist.gettoptags",
                "artist": artist_name,
                "api_key": self.api_key,
                "format": "json",
            }, timeout=4)
            if resp.status_code != 200:
                return True
            tags = resp.json().get("toptags", {}).get("tag", [])
            # İlk 5 tag'e bak (en ağırlıklı olanlar)
            artist_top_tags = {t["name"].lower() for t in tags[:5]}
            # Sanatçının herhangi bir tag'i hedef aileyle kesişiyor mu?
            return bool(artist_top_tags & target_family)
        except Exception:
            return True  # Timeout vb. → eleme yapma

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

        # 2. Mood keyword'lerden yan tür genişletmesi
        for trigger, expansions in _MOOD_TAG_EXPANSIONS.items():
            if trigger in combined_text:
                for exp_tag in expansions:
                    if exp_tag not in tags:
                        tags.append(exp_tag)
                # İlk eşleşen tetikleyiciden sonra dur (aşırı genişlemeyi önle)
                break

        # 3. Maksimum 4 tag kullan
        return tags[:4] if tags else ["pop"]

    # ── Ana arama fonksiyonu ───────────────────────────────────────────────────
    def find_songs(self, mood_data, limit=15):
        try:
            genres   = [g.lower() for g in mood_data.get("genre", [])]
            keywords = [k.lower() for k in mood_data.get("mood_keywords", [])]

            # 1. Dönem tespiti (orijinal inputtan, temizlemeden önce)
            era = self._detect_era(genres, keywords)

            # 2. Akıllı çoklu tag seçimi
            smart_tags  = self._select_smart_tags(genres, keywords)
            primary_tag = smart_tags[0] if smart_tags else "pop"
            color_tags  = smart_tags[1:]  # expansion / yan tür tag'leri

            print(f"🔍 Era: {era} | Primary: #{primary_tag} | Color: {color_tags}")

            # 3. Slot dağılımı: %70 primary, %30 color (color yoksa tümü primary)
            primary_target = round(limit * _PRIMARY_RATIO) if color_tags else limit
            color_target   = limit - primary_target

            # ── Yardımcı: belirli bir tag için ham şarkı listesi çek ──────────
            def _fetch(tag: str, n: int) -> list:
                if era == "new":
                    result = self._find_new_era_songs(tag, n)
                    return result if result else self._find_top_tracks(tag, n)
                return self._find_top_tracks(tag, n)

            # 4a. Primary havuzu (3× fazla çek — quota kaybını telafi et)
            primary_raw = _fetch(primary_tag, max(primary_target * 3, 30))

            # 4b. Color havuzu — color tag'ler arası eşit dağılım
            color_raw: list[dict] = []
            if color_tags:
                per_color = max(round(color_target * 3 / len(color_tags)), 10)
                for ct in color_tags:
                    color_raw.extend(_fetch(ct, per_color))

            # 5. Sanatçı kotası uygulayarak havuzları hedefe dolduran closure
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
                    artist = song["artist_name"].lower()
                    if artist_counts.get(artist, 0) >= MAX_SONGS_PER_ARTIST:
                        continue
                    seen_keys.add(key)
                    artist_counts[artist] = artist_counts.get(artist, 0) + 1
                    filtered_songs.append(song)
                    count += 1

            _admit(primary_raw, primary_target)   # %70 primer
            _admit(color_raw,   color_target)      # %30 color

            # Toplam hâlâ yetersizse kalan slotları primary'den tamamla
            if len(filtered_songs) < limit:
                _admit(primary_raw, limit - len(filtered_songs))

            # 6. Fallback — 15'ten az sonuç varsa ana kategoriye yükselt
            if len(filtered_songs) < 15:
                fallback_tags: list[str] = []
                for tag in smart_tags:
                    parent = _PARENT_CATEGORIES.get(tag)
                    if parent and parent not in smart_tags and parent not in fallback_tags:
                        fallback_tags.append(parent)

                for fb_tag in fallback_tags:
                    if len(filtered_songs) >= limit:
                        break
                    print(f"⚠️ {len(filtered_songs)} sonuç yetersiz (<15), fallback: #{fb_tag}")
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

            return filtered_songs[:limit]

        except Exception as e:
            print(f"❌ Hata: {e}")
            return []
