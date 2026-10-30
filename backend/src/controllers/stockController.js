const StockPrice = require('../models/StockPrice');
const {
  fetchTechnicals,
  fetchHistoricalData,
  fetchUniverseTechnicals,
} = require('../services/pythonServiceClient');

/**
 * @desc    Get latest technical indicators and OHLCV for a ticker
 * @route   GET /api/stocks/:ticker/technicals
 * @access  Public
 */
const getTickerTechnicals = async (req, res) => {
  try {
    const { ticker } = req.params;
    const tickerClean = ticker.toUpperCase().trim();

    // Fetch from Python microservice with automatic DB cache and mock fallback
    const data = await fetchTechnicals(tickerClean);

    // Persist/Cache to MongoDB StockPrice collection if connected
    try {
      if (data && data.latest_close) {
        await StockPrice.findOneAndUpdate(
          { ticker: tickerClean, date: new Date(data.updated_at || Date.now()) },
          {
            ticker: tickerClean,
            date: new Date(data.updated_at || Date.now()),
            open: data.open,
            high: data.high,
            low: data.low,
            close: data.latest_close,
            volume: data.volume,
            daily_return: data.daily_return,
            return_7d: data.return_7d,
            return_30d: data.return_30d,
            indicators: {
              sma_5: data.sma_5,
              sma_10: data.sma_10,
              sma_20: data.sma_20,
              ema_5: data.ema_5,
              ema_10: data.ema_10,
              ema_20: data.ema_20,
              rsi_14: data.rsi_14,
              volatility_20: data.volatility_20,
              momentum_10: data.momentum_10,
            },
          },
          { upsert: true, new: true }
        );
      }
    } catch (dbErr) {
      // Non-blocking database cache warning
    }

    res.status(200).json({
      success: true,
      data,
    });
  } catch (error) {
    console.error(`[StockController Error]:`, error.message);
    res.status(500).json({
      success: false,
      message: `Failed to fetch technical indicators for ${req.params.ticker}`,
      error: error.message,
    });
  }
};

/**
 * @desc    Get historical price series & indicators for charting
 * @route   GET /api/stocks/:ticker/history
 * @access  Public
 */
const getHistoricalData = async (req, res) => {
  try {
    const { ticker } = req.params;
    const { period = '1y' } = req.query;
    const tickerClean = ticker.toUpperCase().trim();

    const data = await fetchHistoricalData(tickerClean, period);
    res.status(200).json({
      success: true,
      data,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: `Failed to fetch historical series for ${req.params.ticker}`,
      error: error.message,
    });
  }
};

/**
 * @desc    Get universe snapshot for all target stocks
 * @route   GET /api/stocks/universe
 * @access  Public
 */
const getUniverseSnapshot = async (req, res) => {
  try {
    const universe = await fetchUniverseTechnicals();
    res.status(200).json({
      success: true,
      universe,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to fetch universe snapshot',
      error: error.message,
    });
  }
};

module.exports = {
  getTickerTechnicals,
  getHistoricalData,
  getUniverseSnapshot,
};
