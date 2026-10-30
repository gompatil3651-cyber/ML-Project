/**
 * Fallback and Mock Data Service for Stock Insight (Scaled to 150 Target Tickers)
 * 
 * Supports the complete 150 S&P Market Leaders universe across Technology,
 * Financials, Healthcare, Consumer, Energy, Industrials, Real Estate,
 * Utilities, and Communication Services.
 */

const TARGET_STOCKS = [
  'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'AVGO', 'ORCL', 'CRM', 'AMD',
  'ADBE', 'CSCO', 'IBM', 'QCOM', 'TXN', 'INTU', 'AMAT', 'MU', 'LRCX', 'NOW',
  'PANW', 'SNPS', 'CDNS', 'ADI', 'KLAC', 'ANET', 'APH', 'MSI', 'FTNT', 'PLTR',
  'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP', 'BLK', 'SCHW', 'USB',
  'PNC', 'TFC', 'COF', 'CB', 'CME', 'ICE', 'SPGI', 'MCO', 'AON', 'MMC',
  'LLY', 'JNJ', 'ABBV', 'MRK', 'PFE', 'ABT', 'TMO', 'DHR', 'AMGN', 'GILD',
  'ISRG', 'VRTX', 'REGN', 'BSX', 'SYK', 'MDT', 'ELV', 'CI', 'HCA', 'ZTS',
  'WMT', 'COST', 'HD', 'LOW', 'MCD', 'NKE', 'TJX', 'SBUX', 'TGT', 'BKNG',
  'MAR', 'CMG', 'ORLY', 'AZO', 'ROST', 'YUM', 'CL', 'PG', 'KO', 'PEP',
  'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PSX', 'VLO', 'OXY', 'FANG', 'KMI',
  'CAT', 'DE', 'GE', 'HON', 'ETN', 'PH', 'EMR', 'UPS', 'UNP', 'RTX',
  'LMT', 'NOC', 'GD', 'WM', 'CSX', 'NSC', 'FDX', 'MMM', 'ITW', 'CARR',
  'AMT', 'PLD', 'EQIX', 'PSA', 'SPG', 'O', 'CCI', 'DLR', 'WELL', 'AVB',
  'NEE', 'CEG', 'SO', 'DUK', 'AEP', 'SRE', 'VST', 'EXC', 'D', 'PEG',
  'TMUS', 'VZ', 'T', 'CMCSA', 'CHTR', 'DIS', 'NFLX', 'FOXA', 'EA', 'TTWO'
];

const COMPANY_NAMES = {
  // Technology
  AAPL: 'Apple Inc.', MSFT: 'Microsoft Corporation', GOOGL: 'Alphabet Inc.', AMZN: 'Amazon.com, Inc.',
  NVDA: 'Nvidia Corporation', META: 'Meta Platforms, Inc.', AVGO: 'Broadcom Inc.', ORCL: 'Oracle Corporation',
  CRM: 'Salesforce, Inc.', AMD: 'Advanced Micro Devices, Inc.', ADBE: 'Adobe Inc.', CSCO: 'Cisco Systems, Inc.',
  IBM: 'International Business Machines', QCOM: 'Qualcomm Inc.', TXN: 'Texas Instruments Inc.', INTU: 'Intuit Inc.',
  AMAT: 'Applied Materials, Inc.', MU: 'Micron Technology, Inc.', LRCX: 'Lam Research Corporation', NOW: 'ServiceNow, Inc.',
  PANW: 'Palo Alto Networks, Inc.', SNPS: 'Synopsys, Inc.', CDNS: 'Cadence Design Systems, Inc.', ADI: 'Analog Devices, Inc.',
  KLAC: 'KLA Corporation', ANET: 'Arista Networks, Inc.', APH: 'Amphenol Corporation', MSI: 'Motorola Solutions, Inc.',
  FTNT: 'Fortinet, Inc.', PLTR: 'Palantir Technologies Inc.',
  // Financials
  JPM: 'JPMorgan Chase & Co.', BAC: 'Bank of America Corporation', WFC: 'Wells Fargo & Company', GS: 'The Goldman Sachs Group',
  MS: 'Morgan Stanley', C: 'Citigroup Inc.', AXP: 'American Express Company', BLK: 'BlackRock, Inc.',
  SCHW: 'The Charles Schwab Corporation', USB: 'U.S. Bancorp', PNC: 'The PNC Financial Services Group', TFC: 'Truist Financial Corp',
  COF: 'Capital One Financial Corporation', CB: 'Chubb Limited', CME: 'CME Group Inc.', ICE: 'Intercontinental Exchange',
  SPGI: 'S&P Global Inc.', MCO: "Moody's Corporation", AON: 'Aon plc', MMC: 'Marsh & McLennan Companies',
  // Healthcare
  LLY: 'Eli Lilly and Company', JNJ: 'Johnson & Johnson', ABBV: 'AbbVie Inc.', MRK: 'Merck & Co., Inc.',
  PFE: 'Pfizer Inc.', ABT: 'Abbott Laboratories', TMO: 'Thermo Fisher Scientific', DHR: 'Danaher Corporation',
  AMGN: 'Amgen Inc.', GILD: 'Gilead Sciences, Inc.', ISRG: 'Intuitive Surgical, Inc.', VRTX: 'Vertex Pharmaceuticals',
  REGN: 'Regeneron Pharmaceuticals', BSX: 'Boston Scientific Corporation', SYK: 'Stryker Corporation', MDT: 'Medtronic plc',
  ELV: 'Elevance Health, Inc.', CI: 'The Cigna Group', HCA: 'HCA Healthcare, Inc.', ZTS: 'Zoetis Inc.',
  // Consumer
  WMT: 'Walmart Inc.', COST: 'Costco Wholesale Corporation', HD: 'The Home Depot, Inc.', LOW: "Lowe's Companies, Inc.",
  MCD: "McDonald's Corporation", NKE: 'NIKE, Inc.', TJX: 'The TJX Companies, Inc.', SBUX: 'Starbucks Corporation',
  TGT: 'Target Corporation', BKNG: 'Booking Holdings Inc.', MAR: 'Marriott International', CMG: 'Chipotle Mexican Grill',
  ORLY: "O'Reilly Automotive, Inc.", AZO: 'AutoZone, Inc.', ROST: 'Ross Stores, Inc.', YUM: 'Yum! Brands, Inc.',
  CL: 'Colgate-Palmolive Company', PG: 'The Procter & Gamble Company', KO: 'The Coca-Cola Company', PEP: 'PepsiCo, Inc.',
  // Energy
  XOM: 'Exxon Mobil Corporation', CVX: 'Chevron Corporation', COP: 'ConocoPhillips', SLB: 'SLB (Schlumberger)',
  EOG: 'EOG Resources, Inc.', PSX: 'Phillips 66', VLO: 'Valero Energy Corporation', OXY: 'Occidental Petroleum',
  FANG: 'Diamondback Energy, Inc.', KMI: 'Kinder Morgan, Inc.',
  // Industrials
  CAT: 'Caterpillar Inc.', DE: 'Deere & Company', GE: 'GE Aerospace', HON: 'Honeywell International Inc.',
  ETN: 'Eaton Corporation plc', PH: 'Parker-Hannifin Corporation', EMR: 'Emerson Electric Co.', UPS: 'United Parcel Service',
  UNP: 'Union Pacific Corporation', RTX: 'RTX Corporation', LMT: 'Lockheed Martin Corporation', NOC: 'Northrop Grumman',
  GD: 'General Dynamics Corporation', WM: 'Waste Management, Inc.', CSX: 'CSX Corporation', NSC: 'Norfolk Southern Corporation',
  FDX: 'FedEx Corporation', MMM: '3M Company', ITW: 'Illinois Tool Works Inc.', CARR: 'Carrier Global Corporation',
  // Real Estate
  AMT: 'American Tower Corporation', PLD: 'Prologis, Inc.', EQIX: 'Equinix, Inc.', PSA: 'Public Storage',
  SPG: 'Simon Property Group, Inc.', O: 'Realty Income Corporation', CCI: 'Crown Castle Inc.', DLR: 'Digital Realty Trust',
  WELL: 'Welltower Inc.', AVB: 'AvalonBay Communities, Inc.',
  // Utilities
  NEE: 'NextEra Energy, Inc.', CEG: 'Constellation Energy Corporation', SO: 'The Southern Company', DUK: 'Duke Energy Corporation',
  AEP: 'American Electric Power', SRE: 'Sempra', VST: 'Vistra Corp.', EXC: 'Exelon Corporation',
  D: 'Dominion Energy, Inc.', PEG: 'Public Service Enterprise Group',
  // Communication
  TMUS: 'T-Mobile US, Inc.', VZ: 'Verizon Communications Inc.', T: 'AT&T Inc.', CMCSA: 'Comcast Corporation',
  CHTR: 'Charter Communications', DIS: 'The Walt Disney Company', NFLX: 'Netflix, Inc.', FOXA: 'Fox Corporation',
  EA: 'Electronic Arts Inc.', TTWO: 'Take-Two Interactive Software'
};

/**
 * Deterministic pseudo-random generator based on ticker string
 */
const getTickerSeed = (ticker) => {
  let hash = 0;
  for (let i = 0; i < ticker.length; i++) {
    hash = ((hash << 5) - hash) + ticker.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash);
};

/**
 * Returns dynamic profile for any of the 150 tickers
 */
const getStockProfile = (ticker) => {
  const t = (ticker || 'NVDA').toUpperCase().trim();
  const seed = getTickerSeed(t);
  const name = COMPANY_NAMES[t] || `${t} Corporation`;

  // Deterministic realistic numbers
  const basePrice = Math.round((50 + (seed % 450) + ((seed % 100) * 0.45)) * 100) / 100;
  const volatility = Math.round((0.15 + ((seed % 20) * 0.01)) * 100) / 100;
  const dailyReturn = Math.round((((seed % 40) - 18) * 0.001) * 10000) / 10000;
  const return7d = Math.round((((seed % 60) - 20) * 0.0015) * 10000) / 10000;
  const return30d = Math.round((((seed % 100) - 30) * 0.002) * 10000) / 10000;
  const rsi = Math.round((42 + (seed % 28)) * 10) / 10;
  const momentum = Math.round((((seed % 30) - 10) * 0.35) * 100) / 100;
  const volume = Math.floor(15000000 + (seed % 50000000));

  // Prediction determination
  let prediction = 'HOLD';
  let conf = 0.72;
  let probs = { BUY: 0.20, HOLD: 0.72, WAIT: 0.08 };
  let sentScore = 0.15;
  let label = 'Neutral';

  if (dailyReturn > 0.005 && rsi > 52) {
    prediction = 'BUY';
    conf = Math.round((0.74 + ((seed % 15) * 0.01)) * 100) / 100;
    probs = { BUY: conf, HOLD: Math.round((1.0 - conf - 0.05) * 100) / 100, WAIT: 0.05 };
    sentScore = Math.round((0.25 + ((seed % 30) * 0.01)) * 100) / 100;
    label = 'Bullish';
  } else if (dailyReturn < -0.005 || rsi < 44) {
    prediction = 'WAIT';
    conf = Math.round((0.70 + ((seed % 15) * 0.01)) * 100) / 100;
    probs = { BUY: 0.06, HOLD: Math.round((1.0 - conf - 0.06) * 100) / 100, WAIT: conf };
    sentScore = Math.round((-0.20 - ((seed % 25) * 0.01)) * 100) / 100;
    label = 'Bearish';
  }

  const headlines = [
    {
      headline: `${name} demonstrates resilient quarterly revenue growth and market share gains`,
      sentiment: label === 'Bearish' ? 'neutral' : 'positive',
      positive_prob: label === 'Bearish' ? 0.20 : 0.82,
      neutral_prob: label === 'Bearish' ? 0.70 : 0.14,
      negative_prob: label === 'Bearish' ? 0.10 : 0.04,
      score: label === 'Bearish' ? 0.10 : 0.78,
      published_at: "Today 10:15 AM",
      url: `https://finance.yahoo.com/quote/${t}`
    },
    {
      headline: `Institutional investors adjust price targets for ${t} following strategic sector update`,
      sentiment: 'positive',
      positive_prob: 0.75,
      neutral_prob: 0.18,
      negative_prob: 0.07,
      score: 0.68,
      published_at: "Today 08:30 AM",
      url: `https://finance.yahoo.com/quote/${t}`
    },
    {
      headline: `Sector analysts evaluate operational cash flow and forward margin guidance for ${name}`,
      sentiment: label === 'Bearish' ? 'negative' : 'neutral',
      positive_prob: 0.15,
      neutral_prob: 0.65,
      negative_prob: 0.20,
      score: label === 'Bearish' ? -0.45 : 0.05,
      published_at: "Yesterday 04:00 PM",
      url: `https://finance.yahoo.com/quote/${t}`
    }
  ];

  return {
    ticker: t,
    name,
    basePrice,
    volatility,
    dailyReturn,
    return7d,
    return30d,
    rsi,
    momentum,
    volume,
    prediction,
    confidence: conf,
    probabilities: probs,
    sentimentScore: sentScore,
    sentimentLabel: label,
    headlines
  };
};

/**
 * Returns fallback technical snapshot for a ticker
 */
const getFallbackTechnicals = (ticker) => {
  const profile = getStockProfile(ticker);
  const close = profile.basePrice;
  const open = Math.round((close * (1 - profile.dailyReturn)) * 100) / 100;
  const high = Math.round((Math.max(open, close) * 1.012) * 100) / 100;
  const low = Math.round((Math.min(open, close) * 0.988) * 100) / 100;

  return {
    ticker: profile.ticker,
    company: profile.name,
    latest_close: close,
    open,
    high,
    low,
    volume: profile.volume,
    daily_return: profile.dailyReturn,
    return_7d: profile.return7d,
    return_30d: profile.return30d,
    sma_5: Math.round((close * 0.995) * 100) / 100,
    sma_10: Math.round((close * 0.990) * 100) / 100,
    sma_20: Math.round((close * 0.980) * 100) / 100,
    ema_5: Math.round((close * 0.997) * 100) / 100,
    ema_10: Math.round((close * 0.992) * 100) / 100,
    ema_20: Math.round((close * 0.985) * 100) / 100,
    rsi_14: profile.rsi,
    volatility_20: profile.volatility,
    momentum_10: profile.momentum,
    updated_at: new Date().toISOString(),
    is_fallback: true,
    _source: 'fallback_mock_service'
  };
};

/**
 * Returns historical candles and indicators for charting
 */
const getFallbackHistory = (ticker, period = '1y') => {
  const profile = getStockProfile(ticker);
  const daysMap = { '1mo': 22, '3mo': 65, '6mo': 128, '1y': 252, '2y': 504, '5y': 1260 };
  const count = daysMap[period] || 252;
  const base = profile.basePrice;

  const records = [];
  const now = new Date();
  let currentClose = base * 0.85;

  for (let i = count; i >= 0; i--) {
    const d = new Date(now);
    d.setDate(d.getDate() - i);
    if (d.getDay() === 0 || d.getDay() === 6) continue;

    const changePct = ((Math.sin(i * 0.3) * 0.015) + (Math.cos(i * 0.7) * 0.01) + 0.0008);
    currentClose = Math.max(10, currentClose * (1 + changePct));
    
    const open = Math.round(currentClose * (1 - (Math.random() * 0.008 - 0.004)) * 100) / 100;
    const close = Math.round(currentClose * 100) / 100;
    const high = Math.round(Math.max(open, close) * (1 + Math.random() * 0.008) * 100) / 100;
    const low = Math.round(Math.min(open, close) * (1 - Math.random() * 0.008) * 100) / 100;
    const volume = Math.floor(15000000 + Math.random() * 25000000);

    records.push({
      Date: d.toISOString().split('T')[0],
      Open: open,
      High: high,
      Low: low,
      Close: close,
      Volume: volume,
      SMA_20: Math.round(close * 0.985 * 100) / 100,
      EMA_20: Math.round(close * 0.990 * 100) / 100,
      RSI_14: Math.round((50 + Math.sin(i * 0.2) * 15) * 10) / 10
    });
  }

  if (records.length > 0) {
    records[records.length - 1].Close = profile.basePrice;
  }

  return {
    ticker: profile.ticker,
    period,
    count: records.length,
    data: records,
    is_fallback: true,
    _source: 'fallback_mock_service'
  };
};

/**
 * Returns latest technical indicators for target stocks
 */
const getFallbackUniverseTechnicals = (limit = 150) => {
  const snapshot = {};
  const targetList = TARGET_STOCKS.slice(0, limit);
  for (const ticker of targetList) {
    snapshot[ticker] = getFallbackTechnicals(ticker);
  }
  return snapshot;
};

/**
 * Returns recommendation prediction for a ticker
 */
const getFallbackPrediction = (ticker) => {
  const profile = getStockProfile(ticker);
  const tech = getFallbackTechnicals(profile.ticker);

  return {
    ticker: profile.ticker,
    company: profile.name,
    prediction: profile.prediction,
    confidence: profile.confidence,
    probabilities: profile.probabilities,
    technical_summary: {
      latest_close: tech.latest_close,
      daily_return: tech.daily_return,
      return_7d: tech.return_7d,
      return_30d: tech.return_30d,
      rsi_14: tech.rsi_14,
      volatility_20: tech.volatility_20,
      momentum_10: tech.momentum_10
    },
    sentiment_summary: {
      Sentiment_Score: profile.sentimentScore,
      News_Count: profile.headlines.length
    },
    model_version: 'xgboost_purged_walkforward_v1',
    evaluated_cv_accuracy: 0.742,
    _source: 'fallback_mock_service'
  };
};

/**
 * Returns universe recommendations for target tickers
 */
const getFallbackUniversePredictions = (limit = 150) => {
  const recs = {};
  const targetList = TARGET_STOCKS.slice(0, limit);
  for (const ticker of targetList) {
    recs[ticker] = getFallbackPrediction(ticker);
  }
  return recs;
};

/**
 * Returns news sentiment aggregate and scored headlines
 */
const getFallbackSentiment = (ticker, limit = 15) => {
  const profile = getStockProfile(ticker);
  const headlines = profile.headlines || [];
  const posCount = headlines.filter(h => h.sentiment === 'positive').length;
  const neuCount = headlines.filter(h => h.sentiment === 'neutral').length;
  const negCount = headlines.filter(h => h.sentiment === 'negative').length;

  return {
    ticker: profile.ticker,
    Sentiment_Score: profile.sentimentScore,
    News_Count: headlines.length,
    positive_count: posCount,
    neutral_count: neuCount,
    negative_count: negCount,
    sentiment_label: profile.sentimentLabel,
    headlines: headlines.slice(0, limit),
    _source: 'fallback_mock_service'
  };
};

/**
 * Returns universe sentiment for target tickers
 */
const getFallbackUniverseSentiment = (limit = 15, maxStocks = 150) => {
  const results = {};
  const targetList = TARGET_STOCKS.slice(0, maxStocks);
  for (const ticker of targetList) {
    results[ticker] = getFallbackSentiment(ticker, limit);
  }
  return results;
};

module.exports = {
  TARGET_STOCKS,
  COMPANY_NAMES,
  getStockProfile,
  getFallbackTechnicals,
  getFallbackHistory,
  getFallbackUniverseTechnicals,
  getFallbackPrediction,
  getFallbackUniversePredictions,
  getFallbackSentiment,
  getFallbackUniverseSentiment
};
