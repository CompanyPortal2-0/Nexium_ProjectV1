// SFU Microservice using mediasoup
// Install: npm install mediasoup express socket.io cors

const express = require('express');
const https = require('https');
const http = require('http');
const fs = require('fs');
const socketIO = require('socket.io');
const mediasoup = require('mediasoup');
const cors = require('cors');
const os = require('os');

console.log('🚀 Starting SFU Server...');

const app = express();
app.use(cors());
app.use(express.json());

// Configuration
const config = {
  listenIp: '0.0.0.0',
  listenPort: 3000,
  
  mediasoup: {
    numWorkers: Object.keys(os.cpus()).length,
    worker: {
      rtcMinPort: 10000,
      rtcMaxPort: 10100,
      logLevel: 'warn',
      logTags: ['info', 'ice', 'dtls', 'rtp', 'srtp', 'rtcp'],
    },
    router: {
      mediaCodecs: [
        {
          kind: 'audio',
          mimeType: 'audio/opus',
          clockRate: 48000,
          channels: 2,
        },
        {
          kind: 'video',
          mimeType: 'video/VP8',
          clockRate: 90000,
          parameters: {
            'x-google-start-bitrate': 1000,
          },
        },
        {
          kind: 'video',
          mimeType: 'video/H264',
          clockRate: 90000,
          parameters: {
            'packetization-mode': 1,
            'profile-level-id': '42e01f',
            'level-asymmetry-allowed': 1,
          },
        },
      ],
    },
    webRtcTransport: {
      listenIps: [
        {
          ip: '0.0.0.0',
          announcedIp: '127.0.0.1', // ⚠️ Change to your LAN IP (e.g., 192.168.1.100)
        },
      ],
      maxIncomingBitrate: 1500000,
      initialAvailableOutgoingBitrate: 1000000,
    },
  },
};

console.log('📋 Configuration loaded');
console.log(`   Workers: ${config.mediasoup.numWorkers}`);
console.log(`   RTC Ports: ${config.mediasoup.worker.rtcMinPort}-${config.mediasoup.worker.rtcMaxPort}`);
console.log(`   Announced IP: ${config.mediasoup.webRtcTransport.listenIps[0].announcedIp}`);

// State management
const workers = [];
let nextWorkerIdx = 0;
const rooms = new Map(); // roomId -> Room

class Room {
  constructor(roomId, worker) {
    this.id = roomId;
    this.router = null;
    this.peers = new Map(); // socketId -> Peer
    this.worker = worker;
  }

  async init() {
    this.router = await this.worker.createRouter({
      mediaCodecs: config.mediasoup.router.mediaCodecs,
    });
    console.log(`   Router created for room: ${this.id}`);
  }

  addPeer(peer) {
    this.peers.set(peer.id, peer);
    console.log(`   Peer ${peer.id} added to room ${this.id} (total: ${this.peers.size})`);
  }

  removePeer(peerId) {
    this.peers.delete(peerId);
    console.log(`   Peer ${peerId} removed from room ${this.id} (remaining: ${this.peers.size})`);
    if (this.peers.size === 0) {
      console.log(`   Room ${this.id} is empty, closing...`);
      this.close();
    }
  }

  getPeers() {
    return Array.from(this.peers.values());
  }

  close() {
    this.router.close();
    rooms.delete(this.id);
    console.log(`   Room ${this.id} closed`);
  }
}

class Peer {
  constructor(id, roomId, socket) {
    this.id = id;
    this.roomId = roomId;
    this.socket = socket;
    this.transports = new Map();
    this.producers = new Map();
    this.consumers = new Map();
  }

  addTransport(transport) {
    this.transports.set(transport.id, transport);
  }

  async connectTransport(transportId, dtlsParameters) {
    const transport = this.transports.get(transportId);
    if (!transport) throw new Error('Transport not found');
    await transport.connect({ dtlsParameters });
  }

  async createProducer(transportId, rtpParameters, kind) {
    const transport = this.transports.get(transportId);
    if (!transport) throw new Error('Transport not found');
    
    const producer = await transport.produce({ kind, rtpParameters });
    this.producers.set(producer.id, producer);
    
    producer.on('transportclose', () => {
      this.producers.delete(producer.id);
    });
    
    return producer;
  }

  async createConsumer(producerId, rtpCapabilities, transport) {
    const room = rooms.get(this.roomId);
    if (!room.router.canConsume({ producerId, rtpCapabilities })) {
      throw new Error('Cannot consume');
    }
    
    const consumer = await transport.consume({
      producerId,
      rtpCapabilities,
      paused: true,
    });
    
    this.consumers.set(consumer.id, consumer);
    
    consumer.on('transportclose', () => {
      this.consumers.delete(consumer.id);
    });
    
    consumer.on('producerclose', () => {
      this.socket.emit('consumerClosed', { consumerId: consumer.id });
      this.consumers.delete(consumer.id);
    });
    
    return consumer;
  }

  close() {
    this.transports.forEach(transport => transport.close());
    this.socket.disconnect();
  }
}

// Initialize mediasoup workers
async function initWorkers() {
  console.log('⚙️  Creating mediasoup workers...');
  for (let i = 0; i < config.mediasoup.numWorkers; i++) {
    try {
      const worker = await mediasoup.createWorker(config.mediasoup.worker);
      
      worker.on('died', () => {
        console.error(`❌ Worker ${i} died, exiting in 2 seconds...`);
        setTimeout(() => process.exit(1), 2000);
      });
      
      workers.push(worker);
      console.log(`   ✅ Worker ${i + 1}/${config.mediasoup.numWorkers} created`);
    } catch (error) {
      console.error(`   ❌ Failed to create worker ${i}:`, error);
      throw error;
    }
  }
  console.log(`✅ All ${workers.length} workers ready`);
}

// Get next worker using round-robin
function getWorker() {
  const worker = workers[nextWorkerIdx];
  nextWorkerIdx = (nextWorkerIdx + 1) % workers.length;
  return worker;
}

// Get or create room
async function getOrCreateRoom(roomId) {
  let room = rooms.get(roomId);
  
  if (!room) {
    console.log(`📦 Creating new room: ${roomId}`);
    room = new Room(roomId, getWorker());
    await room.init();
    rooms.set(roomId, room);
  }
  
  return room;
}

// Check if SSL certificates exist, if not use HTTP
let server;
const certPath = './cert.pem';
const keyPath = './key.pem';

if (fs.existsSync(certPath) && fs.existsSync(keyPath)) {
  console.log('🔒 SSL certificates found, using HTTPS');
  server = https.createServer({
    cert: fs.readFileSync(certPath, 'utf-8'),
    key: fs.readFileSync(keyPath, 'utf-8'),
  }, app);
} else {
  console.log('⚠️  No SSL certificates found, using HTTP');
  console.log('   For production, generate certificates with:');
  console.log('   openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes');
  server = http.createServer(app);
}

const io = socketIO(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST'],
  },
});

// Socket.IO connection handling
io.on('connection', (socket) => {
  console.log(`👤 New peer connected: ${socket.id}`);
  
  let currentPeer = null;
  let currentRoom = null;
  
  socket.on('join', async ({ roomId }, callback) => {
    try {
      console.log(`🚪 Peer ${socket.id} joining room: ${roomId}`);
      currentRoom = await getOrCreateRoom(roomId);
      currentPeer = new Peer(socket.id, roomId, socket);
      currentRoom.addPeer(currentPeer);
      
      const rtpCapabilities = currentRoom.router.rtpCapabilities;
      
      callback({ rtpCapabilities });
      
      const otherPeers = currentRoom.getPeers()
        .filter(p => p.id !== socket.id)
        .map(p => ({ id: p.id }));
      
      socket.emit('peers', { peers: otherPeers });
      socket.to(roomId).emit('newPeer', { peerId: socket.id });
      
      socket.join(roomId);
      console.log(`✅ Peer ${socket.id} joined room ${roomId}`);
    } catch (error) {
      console.error(`❌ Error joining room:`, error);
      callback({ error: error.message });
    }
  });
  
  socket.on('createWebRtcTransport', async ({ producing, consuming }, callback) => {
    try {
      const transport = await currentRoom.router.createWebRtcTransport({
        ...config.mediasoup.webRtcTransport,
        enableUdp: true,
        enableTcp: true,
        preferUdp: true,
      });
      
      currentPeer.addTransport(transport);
      
      callback({
        id: transport.id,
        iceParameters: transport.iceParameters,
        iceCandidates: transport.iceCandidates,
        dtlsParameters: transport.dtlsParameters,
      });
    } catch (error) {
      console.error('❌ Error creating transport:', error);
      callback({ error: error.message });
    }
  });
  
  socket.on('connectWebRtcTransport', async ({ transportId, dtlsParameters }, callback) => {
    try {
      await currentPeer.connectTransport(transportId, dtlsParameters);
      callback({ success: true });
    } catch (error) {
      console.error('❌ Error connecting transport:', error);
      callback({ error: error.message });
    }
  });
  
  socket.on('produce', async ({ transportId, kind, rtpParameters }, callback) => {
    try {
      const producer = await currentPeer.createProducer(transportId, rtpParameters, kind);
      
      callback({ id: producer.id });
      
      socket.to(currentPeer.roomId).emit('newProducer', {
        producerId: producer.id,
        peerId: socket.id,
        kind,
      });
      
      console.log(`🎥 Peer ${socket.id} producing ${kind}`);
    } catch (error) {
      console.error('❌ Error producing:', error);
      callback({ error: error.message });
    }
  });
  
  socket.on('consume', async ({ producerId, rtpCapabilities, transportId }, callback) => {
    try {
      const transport = currentPeer.transports.get(transportId);
      const consumer = await currentPeer.createConsumer(producerId, rtpCapabilities, transport);
      
      callback({
        id: consumer.id,
        producerId,
        kind: consumer.kind,
        rtpParameters: consumer.rtpParameters,
      });
    } catch (error) {
      console.error('❌ Error consuming:', error);
      callback({ error: error.message });
    }
  });
  
  socket.on('resumeConsumer', async ({ consumerId }, callback) => {
    try {
      const consumer = currentPeer.consumers.get(consumerId);
      await consumer.resume();
      callback({ success: true });
    } catch (error) {
      console.error('❌ Error resuming consumer:', error);
      callback({ error: error.message });
    }
  });
  
  socket.on('getProducers', (callback) => {
    if (!currentRoom) return callback({ producers: [] });
    
    const producers = [];
    currentRoom.getPeers().forEach(peer => {
      if (peer.id !== socket.id) {
        peer.producers.forEach((producer, id) => {
          producers.push({
            producerId: id,
            peerId: peer.id,
            kind: producer.kind,
          });
        });
      }
    });
    
    callback({ producers });
  });
  
  socket.on('disconnect', () => {
    console.log(`👋 Peer disconnected: ${socket.id}`);
    
    if (currentPeer && currentRoom) {
      currentPeer.close();
      currentRoom.removePeer(socket.id);
      socket.to(currentPeer.roomId).emit('peerClosed', { peerId: socket.id });
    }
  });
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    rooms: rooms.size,
    workers: workers.length,
  });
});

// Stats endpoint
app.get('/stats', (req, res) => {
  const stats = {
    rooms: rooms.size,
    workers: workers.length,
    totalPeers: 0,
    roomDetails: []
  };
  
  rooms.forEach((room, id) => {
    stats.totalPeers += room.peers.size;
    stats.roomDetails.push({
      id,
      peers: room.peers.size,
    });
  });
  
  res.json(stats);
});

// Root endpoint
app.get('/', (req, res) => {
  res.send(`
    <html>
      <head><title>SFU Server</title></head>
      <body style="font-family: Arial; padding: 40px; background: #1a1a1a; color: white;">
        <h1>🎥 SFU Server Running</h1>
        <p>Server is running successfully!</p>
        <ul>
          <li><a href="/health" style="color: #4CAF50;">Health Check</a></li>
          <li><a href="/stats" style="color: #4CAF50;">Server Stats</a></li>
        </ul>
        <p>Connect your client to: <code>${config.listenIp === '0.0.0.0' ? 'your-server-ip' : config.listenIp}:${config.listenPort}</code></p>
      </body>
    </html>
  `);
});

// Start server
async function start() {
  try {
    console.log('');
    console.log('═══════════════════════════════════════');
    console.log('  SFU MICROSERVICE INITIALIZATION');
    console.log('═══════════════════════════════════════');
    console.log('');
    
    await initWorkers();
    
    server.listen(config.listenPort, config.listenIp, () => {
      console.log('');
      console.log('═══════════════════════════════════════');
      console.log('✅ SFU SERVER STARTED SUCCESSFULLY!');
      console.log('═══════════════════════════════════════');
      console.log('');
      console.log(`🌐 Server URL: ${fs.existsSync(certPath) ? 'https' : 'http'}://localhost:${config.listenPort}`);
      console.log(`🔗 Local IP: ${fs.existsSync(certPath) ? 'https' : 'http'}://${getLocalIP()}:${config.listenPort}`);
      console.log('');
      console.log('📊 Endpoints:');
      console.log(`   - Health: /health`);
      console.log(`   - Stats:  /stats`);
      console.log('');
      console.log('⚠️  IMPORTANT: Update announcedIp to your server IP!');
      console.log(`   Current: ${config.mediasoup.webRtcTransport.listenIps[0].announcedIp}`);
      console.log('');
      console.log('🎯 Ready to accept connections!');
      console.log('═══════════════════════════════════════');
      console.log('');
    });
  } catch (error) {
    console.error('');
    console.error('═══════════════════════════════════════');
    console.error('❌ FATAL ERROR - FAILED TO START SFU');
    console.error('═══════════════════════════════════════');
    console.error('');
    console.error('Error:', error.message);
    console.error('');
    console.error('Stack trace:', error.stack);
    console.error('');
    console.error('Troubleshooting:');
    console.error('  1. Check if ports are available (3000, 10000-10100)');
    console.error('  2. Ensure mediasoup is installed: npm install mediasoup');
    console.error('  3. Check firewall settings');
    console.error('');
    process.exit(1);
  }
}

// Get local IP address
function getLocalIP() {
  const interfaces = os.networkInterfaces();
  for (const name of Object.keys(interfaces)) {
    for (const iface of interfaces[name]) {
      if (iface.family === 'IPv4' && !iface.internal) {
        return iface.address;
      }
    }
  }
  return '127.0.0.1';
}

// Handle process termination
process.on('SIGINT', () => {
  console.log('');
  console.log('⚠️  Shutting down server...');
  workers.forEach(worker => worker.close());
  process.exit(0);
});

start();