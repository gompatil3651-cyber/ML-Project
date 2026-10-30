const mongoose = require('mongoose');

const stockPriceSchema = new mongoose.Schema(
  {
    ticker: {
      type: String,
      required: true,
      uppercase: true,
      trim: true,
      index: true,
    },
    date: {
      type: Date,
      required: true,
      index: true,
    },
    open: { type: Number, required: true },
    high: { type: Number, required: true },
    low: { type: Number, required: true },
    close: { type: Number, required: true },
    volume: { type: Number, required: true },
    daily_return: { type: Number, default: 0 },
    return_7d: { type: Number, default: 0 },
    return_30d: { type: Number, default: 0 },
    indicators: {
      sma_5: { type: Number, default: null },
      sma_10: { type: Number, default: null },
      sma_20: { type: Number, default: null },
      ema_5: { type: Number, default: null },
      ema_10: { type: Number, default: null },
      ema_20: { type: Number, default: null },
      rsi_14: { type: Number, default: null },
      volatility_20: { type: Number, default: null },
      momentum_10: { type: Number, default: null },
    },
  },
  {
    timestamps: true,
  }
);

// Compound index to guarantee uniqueness of price per ticker per date
stockPriceSchema.index({ ticker: 1, date: -1 }, { unique: true });

module.exports = mongoose.model('StockPrice', stockPriceSchema);
