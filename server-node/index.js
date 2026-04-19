const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json());

const server = http.createServer(app);
const io = new Server(server, {
    cors: {
        origin: "*", // In production, replace with your frontend URL
        methods: ["GET", "POST"]
    }
});

// Store active users and their socket IDs
const activeUsers = new Map();

io.on('connection', (socket) => {
    console.log('A user connected:', socket.id);

    // Join room based on User ID to receive personal notifications
    socket.on('join_room', (userId) => {
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
app.post('/emit-notification', (req, res) => {
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

const PORT = process.env.SOCKET_PORT || 3001;
server.listen(PORT, () => {
    console.log(`Socket server running on port ${PORT}`);
});
