#!/bin/bash
# YouTube Entegrasyonu Test Scripti

echo "🎵 YouTube Entegrasyonu Test Scripti"
echo "===================================="
echo ""

# Test 1: Playlist oluştur
echo "📝 Adım 1: AI ile playlist oluşturuluyor..."
RESPONSE=$(curl -s -X POST "http://localhost:8000/playlist/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "90lar Türkçe pop müziği 15 şarkı"}')

echo "✅ Playlist oluşturuldu:"
echo "$RESPONSE" | python3 -m json.tool

# Playlist ID'yi çıkar
PLAYLIST_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('playlist_id', ''))")

if [ -z "$PLAYLIST_ID" ]; then
    echo "❌ Playlist oluşturulamadı!"
    exit 1
fi

echo ""
echo "📋 Playlist ID: $PLAYLIST_ID"
echo ""

# Test 2: YouTube OAuth URL'i al
echo "🔗 Adım 2: YouTube OAuth URL'i oluşturuluyor..."
OAUTH_URL="http://localhost:8000/youtube/start?playlist_id=$PLAYLIST_ID"

echo "✅ YouTube OAuth URL'i hazır:"
echo "$OAUTH_URL"
echo ""

echo "📱 Tarayıcıda bu URL'i aç:"
echo "----------------------------------------"
echo "$OAUTH_URL"
echo "----------------------------------------"
echo ""

echo "⚠️  DİKKAT:"
echo "1. Bu URL'i tarayıcıda açın"
echo "2. Google hesabınızla giriş yapın"
echo "3. İzinleri onaylayın"
echo "4. YouTube playlist'iniz otomatik oluşturulacak!"
echo ""

# URL'i otomatik aç (Linux'ta)
if command -v xdg-open > /dev/null; then
    echo "🌐 Tarayıcıda açılıyor..."
    xdg-open "$OAUTH_URL"
elif command -v gnome-open > /dev/null; then
    gnome-open "$OAUTH_URL"
fi
