import os
import sys
import requests
from dotenv import load_dotenv

# Proje yolu ayarı
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.Agent import DjAI

load_dotenv()

class LastFmMusicFinder:
    def __init__(self):
        self.api_key = os.getenv("LASTFM_API_KEY")
        self.base_url = "http://ws.audioscrobbler.com/2.0/"

    def find_songs(self, mood_data, limit=15):
        try:
            # DjAI'dan gelen listeleri temizleyelim
            genres = [g.lower() for g in mood_data.get('genre', [])]
            keywords = [k.lower() for k in mood_data.get('mood_keywords', [])]
            
            # 1. EN GÜÇLÜ TAG'İ BELİRLEME
            # İlk janra genelde en belirleyici olandır (Örn: 'turkish rap', 'french pop')
            primary_genre = genres[0] if genres else "pop"
            
            # 2. ÜLKE/DİL BAZLI TEMİZLİK
            # Eğer janra içinde spesifik bir ülke varsa (German, French, Turkish vb.)
            # Last.fm'in "newschool" gibi kelimelerle sapıtmasını engellemek için 
            # janrayı ana arama terimi yapıyoruz.
            target_tag = primary_genre

            # 3. ÖZEL DURUM: Eğer janra çok kısaysa veya sadece 'newschool' gibi 
            # belirsiz bir şeyse, mood keyword'lerinden destek al.
            if len(target_tag) < 3 or target_tag in ["new", "old", "best"]:
                target_tag = keywords[0] if keywords else "pop"

            print(f"🎵 Last.fm üzerinde '#{target_tag}' etiketli hitler aranıyor...")

            params = {
                "method": "tag.gettoptracks",
                "tag": target_tag,
                "api_key": self.api_key,
                "format": "json",
                "limit": limit
            }

            response = requests.get(self.base_url, params=params)
            
            if response.status_code != 200:
                return []

            data = response.json()
            tracks = data.get('tracks', {}).get('track', [])
            
            # FALLBACK: Eğer sonuç gelmezse janrayı basitleştir (Örn: 'turkish rap' -> 'rap')
            if not tracks and " " in target_tag:
                simplified_tag = target_tag.split()[-1]
                print(f"⚠️ Sonuç yok, basitleştiriliyor: #{simplified_tag}")
                return self.find_songs({"genre": [simplified_tag]}, limit)

            song_list = []
            for track in tracks:
                song_list.append({
                    "track_name": track['name'],
                    "artist_name": track['artist']['name'],
                    "query": f"{track['name']} {track['artist']['name']} official audio"
                })

            return song_list

        except Exception as e:
            print(f"❌ Hata: {e}")
            return []
