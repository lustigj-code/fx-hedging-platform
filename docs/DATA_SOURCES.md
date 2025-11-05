# Data Sources: Exchange Rates and Market Data

This document explains the exchange rate and market data providers used by the FX Hedging Platform, including free options for development and paid options for production.

---

## Current Implementation (Development/MVP)

### Primary: ExchangeRate-API.com

**Status**: ✅ Fully Implemented

**Website**: https://www.exchangerate-api.com/

**Pricing**:
- Free Tier: 1,500 requests/month
- Paid Tier: $9-49/month for up to 100,000 requests

**Features**:
- 161 currencies supported
- Daily updates (free tier)
- Historical data (paid tier)
- JSON API
- No authentication required for basic use

**API Endpoints**:
```
GET https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{BASE}/{QUOTE}
GET https://v6.exchangerate-api.com/v6/{API_KEY}/history/{BASE}/{YEAR}/{MONTH}/{DAY}
```

**Example Request**:
```bash
curl https://v6.exchangerate-api.com/v6/YOUR_API_KEY/pair/USD/MXN
```

**Response**:
```json
{
    "result": "success",
    "base_code": "USD",
    "target_code": "MXN",
    "conversion_rate": 19.2340,
    "time_last_update_utc": "Mon, 04 Mar 2024 00:00:01 +0000"
}
```

**Usage in Platform**:
- Primary source for real-time FX rates
- Automatic caching (1 hour)
- Fallback to database if API unavailable

**Configuration**:
```bash
# .env
EXCHANGERATE_API_KEY=your_key_here
```

---

## Fallback Sources

### 1. Open Exchange Rates

**Status**: ⚙️ Implemented (Fallback)

**Website**: https://openexchangerates.org/

**Pricing**:
- Free Tier: 1,000 requests/month, hourly updates
- Paid Tier: $12-97/month

**Features**:
- 170+ currencies
- Historical data (paid)
- Time-series API
- Currency conversion

**Configuration**:
```bash
# .env
OPENEXCHANGERATES_API_KEY=your_key_here
```

**When Used**: If ExchangeRate-API.com fails or rate limit exceeded

---

### 2. European Central Bank (ECB)

**Status**: ⚙️ Implemented (EUR pairs)

**Website**: https://www.ecb.europa.eu/stats/eurofxref/

**Pricing**: Free

**Features**:
- Official rates published by ECB
- Daily updates
- EUR as base currency
- Last 90 days of history (free XML feed)
- Highly reliable

**API Endpoints**:
```
https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml
https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml
```

**Example XML Structure**:
```xml
<Cube>
    <Cube time="2024-03-04">
        <Cube currency="USD" rate="1.0845"/>
        <Cube currency="MXN" rate="20.3912"/>
        <Cube currency="BRL" rate="5.4123"/>
    </Cube>
</Cube>
```

**When Used**:
- EUR-based currency pairs
- Cross-rate calculations
- Validation of other sources

---

## Production-Grade Sources (Recommended for Scale)

### 3. Bloomberg Terminal

**Status**: 📝 Stub Implemented (For Future)

**Website**: https://www.bloomberg.com/professional/

**Pricing**: ~$2,000/month per terminal (~$24,000/year)

**Features**:
- Real-time FX rates (millisecond updates)
- Implied volatility surfaces
- Government bond yields (for risk-free rates)
- Historical data (decades of history)
- FX forwards, swaps, NDFs
- News and analysis
- Industry standard

**Data Quality**: ⭐⭐⭐⭐⭐ (Best in industry)

**Implementation Requirements**:
1. Bloomberg Terminal license
2. Terminal installed on server/workstation
3. `blpapi` Python library
4. Authentication via Terminal login

**Example Tickers**:
- Spot Rate: `USDMXN Curncy`
- 1M Implied Vol: `USDMXN1M BGN Curncy`
- 3M Implied Vol: `USDMXN3M BGN Curncy`
- MXN 10Y Rate: `MBONO 10Y Govt`
- USD 10Y Rate: `USGG10YR Index`

**When to Upgrade**:
- Managing >$100M notional
- Need real-time pricing
- Require implied volatility
- Institutional clients

**Installation**:
```bash
pip install blpapi
```

**Sample Code**:
```python
import blpapi

session = blpapi.Session()
session.start()
session.openService("//blp/refdata")

# Request spot rate
request = session.createRequest("ReferenceDataRequest")
request.append("securities", "USDMXN Curncy")
request.append("fields", "PX_LAST")

session.sendRequest(request)
```

---

### 4. Refinitiv (formerly Thomson Reuters)

**Status**: 🔮 Planned

**Website**: https://www.refinitiv.com/

**Pricing**: ~$1,200-1,500/month (~$15,000-18,000/year)

**Features**:
- Real-time and historical FX data
- Datastream for historical analysis
- Eikon platform
- Similar quality to Bloomberg
- Strong in fixed income and FX

**Advantage over Bloomberg**: ~40% cheaper

**When to Consider**: Cost-sensitive alternative to Bloomberg

---

### 5. Currency Cloud / Wise API

**Status**: 🔮 Under Evaluation

**Website**:
- https://www.currencycloud.com/
- https://wise.com/business/api

**Pricing**: Pay-per-transaction (0.1-0.5% of notional)

**Features**:
- Real FX execution (not just data)
- Multi-currency accounts
- API-first design
- Good for FinTech integration

**Use Case**: Combine data + execution in one platform

---

## Volatility Data

### Current: Historical Volatility (90-day)

**Method**: Calculate from historical spot rates

**Formula**:
```python
log_returns = np.log(rates[1:] / rates[:-1])
daily_volatility = np.std(log_returns)
annualized_volatility = daily_volatility * np.sqrt(252)
```

**Pros**:
- Free
- Easy to calculate
- No external dependency

**Cons**:
- Backward-looking (not forward-looking)
- May not reflect current market conditions
- Slower to react to regime changes

---

### Future: Implied Volatility (Market-Based)

**Source**: Bloomberg, Refinitiv, or specialized providers

**Why Better**:
- Forward-looking (reflects market's expectation)
- More accurate for pricing
- Reacts immediately to market events
- Varies by maturity (volatility surface)

**Bloomberg Tickers**:
- 1W: `USDMXN1W BGN Curncy`
- 1M: `USDMXN1M BGN Curncy`
- 3M: `USDMXN3M BGN Curncy`
- 6M: `USDMXN6M BGN Curncy`
- 1Y: `USDMXN1Y BGN Curncy`

**Example**:
```python
# Instead of calculating historical vol
volatility = await volatility_service.calculate_historical_volatility(...)

# Fetch implied vol from Bloomberg
volatility = await bloomberg_provider.get_implied_volatility("USD", "MXN", maturity_days=90)
```

---

## Risk-Free Rates

### Current: Static Configuration

**Source**: Manual entry in `config.py`

**Update Frequency**: Quarterly or as needed

**Current Values** (as of Q1 2024):
```python
DEFAULT_RISK_FREE_RATES = {
    "USD": 0.0450,  # 4.50%
    "EUR": 0.0300,  # 3.00%
    "GBP": 0.0420,  # 4.20%
    "MXN": 0.0900,  # 9.00%
    "COP": 0.1100,  # 11.00%
    "BRL": 0.1150,  # 11.50%
    # ...
}
```

**Pros**:
- Simple
- No API dependency
- Rates don't change daily

**Cons**:
- Manual updates required
- Not market-accurate
- Stale during rate volatility

---

### Future: Real-Time Government Bond Yields

**Source**: Bloomberg or Refinitiv

**Tickers** (10-year benchmarks):
- USD: `USGG10YR Index` (US Treasury)
- EUR: `GTDEM10Y Govt` (German Bund)
- GBP: `GUKG10 Govt` (UK Gilt)
- MXN: `MBONO 10Y Govt` (Mexican Bonos)
- BRL: `GEBR10YR Govt` (Brazil)

**Implementation**:
```python
# Instead of static config
domestic_rate = settings.DEFAULT_RISK_FREE_RATES.get(quote_currency)

# Fetch real-time yield
domestic_rate = await bloomberg_provider.get_risk_free_rate(quote_currency, maturity_years=10)
```

---

## Data Flow Architecture

```
┌─────────────────────────────────────┐
│     Client Request (Calculate      │
│         Option Price)               │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   1. Fetch Spot Rate                │
│   ┌─────────────────────────────┐   │
│   │ Try: ExchangeRate-API.com   │   │
│   │ Fallback: OpenExchangeRates │   │
│   │ Fallback: Database Cache    │   │
│   └─────────────────────────────┘   │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   2. Fetch Historical Rates         │
│   (for volatility calculation)      │
│   ┌─────────────────────────────┐   │
│   │ Try: ExchangeRate-API.com   │   │
│   │ Fallback: ECB (EUR pairs)   │   │
│   │ Fallback: Database          │   │
│   └─────────────────────────────┘   │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   3. Calculate Volatility           │
│   ┌─────────────────────────────┐   │
│   │ Compute 90-day historical   │   │
│   │ Cache for 24 hours          │   │
│   └─────────────────────────────┘   │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   4. Get Risk-Free Rates            │
│   ┌─────────────────────────────┐   │
│   │ Current: Static config      │   │
│   │ Future: Bloomberg bonds     │   │
│   └─────────────────────────────┘   │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   5. Calculate Option Price         │
│   (Garman-Kohlhagen Formula)        │
└─────────────────────────────────────┘
```

---

## Cost Analysis

### Development/MVP (Current Setup)

| Provider | Cost/Month | Requests | Coverage |
|----------|------------|----------|----------|
| ExchangeRate-API | $0 (Free) | 1,500 | Primary |
| Open Exchange Rates | $0 (Free) | 1,000 | Fallback |
| ECB | Free | Unlimited | EUR pairs |
| **Total** | **$0** | **2,500** | **Good** |

**Suitable for**:
- Development
- MVP / Pilot (up to 50 clients)
- <$10M monthly notional

---

### Production (Recommended for Scale)

| Provider | Cost/Month | Features | Use Case |
|----------|------------|----------|----------|
| ExchangeRate-API (Paid) | $49 | 100K req/mo | Spot rates |
| Bloomberg Terminal | $2,000 | Real-time, implied vol | Full suite |
| OR Refinitiv | $1,500 | Real-time, implied vol | Cost-effective alternative |
| **Total (Bloomberg)** | **$2,049** | **Production-grade** | **>$100M notional** |
| **Total (Refinitiv)** | **$1,549** | **Production-grade** | **>$50M notional** |

**Suitable for**:
- Post-Series A
- >100 clients
- >$100M monthly notional
- Institutional clients

---

## Upgrade Path

### Phase 1: MVP (Current) ✅
- Free APIs only
- Historical volatility
- Static risk-free rates
- Suitable for pilot

### Phase 2: Growth ($49/mo)
- Paid ExchangeRate-API
- More reliable
- Higher rate limits
- Historical data access

### Phase 3: Scale ($1,500-2,000/mo)
- Bloomberg OR Refinitiv
- Implied volatility
- Real-time rates
- Professional-grade

### Phase 4: Enterprise (Custom)
- Multiple Bloomberg terminals
- Proprietary data sources
- Direct broker feeds
- Redundancy and failover

---

## API Key Management

### Getting API Keys

1. **ExchangeRate-API**:
   - Visit https://www.exchangerate-api.com/
   - Sign up (free)
   - Copy API key from dashboard

2. **Open Exchange Rates**:
   - Visit https://openexchangerates.org/signup
   - Sign up (free tier available)
   - Get App ID

3. **Bloomberg**:
   - Contact Bloomberg sales
   - Purchase Terminal license
   - Authenticate via Terminal login (no API key needed)

### Configuration

Add to `.env`:
```bash
# Primary
EXCHANGERATE_API_KEY=abc123def456

# Fallback
OPENEXCHANGERATES_API_KEY=xyz789uvw321

# Future
BLOOMBERG_API_KEY=your_terminal_id
```

### Security

- ✅ Never commit API keys to Git
- ✅ Use `.env` files (in `.gitignore`)
- ✅ Rotate keys every 90 days
- ✅ Use different keys for dev/staging/prod
- ✅ Monitor usage for anomalies

---

## Monitoring and Alerts

### Recommended Monitoring

1. **API Health**:
   ```python
   @app.get("/api/data-sources/health")
   async def data_sources_health():
       return {
           "exchangerate_api": await provider1.health_check(),
           "open_exchange_rates": await provider2.health_check(),
           "ecb": await provider3.health_check(),
       }
   ```

2. **Rate Limit Tracking**:
   - Log every API request
   - Alert at 80% of limit
   - Auto-failover to backup source

3. **Data Quality**:
   - Compare rates across sources
   - Alert if difference >1%
   - Flag stale data (>24 hours old)

4. **Cost Tracking**:
   - Monitor requests/month
   - Project costs
   - Alert if approaching limits

---

## Frequently Asked Questions

### Q: Can I use free APIs in production?

**A**: For pilot/MVP with <50 clients, yes. For serious scale (>100 clients, >$50M notional), upgrade to Bloomberg/Refinitiv.

### Q: How accurate are free exchange rates?

**A**: Very accurate for major pairs (USD, EUR). May have slight delays (hourly vs. real-time). Good enough for pricing options with multi-day maturities.

### Q: What if the API goes down?

**A**: We have:
1. Database caching (1 hour for rates, 24 hours for volatility)
2. Multiple fallback providers
3. Graceful degradation (use last known rates)

### Q: Should I use historical or implied volatility?

**A**:
- **Historical**: Free, good for MVP, backward-looking
- **Implied**: Paid (Bloomberg), better for pricing, forward-looking
- **Recommendation**: Start historical, upgrade to implied when revenue justifies Bloomberg cost

### Q: How often should I update risk-free rates?

**A**:
- **Static config**: Quarterly
- **Bloomberg real-time**: Daily
- **Impact on pricing**: Moderate (changing from 4.5% to 5.0% might change option price by ~5-10%)

---

## Support

For data source issues:
- Check API status pages
- Review logs: `docker-compose logs -f backend | grep "exchange_rate"`
- Contact support: data@fxhedging.com

Bloomberg setup assistance: bloomberg@fxhedging.com
