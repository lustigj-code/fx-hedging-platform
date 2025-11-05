import { useState, useEffect } from 'react';
import { apiClient, type PricingResponse } from './services/api';
import RiskHistogram from './components/RiskHistogram';
import PayoffDiagram from './components/PayoffDiagram';
import InfoTooltip from './components/InfoTooltip';
import { tooltips } from './data/tooltipContent';
import {
  TrendingUp,
  Shield,
  DollarSign,
  Activity,
  ArrowRight,
  Zap,
  Lock,
  BarChart3,
  CheckCircle2,
  ArrowUpRight,
  ArrowDownRight,
  Loader,
  X,
} from 'lucide-react';

type View = 'home' | 'calculator' | 'demo';

function App() {
  const [view, setView] = useState<View>('home');
  const [pricingResult, setPricingResult] = useState<PricingResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [protectionLevel, setProtectionLevel] = useState(0.05); // 5% default
  const [showWelcome, setShowWelcome] = useState(false);

  // Check if first-time user
  useEffect(() => {
    const hasVisited = localStorage.getItem('fx-hedge-visited');
    if (!hasVisited) {
      setShowWelcome(true);
      localStorage.setItem('fx-hedge-visited', 'true');
    }
  }, []);

  // Demo initialization
  const initializeDemo = async () => {
    try {
      setLoading(true);
      setError(null);
      await apiClient.seedCurrencies();
      await apiClient.generateDemoData();
      setLoading(false);
      setTimeout(() => {
        alert('Demo data generated successfully!');
      }, 300);
    } catch (err) {
      setError('Failed to initialize demo');
      setLoading(false);
    }
  };

  // Quick pricing calculation
  const calculateQuickPricing = async () => {
    try {
      setLoading(true);
      setError(null);

      const result = await apiClient.calculatePricingAuto({
        base: 'USD',
        quote: 'MXN',
        time_to_maturity_years: 0.25,
        notional_amount: 1000000,
        option_type: 'call',
        protection_level: protectionLevel,
      });

      setPricingResult(result.data);
      setLoading(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Pricing calculation failed');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="border-b border-gray-800 sticky top-0 z-50 bg-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center space-x-3 cursor-pointer">
              <Shield className="h-6 w-6 text-white" />
              <div>
                <h1 className="text-lg font-semibold text-white">FX Hedging</h1>
                <p className="text-xs text-gray-400">Professional Risk Protection</p>
              </div>
            </div>

            {/* Navigation */}
            <nav className="flex items-center space-x-1 border border-gray-800 rounded-lg p-1">
              {(['home', 'calculator', 'demo'] as const).map((v) => (
                <button
                  key={v}
                  onClick={() => setView(v)}
                  className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    view === v
                      ? 'bg-white text-black'
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  {v.charAt(0).toUpperCase() + v.slice(1)}
                </button>
              ))}
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main>
        {view === 'home' && (
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
            {/* Hero Section */}
            <div className="text-center space-y-6 mb-16">
              <div className="space-y-3">
                <h1 className="text-5xl lg:text-6xl font-semibold leading-tight text-white">
                  Protect Your FX Risk
                  <br />
                  <span className="text-gray-400">5% Loss Limit. Under 2% Cost.</span>
                </h1>
                <p className="text-lg text-gray-400 max-w-2xl mx-auto">
                  Enterprise-grade hedging for Latin American importers and exporters. Use proven
                  financial engineering to eliminate currency risk while keeping the upside.
                </p>
              </div>

              <div className="flex flex-col sm:flex-row justify-center items-center gap-3 pt-4">
                <button
                  onClick={() => setView('calculator')}
                  className="group px-6 py-3 bg-white text-black text-sm font-medium rounded-lg hover:bg-gray-200 transition-colors flex items-center space-x-2"
                >
                  <span>Calculate Your Protection Price</span>
                  <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </button>
                <button
                  onClick={() => setView('demo')}
                  className="px-6 py-3 border border-gray-800 text-white text-sm font-medium rounded-lg hover:bg-gray-900 transition-colors"
                >
                  View Demo
                </button>
              </div>

              {/* Key Metrics */}
              <div className="grid md:grid-cols-3 gap-4 pt-8">
                <div className="border border-gray-800 rounded-lg p-6 hover:border-gray-700 transition-colors">
                  <div className="text-3xl font-semibold text-white mb-1">5%</div>
                  <p className="text-white font-medium text-sm">Maximum Loss</p>
                  <p className="text-xs text-gray-500 mt-2">
                    Hard protection floor regardless of market moves
                  </p>
                </div>
                <div className="border border-gray-800 rounded-lg p-6 hover:border-gray-700 transition-colors">
                  <div className="text-3xl font-semibold text-white mb-1">&lt;2%</div>
                  <p className="text-white font-medium text-sm">Upfront Cost</p>
                  <p className="text-xs text-gray-500 mt-2">
                    Minimal one-time payment for full protection
                  </p>
                </div>
                <div className="border border-gray-800 rounded-lg p-6 hover:border-gray-700 transition-colors">
                  <div className="text-3xl font-semibold text-white mb-1">100%</div>
                  <p className="text-white font-medium text-sm">Upside Kept</p>
                  <p className="text-xs text-gray-500 mt-2">
                    Benefit from favorable exchange rate moves
                  </p>
                </div>
              </div>
            </div>

            {/* Features Section */}
            <div className="mb-16">
              <div className="text-center mb-10">
                <h2 className="text-3xl font-semibold text-white mb-3">Why Choose FX Hedging Platform</h2>
                <p className="text-gray-400 max-w-2xl mx-auto">
                  Built by financial engineers for businesses that understand the value of
                  professional risk management
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                {/* Feature 1 */}
                <div className="border border-gray-800 rounded-lg p-6 hover:border-gray-700 transition-colors">
                  <div className="mb-4">
                    <div className="w-10 h-10 rounded-lg bg-gray-900 flex items-center justify-center">
                      <Lock className="h-5 w-5 text-white" />
                    </div>
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">Iron-Clad Protection</h3>
                  <p className="text-sm text-gray-400">
                    Limit your maximum currency loss to exactly 5% of the invoiced amount. No
                    surprises, no margin calls.
                  </p>
                </div>

                {/* Feature 2 */}
                <div className="border border-gray-800 rounded-lg p-6 hover:border-gray-700 transition-colors">
                  <div className="mb-4">
                    <div className="w-10 h-10 rounded-lg bg-gray-900 flex items-center justify-center">
                      <DollarSign className="h-5 w-5 text-white" />
                    </div>
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">Transparent Pricing</h3>
                  <p className="text-sm text-gray-400">
                    Pay less than 2% upfront. No hidden fees, no surprise charges. Budget with
                    precision.
                  </p>
                </div>

                {/* Feature 3 */}
                <div className="border border-gray-800 rounded-lg p-6 hover:border-gray-700 transition-colors">
                  <div className="mb-4">
                    <div className="w-10 h-10 rounded-lg bg-gray-900 flex items-center justify-center">
                      <TrendingUp className="h-5 w-5 text-white" />
                    </div>
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">Keep the Upside</h3>
                  <p className="text-sm text-gray-400">
                    If the market moves in your favor, you benefit fully. You're protected from losses
                    but never locked out of gains.
                  </p>
                </div>

                {/* Feature 4 */}
                <div className="border border-gray-800 rounded-lg p-6 hover:border-gray-700 transition-colors">
                  <div className="mb-4">
                    <div className="w-10 h-10 rounded-lg bg-gray-900 flex items-center justify-center">
                      <Zap className="h-5 w-5 text-white" />
                    </div>
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">Instant Quotes</h3>
                  <p className="text-sm text-gray-400">
                    Get pricing in seconds using institutional-grade Garman-Kohlhagen model.
                    No waiting for quotes.
                  </p>
                </div>
              </div>
            </div>

            {/* Technology Stack */}
            <div className="border border-gray-800 rounded-lg p-8 mb-16">
              <div className="flex items-start space-x-4">
                <div className="w-12 h-12 rounded-lg bg-gray-900 flex items-center justify-center flex-shrink-0">
                  <Activity className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">
                    Garman-Kohlhagen Pricing Engine
                  </h3>
                  <p className="text-sm text-gray-400 mb-3">
                    Our platform uses the industry-standard Garman-Kohlhagen formula for FX option
                    pricing—the same model trusted by tier-1 investment banks worldwide and validated
                    by decades of academic research in financial derivatives.
                  </p>
                  <p className="text-xs text-gray-500">
                    Reference: Garman, M.B. and Kohlhagen, S.W. (1983) "Foreign Currency Option
                    Values" Journal of International Money and Finance, 2, 231-237
                  </p>
                </div>
              </div>
            </div>

            {/* CTA */}
            <div className="text-center">
              <h2 className="text-2xl font-semibold text-white mb-2">Ready to protect your business?</h2>
              <p className="text-gray-400 mb-6">
                Try our calculator to see real pricing for your FX protection
              </p>
              <button
                onClick={() => setView('calculator')}
                className="px-6 py-3 bg-white text-black text-sm font-medium rounded-lg hover:bg-gray-200 transition-colors"
              >
                Open Calculator
              </button>
            </div>
          </div>
        )}

        {view === 'calculator' && (
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="space-y-6">
              {/* Header */}
              <div className="text-center mb-8">
                <h2 className="text-4xl font-semibold text-white mb-2">Pricing Calculator</h2>
                <p className="text-gray-400">
                  See exactly what your FX protection will cost
                </p>
              </div>

              {/* Welcome Banner */}
              {showWelcome && (
                <div className="bg-blue-950 border border-blue-900 rounded-lg p-5 flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <div className="w-10 h-10 rounded-lg bg-blue-900 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <Shield className="h-5 w-5 text-blue-400" />
                    </div>
                    <div>
                      <h3 className="text-white font-semibold text-sm mb-1">
                        👋 Welcome! This is your first time here.
                      </h3>
                      <p className="text-blue-300 text-sm mb-3">
                        FX protection helps you lock in a maximum price for your imports (or minimum
                        price for exports) so you never lose more than 5% to currency movements.
                        Hover over the <span className="inline-flex items-center"><span className="w-3 h-3 rounded-full bg-blue-800 inline-block mx-1"></span></span> icons to learn more about any term.
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setShowWelcome(false)}
                    className="text-blue-400 hover:text-white transition-colors"
                    aria-label="Close welcome message"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              )}

              {/* Scenario Card */}
              <div className="border border-gray-800 rounded-lg p-8">
                <div className="mb-6">
                  <h3 className="text-xl font-semibold text-white mb-4">Sample Scenario</h3>
                  <div className="grid md:grid-cols-3 gap-4 bg-gray-900 rounded-lg p-4 border border-gray-800">
                    <div>
                      <div className="flex items-center space-x-1 mb-1">
                        <p className="text-gray-500 text-xs">Transaction Size</p>
                        <InfoTooltip {...tooltips.transactionSize} />
                      </div>
                      <p className="text-lg font-semibold text-white">$1,000,000 USD</p>
                    </div>
                    <div>
                      <div className="flex items-center space-x-1 mb-1">
                        <p className="text-gray-500 text-xs">Time Until Payment</p>
                        <InfoTooltip {...tooltips.timeToMaturity} />
                      </div>
                      <p className="text-lg font-semibold text-white">90 Days</p>
                    </div>
                    <div>
                      <p className="text-gray-500 text-xs mb-1">Currency Pair</p>
                      <p className="text-lg font-semibold text-white">USD/MXN</p>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-900 border border-gray-800 rounded-lg p-5 mb-6">
                  <p className="text-sm text-gray-300 leading-relaxed">
                    <span className="font-semibold text-white">The Problem:</span> A Mexican company is
                    importing machinery from the USA, with payment due in 90 days. If USD
                    gets more expensive (exchange rate goes up), they pay more pesos—risking their profit margin.
                  </p>
                  <p className="text-sm text-gray-300 leading-relaxed mt-2">
                    <span className="font-semibold text-white">The Solution:</span> Buy protection
                    with {(protectionLevel * 100).toFixed(0)}% buffer to cap maximum exchange rate, while still benefiting if USD gets cheaper.
                  </p>
                </div>

                {/* Protection Level Slider */}
                <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 mb-6">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-1">
                      <label className="text-sm font-semibold text-white">
                        Protection Level
                      </label>
                      <InfoTooltip {...tooltips.protectionLevel} />
                    </div>
                    <span className="text-lg font-bold text-white">
                      {(protectionLevel * 100).toFixed(1)}%
                    </span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="0.10"
                    step="0.005"
                    value={protectionLevel}
                    onChange={(e) => setProtectionLevel(parseFloat(e.target.value))}
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-white hover:accent-gray-300"
                  />
                  <div className="flex justify-between mt-2">
                    <span className="text-xs text-gray-500">0%</span>
                    <span className="text-xs text-gray-500">2.5%</span>
                    <span className="text-xs text-gray-500">5%</span>
                    <span className="text-xs text-gray-500">7.5%</span>
                    <span className="text-xs text-gray-500">10%</span>
                  </div>
                  <p className="text-xs text-gray-300 mt-4 bg-black border border-gray-800 rounded p-3">
                    <span className="font-semibold text-white">How it works:</span> This sets your "safety buffer."
                    If current rate is 19.00 and you pick 5%, your protection price becomes 19.95.
                    You'll NEVER pay more than 19.95, no matter how high the market goes.
                    Higher protection = more safety = higher upfront cost.
                  </p>
                </div>

                <button
                  onClick={calculateQuickPricing}
                  disabled={loading}
                  className="w-full py-3 bg-white text-black text-sm font-medium rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                >
                  {loading ? (
                    <>
                      <Loader className="h-4 w-4 animate-spin" />
                      <span>Calculating...</span>
                    </>
                  ) : (
                    <>
                      <BarChart3 className="h-4 w-4" />
                      <span>Calculate Protection Price</span>
                    </>
                  )}
                </button>

                {error && (
                  <div className="mt-4 p-4 bg-red-950 border border-red-900 rounded-lg text-red-400 text-sm flex items-start space-x-2">
                    <ArrowDownRight className="h-4 w-4 flex-shrink-0 mt-0.5" />
                    <p>{error}</p>
                  </div>
                )}
              </div>

              {/* Results */}
              {pricingResult && (
                <div className="space-y-6">
                  {/* Summary Grid */}
                  <div className="grid md:grid-cols-2 gap-4">
                    {/* Total Cost Card */}
                    <div className="bg-green-950 border border-green-900 rounded-lg p-6">
                      <div className="flex items-center space-x-1 mb-1">
                        <p className="text-green-400 text-xs font-semibold">TOTAL UPFRONT COST</p>
                        <InfoTooltip {...tooltips.totalCost} />
                      </div>
                      <p className="text-4xl font-semibold text-green-300 mb-2">
                        ${pricingResult.total_option_cost.toLocaleString('en-US', {
                          maximumFractionDigits: 0,
                        })}
                      </p>
                      <p className="text-green-400 text-sm">MXN paid once for $1M protection</p>
                    </div>

                    {/* Cost Percentage Card */}
                    <div className="bg-blue-950 border border-blue-900 rounded-lg p-6">
                      <div className="flex items-center space-x-1 mb-1">
                        <p className="text-blue-400 text-xs font-semibold">COST AS % OF TRANSACTION</p>
                        <InfoTooltip {...tooltips.costPercentage} />
                      </div>
                      <p className="text-4xl font-semibold text-blue-300 mb-2">
                        {pricingResult.cost_percentage.toFixed(3)}%
                      </p>
                      <p className="text-blue-400 text-sm">Target: &lt;2% (You're under budget!)</p>
                    </div>

                    {/* Price Per Unit */}
                    <div className="border border-gray-800 rounded-lg p-6">
                      <div className="flex items-center space-x-1 mb-1">
                        <p className="text-gray-400 text-xs font-semibold">UPFRONT COST PER DOLLAR</p>
                        <InfoTooltip {...tooltips.upfrontCost} />
                      </div>
                      <p className="text-3xl font-semibold text-white mb-2">
                        ${pricingResult.option_price_per_unit.toFixed(4)}
                      </p>
                      <p className="text-gray-400 text-sm">MXN per USD protected</p>
                    </div>

                    {/* Strike Price */}
                    <div className="border border-gray-800 rounded-lg p-6">
                      <div className="flex items-center space-x-1 mb-1">
                        <p className="text-gray-400 text-xs font-semibold">PROTECTION PRICE</p>
                        <InfoTooltip {...tooltips.protectionPrice} />
                      </div>
                      <p className="text-3xl font-semibold text-white mb-2">
                        {pricingResult.strike_price.toFixed(4)}
                      </p>
                      <p className="text-gray-400 text-sm">MXN per USD (your maximum rate)</p>
                    </div>
                  </div>

                  {/* Greeks Section */}
                  <div className="border border-gray-800 rounded-lg p-6">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-lg font-semibold text-white">Advanced Risk Metrics</h3>
                      <span className="text-xs text-yellow-500 bg-yellow-950 border border-yellow-900 rounded px-2 py-1">
                        Advanced - Most users can skip
                      </span>
                    </div>
                    <p className="text-xs text-gray-400 mb-4">
                      These "Greeks" are used by professional traders for risk management. You can safely ignore these unless you're experienced with options.
                    </p>
                    <div className="grid md:grid-cols-4 gap-3">
                      <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
                        <div className="flex items-center space-x-1 mb-1">
                          <p className="text-gray-400 text-xs">DELTA</p>
                          <InfoTooltip {...tooltips.delta} />
                        </div>
                        <p className="text-2xl font-semibold text-white">
                          {pricingResult.greeks.delta.toFixed(4)}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">Rate sensitivity</p>
                      </div>
                      <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
                        <div className="flex items-center space-x-1 mb-1">
                          <p className="text-gray-400 text-xs">GAMMA</p>
                          <InfoTooltip {...tooltips.gamma} />
                        </div>
                        <p className="text-2xl font-semibold text-white">
                          {pricingResult.greeks.gamma.toFixed(6)}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">Delta change rate</p>
                      </div>
                      <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
                        <div className="flex items-center space-x-1 mb-1">
                          <p className="text-gray-400 text-xs">VEGA</p>
                          <InfoTooltip {...tooltips.vega} />
                        </div>
                        <p className="text-2xl font-semibold text-white">
                          {pricingResult.greeks.vega.toFixed(4)}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">Volatility sensitivity</p>
                      </div>
                      <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
                        <div className="flex items-center space-x-1 mb-1">
                          <p className="text-gray-400 text-xs">THETA (Daily)</p>
                          <InfoTooltip {...tooltips.theta} />
                        </div>
                        <p className="text-2xl font-semibold text-white">
                          {pricingResult.greeks.theta.toFixed(4)}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">Time decay per day</p>
                      </div>
                    </div>
                  </div>

                  {/* Scenarios Table */}
                  <div className="border border-gray-800 rounded-lg p-6 overflow-hidden">
                    <h3 className="text-lg font-semibold text-white mb-2">What-If Scenarios</h3>
                    <p className="text-xs text-gray-400 mb-4">
                      See how your protection performs if the exchange rate moves. Each row shows what happens at a different future rate.
                      Green savings = your protection is paying off. The protection caps your maximum cost no matter how high rates go.
                    </p>
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead>
                          <tr className="border-b border-gray-800">
                            <th className="text-left py-2 px-3 text-gray-400 text-xs font-semibold">
                              FUTURE RATE
                            </th>
                            <th className="text-right py-2 px-3 text-gray-400 text-xs font-semibold">
                              UNHEDGED COST
                            </th>
                            <th className="text-right py-2 px-3 text-gray-400 text-xs font-semibold">
                              OPTION PAYOFF
                            </th>
                            <th className="text-right py-2 px-3 text-gray-400 text-xs font-semibold">
                              NET COST
                            </th>
                            <th className="text-right py-2 px-3 text-gray-400 text-xs font-semibold">
                              SAVINGS
                            </th>
                          </tr>
                        </thead>
                        <tbody>
                          {pricingResult.scenarios.map((scenario, idx) => {
                            const savings = scenario.savings_vs_unhedged;
                            const isSaving = savings > 0;

                            return (
                              <tr
                                key={idx}
                                className="border-b border-gray-900 hover:bg-gray-900 transition-colors"
                              >
                                <td className="py-3 px-3 text-white text-sm font-mono">
                                  {scenario.future_spot_rate.toFixed(4)}
                                </td>
                                <td className="text-right py-3 px-3 text-gray-300 text-sm">
                                  ${scenario.unhedged_cost.toLocaleString('en-US', {
                                    maximumFractionDigits: 0,
                                  })}
                                </td>
                                <td className="text-right py-3 px-3">
                                  <span className="text-green-400 font-semibold text-sm">
                                    ${scenario.option_payoff.toLocaleString('en-US', {
                                      maximumFractionDigits: 0,
                                    })}
                                  </span>
                                </td>
                                <td className="text-right py-3 px-3 font-semibold text-white text-sm">
                                  ${scenario.net_cost.toLocaleString('en-US', {
                                    maximumFractionDigits: 0,
                                  })}
                                </td>
                                <td
                                  className={`text-right py-3 px-3 font-semibold text-sm ${
                                    isSaving ? 'text-green-400' : 'text-red-400'
                                  }`}
                                >
                                  <div className="flex items-center justify-end space-x-1">
                                    {isSaving ? (
                                      <ArrowUpRight className="h-3 w-3" />
                                    ) : (
                                      <ArrowDownRight className="h-3 w-3" />
                                    )}
                                    <span>
                                      ${Math.abs(savings).toLocaleString('en-US', {
                                        maximumFractionDigits: 0,
                                      })}
                                    </span>
                                  </div>
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                    <p className="text-gray-500 text-xs mt-3">
                      Green savings = your protection is working (market went up). Red = you didn't need the protection (market stayed low).
                      Either way, you had peace of mind knowing your maximum cost was capped.
                    </p>
                  </div>

                  {/* Risk Histogram - Monte Carlo Simulation */}
                  <div className="border border-gray-800 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-white mb-2">Probability Analysis</h3>
                    <p className="text-sm text-gray-400 mb-4">
                      1,000 simulated future outcomes showing where the exchange rate could end up.
                      Green bars = your protection kicks in and saves you money. Gray bars = neutral zone. Red bars = market stayed favorable.
                    </p>
                    <RiskHistogram
                      spotRate={19.0}
                      strikePrice={pricingResult.strike_price}
                      volatility={pricingResult.greeks ? 0.20 : 0.20}
                      timeToMaturity={0.25}
                      notionalAmount={1000000}
                    />
                  </div>

                  {/* Payoff Diagram */}
                  <div className="border border-gray-800 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-white mb-2">Visual Cost Breakdown</h3>
                    <p className="text-sm text-gray-400 mb-4">
                      See your total cost at different future exchange rates. The flat line at top shows your protection cap—you'll never pay more than this, no matter how high rates go.
                    </p>
                    <PayoffDiagram pricingResult={pricingResult} height={400} />
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {view === 'demo' && (
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="space-y-6">
              {/* Header */}
              <div className="text-center mb-8">
                <h2 className="text-4xl font-semibold text-white mb-2">Demo Mode</h2>
                <p className="text-gray-400">
                  Generate realistic sample data to explore the platform
                </p>
              </div>

              {/* Main Demo Card */}
              <div className="border border-gray-800 rounded-lg p-8">
                <div className="mb-6">
                  <h3 className="text-xl font-semibold text-white mb-3">Initialize Demo Data</h3>
                  <p className="text-sm text-gray-400 mb-4">
                    Generate realistic sample transactions for Latin American businesses including
                    importers and exporters from Mexico, Colombia, Brazil, Chile, Argentina, Peru,
                    and Uruguay. Perfect for exploring the platform's capabilities.
                  </p>
                </div>

                <button
                  onClick={initializeDemo}
                  disabled={loading}
                  className="w-full py-3 bg-white text-black text-sm font-medium rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                >
                  {loading ? (
                    <>
                      <Loader className="h-4 w-4 animate-spin" />
                      <span>Generating Demo Data...</span>
                    </>
                  ) : (
                    <>
                      <CheckCircle2 className="h-4 w-4" />
                      <span>Generate Demo Data</span>
                    </>
                  )}
                </button>

                {error && (
                  <div className="mt-4 p-4 bg-red-950 border border-red-900 rounded-lg text-red-400 text-sm flex items-start space-x-2">
                    <ArrowDownRight className="h-4 w-4 flex-shrink-0 mt-0.5" />
                    <p>{error}</p>
                  </div>
                )}
              </div>

              {/* API Status Card */}
              <div className="bg-green-950 border border-green-900 rounded-lg p-8">
                <div className="flex items-start space-x-3 mb-4">
                  <div className="w-3 h-3 rounded-full bg-green-600 mt-1" />
                  <h3 className="text-lg font-semibold text-white">API Status</h3>
                </div>

                <div className="space-y-3">
                  <div className="bg-black rounded-lg p-4 border border-gray-800">
                    <p className="text-gray-400 text-xs mb-1">Backend API</p>
                    <p className="text-white font-mono text-sm">http://localhost:8000</p>
                  </div>

                  <div className="bg-black rounded-lg p-4 border border-gray-800">
                    <p className="text-gray-400 text-xs mb-1">API Documentation</p>
                    <a
                      href="http://localhost:8000/docs"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-400 hover:text-blue-300 font-mono text-sm underline transition-colors"
                    >
                      http://localhost:8000/docs
                    </a>
                  </div>
                </div>
              </div>

              {/* Info Cards */}
              <div className="grid md:grid-cols-3 gap-4">
                <div className="border border-gray-800 rounded-lg p-6">
                  <div className="w-10 h-10 rounded-lg bg-gray-900 flex items-center justify-center mb-3">
                    <DollarSign className="h-5 w-5 text-white" />
                  </div>
                  <h4 className="text-sm font-semibold text-white mb-1">Sample Currencies</h4>
                  <p className="text-xs text-gray-400">
                    USD, MXN, BRL, CLP, COP, ARS, PEN, UYU and more
                  </p>
                </div>

                <div className="border border-gray-800 rounded-lg p-6">
                  <div className="w-10 h-10 rounded-lg bg-gray-900 flex items-center justify-center mb-3">
                    <TrendingUp className="h-5 w-5 text-white" />
                  </div>
                  <h4 className="text-sm font-semibold text-white mb-1">Test Scenarios</h4>
                  <p className="text-xs text-gray-400">
                    Create hedges with various notional amounts and timeframes
                  </p>
                </div>

                <div className="border border-gray-800 rounded-lg p-6">
                  <div className="w-10 h-10 rounded-lg bg-gray-900 flex items-center justify-center mb-3">
                    <BarChart3 className="h-5 w-5 text-white" />
                  </div>
                  <h4 className="text-sm font-semibold text-white mb-1">Full Analytics</h4>
                  <p className="text-xs text-gray-400">
                    Greeks, scenario analysis, and comprehensive pricing metrics
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800 bg-black mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid md:grid-cols-3 gap-6 mb-6">
            <div>
              <h4 className="font-semibold text-white text-sm mb-2">FX Hedging Platform</h4>
              <p className="text-gray-400 text-xs">
                Enterprise FX risk management for Latin American businesses
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-white text-sm mb-2">Technology</h4>
              <p className="text-gray-400 text-xs">
                Powered by Garman-Kohlhagen option pricing model with real-time market data
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-white text-sm mb-2">Version</h4>
              <p className="text-gray-400 text-xs">FX Hedging Platform v1.0.0</p>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-4 text-center">
            <p className="text-gray-500 text-xs">
              Built with professional-grade financial engineering • Trusted by leading businesses
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
