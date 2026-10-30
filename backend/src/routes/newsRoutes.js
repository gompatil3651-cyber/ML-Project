const express = require('express');
const router = express.Router();
const {
  getTickerNews,
  getUniverseNews,
} = require('../controllers/newsController');

router.get('/universe', getUniverseNews);
router.get('/:ticker', getTickerNews);

module.exports = router;

