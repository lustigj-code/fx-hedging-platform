# User Guide: FX Hedging Platform

## Getting Started

### Step 1: Access the Platform

Navigate to: **http://localhost:3000** (development) or **https://yourdomain.com** (production)

### Step 2: Initialize Demo Data (First Time Only)

1. Click the **"Demo"** tab
2. Click **"Generate Demo Data"** button
3. Wait for confirmation message

This creates:
- Sample currencies with risk-free rates
- 8 realistic Latin America business scenarios
- Ready-to-use transactions

## Core Workflows

### Workflow 1: Manual Transaction Entry & Hedge Pricing

**Use Case**: You have a foreign currency invoice and want to price a hedge.

**Steps**:

1. **Navigate to Calculator**
   - Click "Calculator" tab

2. **Review Sample Scenario**
   - Default: Mexican importer buying $1M USD machinery
   - Payment due in 90 days

3. **Calculate Hedge Price**
   - Click "Calculate Hedge Price" button
   - Wait for pricing results (~2-3 seconds)

4. **Review Results**
   - **Option Price**: Cost per unit of foreign currency
   - **Total Cost**: Total option premium in functional currency
   - **Cost %**: Percentage of notional (target: <2%)
   - **Strike Price**: Protection level (default 5% above spot)

5. **Analyze Scenarios**
   - View table showing outcomes at different future exchange rates
   - Green = savings, Red = additional cost

### Workflow 2: Understanding the Hedge

**Key Concepts**:

1. **Strike Price**: The exchange rate at which you're protected
   - For importers: Strike above current spot (protects against appreciation)
   - For exporters: Strike below current spot (protects against depreciation)

2. **Option Premium**: Upfront cost you pay
   - Typically 1-2% of notional
   - One-time payment

3. **Maximum Cost**: Worst-case scenario
   - Strike price × Notional amount
   - Your loss is capped at 5%

4. **Upside Participation**: If exchange rate moves favorably
   - Option expires worthless
   - You buy/sell at better spot rate
   - Only cost: Premium paid

### Workflow 3: Viewing Portfolio (When Implemented)

**Steps**:
1. Navigate to Dashboard
2. View all active hedges
3. See aggregate exposure by currency
4. Identify netting opportunities

## Common Scenarios

### Scenario A: Mexican Importer

**Business**: Manufacturing company in Mexico
**Transaction**: Importing $1,000,000 USD machinery from USA
**Risk**: USD appreciates against MXN, increasing cost in pesos

**Current Spot**: 19.00 MXN/USD
**Invoice Amount**: $1,000,000 USD = 19,000,000 MXN at today's rate
**Payment Due**: 90 days

**Without Hedge**:
- If USD→21.00: Pay 21,000,000 MXN (2M loss)
- If USD→18.00: Pay 18,000,000 MXN (1M gain)
- **Uncertain!**

**With 5% Protection Hedge**:
- Strike: 19.95 MXN/USD
- Premium: ~343,000 MXN (1.8%)
- **Maximum Cost**: 19,950,000 MXN
- **Savings**: If USD goes to 21, save ~710K MXN!

### Scenario B: Colombian Coffee Exporter

**Business**: Coffee exporter in Colombia
**Transaction**: Selling $500,000 USD coffee to USA
**Risk**: USD depreciates against COP, reducing revenue in pesos

**Use**: USD **Put** option (right to sell USD at strike)
**Protection**: Minimum price guaranteed

## Tips for Best Results

1. **Protection Level**:
   - 5%: Standard, balances cost vs. protection
   - 3%: Cheaper premium, less protection
   - 10%: Higher cost, more protection

2. **Time to Maturity**:
   - Longer maturity = higher premium
   - Match hedge to actual payment date

3. **Check Cost %**:
   - Target: <2% of notional
   - If >3%: Consider shorter maturity or less protection

4. **Market Timing**:
   - High volatility = higher premiums
   - Consider hedging when markets are calm

## FAQ

**Q: What happens if I cancel the underlying transaction?**
**A**: You still own the option. If FX moved in your favor, you profit!

**Q: Can I sell the option back?**
**A**: Not in current version. Future: secondary market for options.

**Q: What if I need a different protection level?**
**A**: Use the Strike Adjuster (coming soon) or contact support for custom quote.

**Q: How accurate are the exchange rates?**
**A**: Sourced from exchangerate-api.com. Updated hourly. See DATA_SOURCES.md.

**Q: Is this platform suitable for very large transactions (>$10M)?**
**A**: For >$10M notional, contact us for institutional pricing with Bloomberg data.

## Keyboard Shortcuts

- `Ctrl+K`: Open calculator
- `Ctrl+D`: Go to dashboard
- `Ctrl+H`: View help

## Support

- **Email**: support@fxhedging.com
- **Phone**: +1-XXX-XXX-XXXX
- **Hours**: Mon-Fri 9AM-6PM EST
- **Documentation**: https://docs.fxhedging.com

## Troubleshooting

**"Calculation failed"**: Check internet connection, refresh page
**"Demo data already exists"**: Use "Reset Demo" before generating again
**Slow loading**: Clear browser cache, check API health at /health endpoint
