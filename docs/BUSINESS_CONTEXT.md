# Business Context: FX Hedging Platform

## Executive Summary

The FX Hedging Platform addresses a $2+ trillion problem: small and medium-sized enterprises (SMEs) engaged in international trade bear significant foreign exchange risk but lack access to affordable, appropriate hedging solutions. Our platform democratizes FX risk management by offering a simple, cost-effective hedging service specifically designed for the needs and constraints of SMEs in emerging markets.

**Value Proposition**: Limit FX losses to 5% for less than 2% upfront cost, with zero margin requirements.

---

## The Problem

### Market Opportunity

- **Trade Volume**: SMEs (10-50M revenue) account for ~10% of international trade
- **Geographic Focus**: Latin America, with expansion potential to Africa, Asia, Eastern Europe, ANZ
- **Unmet Need**: 80%+ of target SMEs do not hedge FX risk despite material exposure

### Why SMEs Don't Hedge

1. **High Costs**
   - Banks charge 2-5% in fees alone
   - Collateral requirements (initial margin 5-15% of notional)
   - Opportunity cost of capital tied up in margin accounts

2. **Mental Bandwidth**
   - Complex financial products require expertise
   - Time-consuming to set up and manage
   - Distraction from core business

3. **Fear of Regrets**
   - Forward contracts lock in rates - if rate moves favorably, missed opportunity
   - "Damned if you do, damned if you don't" psychology
   - Hard to explain to board/shareholders

4. **Inadequate Products**
   - Banks focus on large corporates (>$100M revenue)
   - Minimum transaction sizes too large ($5-10M)
   - Not integrated with SME accounting systems
   - One-size-fits-all approach

### Real-World Impact

**Case Study: Mexican Manufacturer**

A Mexican automotive parts manufacturer with $30M annual revenue imports $500K USD of raw materials monthly from the USA.

- **Invoice Date**: January 1, 2024 (rate: 17.50 MXN/USD)
- **Payment Date**: March 30, 2024 (rate: 18.90 MXN/USD)
- **Impact**: 8% increase in cost = 400,000 MXN unexpected loss
- **Annual Impact**: ~5M MXN in FX losses (~2.9% of revenue)

Without hedging tools, this company:
- Cannot accurately forecast costs
- Loses pricing competitiveness
- Faces compressed margins
- May fail to honor fixed-price contracts

---

## The Solution

### Product Design

**FX Call/Put Options** using Garman-Kohlhagen pricing model

1. **Downside Protection**
   - Strike price set 5% above current spot (for importers) or 5% below (for exporters)
   - Maximum loss capped at 5% regardless of currency movement
   - Predictable worst-case scenario for cash flow planning

2. **Upside Participation**
   - If exchange rate moves favorably, client benefits
   - Option expires unexercised, buy/sell at better spot rate
   - Only lose the premium paid

3. **Affordable Pricing**
   - Target: <2% of notional amount
   - Achievable in most market conditions with 90-day maturity and moderate volatility
   - No margin requirements for client (we post margins with brokers)

4. **Simple Integration**
   - Auto-detect foreign currency transactions from accounting software (Odoo, QuickBooks, etc.)
   - One-click hedging proposal
   - Automated execution and settlement

### Example Transaction Flow

**Mexican Importer Use Case**

1. **Transaction Entry** (Manual or from Odoo)
   - Invoice: $1,000,000 USD machinery import
   - Invoice Date: March 1, 2024
   - Payment Due: June 1, 2024 (90 days)
   - Spot Rate: 19.00 MXN/USD

2. **Hedge Proposal** (Automatic)
   - Option Type: USD Call (right to buy USD)
   - Strike Price: 19.95 MXN/USD (5% protection)
   - Expiry: June 1, 2024
   - Premium: 343,000 MXN (1.8% of 19M MXN notional)

3. **Client Decision**
   - **Accept Hedge**: Maximum cost = 19.95M MXN (known)
   - **Reject Hedge**: Exposed to unlimited upside risk

4. **At Maturity** (June 1)
   - **Scenario A** - USD appreciates to 21.00:
     * Without hedge: Pay 21M MXN (2M loss)
     * With hedge: Exercise option, pay 19.95M MXN + 343K premium = 20.29M MXN
     * **Savings: 710K MXN**

   - **Scenario B** - USD depreciates to 18.00:
     * Without hedge: Pay 18M MXN (1M gain)
     * With hedge: Let option expire, pay 18M + 343K premium = 18.34M MXN
     * **Net: Still benefit from favorable move, only pay premium**

### Competitive Advantages

| Feature | Banks | FX Hedging Platform |
|---------|-------|---------------------|
| Minimum Size | $5-10M | $50K |
| Cost | 2-5% + margin | <2% total |
| Margin Required | Yes (5-15%) | No |
| Integration | Manual | Automated (Odoo, QB) |
| Flexibility | Forward contracts (locked) | Options (keep upside) |
| Support | Dedicated to large clients | Optimized for SMEs |

---

## Target Market Analysis

### Primary Market: Latin America

**Why Latin America?**

1. **Currency Volatility**: LatAm currencies are 2-3x more volatile than developed markets
2. **Trade Growth**: Expanding middle class driving import/export growth
3. **Digitalization**: Rapid adoption of cloud accounting (Odoo, Siigo, Contpaqi)
4. **Banking Gap**: Local banks underdeveloped in derivatives offerings
5. **Language/Culture**: Homogeneous Spanish/Portuguese speaking market

**Country Profiles**

| Country | Currency | GDP | FX Vol (annual) | SME Trade | Dominant ERP |
|---------|----------|-----|-----------------|-----------|--------------|
| Mexico | MXN | $1.4T | ~18% | $120B | Contpaqi, Odoo |
| Colombia | COP | $350B | ~22% | $40B | Siigo, Odoo |
| Brazil | BRL | $2.1T | ~20% | $180B | Totvs, SAP |
| Chile | CLP | $300B | ~15% | $60B | Softland, Odoo |
| Peru | PEN | $240B | ~16% | $35B | Siscont, Odoo |
| Argentina | ARS | $630B | ~35% | $50B | Bejerman, Odoo |

### Secondary Markets (Year 2-3)

1. **Africa**: Kenya, Nigeria, South Africa
2. **Asia**: Vietnam, Thailand, Philippines
3. **Eastern Europe**: Poland, Romania, Czech Republic
4. **ANZ**: Australia, New Zealand (Pacific Island trade)

---

## Business Model

### Revenue Streams

1. **Option Premiums** (Primary)
   - Earn the bid-ask spread between our cost to hedge (broker) and price to client
   - Target margin: 20-30 basis points (0.2-0.3%)
   - Volume play: thousands of small transactions vs. dozens of large ones

2. **SaaS Subscription** (Secondary)
   - Monthly/annual subscription for platform access
   - Tiered pricing based on transaction volume
   - $99-$999/month depending on company size

3. **Integration Services** (Tertiary)
   - Custom integration with proprietary ERPs
   - White-label solutions for banks/fintechs
   - Consulting on FX risk management policy

### Unit Economics

**Per Transaction** (Average: $500K notional, 90 days, 5% protection)

- Client Premium: 1.8% = $9,000
- Our Broker Cost: 1.5% = $7,500
- Gross Margin: $1,500 (16.7%)
- Processing Cost: $200 (automation)
- Net Margin: $1,300 per transaction

**Target Volume** (Year 1 - Mexico pilot)

- Clients: 50 SMEs
- Avg Transactions/Client/Year: 24 (2 per month)
- Total Transactions: 1,200
- Revenue: $1.56M
- Costs: $240K (platform) + $600K (ops/sales)
- EBITDA: $720K

---

## Go-To-Market Strategy

### Phase 1: Mexico Pilot (Months 1-6)

**Target**: 10-20 import/export SMEs in Mexico

**Approach**:
1. Partner with Odoo implementation consultants
2. Direct outreach to manufacturers associations (CANACINTRA)
3. Referral program with existing clients
4. Educational content (webinars, case studies)

**Success Metrics**:
- 10 active clients
- 200+ transactions processed
- <2% average pricing achieved
- 90%+ client satisfaction

### Phase 2: LatAm Expansion (Months 7-18)

**Target**: Colombia, Brazil, Chile (100 clients total)

**Approach**:
1. Localize platform (language, currency defaults)
2. Partner with local ERPs (Siigo, Totvs, Softland)
3. Hire country managers
4. Local banking partnerships

### Phase 3: Scale & Diversify (Months 19-36)

**Target**: 1,000 clients across 10 countries

**Approach**:
1. Expand to Africa, Asia, Eastern Europe
2. White-label for local banks
3. API for fintech integration
4. Institutional sales (banks buying for SME clients)

---

## Competitive Landscape

### Direct Competitors

1. **Traditional Banks** (BBVA, Santander, Itaú)
   - **Strengths**: Established relationships, balance sheet
   - **Weaknesses**: Focus on large corporates, slow innovation, high costs
   - **Our Advantage**: Tech-first, SME-optimized, affordable

2. **FX Brokers** (FXCM, OANDA, Interactive Brokers)
   - **Strengths**: Low spreads, global coverage
   - **Weaknesses**: Not designed for corporates, manual processes, no integration
   - **Our Advantage**: Automated hedging, ERP integration, simpler UX

3. **Fintech Competitors** (Bound, Kantox, Hedgebook)
   - **Strengths**: Modern UX, automation
   - **Weaknesses**: Focused on USD/EUR/GBP, expensive, still require margins
   - **Our Advantage**: LatAm expertise, lower cost, zero margin for clients

### Indirect Competitors

1. **No Hedging** (Status Quo - 80% of SMEs)
   - **Our Advantage**: Demonstrable ROI, simple value prop

2. **Natural Hedging** (Matching imports with exports)
   - **Our Advantage**: Augment natural hedges, cover remaining exposure

---

## Risk Mitigation

### Financial Risks

1. **Directional Risk** (Currency moves against us)
   - **Mitigation**: Hedge every client option with broker option (back-to-back)
   - **Residual**: Basis risk (minimal for liquid pairs)

2. **Counterparty Risk** (Broker default)
   - **Mitigation**: Multi-broker relationships, tier-1 only (JP Morgan, Goldman, Citi)
   - **Residual**: Systemic events (diversified across 3+ brokers)

3. **Liquidity Risk** (Can't hedge all client requests)
   - **Mitigation**: Pre-arranged credit lines with brokers
   - **Residual**: Extreme market conditions (temporarily pause new hedges)

### Operational Risks

1. **Integration Failures** (ERP bugs)
   - **Mitigation**: Manual entry fallback, extensive testing
   - **Insurance**: E&O insurance for tech errors

2. **Pricing Errors** (Wrong option price quoted)
   - **Mitigation**: Dual calculation (our model + broker quote), alerts for outliers
   - **Kill Switch**: Manual approval for >$5M notional

3. **Regulatory Changes** (New derivatives rules)
   - **Mitigation**: Legal counsel in each jurisdiction, compliance-first design
   - **Lobbying**: Join SME trade associations, advocate for exemptions

---

## Regulatory Considerations

### Securities Law

- **Status**: FX options are regulated derivatives
- **Required Licenses**:
  - USA: Swap Dealer registration (CFTC) - may qualify for exemption
  - Mexico: CNBV license or partner with licensed entity
  - Brazil: CVM registration

- **Compliance**:
  - KYC/AML procedures
  - Trade reporting (EMIR, Dodd-Frank)
  - Capital adequacy (if dealer, otherwise outsourced to brokers)

### Tax Treatment

- **Client Perspective**: Option premiums are deductible business expenses, payoffs are ordinary income/loss
- **Our Perspective**: Premiums earned are ordinary income, broker costs deductible

---

## Success Metrics & Milestones

### Year 1
- ✅ Proof-of-concept (this platform!)
- ✅ 10 pilot clients in Mexico
- ✅ $10M notional hedged
- ✅ Odoo integration live
- ✅ <2% average pricing achieved

### Year 2
- 100 clients across Mexico, Colombia, Brazil
- $500M notional hedged
- $2.5M revenue, breakeven
- Series A fundraise ($5-10M)

### Year 3
- 1,000 clients across 8 countries
- $5B notional hedged
- $25M revenue, $10M EBITDA
- Potential exit/IPO discussions

---

## Investment Ask

### Seed Round: $2M

**Use of Funds**:
- **Product** ($600K): Finalize integrations, mobile app, advanced analytics
- **Sales & Marketing** ($800K): Country managers, pilot program, content marketing
- **Operations** ($400K): Compliance, legal, broker relationships
- **Runway** ($200K): 18-month operating capital

**Milestones**:
- Months 1-6: Mexico pilot (10-20 clients)
- Months 7-12: Colombia & Chile launch (50 total clients)
- Months 13-18: Brazil launch, Series A preparation (100 total clients)

**Terms**:
- Valuation: $8M pre-money
- Structure: SAFE or priced equity
- Board Seat: Yes for lead investor

---

## Why Now?

1. **Cloud Accounting Adoption**: Odoo, QuickBooks, Xero adoption accelerating in LatAm (30% CAGR)
2. **API Infrastructure**: Modern ERPs have robust APIs for integration
3. **Regulatory Clarity**: Dodd-Frank/EMIR matured, know the rules
4. **Market Volatility**: COVID, geopolitics → SMEs acutely aware of FX risk
5. **Fintech Investment**: $20B+ deployed in LatAm fintech 2020-2024, infrastructure ready

---

## Conclusion

The FX Hedging Platform addresses a massive, underserved market with a scalable, capital-efficient solution. By combining financial engineering expertise with modern technology, we democratize access to sophisticated FX risk management tools that were previously available only to large corporations.

Our proof-of-concept demonstrates:
- ✅ Technical feasibility (Garman-Kohlhagen model working)
- ✅ Pricing viability (<2% target achievable)
- ✅ Integration readiness (Odoo hooks in place)
- ✅ Scalability (currency-agnostic architecture)

**We're ready to pilot, scale, and capture this $2T+ opportunity.**

---

*For investor inquiries: [Contact Information]*
