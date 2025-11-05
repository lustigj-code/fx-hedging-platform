/**
 * API Client for FX Hedging Platform
 *
 * Centralized API communication with the FastAPI backend.
 */
import axios from 'axios';

const API_BASE_URL = (import.meta as unknown as { env: { VITE_API_URL?: string } }).env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export type TransactionType = 'import' | 'export';

export type Transaction = {
  id?: number;
  transaction_type: TransactionType;
  invoice_date: string;
  payment_date: string;
  foreign_currency: string;
  functional_currency: string;
  notional_amount: number;
  spot_rate_at_invoice?: number;
  invoice_reference?: string;
  description?: string;
  source?: string;
};

export type PricingRequest = {
  spot_rate: number;
  strike_price?: number;
  time_to_maturity_years: number;
  volatility: number;
  domestic_rate: number;
  foreign_rate: number;
  notional_amount: number;
  option_type: 'call' | 'put';
  protection_level: number;
};

export type PricingResponse = {
  option_price_per_unit: number;
  total_option_cost: number;
  cost_percentage: number;
  strike_price: number;
  protection_level: number;
  max_cost_to_firm: number;
  d1: number;
  d2: number;
  greeks: {
    delta: number;
    gamma: number;
    vega: number;
    theta: number;
  };
  scenarios: Array<{
    future_spot_rate: number;
    unhedged_cost: number;
    option_payoff: number;
    net_cost: number;
    savings_vs_unhedged: number;
  }>;
  payoff_curve: Array<{
    spot_rate: number;
    unhedged_pnl: number;
    option_payoff: number;
    net_pnl: number;
  }>;
  breakeven_rate: number;
};

// API Methods
export const apiClient = {
  // Demo
  async generateDemoData() {
    return api.post('/api/demo/generate');
  },

  async seedCurrencies() {
    return api.post('/api/demo/seed-currencies');
  },

  async resetDemo() {
    return api.post('/api/demo/reset');
  },

  // Transactions
  async getTransactions() {
    return api.get<Transaction[]>('/api/transactions/');
  },

  async createTransaction(transaction: Transaction) {
    return api.post<Transaction>('/api/transactions/', transaction);
  },

  async getTransaction(id: number) {
    return api.get<Transaction>(`/api/transactions/${id}`);
  },

  // Pricing
  async calculatePricing(request: PricingRequest) {
    return api.post<PricingResponse>('/api/pricing/calculate', request);
  },

  async calculatePricingAuto(params: {
    base: string;
    quote: string;
    time_to_maturity_years: number;
    notional_amount: number;
    option_type?: string;
    protection_level?: number;
  }) {
    return api.post<PricingResponse>('/api/pricing/calculate-auto', null, { params });
  },

  // Exchange Rates
  async getCurrentRate(base: string, quote: string) {
    return api.get('/api/rates/current', { params: { base, quote } });
  },

  // Volatility
  async getVolatility(currencyPair: string) {
    return api.get(`/api/volatility/${currencyPair}`);
  },

  // Portfolio
  async getPortfolioSummary() {
    return api.get('/api/portfolio/summary');
  },

  async getExposures() {
    return api.get('/api/portfolio/exposures');
  },

  // Hedges
  async getHedges() {
    return api.get('/api/hedges/');
  },

  async createHedge(hedge: any) {
    return api.post('/api/hedges/', hedge);
  },

  // Health check
  async healthCheck() {
    return api.get('/health');
  },
};

export default api;
