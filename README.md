# FX Hedging Platform
### Corporate Foreign Exchange Risk Management System

**Limit FX losses to 5% for less than 2% upfront cost**

A production-ready proof-of-concept FX hedging platform for medium-sized import/export businesses in Latin America. Built with FastAPI (Python), React (TypeScript), and powered by the Garman-Kohlhagen option pricing model.

---

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- (Optional) Node.js 20+ and Python 3.11+ for local development

### One-Command Startup

```bash
docker-compose up
```

The platform will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### First-Time Setup

1. **Seed currencies** (run once):
   ```bash
   curl -X POST http://localhost:8000/api/demo/seed-currencies
   ```

2. **Generate demo data**:
   ```bash
   curl -X POST http://localhost:8000/api/demo/generate
   ```

Or use the "Demo" tab in the web interface!

---

## 📊 Business Value Proposition

### Problem
Medium-sized firms (10-50M revenue) don't hedge FX risk due to:
- High costs (fees + collateral requirements)
- Mental bandwidth (complex financial products)
- Fear of regrets (locked-in rates)
- Inadequate products (banks focus on large corporates)

### Solution
- **5% Protection**: Limit maximum loss to 5% of invoiced contracts
- **<2% Cost**: Pay less than 2% upfront (no margin requirements for clients)
- **Keep the Upside**: If exchange rate moves favorably, you still benefit
- **Simple Interface**: Automatically detect foreign currency transactions from accounting software

### Target Market
- **Initial**: Latin America (Mexico, Colombia, Brazil, Chile, Peru, Argentina, Uruguay)
- **Expansion**: Africa, Asia, Eastern Europe, ANZ
- **Focus**: SMEs responsible for ~10% of international trade

---

## 🧮 Technology: Garman-Kohlhagen Formula

The platform uses the **Garman-Kohlhagen model**, the industry standard for FX option pricing.

### Formula
For a call option (importer protection):

```
C = e^(-r_f·T) · S · N(d1) - K · e^(-r_d·T) · N(d2)

where:
d1 = [ln(S·e^(-r_f·T) / K·e^(-r_d·T))] / (σ·√T) + (σ·√T)/2
d2 = d1 - σ·√T
```

**Parameters**:
- S = Current spot rate (e.g., 19 MXN/USD)
- K = Strike price (e.g., 19.95 for 5% protection)
- T = Time to maturity in years (e.g., 0.25 for 90 days)
- σ = Volatility (e.g., 0.20 for 20% annual)
- r_d = Domestic risk-free rate
- r_f = Foreign risk-free rate
- N(x) = Cumulative standard normal distribution

### Test Case Validation
**Input**: S=19, K=19.95, T=0.25, σ=0.20, r_d=0.04, r_f=0.07
**Output**: Call price ≈ 0.343 MXN per USD (~1.8% of notional) ✅

---

## 🏗️ Architecture

```
fx-hedging-platform/
├── backend/               # FastAPI Python backend
│   ├── app/
│   │   ├── models/       # SQLAlchemy database models
│   │   ├── schemas/      # Pydantic validation schemas
│   │   ├── routers/      # API endpoints
│   │   ├── services/     # Business logic
│   │   │   ├── pricing_engine.py      # Garman-Kohlhagen implementation
│   │   │   ├── exchange_rate_service.py
│   │   │   ├── volatility_service.py
│   │   │   └── portfolio_service.py
│   │   └── data_providers/  # Exchange rate APIs
│   └── tests/            # Unit tests
├── frontend/             # React TypeScript frontend
│   └── src/
│       ├── components/   # UI components
│       ├── services/     # API client
│       └── App.tsx       # Main application
├── docs/                 # Documentation
└── docker-compose.yml    # Docker orchestration
```

---

## 📡 API Endpoints

### Core Features

**Exchange Rates**
- `GET /api/rates/current?base=USD&quote=MXN` - Get current rate
- `GET /api/rates/historical` - Historical rates for volatility calculation
- `POST /api/rates/refresh` - Force refresh from API

**Volatility**
- `GET /api/volatility/{currency_pair}` - Get annualized volatility
- `POST /api/volatility/calculate` - Recalculate volatility

**Transactions**
- `GET /api/transactions/` - List all transactions
- `POST /api/transactions/` - Create new transaction
- `POST /api/transactions/upload` - Bulk upload (Odoo integration ready)

**Pricing** (THE CORE!)
- `POST /api/pricing/calculate` - Calculate option price with full analytics
- `POST /api/pricing/calculate-auto` - Auto-fetch rates and calculate

**Hedges**
- `GET /api/hedges/` - List all hedges
- `POST /api/hedges/` - Create/purchase hedge

**Portfolio**
- `GET /api/portfolio/summary` - Comprehensive portfolio analytics
- `GET /api/portfolio/exposures` - Exposures by currency
- `GET /api/portfolio/netting-opportunities` - Natural hedges

**Demo**
- `POST /api/demo/seed-currencies` - Seed currency database
- `POST /api/demo/generate` - Generate sample Latin America transactions
- `POST /api/demo/reset` - Clear demo data

Full interactive documentation: http://localhost:8000/docs

---

## 🎯 Key Features

### ✅ Implemented

1. **Garman-Kohlhagen Pricing Engine**
   - Exact formula implementation with unit tests
   - Greeks calculation (Delta, Gamma, Vega, Theta)
   - Scenario analysis
   - Payoff curve generation

2. **Exchange Rate Integration**
   - exchangerate-api.com (1,500 free requests/month)
   - Caching and fallback mechanisms
   - Upgrade path to Bloomberg/Refinitiv

3. **Volatility Calculation**
   - 90-day historical volatility (annualized)
   - Log returns method with √252 convention

4. **Transaction Management**
   - Manual entry
   - Bulk upload (CSV/JSON)
   - Odoo integration hooks

5. **Portfolio Analytics**
   - Multi-transaction aggregation
   - Netting opportunities identification
   - Exposure breakdown by currency

6. **Demo Mode**
   - 8 realistic Latin America scenarios
   - Pre-seeded currencies with risk-free rates
   - One-click data generation

### 🔮 Upgrade Path

1. **Paid Data Sources**
   - Bloomberg API (implied volatility, real-time rates)
   - Refinitiv/Datastream

2. **Advanced Visualizations**
   - Risk histogram with Monte Carlo simulation
   - Interactive payoff diagrams (Recharts)
   - Heatmaps for multi-currency exposure

3. **Accounting Integrations**
   - Odoo connector (parser ready)
   - Contpaqi (Mexico)
   - Siigo (Colombia)
   - QuickBooks, SAP, Oracle, Microsoft Dynamics

4. **Production Features**
   - Real broker integration
   - Margin posting automation
   - Compliance and reporting

---

## 🧪 Testing

### Run Unit Tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

### Critical Test: Garman-Kohlhagen Formula

```bash
pytest tests/test_pricing_engine.py::TestGarmanKohlhagenPricer::test_exact_formula_reference_case -v
```

This validates the pricing engine against the exact reference case from the spec.

---

## 🛠️ Development

### Backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Exchange Rate API (get free key at exchangerate-api.com)
EXCHANGERATE_API_KEY=your_key_here

# Database (SQLite for dev, PostgreSQL for production)
DATABASE_URL=sqlite+aiosqlite:///./fx_hedging.db
```

---

## 📈 Example Use Case

### Mexican Importer Scenario

**Company**: Mexican manufacturer importing $1,000,000 USD machinery
**Payment Due**: 90 days from invoice
**Current Spot**: 19.00 MXN/USD
**Fear**: USD appreciates to 20+ MXN/USD

**Solution**: Purchase USD call option
- **Strike Price**: 19.95 MXN/USD (5% protection)
- **Option Cost**: ~343,000 MXN (1.8% of notional)
- **Maximum Cost**: 19.95M MXN (vs potentially 20M+ unhedged)
- **If USD drops**: Still buy at favorable spot rate, only lose the premium

**Outcome**: Limited downside, unlimited upside, affordable cost!

---

## 📚 Documentation

- [BUSINESS_CONTEXT.md](docs/BUSINESS_CONTEXT.md) - Detailed problem/solution analysis
- [TECHNICAL_ARCHITECTURE.md](docs/TECHNICAL_ARCHITECTURE.md) - System design
- [API_REFERENCE.md](docs/API_REFERENCE.md) - Complete API documentation
- [INTEGRATION_GUIDE.md](docs/INTEGRATION_GUIDE.md) - Odoo and accounting software
- [DEPLOYMENT.md](docs/DEPLOYMENT.md) - Production deployment guide
- [USER_GUIDE.md](docs/USER_GUIDE.md) - Step-by-step usage instructions
- [DATA_SOURCES.md](docs/DATA_SOURCES.md) - Exchange rate providers

---

## 🌍 Supported Currencies

**Major Currencies**: USD, EUR, GBP, JPY, CNY

**Latin America**:
- 🇲🇽 MXN (Mexican Peso)
- 🇨🇴 COP (Colombian Peso)
- 🇧🇷 BRL (Brazilian Real)
- 🇨🇱 CLP (Chilean Peso)
- 🇵🇪 PEN (Peruvian Sol)
- 🇦🇷 ARS (Argentine Peso)
- 🇺🇾 UYU (Uruguayan Peso)

Currency-agnostic design ready for global expansion!

---

## 💼 For Investors

This proof-of-concept demonstrates:

✅ **Technical Feasibility**: Working implementation of industry-standard pricing model
✅ **Market Understanding**: Solves real pain points for SMEs
✅ **Scalability**: Currency-agnostic, integration-ready architecture
✅ **Cost Effectiveness**: Target <2% pricing achievable in most market conditions
✅ **Production Readiness**: Docker deployment, comprehensive API, extensible design

**Next Steps**:
1. Pilot program with 5-10 Mexican/Colombian SMEs
2. Integrate with Odoo (dominant in LatAm)
3. Establish banking relationships for actual option execution
4. Scale to other LatAm countries, then globally

---

## 📄 License

Proprietary - Corporate FX Hedging Platform v1.0.0

---

## 👥 Contact

For investor inquiries and pilot program participation:
[Contact Information]

---

**Built with**: FastAPI • React • TypeScript • Tailwind CSS • Recharts • SQLAlchemy • Pydantic • NumPy • SciPy • Docker

**Powered by**: Garman-Kohlhagen FX Option Pricing Model (1983)
