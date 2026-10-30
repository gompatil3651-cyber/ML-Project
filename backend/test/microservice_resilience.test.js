const { describe, it, before, after } = require('node:test');
const assert = require('node:assert');
const http = require('node:http');
const mongoose = require('mongoose');

// Ensure test environment is set
process.env.NODE_ENV = 'test';
// Point to non-existent port to guarantee microservice is OFF during testing
process.env.PYTHON_SERVICE_URL = 'http://127.0.0.1:59999';

const { app } = require('../src/server');

let testServer;
let baseUrl;

const request = (path, method = 'GET', body = null) => {
  return new Promise((resolve, reject) => {
    const url = new URL(path, baseUrl);
    const options = {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
    };

    const req = http.request(url, options, (res) => {
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          resolve({ status: res.statusCode, body: parsed });
        } catch {
          resolve({ status: res.statusCode, body: data });
        }
      });
    });

    req.on('error', reject);

    if (body) {
      req.write(JSON.stringify(body));
    }
    req.end();
  });
};

describe('Microservice Offline Resilience Tests', () => {
  before(async () => {
    await new Promise((resolve) => {
      testServer = app.listen(0, () => {
        const port = testServer.address().port;
        baseUrl = `http://127.0.0.1:${port}`;
        resolve();
      });
    });
  });

  after(async () => {
    if (testServer) {
      await new Promise((resolve) => testServer.close(resolve));
    }
    await mongoose.disconnect();
  });

  it('Health Check: gracefully handles offline microservice with 200 OK and OFFLINE_FALLBACK status', async () => {
    const res = await request('/health');
    assert.strictEqual(res.status, 200);
    assert.strictEqual(res.body.status, 'UP');
    assert.ok(res.body.python_microservice);
    assert.strictEqual(res.body.python_microservice.status, 'OFFLINE_FALLBACK');
    assert.strictEqual(res.body.resilient_mode.fallback_active, true);
    assert.strictEqual(res.body.resilient_mode.target_stocks_count, 150);
  });

  it('Root Endpoint: lists all service endpoints including news and health', async () => {
    const res = await request('/');
    assert.strictEqual(res.status, 200);
    assert.strictEqual(res.body.project, 'Stock Insight Backend API');
    assert.ok(res.body.endpoints.stocks);
    assert.ok(res.body.endpoints.predictions);
    assert.ok(res.body.endpoints.news);
  });

  it('Stock Technicals: returns valid indicators for NVDA when microservice is off', async () => {
    const res = await request('/api/stocks/NVDA/technicals');
    assert.strictEqual(res.status, 200);
    assert.strictEqual(res.body.success, true);
    assert.ok(res.body.data);
    assert.strictEqual(res.body.data.ticker, 'NVDA');
    assert.ok(typeof res.body.data.latest_close === 'number');
    assert.ok(typeof res.body.data.rsi_14 === 'number');
    assert.ok(typeof res.body.data.sma_20 === 'number');
    assert.ok(typeof res.body.data.volatility_20 === 'number');
  });

  it('Stock History: returns valid historical candle records for AAPL when microservice is off', async () => {
    const res = await request('/api/stocks/AAPL/history?period=1mo');
    assert.strictEqual(res.status, 200);
    assert.strictEqual(res.body.success, true);
    assert.ok(res.body.data);
    assert.strictEqual(res.body.data.ticker, 'AAPL');
    assert.ok(Array.isArray(res.body.data.data));
    assert.ok(res.body.data.data.length > 0);
    const candle = res.body.data.data[0];
    assert.ok(candle.Date);
    assert.ok(typeof candle.Close === 'number');
    assert.ok(typeof candle.Volume === 'number');
  });

  it('Stock Universe: returns technical snapshot for all 5 target tickers', async () => {
    const res = await request('/api/stocks/universe');
    assert.strictEqual(res.status, 200);
    assert.strictEqual(res.body.success, true);
    assert.ok(res.body.universe);
    for (const sym of ['AMZN', 'GOOGL', 'AAPL', 'NVDA', 'MSFT']) {
      assert.ok(res.body.universe[sym], `Missing ${sym} in universe snapshot`);
      assert.ok(res.body.universe[sym].latest_close > 0);
    }
  });

  it('Predictions: returns BUY/HOLD/WAIT recommendation for MSFT when microservice is off', async () => {
    const res = await request('/api/predictions/MSFT');
    assert.strictEqual(res.status, 200);
    assert.strictEqual(res.body.success, true);
    assert.ok(res.body.data);
    assert.strictEqual(res.body.data.ticker, 'MSFT');
    assert.ok(['BUY', 'HOLD', 'WAIT'].includes(res.body.data.prediction));
    assert.ok(typeof res.body.data.confidence === 'number');
    assert.ok(res.body.data.probabilities.BUY !== undefined);
    assert.ok(res.body.data.probabilities.HOLD !== undefined);
    assert.ok(res.body.data.probabilities.WAIT !== undefined);
  });

  it('Universe Predictions: returns recommendations across all target tickers', async () => {
    const res = await request('/api/predictions/universe');
    assert.strictEqual(res.status, 200);
    assert.strictEqual(res.body.success, true);
    assert.ok(res.body.data);
    for (const sym of ['AMZN', 'GOOGL', 'AAPL', 'NVDA', 'MSFT']) {
      assert.ok(res.body.data[sym], `Missing ${sym} in universe predictions`);
      assert.ok(['BUY', 'HOLD', 'WAIT'].includes(res.body.data[sym].prediction));
    }
  });

  it('News Sentiment: returns scored headlines and sentiment metrics for AMZN', async () => {
    const res = await request('/api/news/AMZN?limit=10');
    assert.strictEqual(res.status, 200);
    assert.strictEqual(res.body.success, true);
    assert.ok(res.body.data);
    assert.strictEqual(res.body.data.ticker, 'AMZN');
    assert.ok(typeof res.body.data.Sentiment_Score === 'number');
    assert.ok(['Bullish', 'Neutral', 'Bearish'].includes(res.body.data.sentiment_label));
    assert.ok(Array.isArray(res.body.data.headlines));
  });

  it('Universe News: returns sentiment across all 5 target tickers', async () => {
    const res = await request('/api/news/universe');
    assert.strictEqual(res.status, 200);
    assert.strictEqual(res.body.success, true);
    assert.ok(res.body.data);
    for (const sym of ['AMZN', 'GOOGL', 'AAPL', 'NVDA', 'MSFT']) {
      assert.ok(res.body.data[sym], `Missing ${sym} in universe news`);
      assert.ok(typeof res.body.data[sym].Sentiment_Score === 'number');
    }
  });

  it('Target Universe Integrity: scaled 150 universe works across sectors (Tech, Fin, Health, Energy, Consumer, etc.)', async () => {
    const crossSectorSample = ['NVDA', 'META', 'JPM', 'GS', 'LLY', 'WMT', 'XOM', 'CAT', 'AMT', 'NEE', 'DIS'];
    for (const ticker of crossSectorSample) {
      const techRes = await request(`/api/stocks/${ticker}/technicals`);
      assert.strictEqual(techRes.status, 200);
      assert.strictEqual(techRes.body.data.ticker, ticker);

      const predRes = await request(`/api/predictions/${ticker}`);
      assert.strictEqual(predRes.status, 200);
      assert.strictEqual(predRes.body.data.ticker, ticker);
      assert.ok(['BUY', 'HOLD', 'WAIT'].includes(predRes.body.data.prediction));
    }
  });
});
