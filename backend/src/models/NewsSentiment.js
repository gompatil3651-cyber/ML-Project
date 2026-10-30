const mongoose = require('mongoose');

const headlineItemSchema = new mongoose.Schema(
  {
    headline: { type: String, required: true },
    sentiment: { type: String, enum: ['positive', 'neutral', 'negative'], required: true },
    positive_prob: { type: Number, default: 0 },
    neutral_prob: { type: Number, default: 0 },
    negative_prob: { type: Number, default: 0 },
    score: { type: Number, default: 0 },
    published_at: { type: String, default: null },
    url: { type: String, default: null },
  },
  { _id: false }
);

const newsSentimentSchema = new mongoose.Schema(
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
      default: Date.now,
      index: true,
    },
    Sentiment_Score: {
      type: Number,
      required: true,
      default: 0,
      comment: 'Aggregated compound sentiment score from -1.0 to 1.0',
    },
    News_Count: {
      type: Number,
      required: true,
      default: 0,
    },
    positive_count: { type: Number, default: 0 },
    neutral_count: { type: Number, default: 0 },
    negative_count: { type: Number, default: 0 },
    sentiment_label: {
      type: String,
      enum: ['Bullish', 'Neutral', 'Bearish'],
      default: 'Neutral',
    },
    headlines: [headlineItemSchema],
  },
  {
    timestamps: true,
  }
);

// Compound index on ticker and date
newsSentimentSchema.index({ ticker: 1, date: -1 });

module.exports = mongoose.model('NewsSentiment', newsSentimentSchema);
