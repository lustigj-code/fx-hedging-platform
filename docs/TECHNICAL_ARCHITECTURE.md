# Technical Architecture

## System Overview

The FX Hedging Platform is a full-stack web application built with modern, scalable technologies:

- **Backend**: FastAPI (Python 3.11+) with async/await
- **Frontend**: React 18 + TypeScript + Tailwind CSS
- **Database**: SQLite (dev) / PostgreSQL (production)
- **Deployment**: Docker + docker-compose
- **API**: RESTful, fully documented with OpenAPI/Swagger

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│  React Frontend (Port 3000)                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Transaction  │  │   Pricing    │  │  Dashboard   │         │
│  │     Form     │  │   Results    │  │   Analytics  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  API Client (Axios)                                            │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS/JSON
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI Backend (Port 8000)                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                     API ROUTERS                         │   │
│  │  /rates  /volatility  /transactions  /pricing          │   │
│  │  /hedges  /portfolio  /integrations  /demo             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                         │                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   BUSINESS LOGIC                        │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │Pricing Engine│  │  Exchange    │  │  Portfolio   │  │   │
│  │  │(Garman-      │  │  Rate        │  │  Service     │  │   │
│  │  │Kohlhagen)    │  │  Service     │  │              │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │ Volatility   │  │ Integration  │  │     Demo     │  │   │
│  │  │  Service     │  │   Service    │  │   Service    │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DATA LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│  SQLAlchemy ORM                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │Currencies│ │ExchRates │ │Volatility│ │Transaction│          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│  ┌──────────┐ ┌──────────┐                                    │
│  │  Hedges  │ │Portfolio │                                    │
│  └──────────┘ └──────────┘                                    │
│                                                                │
│  SQLite (Dev) / PostgreSQL (Prod)                             │
└────────────────────────┬───────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────────┐
│                   EXTERNAL INTEGRATIONS                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ExchangeRate  │  │     Odoo     │  │  QuickBooks  │         │
│  │    API       │  │     ERP      │  │   (Future)   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐                           │
│  │     ECB      │  │  Bloomberg   │                           │
│  │     API      │  │   (Future)   │                           │
│  └──────────────┘  └──────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
```

## Backend Architecture

### Core Components

**1. API Routers** (`app/routers/`)
- Thin controllers that handle HTTP requests/responses
- Input validation via Pydantic schemas
- Delegate business logic to services
- Return structured JSON responses

**2. Services** (`app/services/`)
- **Pricing Engine**: Garman-Kohlhagen formula implementation
- **Exchange Rate Service**: Fetch and cache exchange rates
- **Volatility Service**: Calculate historical volatility
- **Portfolio Service**: Aggregate positions and analytics
- **Integration Service**: Parse Odoo/accounting data
- **Demo Service**: Generate sample data

**3. Models** (`app/models/`)
- SQLAlchemy ORM models
- Database table definitions
- Relationships and constraints

**4. Schemas** (`app/schemas/`)
- Pydantic models for request/response validation
- Type safety and automatic documentation
- Data transformation and serialization

**5. Data Providers** (`app/data_providers/`)
- Abstract interface for exchange rate sources
- Implementations: ExchangeRate-API, OpenExchangeRates, ECB, Bloomberg
- Easy to add new providers

### Request Flow Example

```python
# User Request: POST /api/pricing/calculate
#
# 1. Router receives request (app/routers/pricing.py)
@router.post("/calculate")
async def calculate_pricing(request: PricingRequest):

    # 2. Service processes (app/services/pricing_engine.py)
    result = pricer.price_with_analytics(
        spot_rate=request.spot_rate,
        strike_price=request.strike_price,
        # ...
    )

    # 3. Return validated response (app/schemas/pricing.py)
    return PricingResponse(**result)
```

## Database Schema

### Entity Relationship Diagram

```
┌──────────────┐
│  currencies  │
│──────────────│
│ code (PK)    │
│ name         │
│ risk_free_rate│
└──────┬───────┘
       │
       │ 1:N
       │
┌──────▼───────────┐
│ exchange_rates   │
│──────────────────│
│ id (PK)          │
│ base_currency FK │
│ quote_currency FK│
│ rate             │
│ timestamp        │
└──────────────────┘

┌──────────────────┐
│  transactions    │
│──────────────────│
│ id (PK)          │
│ transaction_type │
│ foreign_currency │───┐
│ functional_curr  │   │ N:1
│ notional_amount  │   │
│ invoice_date     │   │
│ payment_date     │   │
└────────┬─────────┘   │
         │              │
         │ 1:N          │
         │              │
┌────────▼────────┐    │
│     hedges      │    │
│─────────────────│    │
│ id (PK)         │    │
│ transaction_id  │────┘
│ strike_price    │
│ option_price    │
│ total_cost      │
│ greeks...       │
└─────────────────┘

┌──────────────────┐
│ portfolio_pos    │
│──────────────────│
│ id (PK)          │
│ currency_pair    │
│ net_exposure     │
│ total_hedges     │
│ total_premium    │
└──────────────────┘
```

### Key Design Decisions

1. **Separate Exchange Rates Table**: Maintains history, enables volatility calculation
2. **Transaction → Hedge (1:N)**: One transaction can have multiple hedge proposals
3. **Source Field**: Tracks data origin (manual, odoo, api, demo)
4. **Decimal Precision**: DECIMAL(18,8) for rates, DECIMAL(18,2) for amounts

## Frontend Architecture

### Component Structure

```
src/
├── App.tsx                 # Main application shell
├── main.tsx               # Entry point
├── services/
│   └── api.ts            # Axios client, API methods
├── components/
│   ├── TransactionForm.tsx
│   ├── PricingResults.tsx
│   ├── Dashboard.tsx
│   └── ...
├── types/
│   └── index.ts          # TypeScript type definitions
└── hooks/
    └── usePricing.ts     # Custom React hooks
```

### State Management

**Current**: React useState/useEffect (simple, no external dependencies)

**Future (when needed)**:
- Zustand for global state
- React Query for server state management

## Security Architecture

### Authentication (Future)

```
┌──────────┐           ┌──────────┐           ┌──────────┐
│  Client  │──Token──▶ │   API    │──Verify──▶│   JWT    │
│          │           │ Gateway  │           │  Service │
└──────────┘           └──────────┘           └──────────┘
```

Current: API key authentication for integrations only

### Data Security

- HTTPS enforced in production
- API keys stored in environment variables (never in code)
- SQL injection prevention (SQLAlchemy ORM)
- CORS restrictions configured

## Scalability

### Horizontal Scaling

```
           ┌────────────┐
           │Load Balancer│
           └──────┬──────┘
                  │
      ┌───────────┼───────────┐
      │           │           │
┌─────▼────┐┌────▼─────┐┌────▼─────┐
│Backend 1 ││Backend 2 ││Backend 3 │
└─────┬────┘└────┬─────┘└────┬─────┘
      │          │           │
      └──────────┴───────────┘
                 │
          ┌──────▼──────┐
          │  PostgreSQL │
          │ (Primary/   │
          │  Replica)   │
          └─────────────┘
```

### Caching Strategy

1. **Exchange Rates**: 1-hour cache
2. **Volatility**: 24-hour cache
3. **Static Data**: CDN (Cloudflare)

### Performance Optimizations

- Async I/O throughout (FastAPI + aiohttp)
- Database connection pooling
- Lazy loading for historical data
- Pagination for large result sets

## Monitoring & Observability

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Levels used:
logger.debug("Detailed diagnostic info")
logger.info("Normal operations")
logger.warning("Potential issues")
logger.error("Errors that need attention")
logger.critical("System-level failures")
```

### Metrics (Future)

- Prometheus for metrics collection
- Grafana for visualization
- Alert manager for notifications

### Health Checks

```
GET /health          # Application health
GET /api/integrations/status  # Integration health
```

## Testing Strategy

### Unit Tests

- Test each service independently
- Mock external dependencies
- Focus on business logic

```bash
pytest backend/tests/test_pricing_engine.py -v
```

### Integration Tests

- Test API endpoints
- Use test database
- Verify data flow

### End-to-End Tests (Future)

- Playwright or Cypress
- Full user journeys
- Cross-browser testing

## Deployment Architecture

### Development

```
docker-compose up
├── backend (port 8000)
├── frontend (port 3000)
└── database (SQLite file)
```

### Production

```
┌──────────────┐
│  CloudFlare  │  # CDN + DDoS protection
└──────┬───────┘
       │
┌──────▼────────┐
│  Load Balancer│  # AWS ALB / Nginx
└──────┬────────┘
       │
  ┌────┴────┐
  │         │
┌─▼──┐   ┌─▼──┐
│App │   │App │  # ECS Fargate / Docker Swarm
│ 1  │   │ 2  │
└─┬──┘   └─┬──┘
  │        │
  └────┬───┘
       │
┌──────▼────────┐
│  PostgreSQL   │  # RDS Multi-AZ
│  (Primary +   │
│   Replica)    │
└───────────────┘
```

## Technology Choices Rationale

**FastAPI**: Async performance, automatic API docs, Python ecosystem
**React**: Component reusability, large ecosystem, TypeScript support
**SQLAlchemy**: Database agnostic, migrations support, type safety
**Docker**: Consistent environments, easy deployment, scaling
**Pydantic**: Runtime validation, automatic serialization, FastAPI integration
**Tailwind CSS**: Rapid UI development, consistent design, small bundle size

## Future Architecture Enhancements

1. **Message Queue** (Celery + Redis): Background jobs for batch processing
2. **WebSockets**: Real-time pricing updates
3. **GraphQL**: Flexible data fetching (complement REST)
4. **Microservices**: Separate pricing engine, integration service
5. **Event Sourcing**: Audit trail for all transactions
6. **Multi-tenancy**: Isolate data per client

## Code Quality

- **Type Hints**: Python 3.10+ type annotations
- **Linting**: flake8, black for Python; ESLint for TypeScript
- **Documentation**: Docstrings, OpenAPI, README files
- **Git Workflow**: Feature branches, pull requests, code review
