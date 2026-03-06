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
            # Last.fm etiket (tag) mantığıyla çalışır. 
            # Tür ve mood keyword'lerini birleştirip en popüler olanı seçiyoruz.
            genre = mood_data.get('genre', ['pop'])[0]
            mood_tag = mood_data.get('mood_keywords', ['chill'])[0]
            
            # Anahtar kelimeyi belirliyoruz (Örn: "rnb" veya "romantic")
            # Last.fm'de tag aratırken en güçlü olanı seçmek daha iyi sonuç verir.
            target_tag = mood_tag if mood_tag else genre
            
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
                print(f"❌ Last.fm Hatası: {response.status_code}")
                return []

            data = response.json()
            tracks = data.get('tracks', {}).get('track', [])
            
            song_list = []
            for track in tracks:
                # Last.fm zaten en popülerleri getirdiği için ekstra filtreye pek gerek kalmaz
                song_list.append({
                    "track_name": track['name'],
                    "artist_name": track['artist']['name'],
                    "query": f"{track['name']} {track['artist']['name']} official audio"
                })

            return song_list

        except Exception as e:
            print(f"❌ Kritik Hata: {e}")
            return []

