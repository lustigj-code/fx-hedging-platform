import React, { useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
  ResponsiveContainer,
} from 'recharts';

type RiskHistogramProps = {
  spotRate: number;
  strikePrice: number;
  volatility: number;
  timeToMaturity: number;
  notionalAmount: number;
};

type HistogramBin = {
  range: string;
  lowerBound: number;
  upperBound: number;
  frequency: number;
  protectedZone: number;
  loss: number;
  neutral: number;
};

type SimulationResult = {
  spotRate: number;
  pnl: number;
  isProtected: boolean;
  isLoss: boolean;
};

type OutcomeProbabilities = {
  protectedProbability: number;
  lossProbability: number;
  neutralProbability: number;
  expectedSpotRate: number;
  medianSpotRate: number;
  worstCase: number;
  bestCase: number;
  maxLoss: number;
  maxGain: number;
};

/**
 * RiskHistogram Component
 *
 * Visualizes the distribution of potential FX outcomes using Monte Carlo simulation
 * with Geometric Brownian Motion (GBM) model.
 */
const RiskHistogram: React.FC<RiskHistogramProps> = ({
  spotRate,
  strikePrice,
  volatility,
  timeToMaturity,
  notionalAmount,
}) => {
  // Generate Monte Carlo simulation and compute statistics
  const { histogramData, probabilities } = useMemo(() => {
    // Constants for simulation
    const numScenarios = 1000;
    const riskFreeRate = 0; // Risk-neutral measure
    const dt = timeToMaturity;

    // Simulate future spot rates using GBM
    const simulate = (): SimulationResult[] => {
      const results: SimulationResult[] = [];

      for (let i = 0; i < numScenarios; i++) {
        // Generate standard normal random variable using Box-Muller transform
        const u1 = Math.random();
        const u2 = Math.random();
        const z = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);

        // GBM formula: S_T = S_0 * exp((mu - sigma^2/2)*T + sigma*sqrt(T)*Z)
        const drift = (riskFreeRate - (volatility * volatility) / 2) * dt;
        const diffusion = volatility * Math.sqrt(dt) * z;
        const futureSpotRate = spotRate * Math.exp(drift + diffusion);

        // Calculate P&L
        const pnl = (strikePrice - futureSpotRate) * notionalAmount;
        const isProtected = futureSpotRate < strikePrice;
        const isLoss = pnl < 0;

        results.push({
          spotRate: futureSpotRate,
          pnl,
          isProtected,
          isLoss,
        });
      }

      return results;
    };

    const results = simulate();

    // Create histogram bins
    const min = Math.min(...results.map((r) => r.spotRate));
    const max = Math.max(...results.map((r) => r.spotRate));
    const range = max - min;
    const binCount = 30;
    const binWidth = range / binCount;

    const bins: HistogramBin[] = [];

    for (let i = 0; i < binCount; i++) {
      const lowerBound = min + i * binWidth;
      const upperBound = lowerBound + binWidth;

      const binnedResults = results.filter(
        (r) => r.spotRate >= lowerBound && r.spotRate < upperBound
      );

      const protectedZone = binnedResults.filter((r) => r.isProtected).length;
      const loss = binnedResults.filter((r) => r.isLoss).length;
      const neutral = binnedResults.length - protectedZone;

      if (binnedResults.length > 0) {
        bins.push({
          range: `${lowerBound.toFixed(2)}-${upperBound.toFixed(2)}`,
          lowerBound,
          upperBound,
          frequency: binnedResults.length,
          protectedZone,
          loss,
          neutral,
        });
      }
    }

    // Calculate probability statistics
    const protectedCount = results.filter((r) => r.isProtected).length;
    const lossCount = results.filter((r) => r.isLoss).length;
    const neutralCount = results.length - protectedCount;

    const sortedRates = results.map((r) => r.spotRate).sort((a, b) => a - b);
    const expectedSpotRate =
      results.reduce((sum, r) => sum + r.spotRate, 0) / results.length;
    const medianSpotRate = sortedRates[Math.floor(sortedRates.length / 2)];
    const worstCase = sortedRates[0];
    const bestCase = sortedRates[sortedRates.length - 1];

    const maxLoss = Math.min(...results.map((r) => r.pnl));
    const maxGain = Math.max(...results.map((r) => r.pnl));

    const probs: OutcomeProbabilities = {
      protectedProbability: (protectedCount / results.length) * 100,
      lossProbability: (lossCount / results.length) * 100,
      neutralProbability: (neutralCount / results.length) * 100,
      expectedSpotRate,
      medianSpotRate,
      worstCase,
      bestCase,
      maxLoss,
      maxGain,
    };

    return {
      histogramData: bins,
      probabilities: probs,
    };
  }, [spotRate, strikePrice, volatility, timeToMaturity, notionalAmount]);

  // Custom tooltip for better readability
  const CustomTooltip = (props: any) => {
    const { active, payload } = props;
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-300 rounded shadow-lg">
          <p className="text-sm font-semibold text-gray-800">
            Rate Range: {data.range}
          </p>
          <p className="text-sm text-green-600">
            Protected: {data.protectedZone}
          </p>
          <p className="text-sm text-red-600">Loss: {data.loss}</p>
          <p className="text-sm text-gray-600">Neutral: {data.neutral}</p>
          <p className="text-sm font-semibold text-gray-800">
            Total: {data.frequency}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full bg-white rounded-lg shadow-lg p-6">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          FX Risk Distribution Analysis
        </h2>
        <p className="text-sm text-gray-600">
          Monte Carlo simulation of {1000} scenarios showing potential FX outcomes
        </p>
      </div>

      {/* Key Statistics Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <p className="text-xs font-semibold text-blue-700 uppercase tracking-wide">
            Current Spot Rate
          </p>
          <p className="text-2xl font-bold text-blue-900 mt-1">
            {spotRate.toFixed(4)}
          </p>
        </div>

        <div className="bg-red-50 p-4 rounded-lg border border-red-200">
          <p className="text-xs font-semibold text-red-700 uppercase tracking-wide">
            Strike Price
          </p>
          <p className="text-2xl font-bold text-red-900 mt-1">
            {strikePrice.toFixed(4)}
          </p>
        </div>

        <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
          <p className="text-xs font-semibold text-purple-700 uppercase tracking-wide">
            Volatility
          </p>
          <p className="text-2xl font-bold text-purple-900 mt-1">
            {(volatility * 100).toFixed(1)}%
          </p>
        </div>

        <div className="bg-teal-50 p-4 rounded-lg border border-teal-200">
          <p className="text-xs font-semibold text-teal-700 uppercase tracking-wide">
            Time to Maturity
          </p>
          <p className="text-2xl font-bold text-teal-900 mt-1">
            {timeToMaturity.toFixed(2)} yrs
          </p>
        </div>
      </div>

      {/* Histogram Chart */}
      <div className="mb-6 border border-gray-200 rounded-lg p-4 bg-gray-50">
        <ResponsiveContainer width="100%" height={400}>
          <BarChart
            data={histogramData}
            margin={{ top: 20, right: 30, left: 0, bottom: 60 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis
              angle={-45}
              textAnchor="end"
              height={100}
              tick={{ fontSize: 11 }}
              label={{ value: 'Future Spot Rate', position: 'insideBottomRight', offset: -20 }}
            />
            <YAxis
              label={{ value: 'Frequency (scenarios)', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ paddingTop: '20px' }}
              iconType="square"
            />

            {/* Stacked bars for different outcome categories */}
            <Bar dataKey="protectedZone" stackId="a" fill="#10b981" name="Protected Zone" />
            <Bar dataKey="neutral" stackId="a" fill="#9ca3af" name="Neutral" />
            <Bar dataKey="loss" stackId="a" fill="#ef4444" name="Loss" />

            {/* Reference lines for spot rate and strike */}
            <ReferenceLine
              x={histogramData.find(
                (d) =>
                  d.lowerBound <= spotRate && spotRate < d.upperBound
              )?.range}
              stroke="#3b82f6"
              strokeDasharray="5 5"
              label={{
                value: `Current Spot: ${spotRate.toFixed(4)}`,
                position: 'top',
                fill: '#1e40af',
                fontSize: 12,
                fontWeight: 'bold',
              }}
            />
            <ReferenceLine
              x={histogramData.find(
                (d) =>
                  d.lowerBound <= strikePrice && strikePrice < d.upperBound
              )?.range}
              stroke="#dc2626"
              strokeWidth={2}
              label={{
                value: `Strike: ${strikePrice.toFixed(4)}`,
                position: 'top',
                fill: '#7f1d1d',
                fontSize: 12,
                fontWeight: 'bold',
              }}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Outcome Probabilities */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <div className="bg-green-50 p-4 rounded-lg border border-green-300">
          <p className="text-sm font-semibold text-green-800 mb-2">
            Downside Protected
          </p>
          <p className="text-3xl font-bold text-green-600">
            {probabilities.protectedProbability.toFixed(1)}%
          </p>
          <p className="text-xs text-green-700 mt-1">
            Rate below strike price
          </p>
        </div>

        <div className="bg-red-50 p-4 rounded-lg border border-red-300">
          <p className="text-sm font-semibold text-red-800 mb-2">
            Loss Probability
          </p>
          <p className="text-3xl font-bold text-red-600">
            {probabilities.lossProbability.toFixed(1)}%
          </p>
          <p className="text-xs text-red-700 mt-1">
            P&L would be negative
          </p>
        </div>

        <div className="bg-gray-50 p-4 rounded-lg border border-gray-300">
          <p className="text-sm font-semibold text-gray-800 mb-2">
            Neutral Zone
          </p>
          <p className="text-3xl font-bold text-gray-600">
            {probabilities.neutralProbability.toFixed(1)}%
          </p>
          <p className="text-xs text-gray-700 mt-1">
            Between current & strike
          </p>
        </div>
      </div>

      {/* Detailed Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="border border-gray-300 rounded-lg p-4">
          <h3 className="font-semibold text-gray-800 mb-3 flex items-center">
            <span className="w-3 h-3 bg-blue-500 rounded-full mr-2"></span>
            Spot Rate Statistics
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Expected Rate:</span>
              <span className="font-semibold text-gray-800">
                {probabilities.expectedSpotRate.toFixed(4)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Median Rate:</span>
              <span className="font-semibold text-gray-800">
                {probabilities.medianSpotRate.toFixed(4)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Best Case:</span>
              <span className="font-semibold text-green-600">
                {probabilities.bestCase.toFixed(4)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Worst Case:</span>
              <span className="font-semibold text-red-600">
                {probabilities.worstCase.toFixed(4)}
              </span>
            </div>
          </div>
        </div>

        <div className="border border-gray-300 rounded-lg p-4">
          <h3 className="font-semibold text-gray-800 mb-3 flex items-center">
            <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
            P&L Statistics (Notional: {notionalAmount.toLocaleString()})
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Max Gain:</span>
              <span className="font-semibold text-green-600">
                {(probabilities.maxGain / 1000).toFixed(0)}K
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Max Loss:</span>
              <span className="font-semibold text-red-600">
                {(probabilities.maxLoss / 1000).toFixed(0)}K
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Range:</span>
              <span className="font-semibold text-gray-800">
                {((probabilities.maxGain - probabilities.maxLoss) / 1000).toFixed(0)}K
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Strike Protection Value:</span>
              <span className="font-semibold text-blue-600">
                {((strikePrice - probabilities.worstCase) * notionalAmount / 1000).toFixed(0)}K
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-6 p-4 bg-gray-100 rounded-lg border border-gray-300">
        <p className="text-xs text-gray-700">
          <strong>Disclaimer:</strong> This analysis is for illustrative purposes only and uses a simplified
          Geometric Brownian Motion model with risk-neutral measures. Actual FX movements may vary
          significantly. Consult with financial advisors before making hedging decisions.
        </p>
      </div>
    </div>
  );
};

export default RiskHistogram;
