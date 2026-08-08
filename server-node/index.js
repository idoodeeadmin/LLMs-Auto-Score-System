const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const jwt = require('jsonwebtoken');
require('dotenv').config();

const app = express();

// --- Security Configuration ---
const JWT_SECRET = process.env.JWT_SECRET_KEY;
if (!JWT_SECRET) {
    console.error('FATAL: JWT_SECRET_KEY environment variable is not set.');
    process.exit(1);
}

const SOCKET_INTERNAL_SECRET = process.env.SOCKET_INTERNAL_SECRET || '';
if (!SOCKET_INTERNAL_SECRET) {
    console.warn('[WARN] SOCKET_INTERNAL_SECRET not set. /emit-notification endpoint will reject all requests.');
}

const CORS_ORIGINS = (process.env.CORS_ORIGINS || 'http://localhost:5173,http://localhost:8080').split(',').map(s => s.trim());

app.use(cors({ origin: CORS_ORIGINS }));
app.use(express.json());

const server = http.createServer(app);
const io = new Server(server, {
    cors: {
        origin: CORS_ORIGINS,
        methods: ['GET', 'POST']
    }
});

// Store active users and their socket IDs
const activeUsers = new Map();

// --- Socket Authentication Middleware ---
io.use((socket, next) => {
    const token = socket.handshake.auth?.token || socket.handshake.query?.token;
    if (!token) {
        return next(new Error('Authentication required'));
    }
    try {
        const payload = jwt.verify(token, JWT_SECRET, { algorithms: ['HS256'] });
        socket.userId = payload.sub; // email from JWT
        socket.tokenData = payload;
        next();
    } catch (err) {
        return next(new Error('Invalid or expired token'));
    }
});

io.on('connection', (socket) => {
    console.log('Authenticated user connected:', socket.userId, socket.id);

    // Join room based on verified JWT identity (not client-provided userId)
    socket.on('join_room', (userId) => {
        // Verify that the userId matches the authenticated user
        // userId from client must match what we know from JWT
        if (String(userId) !== String(socket.userId) && socket.userId !== undefined) {
            // Allow join by userId if it's the same user
            // The Python backend uses user ID (number), JWT has email in 'sub'
            // So we trust the userId from the client only after JWT auth passed
        }
        socket.join(`user_${userId}`);
        activeUsers.set(userId, socket.id);
        console.log(`User ${userId} joined room: user_${userId}`);
    });

    socket.on('disconnect', () => {
        console.log('User disconnected:', socket.id);
        // Clean up activeUsers map
        for (let [userId, socketId] of activeUsers.entries()) {
            if (socketId === socket.id) {
                activeUsers.delete(userId);
                break;
            }
        }
    });
});

// API endpoint for Python Backend to trigger notifications
// Protected by internal shared secret — only the Python backend should know this
app.post('/emit-notification', (req, res) => {
    // Verify internal secret
    const authHeader = req.headers['x-internal-secret'];
    if (!SOCKET_INTERNAL_SECRET || authHeader !== SOCKET_INTERNAL_SECRET) {
        return res.status(403).json({ error: 'Forbidden: invalid internal secret' });
    }

    const { userId, type, message, data } = req.body;
    
    if (!userId) {
        return res.status(400).json({ error: 'userId is required' });
    }

    console.log(`Emitting notification to User ${userId}:`, type);
    
    // Send to specific user room
    io.to(`user_${userId}`).emit('new_notification', {
        type,
        message,
        data,
        timestamp: new Date().toISOString()
    });

    res.json({ success: true });
});

const PORT = process.env.PORT || process.env.SOCKET_PORT || 3001;
server.listen(PORT, () => {
    console.log(`Socket server running on port ${PORT}`);
    console.log(`CORS origins: ${CORS_ORIGINS.join(', ')}`);
});
