const mongoose = require('mongoose');

const connectDB = async () => {
  try {
    const connUri = process.env.MONGODB_URI || 'mongodb://127.0.0.1:27017/stock_insight';
    
    // Set buffer timeout so operations fail fast if DB is disconnected during testing
    mongoose.set('bufferTimeoutMS', 2500);

    mongoose.connection.on('connected', () => {
      console.log(`[MongoDB] Successfully connected to database.`);
    });

    mongoose.connection.on('error', (err) => {
      console.error(`[MongoDB] Connection error: ${err.message}`);
    });

    mongoose.connection.on('disconnected', () => {
      console.warn(`[MongoDB] Disconnected from database.`);
    });

    const conn = await mongoose.connect(connUri, {
      serverSelectionTimeoutMS: 3000,
    });

    console.log(`[MongoDB] Host: ${conn.connection.host}, DB: ${conn.connection.name}`);
    return conn;
  } catch (error) {
    console.error(`[MongoDB Error] Failed to connect: ${error.message}`);
    console.warn(`[MongoDB Warning] Server will continue running, but database features will be restricted until MongoDB is available.`);
  }
};

module.exports = connectDB;
