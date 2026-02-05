#!/bin/bash
# YouTube Endpoint Direkt Test (Mock Data ile)

echo "🎵 YouTube Endpoint Test (Mock Data)"
echo "====================================="
echo ""

# Mock playlist verisi oluştur
echo "📝 Mock playlist verisi hazırlanıyor..."

# Python script ile direkt playlists_db'ye veri ekle
python3 << 'EOF'
import sys
import json
import uuid

# Test playlist
test_playlist_id = str(uuid.uuid4())
test_playlist = {
    "playlist_name": "90'lar Türkçe Pop Test",
    "tracks": [
        {"artist": "Tarkan", "title": "Şımarık"},
        {"artist": "Mustafa Sandal", "title": "Aya Benzer"},
        {"artist": "Sezen Aksu", "title": "Şarkı Söylemek Lazım"},
        {"artist": "Ajda Pekkan", "title": "Yakar Geçerim"},
        {"artist": "Sertab Erener", "title": "Çocukluktan Geliyorum"}
    ]
}

print(f"✅ Test Playlist ID: {test_playlist_id}")
print(f"✅ Playlist Adı: {test_playlist['playlist_name']}")
print(f"✅ Şarkı Sayısı: {len(test_playlist['tracks'])}")
print()
print("🔗 YouTube OAuth URL:")
print(f"http://localhost:8000/youtube/start?playlist_id={test_playlist_id}")
print()
print("⚠️  Ancak bu playlist henüz bellekte değil!")
print("➡️  Playlist'i belleğe eklemek için API'yi kullanmalısınız.")

EOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 YOUTUBE TEST ADIMLARI:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "YÖNTEM 1: Swagger UI ile Test (Önerilen)"
echo "----------------------------------------"
echo "1. Tarayıcıda aç: http://localhost:8000/docs"
echo "2. '/youtube/start' endpoint'ine tıkla"
echo "3. 'Try it out' butonuna tıkla"
echo "4. playlist_id parametresine herhangi bir UUID gir"
echo "   (örn: 123e4567-e89b-12d3-a456-426614174000)"
echo "5. 'Execute' butonuna tıkla"
echo "6. Response'ta Google OAuth URL'ini göreceksin"
echo "7. Bu URL'e tarayıcıdan git ve Google ile giriş yap"
echo ""
echo "YÖNTEM 2: curl ile Test"
echo "----------------------------------------"
echo "# OAuth URL al:"
echo 'curl "http://localhost:8000/youtube/start?playlist_id=test-123"'
echo ""
echo "YÖNTEM 3: Tarayıcıdan Direkt"
echo "----------------------------------------"
echo "Tarayıcıda aç:"
echo "http://localhost:8000/youtube/start?playlist_id=test-123"
echo ""
echo "⚠️  NOT: Playlist gerçekten oluşturulmadığı için"
echo "    OAuth sonrası 'Playlist not found' hatası alacaksınız."
echo "    Ama OAuth akışını test edebilirsiniz!"
echo ""
