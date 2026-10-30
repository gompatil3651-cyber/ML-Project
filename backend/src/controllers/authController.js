const User = require('../models/User');

/**
 * @desc    Register a new user
 * @route   POST /api/auth/register
 * @access  Public
 */
const register = async (req, res) => {
  try {
    const { name, email, password } = req.body;

    if (!name || !email || !password) {
      return res.status(400).json({
        success: false,
        message: 'Please provide name, email, and password.',
      });
    }

    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).json({
        success: false,
        message: 'User with this email already exists.',
      });
    }

    const user = await User.create({
      name,
      email,
      password,
    });

    const token = user.generateAuthToken();

    res.status(201).json({
      success: true,
      message: 'User registered successfully.',
      token,
      user: {
        id: user._id,
        name: user.name,
        email: user.email,
        role: user.role,
        watchlist: user.watchlist,
      },
    });
  } catch (error) {
    console.error('[AuthController Register Error]:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error during registration.',
      error: error.message,
    });
  }
};

/**
 * @desc    Authenticate user & get token
 * @route   POST /api/auth/login
 * @access  Public
 */
const login = async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({
        success: false,
        message: 'Please provide an email and password.',
      });
    }

    const user = await User.findOne({ email }).select('+password');
    if (!user) {
      return res.status(401).json({
        success: false,
        message: 'Invalid credentials.',
      });
    }

    const isMatch = await user.comparePassword(password);
    if (!isMatch) {
      return res.status(401).json({
        success: false,
        message: 'Invalid credentials.',
      });
    }

    const token = user.generateAuthToken();

    res.status(200).json({
      success: true,
      message: 'Logged in successfully.',
      token,
      user: {
        id: user._id,
        name: user.name,
        email: user.email,
        role: user.role,
        watchlist: user.watchlist,
      },
    });
  } catch (error) {
    console.error('[AuthController Login Error]:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error during login.',
      error: error.message,
    });
  }
};

/**
 * @desc    Get current logged in user
 * @route   GET /api/auth/me
 * @access  Private
 */
const getMe = async (req, res) => {
  try {
    const user = await User.findById(req.user.id);
    res.status(200).json({
      success: true,
      user,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Could not fetch user profile.',
      error: error.message,
    });
  }
};

/**
 * @desc    Update user watchlist
 * @route   PUT /api/auth/watchlist
 * @access  Private
 */
const updateWatchlist = async (req, res) => {
  try {
    const { watchlist } = req.body;
    if (!Array.isArray(watchlist)) {
      return res.status(400).json({
        success: false,
        message: 'Watchlist must be an array of ticker symbols.',
      });
    }

    const updatedUser = await User.findByIdAndUpdate(
      req.user.id,
      { watchlist: watchlist.map((t) => t.toUpperCase().trim()) },
      { new: true }
    );

    res.status(200).json({
      success: true,
      watchlist: updatedUser.watchlist,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error updating watchlist.',
      error: error.message,
    });
  }
};

module.exports = {
  register,
  login,
  getMe,
  updateWatchlist,
};
