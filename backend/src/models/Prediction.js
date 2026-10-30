const mongoose = require('mongoose');

const predictionSchema = new mongoose.Schema(
  {
    ticker: {
      type: String,
      required: true,
      uppercase: true,
      trim: true,
      index: true,
    },
    prediction: {
      type: String,
      enum: ['BUY', 'HOLD', 'WAIT'],
      required: true,
    },
    confidence: {
      type: Number,
      required: true,
      min: 0,
      max: 1,
    },
    probabilities: {
      BUY: { type: Number, default: 0 },
      HOLD: { type: Number, default: 0 },
      WAIT: { type: Number, default: 0 },
    },
    technical_summary: {
      type: Map,
      of: Number,
      default: {},
    },
    sentiment_summary: {
      Sentiment_Score: { type: Number, default: 0 },
      News_Count: { type: Number, default: 0 },
    },
    model_version: {
      type: String,
      default: 'xgboost_v1',
    },
    prediction_date: {
      type: Date,
      default: Date.now,
      index: true,
    },
  },
  {
    timestamps: true,
  }
);

predictionSchema.index({ ticker: 1, prediction_date: -1 });

module.exports = mongoose.model('Prediction', predictionSchema);
