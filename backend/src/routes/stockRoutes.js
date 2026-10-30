const express = require('express');
const router = express.Router();
const {
  getTickerTechnicals,
  getHistoricalData,
  getUniverseSnapshot,
} = require('../controllers/stockController');

router.get('/universe', getUniverseSnapshot);
router.get('/:ticker/technicals', getTickerTechnicals);
router.get('/:ticker/history', getHistoricalData);

module.exports = router;
