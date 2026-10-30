const express = require('express');
const router = express.Router();
const {
  getRecommendation,
  getUniverseRecommendations,
  getPredictionHistory,
} = require('../controllers/predictionController');

router.get('/universe', getUniverseRecommendations);
router.get('/:ticker', getRecommendation);
router.get('/:ticker/history', getPredictionHistory);

module.exports = router;
