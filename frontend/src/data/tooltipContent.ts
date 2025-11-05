export type TooltipContent = {
  term: string;
  shortExplanation: string;
  detailedExplanation?: string;
  example?: string;
  learnMoreLink?: string;
  icon?: 'info' | 'help' | 'warning';
};

export const tooltips: Record<string, TooltipContent> = {
  protectionPrice: {
    term: 'Protection Price (Strike Price)',
    shortExplanation: 'The maximum exchange rate you will ever pay (or minimum you will receive).',
    detailedExplanation:
      'Think of it as a "price ceiling" for importers or a "price floor" for exporters. No matter how much the market moves, you are protected at this rate.',
    example:
      'If the protection price is 19.95 MXN per USD, you will never pay more than 19.95 MXN for each dollar, even if the market goes to 25 MXN/USD.',
    icon: 'info',
  },

  protectionLevel: {
    term: 'Protection Level',
    shortExplanation: 'How much exchange rate movement you want to protect against.',
    detailedExplanation:
      'This sets how far above (for importers) or below (for exporters) the current rate you want your protection. Higher protection = more safety but higher upfront cost.',
    example:
      'If the current rate is 19.00 and you choose 5% protection, your protection price will be 19.95 (19.00 × 1.05). This gives you a 5% buffer.',
    icon: 'info',
  },

  upfrontCost: {
    term: 'Upfront Cost (Option Premium)',
    shortExplanation: 'One-time payment you make today to buy this protection. Non-refundable.',
    detailedExplanation:
      'This is like an insurance premium. You pay it once, upfront, and it gives you the right (but not obligation) to use the protection price on your payment date.',
    example:
      'For $1M transaction with 0.343 MXN/USD cost, you pay 343,000 MXN today to lock in protection for 3 months.',
    icon: 'info',
  },

  spotRate: {
    term: 'Spot Rate',
    shortExplanation: 'The current exchange rate in the market right now.',
    detailedExplanation:
      'This is what you would pay if you exchanged money today. Your protection price is calculated based on this rate plus your protection level.',
    example: 'If spot rate is 19.00 MXN/USD, you can exchange $1 for 19 pesos today.',
    icon: 'info',
  },

  volatility: {
    term: 'Volatility',
    shortExplanation: 'How much the exchange rate jumps around (market uncertainty).',
    detailedExplanation:
      'Higher volatility means the rate changes more dramatically. This makes protection more expensive because there is more risk to cover. Measured as annual percentage.',
    example:
      '20% volatility means the rate typically moves up or down by 20% over a year. 10% volatility = more stable currency = cheaper protection.',
    icon: 'info',
  },

  totalCost: {
    term: 'Total Upfront Cost',
    shortExplanation: 'The total amount you pay today (in your home currency) for this protection.',
    detailedExplanation:
      'This is the upfront cost per unit multiplied by your transaction size. This is a sunk cost - you pay it once and do not get it back, even if you do not use the protection.',
    example:
      'For a $1M transaction with 0.343 MXN/USD cost, you pay 343,000 MXN upfront (about 1.8% of notional).',
    icon: 'info',
  },

  costPercentage: {
    term: 'Cost as % of Transaction',
    shortExplanation: 'What percentage of your transaction size you are paying for protection.',
    detailedExplanation:
      'Lower is better! Our platform targets under 2% for most scenarios. This tells you if the protection is "expensive" relative to the size of the transaction.',
    example: '1.8% means for every 100 pesos you are hedging, you pay 1.80 pesos in upfront cost.',
    icon: 'info',
  },

  maximumCost: {
    term: 'Maximum Cost',
    shortExplanation: 'The absolute worst-case total cost you will ever pay. You will NEVER pay more than this.',
    detailedExplanation:
      'This includes the upfront cost plus the worst-case exchange cost at your protection price. This is your ceiling - the most you could possibly spend.',
    example:
      'If maximum cost is 20,293,000 MXN for $1M transaction, you know with 100% certainty you will not pay more than this, even if the exchange rate goes to 100 MXN/USD.',
    icon: 'info',
  },

  delta: {
    term: 'Delta',
    shortExplanation: 'Advanced metric - How much the option price changes when the exchange rate moves.',
    detailedExplanation:
      'This is a "Greek" used by traders. For most users, you can safely ignore this. It ranges from 0 to 1 and tells you the sensitivity of the option to rate changes.',
    example: 'Delta of 0.52 means if the spot rate goes up by 1 peso, the option value goes up by 0.52 pesos.',
    icon: 'warning',
  },

  gamma: {
    term: 'Gamma',
    shortExplanation: 'Advanced metric - How quickly Delta changes as the rate moves.',
    detailedExplanation:
      'This is a second-order "Greek" used by traders for risk management. For most users, you can safely ignore this. It tells you how stable your Delta is.',
    example: 'High gamma means Delta changes rapidly. Low gamma means Delta is more stable.',
    icon: 'warning',
  },

  vega: {
    term: 'Vega',
    shortExplanation: 'Advanced metric - How much the option price changes when volatility changes.',
    detailedExplanation:
      'This is a "Greek" that measures sensitivity to market uncertainty. For most users, you can safely ignore this. Higher Vega means more exposure to volatility changes.',
    example:
      'Vega of 1500 means if volatility increases by 1%, the option value increases by 1500 MXN.',
    icon: 'warning',
  },

  theta: {
    term: 'Theta',
    shortExplanation: 'Advanced metric - How much value you lose each day as time passes.',
    detailedExplanation:
      'Options lose value over time (time decay). This is a "Greek" that measures that loss per day. For most users, you can safely ignore this.',
    example:
      'Theta of -150 means you lose 150 MXN of option value each day, all else being equal.',
    icon: 'warning',
  },

  transactionSize: {
    term: 'Transaction Size (Notional Amount)',
    shortExplanation: 'The total amount of foreign currency you need to pay or receive.',
    detailedExplanation:
      'This is the size of your import or export transaction. It is the "face value" of the deal you are hedging.',
    example:
      'If you are importing $1,000,000 worth of machinery from the USA, your transaction size is $1,000,000.',
    icon: 'info',
  },

  timeToMaturity: {
    term: 'Time to Maturity',
    shortExplanation: 'How long until your payment is due.',
    detailedExplanation:
      'This is the time between today and when you need to make (or receive) the payment. Longer time = more uncertainty = higher cost.',
    example:
      'If your invoice is due in 90 days, time to maturity is 0.25 years (90/365).',
    icon: 'info',
  },

  callOption: {
    term: 'Call Option',
    shortExplanation: 'Protection for IMPORTERS - caps your maximum exchange rate.',
    detailedExplanation:
      'Use this when you need to BUY foreign currency in the future. It protects you from the currency getting more expensive (exchange rate going UP).',
    example:
      'Mexican importer buying from USA wants to protect against MXN weakening (rate going from 19 to 25).',
    icon: 'info',
  },

  putOption: {
    term: 'Put Option',
    shortExplanation: 'Protection for EXPORTERS - sets your minimum exchange rate.',
    detailedExplanation:
      'Use this when you need to SELL foreign currency in the future. It protects you from the currency getting less valuable (exchange rate going DOWN).',
    example:
      'Colombian coffee exporter to USA wants to protect against COP strengthening (rate going from 4100 to 3500).',
    icon: 'info',
  },
};
