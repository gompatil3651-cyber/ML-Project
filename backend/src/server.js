require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const mongoose = require('mongoose');

const connectDB = require('./config/db');
const authRoutes = require('./routes/authRoutes');
const stockRoutes = require('./routes/stockRoutes');
const predictionRoutes = require('./routes/predictionRoutes');
const newsRoutes = require('./routes/newsRoutes');
const { checkPythonHealth } = require('./services/pythonServiceClient');
const { TARGET_STOCKS } = require('./services/fallbackDataService');

const app = express();
const PORT = process.env.PORT || 5000;

// Security and utility middleware
app.use(helmet());
app.use(cors({
  origin: '*', // Allows Streamlit dashboard and API testing tools
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}));

if (process.env.NODE_ENV !== 'test') {
  app.use(morgan('dev'));
}

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Connect to MongoDB
connectDB();

// Root and System Health Endpoints
app.get('/', (req, res) => {
  res.status(200).json({
    project: 'Stock Insight Backend API',
    version: '1.0.0',
    status: 'online',
    timestamp: new Date().toISOString(),
    endpoints: {
      auth: '/api/auth',
      stocks: '/api/stocks',
      predictions: '/api/predictions',
      news: '/api/news',
      health: '/health',
    },
  });
});

app.get('/health', async (req, res) => {
  const dbStatus = mongoose.connection.readyState === 1 ? 'CONNECTED' : 'DISCONNECTED';
  const pythonStatus = await checkPythonHealth();

  res.status(200).json({
    status: 'UP',
    server_time: new Date().toISOString(),
    database: {
      status: dbStatus,
      name: mongoose.connection.name || 'stock_insight',
    },
    python_microservice: pythonStatus,
    resilient_mode: {
      fallback_active: !pythonStatus.is_available,
      target_stocks_count: TARGET_STOCKS.length,
      target_stocks: TARGET_STOCKS,
    },
  });
});

// API Routes
app.use('/api/auth', authRoutes);
app.use('/api/stocks', stockRoutes);
app.use('/api/predictions', predictionRoutes);
app.use('/api/news', newsRoutes);

// 404 Route Handler
app.use((req, res, next) => {
  res.status(404).json({
    success: false,
    message: `Resource not found at ${req.originalUrl}`,
  });
});

// Global Error Handler
app.use((err, req, res, next) => {
  console.error('[Unhandled Server Error]:', err.stack || err);
  const statusCode = err.statusCode || 500;
  res.status(statusCode).json({
    success: false,
    message: err.message || 'Internal Server Error',
    stack: process.env.NODE_ENV === 'development' ? err.stack : undefined,
  });
});

// Start HTTP server unless in test runner
let server;
if (process.env.NODE_ENV !== 'test') {
  server = app.listen(PORT, () => {
    console.log(`====================================================`);
    console.log(` Stock Insight Backend API running on port ${PORT}`);
    console.log(` Mode: ${process.env.NODE_ENV || 'development'}`);
    console.log(` API Docs & Health: http://localhost:${PORT}/health`);
    console.log(`====================================================`);
  });
}

// Handle unhandled promise rejections
process.on('unhandledRejection', (err) => {
  console.error('[CRITICAL] Unhandled Rejection:', err.message);
});

module.exports = { app, server };
