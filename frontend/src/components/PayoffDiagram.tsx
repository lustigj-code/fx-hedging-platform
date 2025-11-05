import React, { useMemo } from 'react';
import {
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  ComposedChart,
} from 'recharts';
import type { PricingResponse } from '../services/api';

type PayoffDiagramProps = {
  pricingResult: PricingResponse;
  title?: string;
  height?: number;
};

/**
 * PayoffDiagram Component
 *
 * Visualizes option payoff curves showing:
 * - Unhedged P&L (baseline exposure)
 * - Option Payoff (protection benefit)
 * - Net P&L (combined effect)
 *
 * Shows how options cap downside while preserving upside potential.
 */
export const PayoffDiagram: React.FC<PayoffDiagramProps> = ({
  pricingResult,
  title = 'Option Payoff Diagram',
  height = 400,
}) => {
  // Transform payoff_curve data for visualization
  const chartData = useMemo(() => {
    return pricingResult.payoff_curve.map((point) => ({
      spotRate: point.spot_rate,
      unhedgedPnL: point.unhedged_pnl,
      optionPayoff: point.option_payoff,
      netPnL: point.net_pnl,
    }));
  }, [pricingResult.payoff_curve]);

  // Find key rates for reference lines
  const currentSpot = chartData[Math.floor(chartData.length / 2)]?.spotRate || 0;
  const strikePrice = pricingResult.strike_price;
  const breakEvenRate = pricingResult.breakeven_rate;

  // Custom tooltip for detailed information
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-300 rounded shadow-lg">
          <p className="font-semibold text-sm text-gray-900">
            Spot Rate: {data.spotRate.toFixed(4)}
          </p>
          <p className="text-xs text-gray-600 mt-1">
            <span className="inline-block w-12 h-2 bg-blue-500 rounded mr-2"></span>
            Unhedged: ${data.unhedgedPnL.toLocaleString(undefined, { maximumFractionDigits: 2 })}
          </p>
          <p className="text-xs text-gray-600 mt-1">
            <span className="inline-block w-12 h-2 bg-green-500 rounded mr-2"></span>
            Option: ${data.optionPayoff.toLocaleString(undefined, { maximumFractionDigits: 2 })}
          </p>
          <p className="text-xs text-gray-600 mt-1">
            <span className="inline-block w-12 h-2 bg-purple-600 rounded mr-2"></span>
            Net P&L: ${data.netPnL.toLocaleString(undefined, { maximumFractionDigits: 2 })}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full bg-white rounded-lg shadow-md p-6">
      {/* Header */}
      <div className="mb-6">
        <h3 className="text-xl font-bold text-gray-900">{title}</h3>
        <p className="text-sm text-gray-600 mt-1">
          Payoff curves showing how the option hedge protects against adverse FX movements
        </p>
      </div>

      {/* Chart Container */}
      <div className="w-full overflow-x-auto">
        <ResponsiveContainer width="100%" height={height}>
          <ComposedChart data={chartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
            {/* Grid */}
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#e5e7eb"
              vertical={true}
              horizontal={true}
            />

            {/* Axes */}
            <XAxis
              dataKey="spotRate"
              label={{
                value: 'Future Spot Rate',
                position: 'insideBottomRight',
                offset: -5,
                className: 'text-xs font-medium text-gray-700',
              }}
              tickFormatter={(value) => value.toFixed(2)}
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
            />
            <YAxis
              label={{
                value: 'Profit / Loss ($)',
                angle: -90,
                position: 'insideLeft',
                className: 'text-xs font-medium text-gray-700',
              }}
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
              tickFormatter={(value) =>
                `$${(value / 1000).toFixed(0)}K`
              }
            />

            {/* Reference Lines */}
            <ReferenceLine
              x={currentSpot}
              stroke="#9ca3af"
              strokeDasharray="5 5"
              label={{
                value: 'Current Spot',
                position: 'top',
                fill: '#6b7280',
                fontSize: 11,
              }}
            />
            <ReferenceLine
              x={strikePrice}
              stroke="#f59e0b"
              strokeDasharray="5 5"
              label={{
                value: `Strike: ${strikePrice.toFixed(4)}`,
                position: 'top',
                fill: '#d97706',
                fontSize: 11,
              }}
            />
            <ReferenceLine
              y={0}
              stroke="#6b7280"
              strokeWidth={1}
              label={{
                value: 'Breakeven',
                position: 'right',
                fill: '#6b7280',
                fontSize: 11,
              }}
            />

            {/* Unhedged P&L Line (Blue) */}
            <Line
              type="monotone"
              dataKey="unhedgedPnL"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={false}
              isAnimationActive={true}
              name="Unhedged P&L"
              legendType="line"
            />

            {/* Option Payoff Line (Green) */}
            <Line
              type="linear"
              dataKey="optionPayoff"
              stroke="#10b981"
              strokeWidth={2}
              dot={false}
              isAnimationActive={true}
              name="Option Payoff"
              legendType="line"
            />

            {/* Net P&L Line (Purple - Bold) */}
            <Line
              type="monotone"
              dataKey="netPnL"
              stroke="#7c3aed"
              strokeWidth={3}
              dot={false}
              isAnimationActive={true}
              name="Net P&L (Hedged)"
              legendType="line"
            />

            {/* Custom Tooltip */}
            <Tooltip content={<CustomTooltip />} />

            {/* Legend */}
            <Legend
              wrapperStyle={{
                paddingTop: '20px',
              }}
              iconType="line"
              formatter={(value) => <span className="text-sm font-medium">{value}</span>}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Key Metrics Box */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
          <p className="text-xs font-semibold text-blue-900 uppercase tracking-wide">Current Spot</p>
          <p className="text-lg font-bold text-blue-700 mt-1">{currentSpot.toFixed(4)}</p>
        </div>

        <div className="bg-orange-50 rounded-lg p-4 border border-orange-200">
          <p className="text-xs font-semibold text-orange-900 uppercase tracking-wide">
            Strike Price
          </p>
          <p className="text-lg font-bold text-orange-700 mt-1">{strikePrice.toFixed(4)}</p>
        </div>

        <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
          <p className="text-xs font-semibold text-purple-900 uppercase tracking-wide">
            Breakeven Rate
          </p>
          <p className="text-lg font-bold text-purple-700 mt-1">{breakEvenRate.toFixed(4)}</p>
        </div>
      </div>

      {/* Explanation */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
        <h4 className="font-semibold text-sm text-gray-900 mb-2">How to Read This Chart:</h4>
        <ul className="text-sm text-gray-700 space-y-1">
          <li className="flex items-start">
            <span className="inline-block w-2 h-2 bg-blue-500 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
            <span>
              <strong>Unhedged P&L (Blue):</strong> Your profit/loss if you don't hedge. Losses
              increase as rates move against you.
            </span>
          </li>
          <li className="flex items-start">
            <span className="inline-block w-2 h-2 bg-green-500 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
            <span>
              <strong>Option Payoff (Green):</strong> The protective benefit from your option.
              Becomes valuable when rates move against you.
            </span>
          </li>
          <li className="flex items-start">
            <span className="inline-block w-2 h-2 bg-purple-600 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
            <span>
              <strong>Net P&L (Purple):</strong> Your actual P&L with the hedge in place. Notice
              the downside is capped while upside is preserved.
            </span>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default PayoffDiagram;
