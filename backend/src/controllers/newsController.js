const {
  fetchNewsSentiment,
  fetchUniverseSentiment,
} = require('../services/pythonServiceClient');
const NewsSentiment = require('../models/NewsSentiment');

/**
 * @desc    Get scraped Finviz news scored by FinBERT for a ticker
 * @route   GET /api/news/:ticker
 * @access  Public
 */
const getTickerNews = async (req, res) => {
  try {
    const { ticker } = req.params;
    const limit = parseInt(req.query.limit, 10) || 15;
    const tickerClean = ticker.toUpperCase().trim();

    const data = await fetchNewsSentiment(tickerClean, limit);

    // Cache to MongoDB if connected
    try {
      if (data && data.Sentiment_Score !== undefined) {
        await NewsSentiment.create({
          ticker: tickerClean,
          Sentiment_Score: data.Sentiment_Score,
          News_Count: data.News_Count,
          positive_count: data.positive_count,
          neutral_count: data.neutral_count,
          negative_count: data.negative_count,
          sentiment_label: data.sentiment_label,
          headlines: data.headlines || [],
        });
      }
    } catch (dbErr) {
      // Non-blocking database write
    }

    res.status(200).json({
      success: true,
      data,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: `Failed to fetch news sentiment for ${req.params.ticker}`,
      error: error.message,
    });
  }
};

/**
 * @desc    Get news sentiment across target universe
 * @route   GET /api/news/universe
 * @access  Public
 */
const getUniverseNews = async (req, res) => {
  try {
    const limit = parseInt(req.query.limit, 10) || 15;
    const data = await fetchUniverseSentiment(limit);
    res.status(200).json({
      success: true,
      data,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to fetch universe sentiment',
      error: error.message,
    });
  }
};

module.exports = {
  getTickerNews,
  getUniverseNews,
};

