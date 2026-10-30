const express = require('express');
const router = express.Router();
const {
  register,
  login,
  getMe,
  updateWatchlist,
} = require('../controllers/authController');
const { protect } = require('../middlewares/authMiddleware');

router.post('/register', register);
router.post('/login', login);
router.get('/me', protect, getMe);
router.put('/watchlist', protect, updateWatchlist);

module.exports = router;
