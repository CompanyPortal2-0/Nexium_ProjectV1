#!/bin/bash
# Download libraries for offline use - FIXED VERSION
# Run this script once with internet connection

echo "📦 Downloading client libraries (Fixed)..."

# Create libs directory
mkdir -p libs

# Download Socket.IO
echo "⬇️  Downloading Socket.IO..."
curl -L -o libs/socket.io.min.js https://cdn.socket.io/4.6.1/socket.io.min.js

# Download mediasoup-client (UMD bundle that works standalone)
echo "⬇️  Downloading mediasoup-client..."
curl -L -o libs/mediasoup-client.min.js https://cdn.jsdelivr.net/npm/mediasoup-client@3.7.6/dist/mediasoup-client.min.js

# Verify files were downloaded
echo ""
if [ -f "libs/socket.io.min.js" ]; then
    size=$(wc -c < "libs/socket.io.min.js")
    echo "✅ socket.io.min.js downloaded (${size} bytes)"
else
    echo "❌ socket.io.min.js FAILED"
fi

if [ -f "libs/mediasoup-client.min.js" ]; then
    size=$(wc -c < "libs/mediasoup-client.min.js")
    echo "✅ mediasoup-client.min.js downloaded (${size} bytes)"
else
    echo "❌ mediasoup-client.min.js FAILED"
fi

echo ""
echo "📁 Files in libs/:"
ls -lh libs/

echo ""
echo "✅ Setup complete! Now you can use the client HTML file offline!"