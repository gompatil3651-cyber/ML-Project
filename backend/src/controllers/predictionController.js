const Prediction = require('../models/Prediction');
const {
  fetchPrediction,
  fetchUniversePredictions,
} = require('../services/pythonServiceClient');

/**
 * @desc    Get next-session recommendation for a ticker
 * @route   GET /api/predictions/:ticker
 * @access  Public
 */
const getRecommendation = async (req, res) => {
  try {
    const { ticker } = req.params;
    const tickerClean = ticker.toUpperCase().trim();

    // Call service with live microservice -> DB cache -> fallback engine
    const recData = await fetchPrediction(tickerClean);

    // Persist prediction snapshot into MongoDB if connected
    try {
      if (recData && recData.prediction) {
        await Prediction.create({
          ticker: tickerClean,
          prediction: recData.prediction,
          confidence: recData.confidence,
          probabilities: recData.probabilities,
          technical_summary: recData.technical_summary,
          sentiment_summary: recData.sentiment_summary,
          model_version: recData.model_version || 'xgboost_purged_walkforward_v1',
        });
      }
    } catch (dbErr) {
      // Non-blocking database write warning
    }

    res.status(200).json({
      success: true,
      data: recData,
    });
  } catch (error) {
    console.error(`[PredictionController Error]:`, error.message);
    res.status(500).json({
      success: false,
      message: `Failed to fetch prediction for ${req.params.ticker}`,
      error: error.message,
    });
  }
};

/**
 * @desc    Get recommendations across all target stocks
 * @route   GET /api/predictions/universe
 * @access  Public
 */
const getUniverseRecommendations = async (req, res) => {
  try {
    const data = await fetchUniversePredictions();
    res.status(200).json({
      success: true,
      data,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to fetch universe recommendations',
      error: error.message,
    });
  }
};

/**
 * @desc    Get historical predictions for a ticker from database
 * @route   GET /api/predictions/:ticker/history
 * @access  Public
 */
const getPredictionHistory = async (req, res) => {
  try {
    const { ticker } = req.params;
    const limit = parseInt(req.query.limit, 10) || 10;
    let history = [];
    try {
      history = await Prediction.find({ ticker: ticker.toUpperCase() })
        .sort({ createdAt: -1 })
        .limit(limit);
    } catch (dbErr) {
      // Fallback empty history if DB is offline during testing
      history = [];
    }

    res.status(200).json({
      success: true,
      count: history.length,
      history,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Could not fetch prediction history',
      error: error.message,
    });
  }
};

module.exports = {
  getRecommendation,
  getUniverseRecommendations,
  getPredictionHistory,
};
